"""
FinAdvisor - Phidata Implementation
===================================
Framework: `phidata`
Mechanism: Agent + Storage + Tools

How it works:
1.  **Agent**: `phi.agent.Agent` configured with `OpenAIChat`.
2.  **Storage**: `SqlAgentStorage` manages persistent conversation sessions in SQLite.
3.  **Memory**: Phidata handles "chat history" automatically via storage.
4.  **Streaming**: Uses `agent.run(stream=True)` for token-by-token output.

Key File: `src/finadvisor/app-phi.py`
"""
import streamlit as st
import os
import sqlite3
import json
import logging
import requests
from dotenv import load_dotenv

# === PHIDATA IMPORTS ===
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools import Toolkit

# === CONFIG ===
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === DATABASE SETUP (Application State - Profile) ===
# We treat the Profile data as distinct from the Chat History
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
    Updates the user profile with provided information.
    Call this tool when the user provides Name, Age, Income, Goals, or Risk Tolerance.
    The arguments are optional strings.
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
            # Update session state if available
            if "user_profile" in st.session_state:
                st.session_state.user_profile[k] = str(v)
            # Save to persistent DB
            save_memory(f"profile_{k}", str(v))
            updated_count += 1
    
    current = st.session_state.user_profile if "user_profile" in st.session_state else "updated"
    return f"Profile updated. {updated_count} fields saved. Current Data: {current}"

def get_stock_info(symbol: str) -> str:
    """
    Fetches daily stock info from Alpha Vantage for a given symbol (e.g. AAPL).
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
            return f"Stock: {symbol}, Price: ${close_price}, Date: {latest_date}"
        elif "Error Message" in data:
            return f"Error: Invalid symbol '{symbol}'."
        elif "Note" in data:
             return "Error: API limit reached."
    except Exception as e:
        return f"Error: {str(e)}"
    return "Error: Unknown error."

def track_expense(description: str, amount: str) -> str:
    """Records an expense for the user."""
    logger.info(f"Tracking expense: {description} - ${amount}")
    return f"Expense recorded: {description} for ${amount}"

def budget_summary() -> str:
    """Returns a summary of the user's budget."""
    return "Budget Summary: Limit $5000, Spent $1200, Remaining $3800."

# === STREAMLIT UI ===
st.set_page_config(page_title="💸 FinAdvise (Phidata)", page_icon="🤖", layout="centered")
st.title("💸 FinAdvise (Phidata)")
st.caption("Powered by `phidata` Agents & Storage")
with st.expander("ℹ️ How this works"):
    st.markdown('''
    This version uses **Phidata**:
    - **Agent**: `phi.agent.Agent` wraps the model and tools.
    - **Storage**: `SqlAgentStorage` built-in persistence for sessions.
    - **Instructions**: "Gatekeeper" logic injected via system instructions.
    ''')

# Load Memory (App State)
if "memory_loaded" not in st.session_state:
    db_data = load_all_memory()
    profile = {}
    for k, v in db_data.items():
        if k.startswith("profile_"):
            profile[k.replace("profile_", "")] = v
    st.session_state.user_profile = profile
    st.session_state.messages = []
    st.session_state.memory_loaded = True

# === PHIDATA AGENT ===
if "phi_agent" not in st.session_state:
    # We use SqlAgentStorage to persist conversation sessions separately
    storage = SqlAgentStorage(table_name="agent_sessions", db_file=DB_FILE)
    
    st.session_state.phi_agent = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=OPENAI_API_KEY),
        tools=[update_profile, get_stock_info, track_expense, budget_summary],
        instructions=[
            "You are a helpful Personal Finance Assistant.",
            "CRITICAL: PROFILE GATEKEEPER RULES",
            "1. You must know the user's [Name, Age, Income, Financial Goals, Risk Tolerance].",
            "2. Check the context or tool outputs. If MISSING, politely ask for them.",
            "3. DO NOT answer stock/advice questions until profile is complete.",
            "4. Use `update_profile` tool to save data.",
            "Once profile is complete, you can help with stocks, budgets, etc."
        ],
        storage=storage,
        add_history_to_messages=True,
        num_history_responses=5,
        description="A financial advisor",
    )

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
        message_placeholder = st.empty()
        full_response = ""
        
        # Adding Profile Context to the run prompt
        # Phidata doesn't easily allow dynamic system prompt injection per run without rebuilding agent,
        # so we append context to the user message.
        profile_context = f"Context - User Profile: {st.session_state.user_profile}"
        prompt_with_context = f"{profile_context}\n\nUser Message: {user_input}"
        
        # Stream response
        try:
            # We use the agent.run generator
            resp_stream = st.session_state.phi_agent.run(prompt_with_context, stream=True)
            for chunk in resp_stream:
                if chunk.content:
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Phidata Error: {e}")
