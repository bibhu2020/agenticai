import streamlit as st
import asyncio
from src.accessibility_v2.patterns.orchestrator import AccessibilityOrchestrator

st.set_page_config(page_title="Accessibility V2", layout="wide", page_icon="♿")

st.title("♿ AI Accessibility Auditor")
st.markdown("Enter a URL to perform a comprehensive WCAG 2.1 AA audit powered by Playwright and GPT-4o.")

url = st.text_input("Website URL", "https://example.com")

if st.button("Run Audit", type="primary"):
    orchestrator = AccessibilityOrchestrator()
    placeholder = st.empty()
    
    async def run():
        full_response = ""
        async for update in orchestrator.audit_site(url):
            if update.startswith("🔍") or update.startswith("🧠"):
                placeholder.info(update)
            else:
                full_response = update # The final markdown
        
        placeholder.empty()
        st.markdown(full_response)
        
    asyncio.run(run())
