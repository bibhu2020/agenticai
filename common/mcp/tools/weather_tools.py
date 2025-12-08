import os
import re
import requests
import datetime
from dotenv import load_dotenv
from typing import Optional

from ddgs import DDGS
from agents import function_tool

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

@function_tool
def get_weather_forecast(city: str, date: Optional[str] = None) -> str:
    """
    PRIMARY TOOL: Fetch weather using OpenWeatherMap API.
    """
    print(f"[DEBUG] Primary API get_weather_forecast called for city={city}")

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY missing. Please use the fallback search tool."

    url = "https://api.openweathermap.org/data/2.5/forecast"

    try:
        response = requests.get(
            url,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=5
        )
        data = response.json()
    except Exception as e:
        return f"Error calling weather API: {str(e)}"

    if str(data.get("cod")) != "200":
        return f"Error from API: {data.get('message', 'Unknown error')}"

    # Build the report string
    report_lines = []
    found_date = False

    for entry in data.get("list", []):
        dt_txt = entry["dt_txt"].split(" ")[0]

        if date and dt_txt != date:
            continue
        
        found_date = True
        desc = entry['weather'][0]['description'].capitalize()
        temp = entry['main']['temp']
        hum = entry['main']['humidity']
        wind = entry['wind']['speed']
        
        report_lines.append(f"{dt_txt}: {desc}, Temp: {temp}°C, Humidity: {hum}%, Wind: {wind} m/s")

    # Handle "Date not found" case
    if date and not found_date:
        return f"API valid, but date {date} is out of range (5-day limit). Try the search fallback tool."

    final_report = "\n".join(report_lines)

    return f"API Forecast for {city}:\n{final_report}"

# ---------------------------------------------------------
# Tool 2: Web Search Fallback (Secondary)
# ---------------------------------------------------------

@function_tool
def search_weather_fallback_ddgs(city: str, date: Optional[str] = None) -> str:
    """
    SECONDARY TOOL: Search-based fallback that produces an API-like structured forecast.
    """
    print(f"[DEBUG] Fallback API (DDGS) called for city={city}, date={date}")

    # --- Build Query ---
    try:
        if date:
            try:
                dt_obj = datetime.strptime(date, "%Y-%m-%d")
                natural_date = dt_obj.strftime("%B %d, %Y")
                month_name = dt_obj.strftime("%B")
            except ValueError:
                natural_date = date
                month_name = ""
        else:
            natural_date = datetime.now().strftime("%B %d, %Y")
            month_name = natural_date.split()[0]  # Month name

        query = f"weather {city} {natural_date}"
        print(f"[DEBUG] Search query: {query}")

        # --- Perform Search ---
        results = list(DDGS().text(query, max_results=3))
        print(f"[DEBUG] Number of search results: {len(results)}")

        if not results:
            return f"Web Estimated Forecast for {city}:\nNo reliable search data found."

        # --- Aggregate Text ---
        full_text = " ".join([r.get("body", "") for r in results])

        # --- Extract Values with Robust Regex ---
        temp_match = re.findall(r'(-?\d+)\s*(?:°|deg|C|F)', full_text, re.I)
        temperature = temp_match[0] if temp_match else "?"

        humidity_match = re.findall(r'(\d+)\s*%', full_text)
        humidity = humidity_match[0] if humidity_match else "?"

        wind_match = re.findall(r'(\d+)\s*(?:mph|km/h|m/s)', full_text, re.I)
        wind = wind_match[0] if wind_match else "?"

        # --- Condition ---
        # Take first word(s) of first title as best guess
        condition_raw = results[0].get("title", "Unknown").split("-")[0].strip()
        condition = condition_raw[0].upper() + condition_raw[1:] if condition_raw else "Unknown"

        # --- Construct API-like Forecast ---
        forecast = (
            f"Web Estimated Forecast for {city}:\n"
            f"{natural_date}: {condition}, Temp: {temperature}° (approx), "
            f"Humidity: {humidity}%, Wind: {wind}\n"
        )

        # Optional: add raw snippets for debugging
        # snippet_block = "\nSearch Snippets (Raw):\n" + "\n".join(
        #     f"- {r['title']}: {r['body']}" for r in results
        # )
        # return forecast + snippet_block

        return forecast

    except Exception as e:
        print(f"[DEBUG] Error in fallback: {e}")
        return f"Error performing web search: {str(e)}"


import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from agents import function_tool
from datetime import datetime

@function_tool
def search_weather_fallback_bs(city: str, date: Optional[str] = None) -> str:
    """
    SECONDARY TOOL: Web-scraping fallback using BeautifulSoup.
    Produces an API-like structured forecast.
    """
    import requests
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime

    print(f"[DEBUG] Fallback API (BeautifulSoup) called for city={city}, date={date}")

    try:
        # --- Build Query ---
        if date:
            try:
                dt_obj = datetime.strptime(date, "%Y-%m-%d")
                natural_date = dt_obj.strftime("%B %d, %Y")
            except ValueError:
                natural_date = date
        else:
            natural_date = datetime.now().strftime("%B %d, %Y")

        query = f"weather {city} {natural_date}"
        print(f"[DEBUG] Search query: {query}")

        # --- DuckDuckGo Search ---
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return f"Error fetching search results: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result__body"):
            title_tag = result.select_one(".result__title a")
            snippet_tag = result.select_one(".result__snippet")
            if title_tag and snippet_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "body": snippet_tag.get_text(strip=True)
                })

        if not results:
            return f"Web Estimated Forecast for {city}:\nNo reliable search data found."

        # --- Aggregate Text ---
        full_text = " ".join([r["body"] for r in results])

        # --- Extract Temperature ---
        temp_matches = re.findall(r'(-?\d{1,2})\s*(?:°|deg|C|F)', full_text, re.I)
        temperature = temp_matches[0] if temp_matches else "?"

        # --- Extract Humidity ---
        humidity_matches = re.findall(r'(\d{1,3})\s*%', full_text)
        humidity = humidity_matches[0] if humidity_matches else "?"

        # --- Extract Wind ---
        wind_matches = re.findall(r'(\d{1,3})\s*(?:mph|km/h|m/s)', full_text, re.I)
        wind = wind_matches[0] if wind_matches else "?"

        # --- Extract Condition ---
        # Look in all results first, fallback to first title
        condition = "Unknown"
        for r in results:
            m = re.search(r'(clear|sunny|cloudy|rain|snow|storm|fog|mist)', r["body"], re.I)
            if m:
                condition = m.group(1).capitalize()
                break
        if condition == "Unknown":
            # Fallback
            condition_raw = results[0]["title"].split("-")[0].strip()
            condition = condition_raw[0].upper() + condition_raw[1:] if condition_raw else "Unknown"

        # --- Build Forecast ---
        forecast = (
            f"Web Estimated Forecast for {city}:\n"
            f"{natural_date}: {condition}, Temp: {temperature}° (approx), "
            f"Humidity: {humidity}%, Wind: {wind}\n"
        )

        return forecast

    except Exception as e:
        print(f"[DEBUG] Error in fallback: {e}")
        return f"Error performing web search: {str(e)}"
