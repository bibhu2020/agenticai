# test_weather_tools.py
import pytest
from agents import RunContextWrapper
from contexts.user_context import UserContext
from tools.search import get_weather_forecast

class DummyWrapper(RunContextWrapper[UserContext]):
    def __init__(self, context=None):
        self.context = context or UserContext()

def test_weather_forecast_valid_city(monkeypatch):
    # Mock the SerpAPI GoogleSearch.get_dict() to avoid real API calls
    class MockGoogleSearch:
        def __init__(self, params):
            pass
        def get_dict(self):
            return {
                "weather_results": {
                    "forecast_summary": "Sunny with temperatures around 25°C"
                }
            }

    monkeypatch.setattr("weather_tools.GoogleSearch", MockGoogleSearch)

    wrapper = DummyWrapper()
    result = get_weather_forecast(wrapper, "New York", "2025-11-21")

    assert "Sunny" in result
    assert wrapper.context.latest_weather_forecast["city"] == "New York"
    assert wrapper.context.latest_weather_forecast["forecast"] == result

def test_weather_forecast_invalid_city(monkeypatch):
    # Mock to return empty results
    class MockGoogleSearch:
        def __init__(self, params):
            pass
        def get_dict(self):
            return {}

    monkeypatch.setattr("weather_tools.GoogleSearch", MockGoogleSearch)

    wrapper = DummyWrapper()
    result = get_weather_forecast(wrapper, "Atlantis", "2025-11-21")

    assert "not available" in result
    assert wrapper.context.latest_weather_forecast["city"] == "Atlantis"
    assert wrapper.context.latest_weather_forecast["forecast"] == result
