#!/usr/bin/env python3
"""
Summarize tradingagents backtest / LLM logs: group warnings and errors by kind, count lines.

Reads a log file (default: ``run.log`` in repo root) and prints buckets + short samples.

Usage (repo root):
  .venv/bin/python scripts/analyze_run_log.py
  .venv/bin/python scripts/analyze_run_log.py path/to/other.log --samples 3
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path


def classify_line(ln: str) -> str:
    if "UserWarning: Pydantic serializer" in ln or "PydanticSerializationUnexpectedValue" in ln:
        return "A_pydantic_serialization_parsed_mismatch"
    if "DeprecationWarning" in ln:
        return "B_deprecation_langchain_or_python"
    if ln.startswith("WARNING"):
        if "invoke_fallback:" in ln:
            if "LengthFinishReasonError" in ln:
                return "C_structured_llm_output_length_limit_fallback"
            if "ValidationError" in ln and "InvestmentPlanJudgment" in ln:
                return "D_structured_llm_validation_investment_plan"
            if "TypeError" in ln and "NoneType" in ln:
                return "E_structured_llm_parse_empty_choices_typedef"
            if "structured invoke failed" in ln.lower():
                return "F_structured_invoke_failed_other"
            return "G_invoke_fallback_warning_other"
        if "openai_client:" in ln:
            if "LLM provider error" in ln:
                return "H_llm_upstream_provider_retry"
            if "LLM TypeError" in ln:
                return "I_openai_parse_typedef_llm_client"
            return "J_openai_client_warning_other"
        if "kite_stock:" in ln:
            if "Connection reset by peer" in ln:
                return "K_kite_connection_reset_retry"
            return "L_kite_warning_other"
        return "M_warning_uncategorized"
    if "ValidationError" in ln and "InvestmentPlanJudgment" in ln:
        return "N_pydantic_body_investment_plan_judgment"
    if ln.strip().startswith("Traceback (most recent call last):"):
        return "O_traceback_marker_line"
    if "ERROR" in ln[:20]:
        return "P_error_level_line"
    return "Q_other_or_info"


def main() -> None:
    p = argparse.ArgumentParser(description="Group and count log line categories.")
    p.add_argument(
        "log_path",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "run.log"),
        help="Log file path (default: <repo>/run.log)",
    )
    p.add_argument(
        "--samples",
        type=int,
        default=2,
        help="Sample lines printed per bucket (default: 2)",
    )
    args = p.parse_args()
    path = Path(args.log_path)
    if not path.is_file():
        raise SystemExit(f"Not a file: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)

    for ln in lines:
        cat = classify_line(ln)
        counts[cat] += 1
        if len(samples[cat]) < args.samples and cat != "Q_other_or_info":
            samples[cat].append(ln[:240])

    print(f"File: {path} ({len(lines)} lines)\n")
    print("classification (prefix = rough severity / source)\n")

    legend = """
  A–B: dependency noise (serialization / deprecations).
  C–F: structured LLM path (fallbacks usually recover).
  H–I: provider / OpenRouter parse quirks.
  K: Kite transient network (retries).
  N: same as D but from traceback body line.
  O: traceback headers (paired with WARNING above).
"""

    total_tagged = sum(v for k, v in counts.items() if k != "Q_other_or_info")
    info_only = counts.get("Q_other_or_info", 0)
    print(f"Non-INFO-style lines (excluding plain 'other'): {total_tagged}")
    print(f"Other/INFO-style (unclassified): {info_only}")
    print(legend)

    for key in sorted(counts.keys(), key=lambda k: (-counts[k], k)):
        print(f"{counts[key]:6d}  {key}")
        for s in samples.get(key, []):
            print(f"        e.g. {s[:200]}…" if len(s) >= 200 else f"        e.g. {s}")


if __name__ == "__main__":
    main()
