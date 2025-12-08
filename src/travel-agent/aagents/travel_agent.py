from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from contexts import UserContext
from tools import get_weather_forecast
from aagents import flight_agent, hotel_agent, conversational_agent, budget_guardrail
from output_types.travel_plan import TravelPlan

travel_agent = Agent[UserContext](
    name="Travel Planner",
    instructions="""
    You are a travel planning assistant who helps users plan their trips.
    
    You can provide personalized travel recommendations based on the user's destination, duration, budget, and preferences.
    
    The user's preferences are available in the context, which you can use to tailor your recommendations.
    
    Follow this workflow:
    1. Get weather forecasts for destinations
    2. If flight_result and hotel_result are BOTH missing:
      • Do NOT create an itinerary yet.
      • Hand off to flight_agent AND hotel_agent sequentially.
    3. If only one of them is missing:
      • Hand off to the agent whose result is missing.

    4. If BOTH results exist:
        • Combine them with weather data.
        • Produce a final TravelPlan.
    5. Create comprehensive travel plans with activities and notes
    6. Final output should be a day-wise itinerary.
    
    Always be helpful, informative, and enthusiastic about travel.
    """,
    model="gpt-4o-mini",
    tools=[get_weather_forecast],
    handoffs=[flight_agent, hotel_agent, conversational_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=budget_guardrail),
    ],
    output_type=TravelPlan
)