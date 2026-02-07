# Weather MCP Server

A comprehensive weather and location intelligence server for the Model Context Protocol.

## Tools

- `get_current_weather`: Fetch current conditions for any city.
- `get_forecast`: 5-day / 3-hour forecast mapping.
- `get_air_quality`: Real-time AQI and pollutant breakdown.
- `search_places`: Discover location IDs and addresses via Google Places.
- `get_place_details`: Deep dive into specific location metadata.

## Configuration

Required environment variables:
- `OPENWEATHER_API_KEY`: From [OpenWeatherMap](https://openweathermap.org/api)
- `GPLACES_API_KEY`: From [Google Maps Platform](https://console.cloud.google.com/)

## Local Development

```bash
docker build -t mcp-weather -f src/mcp-weather/Dockerfile .
docker run -p 7860:7860 \
  -e OPENWEATHER_API_KEY=your_key \
  -e GPLACES_API_KEY=your_key \
  mcp-weather
```
