import streamlit as st

def render_hero():
    st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Interview Assistant</div>
    <div class="hero-subtitle">Automated Resume Analysis & Interview Prep • Powered by AutoGen</div>
</div>
""", unsafe_allow_html=True)
