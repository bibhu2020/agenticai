import streamlit as st
import asyncio
import sys
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Ensure we can import from local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../.."))
if repo_root not in sys.path:
    sys.path.append(repo_root)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from common.utility.autogen_model_factory import AutoGenModelFactory
from teams.team import get_trading_team, extract_json
from tools.news_data import get_sentiment_pipeline

# ------------------------------------------------------------------------------
# Streamlit Config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="AI Market Analyst", page_icon="📈", layout="wide")

from datetime import datetime, time
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python < 3.9 fallback, though we expect 3.9+
    # For now assuming standard lib is fine.
    pass

def check_market_hours():
    """Checks if the US Market (NYSE/Nasdaq) is currently open."""
    try:
        # US Markets operate on Eastern Time
        et_zone = ZoneInfo("US/Eastern")
        now = datetime.now(et_zone)
        
        # 1. Check Weekday (Mon=0, Sun=6)
        if now.weekday() >= 5:
            return False, "Market is closed (Weekend)."
            
        # 2. Check Time (09:30 to 16:00)
        current_time = now.time()
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        if market_open <= current_time <= market_close:
            return True, "Market is Open."
        else:
            return False, f"Market is closed (Hours: 09:30-16:00 ET). Current ET: {current_time.strftime('%H:%M')}"
            
    except Exception as e:
        # Fallback if timezone db is missing
        return True, f"Market hours check skipped (Error: {e})"

# ENFORCE GUARDRAIL
is_open, msg = check_market_hours()
if not is_open:
    st.error(f"⛔ {msg}")
    st.info("The AI Market Analyst is only active during US Market Hours to ensure real-time data accuracy.")
    st.stop()


