"""Build a TradingAgents-compatible config dict from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


def build_config() -> dict:
    """Construct the config dict expected by TradingAgentsGraph."""
    from tradingagents.default_config import DEFAULT_CONFIG

    config = dict(DEFAULT_CONFIG)

    # LLM provider
    if os.getenv("LLM_PROVIDER"):
        config["llm_provider"] = os.getenv("LLM_PROVIDER")
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
