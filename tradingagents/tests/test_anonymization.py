from tradingagents.anonymization.ticker_map import TickerMapper, deanonymize_ticker, scrub_ticker_text


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

