"""Tests for /history endpoint parameter validation."""


def test_invalid_days(client):
    r = client.get("/history/AAPL?days=abc")
    assert r.status_code == 400
    assert "int" in r.get_json()["error"]


def test_days_out_of_range(client):
    r = client.get("/history/AAPL?days=999")
    assert r.status_code == 400
    assert "365" in r.get_json()["error"]
