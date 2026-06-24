"""Tests for Odyssey (travel-planner) — output types, UserContext, and tool structure."""
import sys
import os
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_odyssey_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src/odyssey")
)
if _odyssey_path not in sys.path:
    sys.path.insert(0, _odyssey_path)

# Stub external deps before importing project modules
for _mod in ["agents", "logfire", "streamlit"]:
    sys.modules.setdefault(_mod, MagicMock())

sys.modules["agents"].Agent = MagicMock(return_value=MagicMock())
sys.modules["agents"].Runner = MagicMock()
sys.modules["agents"].function_tool = lambda f: f
sys.modules["agents"].ModelSettings = MagicMock()
sys.modules["agents"].InputGuardrail = MagicMock()
sys.modules["agents"].GuardrailFunctionOutput = MagicMock()
sys.modules["agents"].InputGuardrailTripwireTriggered = Exception
sys.modules["agents"].RunContextWrapper = MagicMock()

from contexts.user_context import UserContext
from output_types.flight_recommendation import FlightRecommendation, FlightSearchResults
from output_types.hotel_recommendation import HotelRecommendation, HotelSearchResults
from output_types.travel_plan import TravelPlan


# ── UserContext ───────────────────────────────────────────────────────────────

def test_user_context_defaults():
    ctx = UserContext(user_id="u1")
    assert ctx.user_id == "u1"
    assert ctx.preferred_airlines == []
    assert ctx.hotel_amenities == []
    assert ctx.source_destination is None
    assert isinstance(ctx.session_start, datetime)


def test_user_context_with_fields():
    ctx = UserContext(
        user_id="u2",
        source_destination="NYC",
        target_destination="LAX",
        travel_dates="2025-08-01 to 2025-08-10",
        preferred_airlines=["Delta", "United"],
        budget_level="mid",
    )
    assert ctx.source_destination == "NYC"
    assert ctx.target_destination == "LAX"
    assert len(ctx.preferred_airlines) == 2
    assert ctx.budget_level == "mid"


def test_user_context_is_dataclass():
    from dataclasses import fields
    field_names = {f.name for f in fields(UserContext)}
    assert "user_id" in field_names
    assert "session_start" in field_names


# ── FlightRecommendation ──────────────────────────────────────────────────────

def test_flight_recommendation_fields():
    fr = FlightRecommendation(
        airline="Delta",
        departure_time="10:00 AM",
        arrival_time="2:00 PM",
        price=350.0,
        direct_flight=True,
        recommendation_reason="Best value",
    )
    assert fr.airline == "Delta"
    assert fr.direct_flight is True
    assert fr.price == 350.0


def test_flight_search_results_list():
    flights = FlightSearchResults(results=[
        FlightRecommendation(
            airline="AA", departure_time="08:00", arrival_time="11:00",
            price=200.0, direct_flight=True, recommendation_reason="Cheap",
        ),
        FlightRecommendation(
            airline="UA", departure_time="12:00", arrival_time="15:00",
            price=250.0, direct_flight=False, recommendation_reason="Convenient timing",
        ),
    ])
    assert len(flights.results) == 2
    assert flights.results[0].airline == "AA"


# ── HotelRecommendation ───────────────────────────────────────────────────────

def test_hotel_recommendation_fields():
    hr = HotelRecommendation(
        name="Grand Hyatt",
        location="Downtown LA",
        price_per_night=180.0,
        amenities=["Pool", "Gym", "WiFi"],
        recommendation_reason="Central location",
    )
    assert hr.name == "Grand Hyatt"
    assert "Pool" in hr.amenities
    assert hr.price_per_night == 180.0


def test_hotel_search_results_list():
    hotels = HotelSearchResults(results=[
        HotelRecommendation(
            name="Marriott", location="Airport", price_per_night=120.0,
            amenities=["Free shuttle"], recommendation_reason="Close to airport",
        ),
    ])
    assert len(hotels.results) == 1


# ── TravelPlan ────────────────────────────────────────────────────────────────

def _make_plan():
    return TravelPlan(
        destination="Paris",
        duration_days=7,
        budget=3000.0,
        weather_remark="Mild with occasional rain",
        activities=["Eiffel Tower", "Louvre", "Seine cruise"],
        notes="Book tickets in advance",
    )


def test_travel_plan_basic_fields():
    plan = _make_plan()
    assert plan.destination == "Paris"
    assert plan.duration_days == 7
    assert len(plan.activities) == 3


def test_travel_plan_default_empty_lists():
    plan = _make_plan()
    assert plan.flight_options == []
    assert plan.hotel_options == []


def test_travel_plan_with_options():
    flight = FlightRecommendation(
        airline="Air France", departure_time="09:00", arrival_time="21:00",
        price=800.0, direct_flight=True, recommendation_reason="Direct to CDG",
    )
    hotel = HotelRecommendation(
        name="Hotel du Louvre", location="1st Arrondissement",
        price_per_night=250.0, amenities=["Breakfast", "WiFi"],
        recommendation_reason="Walking distance to Louvre",
    )
    plan = TravelPlan(
        destination="Paris", duration_days=7, budget=3000.0,
        flight_options=[flight], hotel_options=[hotel],
        weather_remark="Mild", activities=["Louvre"], notes="",
    )
    assert len(plan.flight_options) == 1
    assert plan.flight_options[0].airline == "Air France"
    assert plan.hotel_options[0].name == "Hotel du Louvre"


def test_travel_plan_serialisable():
    plan = _make_plan()
    d = plan.model_dump()
    assert "destination" in d
    assert "flight_options" in d
    assert "hotel_options" in d
