"""
FinAdvisor - LangGraph Implementation
=====================================
Framework: `langgraph`
Mechanism: State Machine (StateGraph) with Nodes & Conditional Edges

How it works:
1.  **State**: `FinanceState` (TypedDict) holds the conversation context.
2.  **Nodes**: Functions like `detect_intent`, `collect_user_data`, `get_stock_info`.
3.  **Routing**: `get_next_node` determines the flow based on intent classification.
4.  **Persistence**: `SqliteSaver` (or manual DB hooks) tracks history.

Key File: `src/finadvisor/app-lg.py`
"""
import streamlit as st
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Optional, Dict
import re
from dotenv import load_dotenv
import os
import requests
import logging
import sqlite3

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
        logger.info(f"[DB] Saved {key}")
    except Exception as e:
        logger.error(f"[DB] Error saving {key}: {e}")

def load_all_memory() -> Dict[str, str]:
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

# === CONFIG ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONSTANTS ===
INTENT_DETECTION_NODE = "Intent Detection"

# === STATE ===
class FinanceState(TypedDict):
    user_input: str
    intent: Optional[str]
    data: Optional[dict]
    user_profile: Optional[Dict[str, str]]  # Age, income, goals, risk tolerance
    short_term_memory: Optional[Dict[str, str]]  # In-session memory
    long_term_memory: Optional[Dict[str, str]]  # Cross-session memory
    hitl_flag: Optional[bool]  # Flag for high-risk queries

# === LLM ===
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# llm = ChatOpenAI(
#     model="llama3.2:3b",
#     api_key="ollama",
#     base_url="http://localhost:30786/v1",
# )


# === USER PROFILE COLLECTION ===
import json

