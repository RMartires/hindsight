import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    # OpenAI-compatible clients only (OpenAI, OpenRouter, xAI, Ollama): forwarded to ChatOpenAI
    # max_retries = HTTP-level retries in the OpenAI SDK (5xx, 429, etc.)
    "llm_max_retries": None,
    "llm_timeout": None,
    # Max LLM API completions per rolling 60s (all models share one limit). None disables.
    "llm_rate_limit_rpm": None,
    # Max output tokens per completion for OpenAI-compatible providers.
    # Use this to stay under upstream provider caps (e.g. OpenRouter providers).
    "llm_max_tokens": None,
    # Soft cap on input prompt size (message history) sent to the LLM.
    # This is enforced in agent nodes by trimming the oldest message content.
    # Note: this is approximate unless a tokenizer is available.
    "llm_max_input_tokens": None,
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Paper/backtest ablations (A1/A2/A3/Full) are expressed via config keys.
    # `tradingagents.paper_ablation.apply_paper_ablation_to_config` applies PAPER_ABLATION (``scripts/backtest_mvp``).
    "paper_ablation": os.getenv("PAPER_ABLATION", "").strip().lower() or "full",
    "selected_analysts": ["market", "social", "news", "fundamentals"],
    "run_investment_debate": True,
    "run_risk_phase": True,
    # Anonymization (ROADMAP §3.1/§3.2). When enabled, the graph run sets a per-run mapping in config.
    "enable_anonymization": (os.getenv("ENABLE_ANONYMIZATION", "").strip().lower() in ("1", "true", "yes", "y")),
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: alpha_vantage, yfinance, kite
        "technical_indicators": "yfinance",  # Options: alpha_vantage, yfinance, kite
        "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance (kite not supported)
        "news_data": "yfinance",             # Options: alpha_vantage, yfinance (kite not supported)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
    # Paper backtest: transaction cost as basis points of traded notional per BUY/SELL (0 = off).
    "backtest_cost_bps": float(os.getenv("BACKTEST_COST_BPS", "0") or 0),
    # ``flat_bps`` | ``zerodha_delivery`` | ``zerodha_intraday`` (see tradingagents.backtest.zerodha_fees).
    "backtest_cost_model": os.getenv("BACKTEST_COST_MODEL", "flat_bps").strip() or "flat_bps",
    # Extra execution haircut on traded notional (bps), applied in addition to cost model fees.
    "backtest_slippage_bps": float(os.getenv("BACKTEST_SLIPPAGE_BPS", "0") or 0),
    # When unset, optional default for backtest_cost_bps (India): see env KITE_BROKERAGE_BPS in scripts.
    # Simulation: max calendar date for OHLCV/news downloads (set per run in propagate).
    "simulation_data_end": None,
    # ``prior_calendar_day`` (default) or ``trade_date`` — upper bound for data relative to trade_date.
    "simulation_data_end_policy": os.getenv("SIMULATION_DATA_END_POLICY", "prior_calendar_day").strip()
    or "prior_calendar_day",
}
