"""Build a TradingAgents-compatible config dict from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Repo-root `.env` (single file for backend, scripts, and CLI).
_repo_root = Path(__file__).resolve().parent.parent
load_dotenv(_repo_root / ".env")


def build_config() -> dict:
    """Construct the config dict expected by TradingAgentsGraph."""
    from tradingagents.default_config import DEFAULT_CONFIG

    config = dict(DEFAULT_CONFIG)

    # LLM provider — TradingAgents defaults to "openai" (needs OPENAI_API_KEY).
    # If only OpenRouter is configured, use OPENROUTER_API_KEY + provider "openrouter".
    explicit_provider = os.getenv("LLM_PROVIDER")
    if explicit_provider:
        config["llm_provider"] = explicit_provider
    elif os.getenv("OPENROUTER_API_KEY") and not (
        os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    ):
        config["llm_provider"] = "openrouter"
    if os.getenv("DEEP_THINK_LLM"):
        config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM")
    if os.getenv("QUICK_THINK_LLM"):
        config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM")
    if os.getenv("BACKEND_URL"):
        config["backend_url"] = os.getenv("BACKEND_URL")

    # Rate limits
    if os.getenv("LLM_RATE_LIMIT_RPM"):
        config["llm_rate_limit_rpm"] = int(os.getenv("LLM_RATE_LIMIT_RPM"))
    if os.getenv("LLM_MAX_RETRIES"):
        config["llm_max_retries"] = int(os.getenv("LLM_MAX_RETRIES"))
    if os.getenv("LLM_TIMEOUT"):
        config["llm_timeout"] = float(os.getenv("LLM_TIMEOUT"))
    if os.getenv("LLM_MAX_TOKENS"):
        config["llm_max_tokens"] = int(os.getenv("LLM_MAX_TOKENS"))

    # Debate rounds
    if os.getenv("MAX_DEBATE_ROUNDS"):
        config["max_debate_rounds"] = int(os.getenv("MAX_DEBATE_ROUNDS"))
    if os.getenv("MAX_RISK_DISCUSS_ROUNDS"):
        config["max_risk_discuss_rounds"] = int(os.getenv("MAX_RISK_DISCUSS_ROUNDS"))

    # Data vendors
    for key in ("core_stock_apis", "technical_indicators", "fundamental_data", "news_data"):
        env_key = f"DATA_VENDOR_{key.upper()}"
        if os.getenv(env_key):
            config["data_vendors"][key] = os.getenv(env_key)

    return config
