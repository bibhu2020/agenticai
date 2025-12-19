import streamlit as st

def apply_custom_styles():
    st.markdown("""
<style>
    /* GLOBAL LAYOUT */
    div.block-container {
        padding-top: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stChatMessage { background-color: #262730; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .report-container { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    h1, h2, h3 { color: #f0f2f6; }
    
    /* HERO BANNER - CONTAINED */
    .hero-banner {
        width: 100%;
        height: 120px;
        background: transparent; 
        color: #333;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        margin-top: -30px; /* Pull Up */
        z-index: 1;
        padding-top: 10px;
        border-bottom: 1px solid #eee;
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        /* Black Gradient */
        background: -webkit-linear-gradient(#000000, #333333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #000;
    }
    
    /* MOVE SIDEBAR UP */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)
