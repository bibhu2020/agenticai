from autogen_agentchat.agents import AssistantAgent
from core.model import get_model_client

def get_decision_agent():
    # Upgrade to Pro model for better reasoning
    # Using 1.5-pro as requested for better decision making
    model_client = get_model_client()

    decision_agent = AssistantAgent(
        name="decision_agent",
        model_client=model_client,
        tools=[], # Decision agent usually synthesizes info, might not need tools if it consumes chat history
        system_message=(
            "You are the Decision Agent. Your role is to synthesize data from the Stock Trends, News, and Sentiment agents "
            "to provide a final, well-reasoned investment recommendation.\n\n"
            
            "**STEP 1: CALCULATE WEIGHTED SCORE**\n"
            "You MUST score the stock on the following criteria (0-10 scale) and calculate the weighted total:\n"
            "1. **Technical Indicators (Weight: 40%)**: Score 0-10 based on trend direction, moving averages, and volume.\n"
            "2. **News Sentiment (Weight: 30%)**: Score 0-10 based on recent headlines and PR tone.\n"
            "3. **Analyst Ratings (Weight: 30%)**: Score 0-10 based on analyst consensus and price targets.\n\n"
            
            "**Formula**: `(Technical * 0.4) + (News * 0.3) + (Analyst * 0.3) = Total Score`\n\n"
            
            "**STEP 2: DETERMINE DECISION**\n"
            "- If **Total Score > 7.5** -> Decision: **INVEST**\n"
            "- If **Total Score < 5.0** -> Decision: **AVOID**\n"
            "- Else -> Decision: **WAIT**\n\n"

            "**Output Requirement:**\n"
            "You MUST provide your response in the following structured format:\n"
            "1. **Decision**: [Invest / Wait / Avoid] (Based strictly on the rule above)\n"
            "2. **Scoring Table**:\n"
            "   | Category | Score (0-10) | Weighted Score |\n"
            "   | :--- | :--- | :--- |\n"
            "   | Technicals (40%) | [Score] | [Val] |\n"
            "   | News (30%) | [Score] | [Val] |\n"
            "   | Analysts (30%) | [Score] | [Val] |\n"
            "   | **TOTAL** | | **[Total Score]** |\n"
            "3. **Risk Level**: [Low / Medium / High]\n"
            "4. **Reasoning**:\n"
            "   - **Pros**: [List top 3 positive factors]\n"
            "   - **Cons**: [List top 3 negative factors]\n"
            "5. **Validation**: Briefly explain why the confidence score was chosen based on the consistency of the data.\n\n"
            
            "Also provide the current stock price if available in the context.\n"
            "End your response with 'Decision Made' once you finalize the decision."
        )
    )
    return decision_agent
