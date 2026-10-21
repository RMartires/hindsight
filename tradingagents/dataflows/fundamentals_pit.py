"""Point-in-time filter for fundamental vendor text.

Statement tables from yfinance are dated on the column header, so columns
whose period ends after ``simulation_data_end`` are removed. The company
overview is one live snapshot with no per-field date, so market ratios and
trailing totals are omitted while a simulation cap is set. Live runs, where
``simulation_data_end`` is unset, are left unchanged.
"""

from __future__ import annotations

import csv
import json
import logging
import re
from io import StringIO

from tradingagents.dataflows.simulation_context import get_simulation_data_end_configured

_log = logging.getLogger(__name__)

_DATE_CELL = re.compile(r"^(\d{4}-\d{2}-\d{2})")

# Stable identity lines. Every other overview line is a live market snapshot.
_OVERVIEW_KEEP_LABELS = {"Name", "Sector", "Industry"}

_OVERVIEW_IDENTITY_JSON_KEYS = {
    "Symbol",
    "symbol",
    "Name",
    "name",
    "Sector",
    "sector",
    "Industry",
    "industry",
    "Exchange",
    "exchange",
    "Country",
    "country",
    "Currency",
    "currency",
    "AssetType",
    "FiscalYearEnd",
}


def apply_fundamentals_point_in_time(text: str, cutoff: str | None = None) -> str:
    """Drop fundamental text that is dated after the simulation cap.

    ``cutoff`` defaults to ``simulation_data_end``. When that cap is unset the
    text is returned unchanged.
    """
    cap = (cutoff if cutoff is not None else get_simulation_data_end_configured())
    if not cap or not text:
        return text
    cap = str(cap).strip()[:10]
    try:
        return _apply(text, cap)
    except Exception:
        _log.warning("fundamentals_pit_failed cutoff=%s", cap, exc_info=True)
        return (
            f"# Fundamental data omitted: point-in-time filter failed for cutoff {cap}."
        )


def _apply(text: str, cap: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        filtered = _filter_json(text, cap)
        if filtered is not None:
            return filtered
    if _statement_header_index(text) is not None:
        return _filter_statement(text, cap)
    if _looks_like_overview(text):
        return _filter_overview(text, cap)
    return text


def _statement_header_index(text: str) -> int | None:
    for i, line in enumerate(text.splitlines()):
        cells = _csv_cells(line)
        if any(_DATE_CELL.match(cell.strip()) for cell in cells):
            return i
    return None


def _looks_like_overview(text: str) -> bool:
    if "Company Fundamentals" in text:
        return True
    for line in text.splitlines():
        label, sep, _value = line.partition(":")
        if sep and label.strip() in _OVERVIEW_KEEP_LABELS:
            return True
        if label.strip() in {"Market Cap", "PE Ratio (TTM)", "52 Week High"}:
            return True
    return False


def _filter_statement(text: str, cap: str) -> str:
    lines = text.splitlines()
    header_idx = _statement_header_index(text)
    if header_idx is None:
        return text
    preamble = lines[:header_idx]
    rows = list(csv.reader(lines[header_idx:]))
    if not rows:
        return text
    header = rows[0]
    keep = [
        i
        for i, cell in enumerate(header)
        if _keep_statement_column(cell, cap)
    ]
    dated = [header[i].strip()[:10] for i in keep if _DATE_CELL.match(header[i].strip())]
    note = f"# Statement periods after {cap} omitted."
    new_preamble = [_rewrite_preamble_line(line, note) for line in preamble]
    if note not in new_preamble:
        new_preamble.append(note)
    if not dated:
        body = f"No statement periods on or before {cap}."
    else:
        trimmed = [_take_columns(row, keep) for row in rows]
        buf = StringIO()
        csv.writer(buf, lineterminator="\n").writerows(trimmed)
        body = buf.getvalue().rstrip("\n")
    head = "\n".join(new_preamble).rstrip("\n")
    return f"{head}\n\n{body}\n"


def _keep_statement_column(cell: str, cap: str) -> bool:
    match = _DATE_CELL.match(cell.strip())
    if not match:
        return True
    return match.group(1) <= cap


def _rewrite_preamble_line(line: str, note: str) -> str:
    if "Data retrieved on:" in line:
        return note
    return line


def _take_columns(row: list[str], keep: list[int]) -> list[str]:
    return [row[i] if i < len(row) else "" for i in keep]


def _filter_overview(text: str, cap: str) -> str:
    note = (
        "# Live market snapshot omitted. Dated financial statements are limited "
        f"to periods ending on or before {cap}."
    )
    kept: list[str] = []
    for line in text.splitlines():
        if line.startswith("# "):
            if "Data retrieved on:" in line:
                continue
            kept.append(line)
            continue
        label, sep, _value = line.partition(":")
        if sep and label.strip() in _OVERVIEW_KEEP_LABELS:
            kept.append(line)
    if note not in kept:
        kept.append(note)
    return "\n".join(kept).rstrip() + "\n"


def _filter_json(text: str, cap: str) -> str | None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and (
        "annualReports" in data or "quarterlyReports" in data
    ):
        for key in ("annualReports", "quarterlyReports"):
            rows = data.get(key)
            if isinstance(rows, list):
                data[key] = [
                    row
                    for row in rows
                    if isinstance(row, dict)
                    and str(row.get("fiscalDateEnding", ""))[:10] <= cap
                    and str(row.get("fiscalDateEnding", ""))[:10] != ""
                ]
        return json.dumps(data)
    if isinstance(data, dict):
        kept = {
            key: value
            for key, value in data.items()
            if key in _OVERVIEW_IDENTITY_JSON_KEYS
        }
        kept["point_in_time_note"] = (
            "Live overview fields omitted. "
            f"Statement periods after {cap} omitted."
        )
        return json.dumps(kept)
    return None


def _csv_cells(line: str) -> list[str]:
    try:
        return next(csv.reader([line]))
    except csv.Error:
        return [line]
