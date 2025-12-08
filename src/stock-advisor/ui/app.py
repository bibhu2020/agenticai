# ui/app_agentic.py

from agents import Agent, Runner, Tool
from agent_tools.data_agent import DataAgent
from agent_tools.sentiment_agent import SentimentAgent
from agent_tools.strategy_agent import StrategyAgent
import gradio as gr

# Initialize underlying agents as tools
data_agent = DataAgent()
sentiment_agent = SentimentAgent()
strategy_agent = StrategyAgent()

# Wrap agent methods as Tools
tools = [
    Tool(
        name="Fetch OHLCV & Company Info",
        func=lambda query: data_agent.fetch(query),
        description="Fetches historical OHLCV and basic company info for a given stock ticker."
    ),
    Tool(
        name="Analyze Market Sentiment",
        func=lambda query: sentiment_agent.analyze(query),
        description="Returns the market sentiment for a company, sector, or index based on news & social media."
    ),
    Tool(
        name="Option Strategy Recommendation",
        func=lambda query: strategy_agent.recommend(query),
        description="Recommends option trading strategies based on market trends and sentiment analysis."
    )
]

# Define Stock Advisor Agent
stock_agent = Agent(
    name="Stock Advisor",
    instructions="""
You are a specialized financial advisor. You only answer questions related to stock data,
market sentiment, upcoming earnings, or option trading recommendations. 
Use the available tools to fetch data and provide accurate, concise, and actionable advice.
""",
    tools=tools,
    model="gpt-4o-mini"
)

# Orchestrator to manage agent reasoning
orchestrator = Runner(
    agents=[stock_agent],
    model="gpt-4o-mini",
    max_parallel=3  # Allow parallel tool execution
)

# Predefined prompts
PROMPTS = [
    "Recommend me 3 high profitable option trading based on market news and sentiments.",
    "Tell me how is the overall market sentiment this week.",
    "Tell me the upcoming earnings in next 2 weeks.",
    "Provide a summary of Apple Inc.'s financials and latest stock price.",
    "Analyze the trend of Tesla stock in the last month."
]

# Gradio UI
def stock_chatbot(query: str) -> str:
    try:
        # Orchestrator routes query to Stock Advisor agent
        response = orchestrator.run(stock_agent, query)
        return response.output_text
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks(title="Agentic Stock Chatbot") as app:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Stock Chatbot Prompts")
            for prompt in PROMPTS:
                btn = gr.Button(prompt)
                btn.click(lambda p=prompt: [(p, stock_chatbot(p))], [], gr.Chatbot())
        with gr.Column(scale=3):
            chatbox = gr.Chatbot(label="Stock Advisor")
            user_input = gr.Textbox(placeholder="Ask a stock-related question...", lines=2)
            submit_btn = gr.Button("Send")

    def submit_query(message, history):
        response = stock_chatbot(message)
        return history + [(message, response)], ""

    submit_btn.click(submit_query, [user_input, chatbox], [chatbox, user_input])
    user_input.submit(submit_query, [user_input, chatbox], [chatbox, user_input])

if __name__ == "__main__":
    app.launch()
