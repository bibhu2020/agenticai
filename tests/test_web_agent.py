# tests/test_web_agent.py
import pytest
from dotenv import load_dotenv
from agents import Runner, trace
from ..common.aagents.web_agent import web_agent
import json
from typing import Any, List

load_dotenv()


def format_search_results_md(results: Any) -> str:
    """Convert search-results JSON (string/dict/list) to a Markdown string."""
    if isinstance(results, str):
        try:
            results = json.loads(results)
        except json.JSONDecodeError:
            return f"```\n{results}\n```"

    if isinstance(results, dict):
        if "results" in results and isinstance(results["results"], list):
            items = results["results"]
        elif "items" in results and isinstance(results["items"], list):
            items = results["items"]
        else:
            list_vals = [v for v in results.values() if isinstance(v, list)]
            items = list_vals[0] if list_vals else [results]
    elif isinstance(results, list):
        items = results
    else:
        return str(results)

    md_lines: List[str] = []
    md_lines.append(f"# Search Results ({len(items)})\n")

    for i, r in enumerate(items, start=1):
        if hasattr(r, "model_dump"):
            r = r.model_dump()
        elif hasattr(r, "dict"):
            r = r.dict()

        if not isinstance(r, dict):
            md_lines.append(f"## {i}. Result\n\n```\n{r}\n```\n")
            continue

        title = r.get("title") or r.get("heading") or r.get("name") or "No title"
        link = r.get("link") or r.get("url") or ""
        snippet = r.get("snippet") or r.get("body") or r.get("summary") or ""
        source = r.get("source") or r.get("site") or ""
        date = r.get("datetime") or r.get("date") or ""

        if date:
            md_lines.append(f"### {i}. {title} ({date})\n")
        else:
            md_lines.append(f"### {i}. {title}\n")

        meta_parts = []
        if link:
            meta_parts.append(f"**Link:** {link}")
        if source:
            meta_parts.append(f"**Source:** {source}")
        if meta_parts:
            md_lines.append(" · ".join(meta_parts) + "\n")

        if snippet:
            snippet = snippet.replace("\n", " ").strip()
            md_lines.append(f"> {snippet}\n")

        md_lines.append("---\n")

    return "\n".join(md_lines)


@pytest.mark.asyncio
async def test_web_agent_run():
    """Test the web_agent for recent news headlines in India."""
    with trace("News Headline Agent Run"):
        response = await Runner.run(
            web_agent,
            input=(
                "Find out RECENT news headlines in India? "
                "The news should be the MOST recent available. "
                "Ignore anything older than 1 day."
            ),
        )

    # Print formatted output for debugging
    print("\n[DEBUG] Agent Final Output:\n")
    print(format_search_results_md(response.final_output))

    # Assertions
    assert response.final_output is not None
    assert isinstance(response.final_output, (str, list, dict))
