import streamlit as st
import asyncio
import sys
import os

# Add local directory to path logic
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from graph import create_graph

st.set_page_config(page_title="AI Market Analyst v2", page_icon="📈", layout="wide")

# (CSS Copied/Adapted from v1 for consistency)
st.markdown("""
<style>
    /* ... (Same CSS as v1 or improved) ... */
    .hero-banner {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 2rem;
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">MARKET ANALYST v2</div>
    <div class="hero-subtitle">LangGraph Enabled Multi-Agent System</div>
</div>
""", unsafe_allow_html=True)

if "analysis_log" not in st.session_state:
    st.session_state.analysis_log = []

ticker_input = st.text_input("Enter Ticker", value="NVDA")

if st.button("🚀 Start Analysis"):
    st.session_state.analysis_log = []
    
    async def run_analysis():
        graph = create_graph()
        initial_state = {"ticker": ticker_input, "messages": []}
        
        async for event in graph.astream(initial_state):
            for node, state_update in event.items():
                if 'messages' in state_update:
                    for msg in state_update['messages']:
                         st.session_state.analysis_log.append(msg)
                         st.write(msg) # Stream log
                         
                if node == "risk_manager":
                    st.markdown("---")
                    st.markdown(state_update['final_report'])

    asyncio.run(run_analysis())
