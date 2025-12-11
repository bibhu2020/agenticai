import streamlit as st
import asyncio
from teams.team import get_investment_team

st.set_page_config(page_title="Stock Investment Analyst", layout="wide")

st.title("📈 Stock Investment Analyst")
st.markdown("Enter a stock ticker to get a comprehensive analysis from our AI investment team.")

# Input section
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        stock_name = st.text_input("Stock Ticker", value="Tesla", label_visibility="collapsed", placeholder="e.g. NVDA, TSLA, AAPL")
    with col2:
        analyze_btn = st.button("Analyze Stock", type="primary", use_container_width=True)

async def run_analysis(ticker):
    task = f"Analyze stock trends, news, and sentiment for {ticker}, plus analyst reports and expert opinions, and then decide whether to invest."
    
    st.markdown(f"### Analysis for **{ticker}**")
    
    # Container for live updates
    chat_container = st.container()
    
    try:
        # Run the team stream
        investment_team = get_investment_team()
        stream = investment_team.run_stream(task=task)
        
        # Define icons for each agent
        AGENT_ICONS = {
            "stock_trends_agent": "📈",
            "news_agent": "📰",
            "sentiment_agent": "💡",
            "decision_agent": "⚖️",
            "user": "👤",
            "System": "⚙️"
        }
        
        async for message in stream:
            # Check if message has source and content attributes typical of agent messages
            source = getattr(message, 'source', 'System')
            
            with chat_container:
                if 'TaskResult' in message.__class__.__name__:
                    if hasattr(message, 'stop_reason') and message.stop_reason:
                         st.info(f"Analysis Completed: {message.stop_reason}")
                    continue

                # Use the icon mapping, default to None (Streamlit default) if not found
                avatar = AGENT_ICONS.get(source, None)
                
                with st.chat_message(source, avatar=avatar):
                    # Handle Tool Call events specifically to make them look like system logs
                    if 'ToolCall' in message.__class__.__name__:
                        with st.expander(f"⚙️ Tool Usage: {source}", expanded=False):
                            st.write(message)
                        continue

                    content = getattr(message, 'content', "")
                    st.write(content)
                    
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")

if analyze_btn:
    if stock_name:
        with st.spinner(f"Gathering data and analyzing {stock_name}..."):
            # Create a new event loop for this run if needed, or simply run
            asyncio.run(run_analysis(stock_name))
    else:
        st.warning("Please enter a valid stock ticker.")
