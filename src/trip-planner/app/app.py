import gradio as gr
import requests
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend endpoint - use environment variable or default to Hugging Face
BASE_URL = os.getenv("API_BASE_URL", "https://mishrabp-trip-advisor-api.hf.space")

def format_travel_plan(answer):
    """Format the travel plan response with markdown styling"""
    return f"""### 🗺️ AI-Generated Travel Plan  
**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}  
**Created by:** Kube9t's Travel Agent

---

{answer}

---

📝 *Please double-check all travel details, costs, and dates before booking.*"""

def query_travel_agent(message, history):
    """Handle the travel agent query and format the response"""
    try:
        # Make API request
        payload = {"question": message}
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            formatted_response = {
                "role": "assistant",
                "content": format_travel_plan(answer)
            }
        else:
            formatted_response = {
                "role": "assistant",
                "content": f"❌ Bot failed to respond: {response.text}"
            }
    except Exception as e:
        formatted_response = {
            "role": "assistant",
            "content": f"⚠️ Something went wrong: {str(e)}"
        }
    
    # Return updated history
    return history + [
        {"role": "user", "content": message},
        formatted_response
    ]

def create_demo():
    """Create and configure the Gradio interface"""
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        # Header
        gr.Markdown(
            """
            # 🌍 Travel Planner Agentic Application
            Let me help you design your next perfect trip — just tell me where you want to go!
            """
        )
        
        with gr.Row():
            # Sidebar
            with gr.Column(scale=1):
                gr.Image(
                    "https://cdn-icons-png.flaticon.com/512/201/201623.png",
                    width=80,
                    show_label=False
                )
                gr.Markdown("### Navigation")
                gr.Markdown("- 🏠 Home\n- 🧳 My Trips\n- ⚙️ Settings")
                gr.Markdown("---")
                gr.Markdown("*Powered by Kube9t's Travel Agent AI*")
            
            # Main chat interface
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=400,
                    show_label=False,
                    avatar_images=["👤", "🤖"],
                    type="messages"  # Use new message format
                )
                msg = gr.Textbox(
                    label="Ask me something like: 'Plan a 7 days trip to Washington-DC, NewYork, and Niagra.'",
                    placeholder="Type your travel query here...",
                    lines=2
                )
                with gr.Row():
                    submit = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear")

        # Event handlers
        msg.submit(
            fn=query_travel_agent,
            inputs=[msg, chatbot],
            outputs=chatbot
        ).then(
            fn=lambda: "",
            outputs=msg
        )
        
        submit.click(
            fn=query_travel_agent,
            inputs=[msg, chatbot],
            outputs=chatbot
        ).then(
            fn=lambda: "",
            outputs=msg
        )
        
        clear.click(lambda: [], outputs=chatbot)

    return demo

# Create and launch the app
app = create_demo()

if __name__ == "__main__":
    # Determine if running locally
    is_local = os.getenv("RUNNING_LOCAL", "false").lower() == "true"
    
    # Launch with appropriate settings
    if is_local:
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False
        )
    else:
        app.launch()