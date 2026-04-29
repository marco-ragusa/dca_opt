# tests/unit/test_tickers_endpoint.py
"""Unit tests for GET /v1/tickers/search."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _mock_search(quotes: list[dict]) -> MagicMock:
    m = MagicMock()
    m.quotes = quotes
    return m


def _quote(symbol: str, shortname: str, exchange: str, quote_type: str) -> dict:
    return {
        "symbol": symbol,
        "shortname": shortname,
        "exchange": exchange,
        "quoteType": quote_type,
    }


def test_returns_matching_results(client):
    quotes = [_quote("VWCE.DE", "Vanguard FTSE All-World", "XETRA", "ETF")]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=VWCE")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["ticker"] == "VWCE.DE"
    assert results[0]["name"] == "Vanguard FTSE All-World"
    assert results[0]["exchange"] == "XETRA"
    assert results[0]["type"] == "ETF"


def test_index_type_excluded(client):
    quotes = [
        _quote("VWCE.DE", "Vanguard FTSE All-World", "XETRA", "ETF"),
        _quote("^GSPC", "S&P 500", "SNP", "INDEX"),
    ]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=SP500")
    assert resp.status_code == 200
    tickers = [r["ticker"] for r in resp.json()["results"]]
    assert "^GSPC" not in tickers
    assert "VWCE.DE" in tickers


def test_future_type_excluded(client):
    quotes = [_quote("ES=F", "E-Mini S&P 500", "CME", "FUTURE")]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=ES")
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_option_type_excluded(client):
    quotes = [_quote("AAPL240119C00150000", "AAPL Call", "OPR", "OPTION")]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=AAPL")
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_crypto_included(client):
    quotes = [_quote("BTC-USD", "Bitcoin USD", "CCC", "CRYPTOCURRENCY")]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=BTC")
    assert resp.status_code == 200
    assert resp.json()["results"][0]["ticker"] == "BTC-USD"


def test_currency_included(client):
    quotes = [_quote("EURCHF=X", "EUR/CHF", "CCY", "CURRENCY")]
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search(quotes)):
        resp = client.get("/v1/tickers/search?q=EURCHF")
    assert resp.status_code == 200
    assert resp.json()["results"][0]["ticker"] == "EURCHF=X"


def test_empty_results(client):
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search([])):
        resp = client.get("/v1/tickers/search?q=XXXX")
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_shortname_fallback_to_longname(client):
    quote = {
        "symbol": "VAGF.DE",
        "longname": "Vanguard Global Aggregate Bond",
        "exchange": "XETRA",
        "quoteType": "ETF",
    }
    with patch("app.api.v1.routes.tickers.yf.Search", return_value=_mock_search([quote])):
        resp = client.get("/v1/tickers/search?q=VAGF")
    assert resp.status_code == 200
    assert resp.json()["results"][0]["name"] == "Vanguard Global Aggregate Bond"


def test_missing_q_returns_422(client):
    resp = client.get("/v1/tickers/search")
    assert resp.status_code == 422


def test_single_char_q_returns_422(client):
    resp = client.get("/v1/tickers/search?q=V")
    assert resp.status_code == 422


def test_yfinance_exception_returns_503(client):
    with patch("app.api.v1.routes.tickers.yf.Search", side_effect=Exception("timeout")):
        resp = client.get("/v1/tickers/search?q=VWCE")
    assert resp.status_code == 503
    assert resp.json()["detail"] == "Market data unavailable"
