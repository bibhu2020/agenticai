from core.state import AgentState
from tools.market_data import get_market_data
from tools.news_data import get_news_sentiment
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# --- LLM Setup ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# --- Nodes ---

def market_analyst_node(state: AgentState):
    print("--- MARKET ANALYST (AI) ---")
    ticker = state['ticker']
    
    # 1. Get raw data (Tool)
    try:
        raw_data = get_market_data(ticker)
    except Exception as e:
        raw_data = {"error": str(e)}

    # 2. AI Reasoning
    system_prompt = "You are a veteran Technical Analyst. Analyze the provided market data and trends. Be decisive."
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze the technicals for {ticker}.\nData: {raw_data}")
    ])
    chain = prompt | llm
    analysis = chain.invoke({"ticker": ticker, "raw_data": str(raw_data)}).content
    
    return {
        "market_data": raw_data, 
        "messages": [f"**Market Analyst**: {analysis}"]
    }

def sentiment_analyst_node(state: AgentState):
    print("--- SENTIMENT ANALYST (AI) ---")
    ticker = state['ticker']
    
    # 1. Get raw data (Tool)
    try:
        raw_data = get_news_sentiment(ticker)
    except Exception as e:
        raw_data = {"error": str(e)}

    # 2. AI Reasoning
    system_prompt = "You are a News Sentiment Expert. Summarize the market mood based on these headlines. Ignore noise."
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze sentiment for {ticker}.\nData: {raw_data}")
    ])
    chain = prompt | llm
    analysis = chain.invoke({"ticker": ticker, "raw_data": str(raw_data)}).content

    return {
        "sentiment_data": raw_data,
        "messages": [f"**Sentiment Analyst**: {analysis}"]
    }

def strategy_advisor_node(state: AgentState):
    print("--- STRATEGY ADVISOR (AI) ---")
    
    # Needs context from previous agents
    # We can perform a "history search" or just grab the latest messages from the state if we structured it
    # But simpler is to use the data + the implicit context if we passed it. 
    # Since we are in a graph, state accumulates.
    
    market_msg = [m for m in state['messages'] if "Market Analyst" in m][-1]
    sentiment_msg = [m for m in state['messages'] if "Sentiment Analyst" in m][-1]
    
    system_prompt = (
        "You are a master Options Strategist. Based on the Technical and Sentiment analysis provided, "
        "propose a high-probability trade. You MUST output a structured strategy."
    )
    
    user_prompt = f"""
    {market_msg}
    
    {sentiment_msg}
    
    Propose an optimal option strategy (Spread, Iron Condor, etc) or a raw stock trade.
    """

    class Strategy(BaseModel):
        action: str = Field(description="BUY, SELL, or WAIT")
        confidence: float = Field(description="Confidence score 0-100")
        entry: float = Field(description="Entry price target")
        exit: float = Field(description="Exit price target")
        stop_loss: float = Field(description="Stop loss price")
        reasoning: str = Field(description="Detailed reasoning for the trade structure")

    chain = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ]) | llm.with_structured_output(Strategy)
    
    result = chain.invoke({})
    
    strategy_data = {
        "action": result.action,
        "confidence": result.confidence,
        "entry": result.entry,
        "exit": result.exit,
        "stop_loss": result.stop_loss,
        "reasoning": result.reasoning
    }
    
    return {
        "strategy_data": strategy_data,
        "messages": [f"**Strategy Advisor**: Proposed {result.action} ({result.confidence}% Conf). {result.reasoning}"]
    }

def risk_manager_node(state: AgentState):
    print("--- RISK MANAGER (AI) ---")
    strategy = state['strategy_data']
    market_msg = [m for m in state['messages'] if "Market Analyst" in m][-1]
    
    system_prompt = (
        "You are a conservative Risk Manager. Review the proposed strategy. "
        "Critique it heavily. Check if the confidence alignment matches the data. "
        "Output your final decision."
    )
    
    user_prompt = f"""
    Context:
    {market_msg}
    
    Proposed Strategy:
    Action: {strategy['action']}
    Confidence: {strategy['confidence']}
    Reasoning: {strategy['reasoning']}
    
    Do you approve?
    """
    
    # AI critique
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", user_prompt)])
    chain = prompt | llm
    critique = chain.invoke({}).content
    
    # Logic fallback for the "Final Decision" flag, but strictly AI driven would parse the critique
    approved = True
    if "reject" in critique.lower() or strategy['confidence'] < 70:
        approved = False
        
    final_report = f"""
    ## 🛡️ Risk Manager Validation
    
    **Status**: {"✅ APPROVED" if approved else "❌ REJECTED"}
    
    **Critique**: 
    {critique}
    
    ---
    ### Final Strategy
    *   **Action**: {strategy['action']}
    *   **Entry**: {strategy['entry']}
    *   **Target**: {strategy['exit']}
    *   **Stop**: {strategy['stop_loss']}
    """
    
    return {
        "final_report": final_report,
        "messages": [f"**Risk Manager**: {critique}"]
    }
