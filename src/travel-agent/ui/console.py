from agents import Runner, InputGuardrailTripwireTriggered
import asyncio
from contexts import UserContext
from aagents import travel_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Main Function ---

async def main():
    # Create a user context with some preferences
    user_context = UserContext(
        user_id="user123",
        preferred_airlines=["SkyWays", "OceanAir"],
        hotel_amenities=["WiFi", "Pool"],
        budget_level="mid-range"
    )
    
    # Example queries to test different aspects of the system
    queries = [
        "I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there?",
        "I'm planning a trip to Tokyo for a week, looking to spend under $5,000. Suggestions?",
        "I need a flight from New York to Chicago tomorrow",
        "Find me a hotel in Paris with a pool for under $400 per night",
        "I want to go to Dubai for a week with only $300"  # This should trigger the budget guardrail
    ]
    
    for query in queries:
        print("\n" + "="*50)
        print(f"QUERY: {query}")
        print("="*50)
        
        try:
            result = await Runner.run(travel_agent, query, context=user_context)
            
            print("\nFINAL RESPONSE:")
            
            # Format the output based on the type of response
            if hasattr(result.final_output, "airline"):  # Flight recommendation
                flight = result.final_output
                print("\n✈️ FLIGHT RECOMMENDATION ✈️")
                print(f"Airline: {flight.airline}")
                print(f"Departure: {flight.departure_time}")
                print(f"Arrival: {flight.arrival_time}")
                print(f"Price: ${flight.price}")
                print(f"Direct Flight: {'Yes' if flight.direct_flight else 'No'}")
                print(f"\nWhy this flight: {flight.recommendation_reason}")
                
                # Show user preferences that influenced this recommendation
                airlines = user_context.preferred_airlines
                if airlines and flight.airline in airlines:
                    print(f"\n👤 NOTE: This matches your preferred airline: {flight.airline}")
                
            elif hasattr(result.final_output, "name") and hasattr(result.final_output, "amenities"):  # Hotel recommendation
                hotel = result.final_output
                print("\n🏨 HOTEL RECOMMENDATION 🏨")
                print(f"Name: {hotel.name}")
                print(f"Location: {hotel.location}")
                print(f"Price per night: ${hotel.price_per_night}")
                
                print("\nAmenities:")
                for i, amenity in enumerate(hotel.amenities, 1):
                    print(f"  {i}. {amenity}")
                
                # Highlight matching amenities from user preferences
                preferred_amenities = user_context.hotel_amenities
                if preferred_amenities:
                    matching = [a for a in hotel.amenities if a in preferred_amenities]
                    if matching:
                        print("\n👤 MATCHING PREFERRED AMENITIES:")
                        for amenity in matching:
                            print(f"  ✓ {amenity}")
                
                print(f"\nWhy this hotel: {hotel.recommendation_reason}")
                
            elif hasattr(result.final_output, "destination"):  # Travel plan
                travel_plan = result.final_output
                print(f"\n🌍 TRAVEL PLAN FOR {travel_plan.destination.upper()} 🌍")
                print(f"Duration: {travel_plan.duration_days} days")
                print(f"Budget: ${travel_plan.budget}")
                
                # Show budget level context
                budget_level = user_context.budget_level
                if budget_level:
                    print(f"Budget Category: {budget_level.title()}")
                
                print("\n🎯 RECOMMENDED ACTIVITIES:")
                for i, activity in enumerate(travel_plan.activities, 1):
                    print(f"  {i}. {activity}")
                
                print(f"\n📝 NOTES: {travel_plan.notes}")
            
            else:  # Generic response
                print(result.final_output)
                
        except InputGuardrailTripwireTriggered as e:
            print("\n⚠️ GUARDRAIL TRIGGERED ⚠️")

if __name__ == "__main__":
    asyncio.run(main())