# CSS for Hero Banner and Layout
st.markdown("""
<style>
    /* GLOBAL */
    html {
        -webkit-text-size-adjust: 100%; /* Prevent iOS font boosting */
    }
    
    /* REMOVE TOP PADDING & RESPONSIVE CONTAINER */
    div.block-container {
        padding-top: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    @media (max-width: 768px) {
        div.block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        .stMarkdown p, .stMarkdown li, .stChatMessage p {
            font-size: 16px !important;
        }
        
        .hero-title {
            font-size: 1.8rem !important;
        }
    }
    
    /* HIDE HEADER */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* HERO BANNER */
    .hero-banner {
        width: 100vw;
        height: 140px;
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-left: -50vw;
        margin-right: -50vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-top: -60px; /* Pull up into the whitespace */
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        z-index: 999;
        padding-top: 30px; /* Push text down */
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: -webkit-linear-gradient(#fff, #a3c9e6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.0rem;
        opacity: 0.8;
        font-weight: 300;
    }

    /* INPUT SECTION */
    .input-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* CHAT BUBBLES */
    .stChatMessage { 
        background-color: #2E2E2E; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 10px; 
        border: 1px solid #444;
        color: #FFFFFF !important;
    }
    /* FIX DULL HEADINGS & TEXT */
    .stChatMessage div, .stChatMessage span, .stChatMessage p, .stChatMessage li {
        color: #FFFFFF !important;
    }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage h4, .stChatMessage h5, .stChatMessage h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .stChatMessage strong {
        color: #81D4FA !important; /* Light Blue for emphasis */
    }
    .stChatMessage code {
        color: #FFEB3B !important; /* Yellow for code to pop */
        background-color: #424242 !important;
        font-weight: bold;
    }
    .stChatMessage pre {
        background-color: #212121 !important;
        border: 1px solid #444;
    }

    /* CARDS */
    .rec-card-trade {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .rec-card-wait {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #555;
        color: #ddd;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# OPTIMIZATION: Pre-load Models
# ------------------------------------------------------------------------------
@st.cache_resource
def preload_model():
    """Warms up the FinBERT model so the first query is fast."""
    return get_sentiment_pipeline()

# Call immediately on startup
if "model_loaded" not in st.session_state:
    with st.spinner("Initializing AI Core (FinBERT)..."):
        preload_model()
    st.session_state.model_loaded = True

# ------------------------------------------------------------------------------
# HERO SECTION
# ------------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">MARKET ANALYST</div>
    <div class="hero-subtitle">Real-Time AI Trading Intelligence • Powered by Multi-Agent Swarm</div>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ **DISCLAIMER**: This tool is for **educational and research purposes only**. It is NOT financial advice. Do not use this for real-money trading without consulting a certified financial advisor.")

# ------------------------------------------------------------------------------
# STATE MANAGEMENT
# ------------------------------------------------------------------------------
if "analyzing" not in st.session_state:
    st.session_state.analyzing = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []

def start_analysis():
    st.session_state.analyzing = True
    st.session_state.logs = [] # Clear logs on new run
    st.session_state.analysis_results = [] # Clear results on new run

# ------------------------------------------------------------------------------
# INPUT SECTION (Main Screen)
# ------------------------------------------------------------------------------
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    ticker_input = st.text_input("Enter Ticker Symbols (comma separated)", value="NVDA", help="Comma separated", placeholder="e.g. SPY, TCS.NS")

with col2:
    model_provider = st.selectbox("AI Model", ["openai", "google", "groq"], index=0)

with col3:
    st.write("") 
    st.write("") 
    analyze_btn = st.button(
        "🚀 Start Analysis", 
        type="primary", 
        use_container_width=True,
        on_click=start_analysis,
        disabled=st.session_state.analyzing
    )

st.markdown("---")

# ------------------------------------------------------------------------------
# RENDER PREVIOUS LOGS & RESULTS (State persistence)
# ------------------------------------------------------------------------------
chat_container = st.container()

# Draw any logs we already have (from previous or current run)
with chat_container:
    for log in st.session_state.logs:
        with st.chat_message(log["source"], avatar=log["avatar"]):
            st.markdown(log["content"], unsafe_allow_html=True)

# Draw summary table if we have results and NOT analyzing (analyzing clears it)
if st.session_state.analysis_results and not st.session_state.analyzing:
     st.subheader("📊 Executive Summary")
     df = pd.DataFrame(st.session_state.analysis_results)
     st.dataframe(df, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------------------
# Main Logic
# ------------------------------------------------------------------------------

async def run_analysis_stream(ticker: str, provider: str) -> dict:
    
    # 1. Setup Model
    if provider == "openai":
        model_name = "gpt-4o"
        family = "gpt"
    elif provider == "groq":
        model_name = "llama-3.3-70b-versatile"
        family = "groq" 
    else:
        model_name = "gemini-2.5-flash"
        family = "gemini"
    
    try:
        model_client = AutoGenModelFactory.get_model(
            provider=provider,
            model_name=model_name,
            temperature=0.2,
            model_info={"family": family, "vision": False, "function_calling": True, "json_output": True, "structured_output": True}
        )
    except Exception as e:
        error_msg = f"Error initializing model: {e}"
        st.error(error_msg)
        return {}

    # 2. Get Team
    team = get_trading_team(model_client)
    
    # 3. Construct Task
    task = f"""
    Perform a real-time trade analysis for {ticker}.
    1. MarketAnalyst: detailed technicals.
    2. SentimentAnalyst: news sentiment (Top 5 stories).
    3. StrategyAdvisor: recommend a spread with >70% confidence.
    4. RiskManager: validate. Output JSON with "final_decision" (TRADE/WAIT), "confidence", and "actionable_recommendation".
    """
    
    st.markdown(f"### 🔍 Analyzing {ticker}...")
    final_output = {}
    
    # Agent Icon Mapping
    AGENT_ICONS = {
        "MarketAnalyst": "📊",
        "SentimentAnalyst": "📰",
        "StrategyAdvisor": "🧠",
        "RiskManager": "🛡️",
        "System": "🤖",
        "User": "🕵️‍♂️" # Simple Red Square Emoji to guarantee visibility/color
    }

    try:
        # 0. Show User Request in Chat
        user_text = f"Analyze {ticker} ({provider})"
        user_avatar = AGENT_ICONS["User"]
        
        # Render User Msg
        with chat_container:
            with st.chat_message("User", avatar=user_avatar):
                st.markdown(user_text)
        
        # Log User Msg
        st.session_state.logs.append({
            "source": "User",
            "content": user_text,
            "avatar": user_avatar
        })

        async for message in team.run_stream(task=task):
            # Normalizing source to handle 'user' vs 'User' or generic names
            raw_source = getattr(message, 'source', 'System')
            source = raw_source
            
            # Helper to map source to icon key
            if source.lower() == 'user': 
                source = 'User'
            
            # Skip echoing the huge prompt task if it comes back from the stream with 'User' source
            if source == 'User' and "Perform a real-time trade analysis" in getattr(message, 'content', ''):
                continue

            content = getattr(message, 'content', '')
            
            if not content and 'ToolCall' not in str(type(message)):
                continue

            # Render to UI immediately
            avatar_icon = AGENT_ICONS.get(source, "🤖")
            with chat_container:
                with st.chat_message(source, avatar=avatar_icon):
                    st.markdown(content)
            
            # Persist to state
            st.session_state.logs.append({
                "source": source,
                "content": content,
                "avatar": avatar_icon
            })
            
            if source == "RiskManager":
                parsed = extract_json(content)
                if parsed:
                    final_output = parsed
    
    except Exception as e:
        st.error(f"Analysis failed for {ticker}: {e}")
        return {}

    # Final Card
    if final_output:
        decision = final_output.get("final_decision", "WAIT").upper()
        confidence = final_output.get("confidence", 0)
        action = final_output.get("actionable_recommendation", "No actionable data.")
        reasoning = final_output.get("risk_warning", "")
        
        # Entry Data
        entry_signal = final_output.get("entry_signal", "")
        entry_price = final_output.get("entry_price", "N/A")
        entry_display = ""
        if entry_signal and entry_price != "N/A":
            entry_display = f"<p style='margin: 5px 0; font-size: 1.1em;'>💰 <b>Entry</b>: ${entry_price} ({entry_signal})</p>"

        css_class = "rec-card-trade" if decision == "TRADE" else "rec-card-wait"
        icon = "🚀" if decision == "TRADE" else "⏳"
        
        card_html = f"""
        <div class="{css_class}">
            <h2 style="margin-top:0;">{icon} {ticker}: {decision} <span style="font-size: 0.6em; opacity: 0.8;">({confidence}% Conf)</span></h2>
            <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">{action}</p>
            {entry_display}
            <p style="opacity: 0.9;"><i>{reasoning}</i></p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Persist card as a system log so it reappears
        st.session_state.logs.append({
             "source": "System", 
             "content": card_html, 
             "avatar": "🤖"
        })
        
        return {
            "Ticker": ticker,
            "Decision": decision,
            "Confidence": f"{confidence}%",
            "Action": action
        }
    else:
        st.warning(f"No structured result for {ticker}.")
        return {"Ticker": ticker, "Decision": "ERROR", "Confidence": "0%", "Action": "Error"}

# Execute only if state says we are analyzing
if st.session_state.analyzing:
    try:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
        
        if not tickers:
            st.warning("Please enter valid ticker symbols.")
        else:
            current_results = []
            for ticker in tickers:
                res = asyncio.run(run_analysis_stream(ticker, model_provider))
                current_results.append(res)
                st.markdown("---")
                
            if current_results:
                # Save results to state
                st.session_state.analysis_results = current_results
                
                # Render table immediately for this run
                st.subheader("📊 Executive Summary")
                df = pd.DataFrame(current_results)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
    finally:
        # Reset state so button becomes enabled again
        st.session_state.analyzing = False
        st.rerun()
