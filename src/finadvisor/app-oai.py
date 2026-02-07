"""
FinAdvisor - OpenAI Agents SDK Implementation
==============================================
Framework: `openai-agents` (Custom Pattern) & `openai` SDK
Mechanism: Manual Tool Execution & Agent Class Wrapper

How it works:
1.  **Agent Class**: Wraps the OpenAI Chat Completions API.
2.  **Runner**: Manages the execution loop (Run -> Call Tools -> Run Again).
3.  **SQliteSession**: Persists conversation history in a local database.
4.  **@function_tool**: Decorator that registers Python functions as JSON schemas for the model.

Key File: `src/finadvisor/app-oai.py`
"""
import streamlit as st
import os
import sqlite3
import json
import logging
import asyncio
import requests
from dotenv import load_dotenv

# === AGENTS FRAMEWORK ===
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, SQLiteSession

# === CONFIG ===
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === DATABASE SETUP (Application State) ===
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

# === TOOLS DEFINITION (Using @function_tool) ===

@function_tool
def update_profile(name: str = None, age: str = None, income: str = None, financial_goals: str = None, risk_tolerance: str = None):
    """
    Updates the user profile with provided information (Name, Age, Income, Goals, Risk).
    Call this tool when the user provides any of these details.
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
            # Update session state if available (for UI visibility)
            if "user_profile" in st.session_state:
                st.session_state.user_profile[k] = str(v)
            # Save to persistent DB
            save_memory(f"profile_{k}", str(v))
            updated_count += 1
    
    # Return status for the Agent
    current_profile_str = json.dumps(st.session_state.user_profile) if "user_profile" in st.session_state else "updated"
    return f"Success: Updated {updated_count} fields. Current Profile: {current_profile_str}"

@function_tool
def get_stock_info(symbol: str):
    """
    Fetches daily stock info from Alpha Vantage for a given symbol (e.g., AAPL).
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

@function_tool
def track_expense(description: str, amount: str):
    """
    Records an expense (Mock).
    """
    logger.info(f"Tracking expense: {description} - ${amount}")
    return f"Recorded expense: {description} for ${amount}"

@function_tool
def budget_summary():
    """
    Returns a summary of the user's budget (Mock).
    """
    return "Budget Summary: Monthly Limit $5000, Spent $1200, Remaining $3800."

# === AGENT DEFINITION ===

# Initialize Async Client for the Agent
from openai import AsyncOpenAI
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# We define the model with the client
openai_model = OpenAIChatCompletionsModel(openai_client=async_client, model="gpt-4o")

finance_agent = Agent(
    name="FinAdvisor",
    instructions="""
    You are a helpful and polite Personal Finance Assistant.
    
    **CRITICAL RULE: USER PROFILE GATEKEEPER**
    Check the User Profile before answering ANY questions about stocks, advice, or budget.
    The required fields are: [Name, Age, Income, Financial Goals, Risk Tolerance].
    
    1. IF any field is missing (check the 'Current Profile' context):
       - You MUST politely ask for the missing information specially Name, Age and Income first.
       - Do NOT provide financial advice or stock data until the profile is complete.
       - Use the `update_profile` tool when the user provides data.
    
    2. IF the profile is complete:
       - You may proceed to help with stocks (use `get_stock_info`), budgets, etc.
       - Confirm the user's identity if they ask "Do you remember me?" (e.g., "Yes, you are [Name]...").
    
    Be concise, friendly, and professional.
    """,
    tools=[update_profile, get_stock_info, track_expense, budget_summary],
    model=openai_model
)

# === STREAMLIT UI ===
st.set_page_config(page_title="💸 FinAdvise (OpenAI Agents)", page_icon="🤖", layout="centered")
st.title("💸 FinAdvise (OpenAI Agents)")
st.caption("Powered by `openai-agents` SDK (Manual Tool Execution Pattern)")
with st.expander("ℹ️ How this works"):
    st.markdown('''
    This version uses the **OpenAI Agents SDK** pattern:
    - **Agent**: `agents.Agent` class wraps the model.
    - **Tools**: Functions decorated with `@function_tool`.
    - **Runner**: `agents.Runner` executes the loop until completion.
    ''')

# Initialize Session State Variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load/Init Profile from DB (Application State)
if "memory_loaded" not in st.session_state:
    db_data = load_all_memory()
    profile = {}
    for k, v in db_data.items():
        if k.startswith("profile_"):
            profile[k.replace("profile_", "")] = v
    st.session_state.user_profile = profile
    st.session_state.memory_loaded = True

# Initialize Agent Session (Conversational State)
if "agent_session" not in st.session_state:
    # Use a fixed session ID or random one. Here we use 'default' for persistence across reloads if desired,
    # or uuid to start fresh. Let's use a persistent one for now to match 'memory.db' vibes.
    st.session_state.agent_session = SQLiteSession("finadvisor_chat_session.db")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if user_input := st.chat_input("How can I help you today?"):
    # 1. Append User Message to UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Run Agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                # Inject User Profile Context into the prompt or instruction? 
                # The agent instructions say "Check the 'Current Profile' context".
                # We can prepend the profile to the prompt to ensure the agent "sees" it every turn.
                context_prompt = f"Current Profile Context: {json.dumps(st.session_state.user_profile)}\n\nUser Query: {user_input}"
                
                # Run the agent using the Runner
                # Runner.run is async, so we use asyncio.run
                result = asyncio.run(
                    Runner.run(
                        finance_agent, 
                        context_prompt, 
                        session=st.session_state.agent_session
                    )
                )
                
                final_response = result.final_output
                message_placeholder.markdown(final_response)
                
                # 3. Append Assistant Message to UI
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                
            except Exception as e:
                st.error(f"Agent Error: {e}")
