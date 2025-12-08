# tests/test_app.py
import pytest
from unittest.mock import patch, MagicMock
from ui.app import analyze_stock

# -----------------------------
# Test analyze_stock function
# -----------------------------
def test_analyze_stock_success():
    mock_result = {
        "price": 150.0,
        "sentiment": "Positive",
        "signal": "Buy"
    }

    # Patch the orchestrator inside app
    with patch("ui.app.orchestrator") as mock_orch:
        mock_orch.analyze_stock.return_value = mock_result
        result = analyze_stock("AAPL")
        assert isinstance(result, dict)
        assert result["price"] == str(150.0)
        assert result["sentiment"] == "Positive"
        assert result["signal"] == "Buy"
        mock_orch.analyze_stock.assert_called_once_with("AAPL")


def test_analyze_stock_lowercase_symbol():
    mock_result = {"price": 200.0}
    with patch("ui.app.orchestrator") as mock_orch:
        mock_orch.analyze_stock.return_value = mock_result
        result = analyze_stock("msft")
        assert "price" in result
        assert result["price"] == str(200.0)
        mock_orch.analyze_stock.assert_called_once_with("MSFT")


def test_analyze_stock_error():
    with patch("ui.app.orchestrator") as mock_orch:
        mock_orch.analyze_stock.side_effect = Exception("API failed")
        result = analyze_stock("TSLA")
        assert "error" in result
        assert result["error"] == "API failed"
        mock_orch.analyze_stock.assert_called_once_with("TSLA")