async def collect_user_data(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: collect_user_data with input: {state['user_input']}")
    user_input = state['user_input']
    user_profile = state.get('user_profile', {})
    short_term_memory = state.get('short_term_memory', {})

    # === STEP 1: EXTRACTION (Silent) ===
    # A dedicated, strict call just to get the JSON data
    extraction_prompt = (
        f"Extract profile data from this text: '{user_input}'.\n"
        f"Return ONLY a raw JSON object (no markdown, no extra text) with keys: "
        f"'name', 'age', 'income', 'financial_goals', 'risk_tolerance'.\n"
        f"If a value is not found, use null.\n"
        f"Example output: {{\"name\": \"John\", \"age\": \"53\", \"income\": null, \"financial_goals\": null, \"risk_tolerance\": null}}"
    )
    try:
        extract_response = await llm.ainvoke(extraction_prompt)
        content = extract_response.content.strip().replace("```json", "").replace("```", "")
        # Try to parse JSON
        extracted_data = json.loads(content)
        
        # Update profile with found values
        for key, val in extracted_data.items():
            if val and str(val).lower() != "null" and val != "None":
                user_profile[key.lower()] = str(val)
                save_memory(f"profile_{key.lower()}", str(val)) # Persist to DB
                logger.info(f"[DEBUG] Extracted {key}: {val}")
    except Exception as e:
        logger.error(f"[DEBUG] Extraction failed: {e}")

    # === STEP 2: CONVERSATION (Chatty) ===
    # Check what is still missing
    required_fields = ["name", "age", "income", "financial_goals", "risk_tolerance"]
    missing_fields = [f for f in required_fields if f not in user_profile]
    
    if missing_fields:
        next_field = missing_fields[0].replace("_", " ")
        conversation_prompt = (
            f"You are a helpful financial assistant assistant. The user just said: '{user_input}'.\n"
            f"We have captured these details: {user_profile}.\n"
            f"We are MISSING: {missing_fields}.\n"
            f"Your Task:\n"
            f"1. Acknowledge what they said (briefly).\n"
            f"2. Politely ask for the next missing field: '{next_field}'. (If asking for name, be friendly like 'May I have your name?').\n"
            f"3. Do NOT mention 'JSON' or 'extraction'. Just chat naturally."
        )
    else:
        conversation_prompt = (
            f"You are a helpful financial assistant. The user just said: '{user_input}'.\n"
            f"Profile is COMPLETE: {user_profile}.\n"
            f"Task: If they asked 'do you remember me' or similar, confirm enthusiastically with their details (Name, Age, etc.). "
            f"Otherwise, thank them for completing their profile and offer help with stocks/budgets."
        )

    chat_response = await llm.ainvoke(conversation_prompt)
    message = chat_response.content.strip()

    short_term_memory['last_question'] = message
    return {**state, "user_profile": user_profile, "data": {"response": message}, "short_term_memory": short_term_memory}


# === INTENT DETECTION ===
async def detect_intent(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: detect_intent with input: {state['user_input']}")
    user_input = state['user_input']
    short_term_memory = state.get('short_term_memory', {})
    long_term_memory = state.get('long_term_memory', {})

    prompt = (
        f"Classify the user's intent into one of: 'profile', 'stock', 'expense', 'budget', 'advice', or 'unknown'.\n"
        f"User input: {user_input}\n"
        f"Previous intent: {short_term_memory.get('previous_intent', 'none')}\n"
        f"Long-term context: {long_term_memory.get('last_advice', 'none')}\n"
        f"User input: {user_input}\n"
        f"Previous intent: {short_term_memory.get('previous_intent', 'none')}\n"
        f"Long-term context: {long_term_memory.get('last_advice', 'none')}\n"
        f"IMPORTANT: If 'Previous intent' was 'profile' and the user input looks like an answer (e.g., a number, an amount, or a short phrase) to a profile question, classify as 'profile'.\n"
        f"IMPORTANT: Questions like 'do you know me?', 'who am I?', or 'what is my name?' should be classified as 'profile'.\n"
        f"Intent:"
    )
    response = await llm.ainvoke(prompt)
    content = response.content.strip().lower()

    match = re.search(r"(profile|stock|expense|budget|advice)", content)
    intent = match.group(1) if match else "unknown"
    short_term_memory['previous_intent'] = intent

    high_risk_keywords = ["liquidate", "retirement", "all my savings", "entire portfolio"]
    hitl_flag = any(keyword in user_input.lower() for keyword in high_risk_keywords)

    return {**state, "intent": intent, "short_term_memory": short_term_memory, "hitl_flag": hitl_flag}

# === STOCK INFO ===
async def get_stock_info(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: get_stock_info with input: {state['user_input']}")
    user_input = state['user_input']
    short_term_memory = state.get('short_term_memory', {})
    user_profile = state.get('user_profile', {})

    # Extract stock symbol using LLM with strict instructions
    prompt = (
        f"Extract the stock symbol (e.g., 'AAPL' for Apple) from the request: {user_input}. "
        f"Return only the symbol (e.g., 'AAPL') or 'UNKNOWN' if unclear. Do not include extra text."
    )
    response = await llm.ainvoke(prompt)
    stock_symbol = response.content.strip().upper()

    # Validate stock symbol with regex
    if not re.match(r'^[A-Z]{1,5}$', stock_symbol) or stock_symbol == 'UNKNOWN':
        message = f"Sorry, I couldn't identify a valid stock symbol from '{user_input}'. Please specify the stock (e.g., 'AAPL' for Apple)."
        logger.warning(f"Invalid stock symbol extracted: {stock_symbol}")
    else:
        # Call Alpha Vantage API
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Alpha Vantage API response for {stock_symbol}: {data.keys()}")

            if "Time Series (Daily)" in data:
                latest_date = list(data["Time Series (Daily)"].keys())[0]
                stock_data = data["Time Series (Daily)"][latest_date]
                close_price = stock_data["4. close"]
                message = f"The latest closing price for {stock_symbol} is ${close_price} (as of {latest_date})."

                # Add risk tolerance advice
                risk_tolerance = user_profile.get('risk tolerance', 'unknown')
                risk_prompt = (
                    f"Provide a brief note on investing in {stock_symbol} tailored to a user with {risk_tolerance} risk tolerance. "
                    f"Keep it clear and empathetic."
                )
                risk_response = await llm.ainvoke(risk_prompt)
                message += f"\n{risk_response.content.strip()}"
            elif "Error Message" in data:
                message = f"Error from Alpha Vantage: {data['Error Message']}. Please check the stock symbol or try again later."
                logger.error(f"Alpha Vantage error for {stock_symbol}: {data['Error Message']}")
            elif "Note" in data and "rate limit" in data["Note"].lower():
                message = "Alpha Vantage API rate limit exceeded. Please try again in a minute."
                logger.warning(f"Rate limit exceeded for {stock_symbol}: {data['Note']}")
            else:
                message = f"No data available for {stock_symbol}. Please check the symbol or try again later."
                logger.error(f"No time series data for {stock_symbol}: {data}")
        except requests.RequestException as e:
            message = f"Error fetching data for {stock_symbol}: {str(e)}. Please try again later."
            logger.error(f"Request error for {stock_symbol}: {str(e)}")

    short_term_memory['last_stock_requested'] = user_input
    return {**state, "data": {"response": message}, "short_term_memory": short_term_memory}

# === MOCK EXPENSE TRACKING ===
async def track_expenses(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: track_expenses with input: {state['user_input']}")
    user_input = state['user_input']
    short_term_memory = state.get('short_term_memory', {})
    user_profile = state.get('user_profile', {})

    prompt = (
        f"Mock adding an expense based on: {user_input}. "
        f"Consider user profile: {user_profile}. "
        f"Reply with a confirmation message, e.g., 'Added expense of $50 for groceries.'"
    )
    response = await llm.ainvoke(prompt)
    message = response.content.strip()

    short_term_memory['last_expense'] = user_input
    return {**state, "data": {"response": message}, "short_term_memory": short_term_memory}

# === MOCK BUDGET SUMMARY ===
async def budget_summary(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: budget_summary")
    user_profile = state.get('user_profile', {})
    prompt = (
        f"Mock a simple budget summary with categories and totals, tailored to user profile: {user_profile}. "
        f"Use clear, empathetic language."
    )
    response = await llm.ainvoke(prompt)
    message = response.content.strip()
    return {**state, "data": {"response": message}}

# === PERSONALIZED ADVICE ===
async def provide_advice(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: provide_advice with input: {state['user_input']}")
    user_input = state['user_input']
    user_profile = state.get('user_profile', {})
    long_term_memory = state.get('long_term_memory', {})

    prompt = (
        f"Provide personalized financial advice based on: {user_input}. "
        f"User profile: {user_profile}. "
        f"Previous advice: {long_term_memory.get('last_advice', 'none')}. "
        f"Use clear, empathetic language suitable for users with limited financial literacy."
    )
    response = await llm.ainvoke(prompt)
    message = response.content.strip()

    long_term_memory['last_advice'] = message
    save_memory("last_advice", message) # Persist last advice
    return {**state, "data": {"response": message}, "long_term_memory": long_term_memory}

# === HUMAN-IN-THE-LOOP ===
async def human_in_the_loop(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: human_in_the_loop with input: {state['user_input']}")
    user_input = state['user_input']
    prompt = (
        f"The query '{user_input}' has been flagged as high-risk. "
        f" Judges to a human financial advisor: This query requires review by a financial advisor. "
        f"Please wait for expert input before proceeding."
    )
    message = prompt
    return {**state, "data": {"response": message}}

# === FALLBACK ===
async def fallback(state: FinanceState) -> FinanceState:
    logger.info(f"[DEBUG] Executing tool: fallback")
    message = "🤔 Sorry, I didn't understand. Try asking about stocks, expenses, budgets, or financial advice."
    return {**state, "data": {"response": message}}

# === BUILD GRAPH ===
def get_next_node(state: FinanceState) -> str:
    logger.info(f"[DEBUG] Evaluating get_next_node for intent: {state.get('intent')}")
    
    # === MANDATORY PROFILE CHECK ===
    user_profile = state.get("user_profile", {})
    required_fields = ["name", "age", "income", "financial_goals", "risk_tolerance"]
    # Check if ANY required field is missing
    if any(field not in user_profile for field in required_fields):
        logger.info("[DEBUG] Profile incomplete. Redirecting to Collect User Data.")
        return "Collect User Data"
    # ===============================
    
    if state.get("hitl_flag", False):
        return "human_in_the_loop"
    valid_intents = ["profile", "stock", "expense", "budget", "advice"]
    return state["intent"] if state["intent"] in valid_intents else "fallback"

builder = StateGraph(FinanceState)

builder.add_node(INTENT_DETECTION_NODE, detect_intent)
builder.add_node("Collect User Data", collect_user_data)
builder.add_node("Stock Info", get_stock_info)
builder.add_node("Expense Tracker", track_expenses)
builder.add_node("Budget Summary", budget_summary)
builder.add_node("Provide Advice", provide_advice)
builder.add_node("Human in the Loop", human_in_the_loop)
builder.add_node("Fallback", fallback)
builder.set_entry_point(INTENT_DETECTION_NODE)

builder.add_conditional_edges(
    INTENT_DETECTION_NODE,
    get_next_node,
    {
        "Collect User Data": "Collect User Data",
        "profile": "Collect User Data",
        "stock": "Stock Info",
        "expense": "Expense Tracker",
        "budget": "Budget Summary",
        "advice": "Provide Advice",
        "human_in_the_loop": "Human in the Loop",
        "fallback": "Fallback"
    }
)
finance_bot = builder.compile()

# === GENERATE GRAPH IMAGE ===
if not os.path.exists("graph.png"):
    try:
        graph_image = finance_bot.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(graph_image)
        logger.info("Graph image saved as graph.png")
    except Exception as e:
        logger.error(f"Failed to save graph image: {e}")
else:
    logger.info("Graph image already exists. Skipping generation.")

# === STREAMLIT UI ===
st.set_page_config(page_title="💸 FinAdvise (LangGraph)", page_icon="💬", layout="centered")
st.title("💸 FinAdvise (LangGraph)")
st.caption("Powered by `langgraph` State Machine")
with st.expander("ℹ️ How this works"):
    st.markdown('''
    This version uses **LangGraph**:
    - **Architecture**: A cyclical graph of nodes (functions).
    - **Intent Detection**: First node classifies user input.
    - **Routing**: Conditional edges direct the flow (e.g., Stock -> Stock Node, Advice -> Advice Node).
    - **Human-in-the-Loop**: Can interrupt high-risk actions.
    ''')

if "messages" not in st.session_state:
    st.session_state.messages = []
    
# === LOAD MEMORY ON STARTUP ===
if "memory_loaded" not in st.session_state:
    db_data = load_all_memory()
    
    # Reconstruct user_profile from DB keys starting with "profile_"
    profile = {}
    lt_memory = {}
    for k, v in db_data.items():
        if k.startswith("profile_"):
            profile[k.replace("profile_", "")] = v
        else:
            lt_memory[k] = v
            
    st.session_state.user_profile = profile
    st.session_state.long_term_memory = lt_memory
    st.session_state.memory_loaded = True
    logger.info(f"[INIT] Loaded profile: {profile}")

if "long_term_memory" not in st.session_state:
    st.session_state.long_term_memory = {}
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            state = {
                "user_input": user_input,
                "intent": None,
                "data": None,
                "user_profile": st.session_state.get("user_profile", {}),
                "short_term_memory": {},
                "long_term_memory": st.session_state.long_term_memory,
                "hitl_flag": False
            }
            print('fresh call')
            final_state = asyncio.run(finance_bot.ainvoke(state))
            bot_reply = final_state['data']['response']
            st.session_state.user_profile = final_state.get('user_profile', {})
            st.session_state.long_term_memory = final_state.get('long_term_memory', {})
            st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})