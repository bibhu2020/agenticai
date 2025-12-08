import streamlit as st
import requests
import datetime

BASE_URL = "https://mishrabp-trip-advisor-api.hf.space/"   # Backend endpoint

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Travel Planner Agentic Application",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Sidebar Navigation
# ---------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=80)
    st.title("🌍 Travel Planner")
    st.markdown("Plan your trips effortlessly with AI ✈️")
    st.markdown("---")
    st.subheader("Navigation")
    st.page_link("https://openai.com", label="🏠 Home", disabled=True)
    st.page_link("https://openai.com", label="🧳 My Trips", disabled=True)
    st.page_link("https://openai.com", label="⚙️ Settings", disabled=True)
    st.markdown("---")
    st.caption("Powered by Kube9t's Travel Agent AI")

# ---------------------------
# Hero Section
# ---------------------------
st.markdown(
    """
    <div style="background-color:#0c2a45; padding:2rem 1rem; border-radius:10px;">
        <h1 style="color:white; text-align:center;">🌍 Travel Planner Agentic Application</h1>
        <p style="color:white; text-align:center; font-size:1.2rem;">
            Let me help you design your next perfect trip — just tell me where you want to go!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### ✨ What can I help you plan today?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input form
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("Ask me something like: 'Plan a 7 days trip to Washnigton-DC, NewYork, and Niagra.'")
    submit_button = st.form_submit_button("Send")

# Handle form submission
if submit_button and user_input.strip():
    try:
        with st.spinner("🧠 Thinking..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            markdown_content = f"""
### 🗺️ AI-Generated Travel Plan  
**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}  
**Created by:** Kube9t's Travel Agent

---

{answer}

---

📝 *Please double-check all travel details, costs, and dates before booking.*
"""
            st.markdown(markdown_content)
        else:
            st.error("❌ Bot failed to respond: " + response.text)

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
