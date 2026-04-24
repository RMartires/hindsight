from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import pandas as pd
from stockstats import wrap

from tradingagents.dataflows.stockstats_utils import _clean_dataframe


@dataclass(frozen=True)
class IndicatorSpec:
    """Single source of truth for supported technical indicators (stockstats-backed).

    Notes:
    - Indicator IDs are the names passed to the `get_indicators` tool and vendor implementations.
    - `stockstats_name` is the column name we trigger on the stockstats-wrapped DataFrame.
    - v1 ships a Tier-1 subset to keep validation tractable; the catalog can be extended later.
    """

    indicator_id: str
    stockstats_name: str
    category: str
    description: str
    tier: int = 1


def _tier1_specs() -> tuple[IndicatorSpec, ...]:
    # Tier-1 starts as the set already supported across the existing vendors.
    # Keep descriptions consistent with the current vendor dictionaries so prompts/tool output remain stable.
    return (
        IndicatorSpec(
            indicator_id="close_50_sma",
            stockstats_name="close_50_sma",
            category="trend",
            description=(
                "50 SMA: A medium-term trend indicator. "
                "Usage: Identify trend direction and serve as dynamic support/resistance. "
                "Tips: It lags price; combine with faster indicators for timely signals."
            ),
        ),
        IndicatorSpec(
            indicator_id="close_200_sma",
            stockstats_name="close_200_sma",
            category="trend",
            description=(
                "200 SMA: A long-term trend benchmark. "
                "Usage: Confirm overall market trend and identify golden/death cross setups. "
                "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
            ),
        ),
        IndicatorSpec(
            indicator_id="close_10_ema",
            stockstats_name="close_10_ema",
            category="trend",
            description=(
                "10 EMA: A responsive short-term average. "
                "Usage: Capture quick shifts in momentum and potential entry points. "
                "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
            ),
        ),
        IndicatorSpec(
            indicator_id="macd",
            stockstats_name="macd",
            category="momentum",
            description=(
                "MACD: Computes momentum via differences of EMAs. "
                "Usage: Look for crossovers and divergence as signals of trend changes. "
                "Tips: Confirm with other indicators in low-volatility or sideways markets."
            ),
        ),
        IndicatorSpec(
            indicator_id="macds",
            stockstats_name="macds",
            category="momentum",
            description=(
                "MACD Signal: An EMA smoothing of the MACD line. "
                "Usage: Use crossovers with the MACD line to trigger trades. "
                "Tips: Should be part of a broader strategy to avoid false positives."
            ),
        ),
        IndicatorSpec(
            indicator_id="macdh",
            stockstats_name="macdh",
            category="momentum",
            description=(
                "MACD Histogram: Shows the gap between the MACD line and its signal. "
                "Usage: Visualize momentum strength and spot divergence early. "
                "Tips: Can be volatile; complement with additional filters in fast-moving markets."
            ),
        ),
        IndicatorSpec(
            indicator_id="rsi",
            stockstats_name="rsi",
            category="momentum",
            description=(
                "RSI: Measures momentum to flag overbought/oversold conditions. "
                "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
                "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
            ),
        ),
        IndicatorSpec(
            indicator_id="boll",
            stockstats_name="boll",
            category="volatility",
            description=(
                "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
                "Usage: Acts as a dynamic benchmark for price movement. "
                "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
            ),
        ),
        IndicatorSpec(
            indicator_id="boll_ub",
            stockstats_name="boll_ub",
            category="volatility",
            description=(
                "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
                "Usage: Signals potential overbought conditions and breakout zones. "
                "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
            ),
        ),
        IndicatorSpec(
            indicator_id="boll_lb",
            stockstats_name="boll_lb",
            category="volatility",
            description=(
                "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
                "Usage: Indicates potential oversold conditions. "
                "Tips: Use additional analysis to avoid false reversal signals."
            ),
        ),
        IndicatorSpec(
            indicator_id="atr",
            stockstats_name="atr",
            category="volatility",
            description=(
                "ATR: Averages true range to measure volatility. "
                "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
                "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
            ),
        ),
        IndicatorSpec(
            indicator_id="vwma",
            stockstats_name="vwma",
            category="volume",
            description=(
                "VWMA: A moving average weighted by volume. "
                "Usage: Confirm trends by integrating price action with volume data. "
                "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
            ),
        ),
        IndicatorSpec(
            indicator_id="mfi",
            stockstats_name="mfi",
            category="volume",
            description=(
                "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure "
                "buying and selling pressure. Usage: Identify overbought (>80) or oversold (<20) conditions and "
                "confirm the strength of trends or reversals. Tips: Use alongside RSI or MACD to confirm signals; "
                "divergence between price and MFI can indicate potential reversals."
            ),
        ),
    )


def tier1_indicator_ids() -> list[str]:
    return [s.indicator_id for s in _tier1_specs()]


def tier1_indicator_descriptions() -> dict[str, str]:
    return {s.indicator_id: s.description for s in _tier1_specs()}


def tier1_indicator_specs() -> dict[str, IndicatorSpec]:
    return {s.indicator_id: s for s in _tier1_specs()}


def validate_tier1_indicator(indicator_id: str) -> None:
    if indicator_id not in tier1_indicator_specs():
        raise ValueError(
            f"Indicator {indicator_id} is not supported. Please choose from: {tier1_indicator_ids()}"
        )


def compute_indicators(
    ohlcv: pd.DataFrame,
    indicator_ids: Sequence[str],
) -> pd.DataFrame:
    """Compute stockstats-backed indicators for an OHLCV dataframe.

    Args:
        ohlcv: DataFrame containing at least Date/Open/High/Low/Close/Volume columns.
        indicator_ids: Logical indicator ids (Tier-1 ids from this module).

    Returns:
        DataFrame indexed by Date (YYYY-MM-DD str) with one column per indicator id.
    """
    if not isinstance(ohlcv, pd.DataFrame):
        raise TypeError("ohlcv must be a pandas DataFrame")
    specs = tier1_indicator_specs()
    requested = [str(i).strip() for i in indicator_ids if str(i).strip()]
    if not requested:
        return pd.DataFrame()
    unknown = [i for i in requested if i not in specs]
    if unknown:
        raise ValueError(
            f"Unsupported indicator(s): {unknown}. Please choose from: {tier1_indicator_ids()}"
        )

    data = _clean_dataframe(ohlcv.copy())
    if data.empty:
        return pd.DataFrame(index=pd.Index([], name="Date"))
    df = wrap(data)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    out = pd.DataFrame({"Date": df["Date"]})
    for ind_id in requested:
        spec = specs[ind_id]
        # Trigger stockstats calculation.
        _ = df[spec.stockstats_name]
        out[ind_id] = df[spec.stockstats_name]

    out = out.set_index("Date")
    return out


def format_tier1_indicator_list_for_prompt() -> str:
    """Compact, prompt-friendly list of Tier-1 indicators with descriptions."""
    specs = _tier1_specs()
    parts: list[str] = []
    by_cat: dict[str, list[IndicatorSpec]] = {}
    for s in specs:
        by_cat.setdefault(s.category, []).append(s)

    category_labels = {
        "trend": "Moving Averages / Trend",
        "momentum": "Momentum",
        "volatility": "Volatility",
        "volume": "Volume",
    }
    for cat in ("trend", "momentum", "volatility", "volume"):
        items = by_cat.get(cat, [])
        if not items:
            continue
        parts.append(f"{category_labels.get(cat, cat)}:")
        for s in items:
            parts.append(f"- {s.indicator_id}: {s.description}")
        parts.append("")
    return "\n".join(parts).rstrip()

