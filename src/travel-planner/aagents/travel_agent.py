from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts import UserContext
from tools import get_weather_forecast, search_flights, search_hotels
from aagents import conversational_agent, budget_guardrail
from output_types.travel_plan import TravelPlan

travel_agent = Agent[UserContext](
    name="Travel Planner",
    instructions="""
    You are a travel planning assistant.
    
    Follow this workflow:
    1. Call 'get_weather_forecast' for the destination.
    2. Call 'search_flights' to get a list of flight options.
    3. Call 'search_hotels' to get a list of hotel options.
    4. Compile all results into a final 'TravelPlan'.
    
    CRITICAL: The final output MUST be a 'TravelPlan' object containing:
    - 'flight_options': The list of flights returned by search_flights.
    - 'hotel_options': The list of hotels returned by search_hotels.
    - 'weather_remark': A summary of the weather forecast.
    - 'activities': Recommended activities based on location and weather.
    - 'notes': Any final travel advice.
    
    Do not output single recommendations. Use the lists.
    """,
    model="gpt-4-turbo",
    tools=[get_weather_forecast, search_flights, search_hotels],
    handoffs=[conversational_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=budget_guardrail),
    ],
    output_type=TravelPlan
)