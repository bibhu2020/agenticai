"""
FinAdvisor - AutoGen 0.4 Implementation
=======================================
Framework: `autogen-agentchat` (v0.4+)
Mechanism: Multi-Agent System (Agents + Teams + Streams)

How it works:
1.  **AssistantAgent**: "FinAdvisor" (LLM-backed) with system instructions.
2.  **RoundRobinGroupChat**: A "Team" that manages the flow. In this case, 
    it holds the single agent to provide a unified `run_stream` interface.
3.  **FunctionTool**: Wraps Python functions for the agent.
4.  **Streaming**: The UI consumes `team.run_stream()` to display tokens/messages.

Key File: `src/finadvisor/app-ag.py`
"""
import streamlit as st
import os
import sys
import sqlite3
import json
import logging
import asyncio
import requests
from dotenv import load_dotenv

# === PATH SETUP FOR COMMON MODULES ===
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../../"))
if repo_root not in sys.path:
    sys.path.append(repo_root)

# === AUTOGEN 0.4 IMPORTS ===
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from common.utility.autogen_model_factory import AutoGenModelFactory

# === CONFIG ===
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === DATABASE SETUP ===
DB_FILE = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def save_memory(key: str, value: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()
        logger.info(f"[DB] Saved {key}: {value}")
    except Exception as e:
        logger.error(f"[DB] Error saving {key}: {e}")

def load_all_memory():
    memory = {}
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT key, value FROM memory")
        rows = c.fetchall()
        for row in rows:
            memory[row[0]] = row[1]
        conn.close()
        logger.info("[DB] Memory loaded")
    except Exception as e:
        logger.error(f"[DB] Error loading memory: {e}")
    return memory

# Initialize DB on import
init_db()


# === TOOLS ===

def update_profile(name: str = None, age: str = None, income: str = None, financial_goals: str = None, risk_tolerance: str = None) -> str:
    """
    Updates the user profile. Call this when the user provides Name, Age, Income, Goals, or Risk.
    """
    updates = {
        "name": name, 
        "age": age, 
        "income": income, 
        "financial_goals": financial_goals, 
        "risk_tolerance": risk_tolerance
    }
    updated_count = 0
    for k, v in updates.items():
        if v:
            # Update session state if initialized
            if "user_profile" in st.session_state:
                st.session_state.user_profile[k] = str(v)
            # Save to persistent DB
            save_memory(f"profile_{k}", str(v))
            updated_count += 1
    
    current = st.session_state.user_profile if "user_profile" in st.session_state else "updated"
    return f"Profile updated. {updated_count} fields saved. Current Profile: {current}"

def get_stock_info(symbol: str) -> str:
    """
    Fetches daily stock info from Alpha Vantage.
    """
    if not symbol:
        return "Error: No symbol provided."
    
    symbol = symbol.upper()
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if "Time Series (Daily)" in data:
            latest_date = list(data["Time Series (Daily)"].keys())[0]
            stock_data = data["Time Series (Daily)"][latest_date]
            close_price = stock_data["4. close"]
            return f"{symbol} Price: ${close_price} (Date: {latest_date})"
        elif "Error Message" in data:
            return f"Error: Invalid symbol '{symbol}'."
        elif "Note" in data:
             return "Error: API limit reached."
    except Exception as e:
        return f"Error: {str(e)}"
    return "Error: Unknown error."

def track_expense(description: str, amount: str) -> str:
    """
    Records an expense.
    """
    logger.info(f"Tracking expense: {description} - ${amount}")
    return f"Expense recorded: {description} for ${amount}"

def budget_summary() -> str:
    """
    Returns a summary of budget.
    """
    return "Budget Summary: Limit $5000, Spent $1200, Remaining $3800."

# === STREAMLIT UI ===
st.set_page_config(page_title="💸 FinAdvise (AutoGen)", page_icon="🤖", layout="centered")
st.title("💸 FinAdvise (AutoGen 0.4)")
st.caption("Powered by `autogen-agentchat` (Multi-Agent Team Pattern)")
with st.expander("ℹ️ How this works"):
    st.markdown('''
    This version uses **AutoGen 0.4**:
    - **Agents**: `AssistantAgent` defined with specific model and tools.
    - **Teams**: `RoundRobinGroupChat` orchestrates the execution (simple 1-agent team here).
    - **Tools**: `FunctionTool` wraps local Python functions.
    - **Streaming**: Uses `run_stream()` for real-time feedback.
    ''')

# Load Memory
if "memory_loaded" not in st.session_state:
    db_data = load_all_memory()
    profile = {}
    for k, v in db_data.items():
        if k.startswith("profile_"):
            profile[k.replace("profile_", "")] = v
    st.session_state.user_profile = profile
    st.session_state.messages = []
    st.session_state.memory_loaded = True

# === AGENT INITIALIZATION ===
async def run_agent(user_input: str):
    # 1. Create Model Client
    model_client = AutoGenModelFactory.get_model(
        provider="openai",
        model_name="gpt-4o",
        temperature=0
    )

    # 2. Wrap Tools
    tools = [
        FunctionTool(update_profile, description="Updates user profile."),
        FunctionTool(get_stock_info, description="Get stock info."),
        FunctionTool(track_expense, description="Track expense."),
        FunctionTool(budget_summary, description="Get budget summary.")
    ]

    # 3. Create Assistant
    fin_advisor = AssistantAgent(
        name="FinAdvisor",
        model_client=model_client,
        tools=tools,
        system_message="""
        You are a helpful Personal Finance Assistant.
        
        **PROFILE GATEKEEPER RULES:**
        1. You must know the user's [Name, Age, Income, Financial Goals, Risk Tolerance].
        2. Check the context or tool outputs for this info.
        3. IF MISSING: Politely ask for the missing fields (e.g., "May I have your name and age?").
        4. DO NOT answer questions about stocks or advice until the profile is complete.
        5. Use `update_profile` tool to save data.
        
        Once profile is complete, help with stocks, budgets, etc.
        """
    )

    # 4. Create Team (Single Agent + User Logic)
    # Market Analyst uses RoundRobinGroupChat. We can use that for a single agent + user context approach.
    team = RoundRobinGroupChat(
        participants=[fin_advisor],
        max_turns=1 # We just want one response per user input
    )

    # 5. Run Stream
    # We inject the user input as a task
    context_str = f"Current Profile: {st.session_state.user_profile}"
    task = f"{context_str}\n\nUser Input: {user_input}"
    
    full_response = ""
    message_placeholder = st.empty()

    async for message in team.run_stream(task=task):
        # In AutoGen 0.4, messages are emitted.
        # We look for the Assistant's text response.
        source = getattr(message, 'source', '')
        content = getattr(message, 'content', '')
        
        if source == "FinAdvisor" and isinstance(content, str):
            full_response = content # Capture the latest content
            message_placeholder.markdown(full_response)
        
    return full_response

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if user_input := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                final_response = asyncio.run(run_agent(user_input))
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            except Exception as e:
                st.error(f"AutoGen Error: {e}")
