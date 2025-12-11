from autogen_agentchat.agents import AssistantAgent
from aagents.common import get_model_client

def get_decision_agent():
    # Upgrade to Pro model for better reasoning
    # Using 1.5-pro as requested for better decision making
    model_client = get_model_client(model="gemini-3-pro-preview", temperature=0.1)

    decision_agent = AssistantAgent(
        name="decision_agent",
        model_client=model_client,
        tools=[], # Decision agent usually synthesizes info, might not need tools if it consumes chat history
        system_message=(
            "You are the Decision Agent. Your role is to synthesize data from the Stock Trends, News, and Sentiment agents "
            "to provide a final, well-reasoned investment recommendation.\n\n"
            
            "**Output Requirement:**\n"
            "You MUST provide your response in the following structured format:\n"
            "1. **Decision**: [Invest / Wait / Avoid]\n"
            "2. **Confidence Score**: [0-100%]\n"
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
