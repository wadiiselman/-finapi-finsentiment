from unittest.mock import patch
from finapi.sentiment import analyze, SentimentResult


@patch("finapi.sentiment.get_pipeline")
def test_analyze_positive(mock_pipe):

    mock_pipe.return_value = lambda text: [{"label": "positive", "score": 0.95}]

    result = analyze("Apple beats expectations")

    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.score == 0.95


def test_analyze_empty_raises():
    import pytest

    with pytest.raises(ValueError):
        analyze("")
