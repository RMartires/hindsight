from tradingagents.anonymization.ticker_map import (
    TickerMapper,
    deanonymize_ticker,
    encode_ticker_for_vendor,
    resolve_ticker_for_vendor,
    scrub_ticker_text,
)
from tradingagents.anonymization.noun_scrubber import scrub_news_text


def test_ticker_mapper_is_deterministic():
    m1 = TickerMapper.for_real_ticker("RELIANCE.NS")
    m2 = TickerMapper.for_real_ticker("RELIANCE.NS")
    assert m1.anon_ticker == m2.anon_ticker
    assert m1.real_ticker == "RELIANCE.NS"


def test_deanonymize_and_scrub_roundtrip():
    mapper = TickerMapper.for_real_ticker("TCS.NS")
    cfg = {"enable_anonymization": True, **mapper.to_config_payload()}
    assert deanonymize_ticker(mapper.anon_ticker, cfg) == "TCS.NS"
    assert deanonymize_ticker("TCS.NS", cfg) == "TCS.NS"
    assert scrub_ticker_text("hello TCS.NS world", cfg).count(mapper.anon_ticker) == 1


def test_encode_alpha_vantage_colon_exchange_suffix():
    assert encode_ticker_for_vendor("RELIANCE.NS", "alpha_vantage") == "RELIANCE:NSE"
    assert encode_ticker_for_vendor("RELIANCE.NS", "local") == "RELIANCE.NS"
    assert encode_ticker_for_vendor("FOO.BO", "alpha_vantage") == "FOO:BSE"


def test_scrub_aliases_include_vendor_encoded_forms():
    mapper = TickerMapper.for_real_ticker("RELIANCE.NS")
    cfg = {
        "enable_anonymization": True,
        **mapper.to_config_payload(),
        "data_vendors": {"news_data": "alpha_vantage"},
    }
    assert scrub_ticker_text("news about RELIANCE:NSE today", cfg) == f"news about {mapper.anon_ticker} today"
    assert scrub_ticker_text("price for RELIANCE.NS", cfg) == f"price for {mapper.anon_ticker}"


def test_resolve_ticker_for_vendor_news_alpha_vantage():
    mapper = TickerMapper.for_real_ticker("RELIANCE.NS")
    cfg = {
        "enable_anonymization": True,
        **mapper.to_config_payload(),
        "data_vendors": {"news_data": "alpha_vantage"},
    }
    assert resolve_ticker_for_vendor(mapper.anon_ticker, "get_news", cfg) == "RELIANCE:NSE"


def test_scrub_news_av_error_replaces_vendor_and_canonical_tickers():
    mapper = TickerMapper.for_real_ticker("RELIANCE.NS")
    cfg = {"enable_anonymization": True, **mapper.to_config_payload()}
    raw = (
        '{"Error Message": "Invalid ticker format: RELIANCE:NSE. '
        'Ticker can only contain alphanumeric characters, colons, underscores, and hyphens"}'
    )
    out = scrub_news_text(raw, cfg)
    assert mapper.anon_ticker in out
    assert "RELIANCE:NSE" not in out
    assert "RELIANCE.NS" not in out

