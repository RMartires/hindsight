"""Filters for dependency noise during long backtests (not application bugs)."""


def apply_backtest_warning_filters() -> None:
    """Suppress known noisy warnings from LangChain + Pydantic structured output and deprecations."""
    import warnings

    # LC + OpenAI structured parse: serialized message has `parsed` set while schema expected none.
    warnings.filterwarnings(
        "ignore",
        message=r".*PydanticSerializationUnexpectedValue.*",
        category=UserWarning,
    )
    # langchain_core (Python 3.14+): asyncio.iscoroutinefunction
    warnings.filterwarnings(
        "ignore",
        message=r".*asyncio\.iscoroutinefunction.*",
        category=DeprecationWarning,
        module=r"langchain_core\.runnables\.utils",
    )
    # Langfuse SDK: trace-level I/O helper (we use span.update instead where applicable).
    warnings.filterwarnings(
        "ignore",
        message=r".*Trace-level input/output is deprecated.*",
        category=DeprecationWarning,
    )
