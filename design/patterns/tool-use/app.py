import os
import time
from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# Tool 1: Get Weather
@function_tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a specific city.
    
    Args:
        city: The name of the city (e.g., "London", "New York").
    """
    start_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n[Tool Call] Fetching weather for: {city} (Start: {start_time})")
    
    # Simulate partial latency to check for parallelism
    time.sleep(1)
    
    # Mock data
    weather_data = {
        "London": "15°C, Cloudy",
        "New York": "22°C, Sunny",
        "Tokyo": "18°C, Raining",
        "Paris": "16°C, Partly Cloudy",
        "San Francisco": "14°C, Foggy"
    }
    
    result = weather_data.get(city, "Unknown weather data")
    end_time = datetime.now().strftime("%H:%M:%S")
    print(f"[Tool Result] {result} (End: {end_time})")
    return result

# Tool 2: Get Local Time
@function_tool
def get_local_time(city: str) -> str:
    """
    Get the current local time for a specific city.
    
    Args:
        city: The name of the city.
    """
    print(f"\n[Tool Call] Fetching time for: {city}")

    # Mock data
    time_data = {
        "London": "14:00 (2:00 PM)",
        "New York": "09:00 (9:00 AM)",
        "Tokyo": "23:00 (11:00 PM)",
        "Paris": "15:00 (3:00 PM)",
        "San Francisco": "06:00 (6:00 AM)"
    }

    result = time_data.get(city, "Unknown time data")
    print(f"[Tool Result] {result}")
    return result

# Define the agent with BOTH tools
assistant_agent = Agent(
    name="CityAssistant",
    instructions="""
        You are a helpful assistant. 
        You have access to tools to check weather and local time.
        Use the appropriate tool based on the user's specific request.
        If the user asks for both, you can use both tools.
    """,
    model="gpt-4o-mini",
    tools=[get_weather, get_local_time]
)

if __name__ == "__main__":
    # Test Scenario 1: Weather Request
    question1 = "What is the weather like in New York?"
    print(f"\n--- Scenario 1: Weather Request ---\nUser Question: {question1}")
    Runner.run_sync(assistant_agent, question1)

    # Test Scenario 2: Time Request
    question2 = "What time is it in Tokyo?"
    print(f"\n--- Scenario 2: Time Request ---\nUser Question: {question2}")
    Runner.run_sync(assistant_agent, question2)
    
    # Test Scenario 3: Mixed Request
    question3 = "I'm planning a call to London. What's the weather and time there right now?"
    print(f"\n--- Scenario 3: Mixed Request ---\nUser Question: {question3}")
    result = Runner.run_sync(assistant_agent, question3)

    print(f"\nFINAL ANSWER (Scenario 3):\n{result.final_output}")

    # Test Scenario 4: Parallel Tool Calls
    question4 = "What is the weather in London, New York, and Tokyo?"
    print(f"\n--- Scenario 4: Parallel Tool Calls ---\nUser Question: {question4}")
    result_parallel = Runner.run_sync(assistant_agent, question4)
    
    print(f"\nFINAL ANSWER (Scenario 4):\n{result_parallel.final_output}")
