# app.py
import os
import nest_asyncio
import asyncio
import json
from datetime import datetime
import streamlit as st
from agents import Agent, Runner, trace, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import aiohttp
from xml.etree import ElementTree as ET
from openai import AsyncOpenAI

# Allow nested async in Jupyter/Streamlit
nest_asyncio.apply()
load_dotenv()  # Load .env with OPENAI_API_KEY

TEMPLATE_PATH = os.path.abspath("templates/dashboard_template.html")


async def fetch_sitemap_urls(base_url: str):
    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
    urls = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(sitemap_url) as resp:
                if resp.status != 200:
                    return [base_url]
                xml_text = await resp.text()
                root = ET.fromstring(xml_text)
                urls = [elem.text for elem in root.findall(".//{*}loc")]
        except:
            return [base_url]
    return urls if urls else [base_url]


async def run_accessibility_audit(base_url: str):
    script_path = os.path.abspath("mcp/server.py")
    if not os.path.exists(script_path):
        st.error(f"MCP server not found: {script_path}")
        return None

    params = {"command": "uv", "args": ["run", script_path]}
    # model = "gpt-4.1-mini"

    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    google_api_key = os.getenv('GOOGLE_API_KEY')
    gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
    model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client) 

    try:
        async with MCPServerStdio(params=params, client_session_timeout_seconds=180) as accessibility_server:
            urls_to_audit = await fetch_sitemap_urls(base_url)
            audit_results = {}
            page_summaries = {}

            progress_placeholder = st.empty()  # dynamic progress updates

            audit_instructions = (
                "You are an AI assistant specialized in ADA/WCAG compliance. "
                "Audit a webpage and produce a Markdown report including all rules with columns: "
                "Level, Rule, Pass/Fail, Reason, Recommendation."
            )

            for idx, url in enumerate(urls_to_audit, start=1):
                progress_placeholder.info(f"🔹 Auditing page {idx}/{len(urls_to_audit)}: {url}")
                audit_agent = Agent(
                    name="accessibility_agent",
                    instructions=audit_instructions,
                    model=model,
                    mcp_servers=[accessibility_server]
                )
                with trace(f"audit_{url}"):
                    result = await Runner.run(audit_agent, f"Audit {url} for ADA/WCAG compliance.")
                markdown_output = result.final_output if result and result.final_output else ""
                audit_results[url] = markdown_output

                # Compute per-page summary
                passed = failed = warning = 0
                for line in markdown_output.splitlines():
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 5:
                            status = parts[2].lower()
                            if "pass" in status:
                                passed += 1
                            elif "fail" in status:
                                failed += 1
                            elif "warn" in status or "warning" in status:
                                warning += 1
                page_summaries[url] = {"pass": passed, "fail": failed, "warning": warning}

            # Prepare JSON data for template
            audit_json = []
            for page, md in audit_results.items():
                rows = []
                for line in md.splitlines():
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 5:
                            rows.append({
                                "level": parts[0],
                                "rule": parts[1],
                                "status": parts[2],
                                "reason": parts[3],
                                "recommendation": parts[4],
                            })
                audit_json.append({
                    "page": page,
                    "rows": rows,
                    "summary": page_summaries.get(page, {"pass": 0, "fail": 0, "warning": 0})
                })

            # Load template
            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                template_html = f.read()

            html_content = template_html.replace("<!--AUDIT_JSON_PLACEHOLDER-->", json.dumps(audit_json))

            # Save HTML report
            output_dir = os.path.abspath("output")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"accessibility_dashboard_{timestamp}.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            progress_placeholder.success(f"✅ Accessibility audit complete! Report saved to `{output_file}`.")

            return html_content

    except Exception as e:
        st.error(f"Error running audit: {e}")
        return None


# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Accessibility Dashboard", layout="wide")
st.title("🌐 Site Accessibility Audit Dashboard")

site_url = st.text_input("Enter the website URL", "https://oauthapp.azurewebsites.net")

if st.button("Run Audit") and site_url:
    html_output = asyncio.run(run_accessibility_audit(site_url))
    if html_output:
        st.components.v1.html(html_output, height=900, scrolling=True)
