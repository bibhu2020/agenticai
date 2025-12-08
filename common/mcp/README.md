# MCP Tools Server

A Model Context Protocol (MCP) server that exposes all tools from the `tools/` folder via stdio transport.

## Features

- **Dynamic Tool Discovery**: Automatically discovers and registers all tools from the tools folder
- **Stdio Transport**: Compatible with Claude Desktop and other MCP clients
- **Comprehensive Tool Coverage**: Exposes ~13 tools across 6 categories:
  - Google Search (google_tools)
  - News API (news_tools)
  - DuckDuckGo Search (search_tools)
  - Time Utilities (time_tools)
  - Weather Forecast (weather_tools)
  - Yahoo Finance (yf_tools)

## Installation

1. Install required dependencies:
```bash
pip install mcp requests beautifulsoup4 ddgs yfinance python-dotenv pydantic
```

2. Set up environment variables in `.env`:
```bash
# Google Search (Serper.dev)
SERPER_API_KEY=your_serper_api_key

# News API
NEWS_API_KEY=your_news_api_key

# Weather API
OPENWEATHER_API_KEY=your_openweather_api_key

# Google AI (for agents)
GOOGLE_API_KEY=your_google_api_key

# Groq (for agents)
GROQ_API_KEY=your_groq_api_key
```

## Usage

### Running the Server

```bash
cd common/mcp
python mcp_server.py
```

The server will:
1. Discover all tools from the `tools/` folder
2. Print registered tools to stderr
3. Start listening on stdio for MCP protocol messages

### Integrating with Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tools-server": {
      "command": "python",
      "args": ["/absolute/path/to/agenticaiprojects/common/mcp/mcp_server.py"],
      "env": {
        "SERPER_API_KEY": "your_key",
        "NEWS_API_KEY": "your_key",
        "OPENWEATHER_API_KEY": "your_key"
      }
    }
  }
}
```

### Available Tools

The server exposes the following tools:

**Google Search:**
- `google_tools.google_search` - General Google search
- `google_tools.google_search_recent` - Time-filtered Google search

**News:**
- `news_tools.get_top_headlines` - Top headlines by country
- `news_tools.search_news` - Search news by topic
- `news_tools.get_news_by_category` - News by category

**Search & Content:**
- `search_tools.duckduckgo_search` - DuckDuckGo search
- `search_tools.fetch_page_content` - Extract page content

**Time:**
- `time_tools.current_datetime` - Get current date/time

**Weather:**
- `weather_tools.get_weather_forecast` - Weather forecast via API
- `weather_tools.search_weather_fallback_ddgs` - Weather via DuckDuckGo
- `weather_tools.search_weather_fallback_bs` - Weather via web scraping

**Finance:**
- `yf_tools.get_summary` - Stock summary
- `yf_tools.get_market_sentiment` - Market sentiment analysis
- `yf_tools.get_history` - Historical stock data

## Development

### Adding New Tools

1. Create a new file in `tools/` folder (e.g., `my_tools.py`)
2. Decorate functions with `@function_tool`
3. The server will automatically discover and register them on next restart

### Testing

```bash
# Test the server
cd common/mcp
python mcp_server.py

# In another terminal, you can send MCP protocol messages via stdin
# Or use an MCP client library to test
```

## Troubleshooting

**Tools not discovered:**
- Check that functions are decorated with `@function_tool`
- Verify the module is in the `tools/` folder
- Check stderr output for registration messages

**API errors:**
- Verify environment variables are set correctly
- Check API key validity
- Review tool-specific error messages in stderr

## License

Part of the agenticaiprojects repository.
