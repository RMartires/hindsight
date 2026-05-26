from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Dict, Optional

from tradingagents.dataflows.config import get_config

_LOG = logging.getLogger(__name__)
_STOCK_ANON_RE = re.compile(r"STOCK_\d{4}$")

# Alpha Vantage NEWS_SENTIMENT rejects exchange dots (e.g. RELIANCE.NS) but accepts
# colon forms (RELIANCE:NSE). See vendor encode/decode helpers below.
_VENDORS_COLON_EXCHANGE = frozenset({"alpha_vantage"})
_DOT_TO_COLON_SUFFIX = (
    (".NSE", ":NSE"),
    (".NS", ":NSE"),
    (".BSE", ":BSE"),
    (".BO", ":BSE"),
)


def _stable_stock_id(real: str) -> str:
    s = (real or "").strip().upper()
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    # 4 digits is enough for single-ticker runs; deterministic across runs.
    n = int(h[:8], 16) % 10_000
    return f"STOCK_{n:04d}"


@dataclass(frozen=True)
class TickerMapper:
    """Deterministic reversible mapping for a single run.

    We store the mapping in the global config (dataflows.config) so tool wrappers
    can de-anonymize tool arguments before hitting vendors, then re-scrub outputs.
    """

    real_ticker: str
    anon_ticker: str

    @staticmethod
    def for_real_ticker(real_ticker: str) -> "TickerMapper":
        return TickerMapper(real_ticker=real_ticker, anon_ticker=_stable_stock_id(real_ticker))

    def to_config_payload(self) -> Dict[str, Dict[str, str]]:
        ticker_map = {self.real_ticker: self.anon_ticker}
        return {
            "anonymization_ticker_map": ticker_map,
            "anonymization_ticker_unmap": {self.anon_ticker: self.real_ticker},
            "anonymization_ticker_scrub_aliases": build_scrub_aliases(ticker_map),
        }


def get_active_ticker_mapper(cfg: Optional[dict] = None) -> Optional[TickerMapper]:
    c = cfg or get_config()
    if not c.get("enable_anonymization"):
        return None
    m = c.get("anonymization_ticker_map") or {}
    if not isinstance(m, dict) or not m:
        return None
    real_ticker, anon_ticker = next(iter(m.items()))
    if not isinstance(real_ticker, str) or not isinstance(anon_ticker, str):
        return None
    return TickerMapper(real_ticker=real_ticker, anon_ticker=anon_ticker)


def coerce_agent_symbol(symbol: str, cfg: Optional[dict] = None) -> str:
    """Normalize agent-emitted ticker before ``deanonymize_ticker``.

    When anonymization is on and the session has a **single** mapped anonymous id,
    repair common LLM mistakes: truncated ``ST``, or a wrong ``STOCK_####`` that
    is not in the session unmap.
    """
    c = cfg or get_config()
    s = (symbol or "").strip()
    if not c.get("enable_anonymization"):
        return s
    unmap = c.get("anonymization_ticker_unmap") or {}
    if not isinstance(unmap, dict) or not unmap:
        return s
    if s in unmap:
        return s
    if len(unmap) != 1:
        return s
    only_anon = next(iter(unmap.keys()))
    if not isinstance(only_anon, str):
        return s
    if s == "ST" or (_STOCK_ANON_RE.match(s) and s not in unmap):
        _LOG.info(
            "coerce_agent_symbol: replacing agent symbol %r with session ticker %r",
            s,
            only_anon,
        )
        return only_anon
    return s


def encode_ticker_for_vendor(canonical: str, vendor: str) -> str:
    """Return a vendor-safe ticker while keeping canonical form in the session map."""
    primary = (vendor or "").strip().lower().split(",")[0]
    if primary not in _VENDORS_COLON_EXCHANGE:
        return (canonical or "").strip()
    s = (canonical or "").strip().upper()
    for dot_suffix, colon_suffix in _DOT_TO_COLON_SUFFIX:
        if s.endswith(dot_suffix):
            return s[: -len(dot_suffix)] + colon_suffix
    return s


def vendor_ticker_aliases(canonical: str) -> set[str]:
    """All real/vendor ticker spellings that may appear in vendor responses."""
    base = (canonical or "").strip()
    if not base:
        return set()
    forms = {base}
    encoded = encode_ticker_for_vendor(base, "alpha_vantage")
    forms.add(encoded)
    if ":" in encoded:
        forms.add(encoded.replace(":", "_"))
    return forms


def build_scrub_aliases(ticker_map: Dict[str, str]) -> Dict[str, str]:
    """Map canonical + vendor-encoded tickers back to anonymous ids for output scrubbing."""
    aliases: Dict[str, str] = {}
    if not isinstance(ticker_map, dict):
        return aliases
    for real, anon in ticker_map.items():
        if not isinstance(real, str) or not isinstance(anon, str) or not real:
            continue
        for form in vendor_ticker_aliases(real):
            for variant in {form, form.upper(), form.lower()}:
                aliases[variant] = anon
    return aliases


def deanonymize_ticker(t: str, cfg: Optional[dict] = None) -> str:
    """Map STOCK_#### back to the canonical real ticker (e.g. RELIANCE.NS)."""
    c = cfg or get_config()
    if not c.get("enable_anonymization"):
        return t
    unmap = c.get("anonymization_ticker_unmap") or {}
    if isinstance(unmap, dict):
        real = unmap.get((t or "").strip())
        if isinstance(real, str) and real.strip():
            return real.strip()
    return t


def resolve_ticker_for_vendor(
    agent_symbol: str,
    method: str,
    cfg: Optional[dict] = None,
) -> str:
    """Coerce agent symbol, de-anonymize, then apply vendor-specific ticker encoding."""
    c = cfg or get_config()
    canonical = deanonymize_ticker(coerce_agent_symbol(agent_symbol, c), c)
    from tradingagents.dataflows.interface import get_category_for_method, get_vendor

    category = get_category_for_method(method)
    vendor = get_vendor(category, method, c)
    return encode_ticker_for_vendor(canonical, vendor)


def scrub_ticker_text(text: str, cfg: Optional[dict] = None) -> str:
    """Replace canonical and vendor-encoded tickers with anonymized IDs."""
    if not text:
        return text
    c = cfg or get_config()
    if not c.get("enable_anonymization"):
        return text

    aliases = c.get("anonymization_ticker_scrub_aliases") or {}
    if isinstance(aliases, dict) and aliases:
        out = str(text)
        for real_form in sorted(aliases, key=len, reverse=True):
            anon = aliases[real_form]
            if isinstance(anon, str) and real_form:
                out = out.replace(real_form, anon)
        return out

    m = c.get("anonymization_ticker_map") or {}
    if not isinstance(m, dict) or not m:
        return text
    out = str(text)
    for real, anon in m.items():
        if not isinstance(real, str) or not isinstance(anon, str):
            continue
        if not real:
            continue
        out = out.replace(real, anon)
        out = out.replace(real.upper(), anon)
        out = out.replace(real.lower(), anon)
    return out

