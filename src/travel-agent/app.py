import os
import sys
from pathlib import Path
import streamlit as st
import asyncio
import uuid
import json
import logfire
from datetime import datetime
from typing import List, Dict, Any
from aagents import travel_agent
from contexts import UserContext
from output_types import TravelPlan
from output_types import FlightRecommendation
from output_types import HotelRecommendation
from agents import Runner


# Load environment variables


# Logger configuration
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_openai_agents()

# Page configuration
st.set_page_config(
    page_title="Travel Planner Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Premium, Compact Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }

    /* ---------------------------------------------------------------------
       LAYOUT & HERO BANNER (Chatbot Style)
       --------------------------------------------------------------------- */

    /* Desktop Layout */
    @media (min-width: 769px) {
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 2rem !important;
            /* Restore standard centered layout */
            max-width: 1200px !important; 
        }
        
        .hero-container {
            margin-top: 1rem;
            /* Remove negative margins to keep it contained */
            margin-left: 0;
            margin-right: 0;
            padding: 2rem 1rem 1.5rem 1rem;
            border-radius: 16px; /* Rounded corners since it's floating now */
        }
    }
    
    /* Mobile Layout */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0 !important;
        }
        
        .hero-container {
            margin-top: 0.5rem;
            margin-left: 0;
            margin-right: 0;
            padding: 1.5rem 1rem;
            border-radius: 12px;
        }
    }
    
    /* Hero Styling */
    .hero-container {
        /* Travel Theme Gradient */
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
        color: white;
        text-align: center;
        border-radius: 16px; /* consistent rounded corners */
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        position: relative;
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: white !important;
        -webkit-text-fill-color: white !important; /* Override previous gradient text */
        background: none !important;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 400;
        color: rgba(255,255,255,0.95) !important;
        margin-top: 0;
    }
    
    /* Remove Header Decoration */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0 !important;
        z-index: 100;
    }
    div[data-testid="stDecoration"] { display: none; }

    /* Compact Form Card */
    .form-card {
        background: transparent;
        padding: 0;
        border-radius: 0;
        box-shadow: none;
        border: none;
        margin-bottom: 1rem;
        margin-top: -0.5rem;
    }

    /* Compact Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 0.4rem !important;
        border: 1px solid #e0e0e0;
        padding: 0.3rem 0.5rem;
        font-size: 0.9rem;
        min-height: 2rem;
    }
    
    .stMarkdown h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Primary Button */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #0ba360 0%, #3cba92 100%); /* Match Hero */
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 0.4rem;
        font-size: 1rem;
        line-height: 1.2;
    }
    
    /* Results Grid Area */
    .results-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    /* Output Cards */
    .output-card {
        background: white;
        border: 1px solid #eaeaea;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        height: 100%;
    }
    
    .output-card h3 {
        font-size: 1rem; 
        margin-top: 0;
        color: #2c3e50;
    }
    
    /* Chat message container adjustment */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .avatar { width: 32px; height: 32px; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "latest_plan" not in st.session_state:
    st.session_state.latest_plan = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(user_id=str(uuid.uuid4()))
if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def handle_user_message(user_input: str):
    """Add user message to history and queue for processing."""
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    st.session_state.processing_message = user_input

def format_agent_response(output):
    """Format structured output into HTML for display."""
    if hasattr(output, "model_dump"):
        output = output.model_dump()
    
    # Grid item wrapper
    wrapper_start = '<div class="output-card">'
    wrapper_end = '</div>'

    if isinstance(output, dict):
        if "destination" in output:  # TravelPlan
            activities_html = "".join([f"<li>{a}</li>" for a in output.get('activities', [])])
            return f"""
            {wrapper_start}
                <h3>🌟 Travel Plan: {output.get('destination', 'Your Trip')}</h3>
                <div style="display:flex; gap:0.5rem; margin-bottom:0.5rem;">
                    <span style="background:#e3f2fd; color:#1565c0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">
                        📅 {output.get('duration_days', 'N/A')} days
                    </span>
                    <span style="background:#e8f5e9; color:#2e7d32; padding:2px 6px; border-radius:4px; font-size:0.8rem;">
                        💰 ${output.get('budget', 'N/A')}
                    </span>
                </div>
                <strong>✨ Recommended Activities:</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.2rem;">{activities_html}</ul>
                <p style="color:#666; font-style:italic; margin-top:0.5rem;">📝 {output.get('notes', '')}</p>
            {wrapper_end}
            """
            
        elif "airline" in output:  # FlightRecommendation
            return f"""
            {wrapper_start}
                <h3>✈️ Flight to {output.get('destination', 'Destination')}</h3>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.25rem; margin-bottom:0.5rem; font-size:0.8rem;">
                    <div><strong>Airline:</strong> {output.get('airline', 'N/A')}</div>
                    <div><strong>Price:</strong> ${output.get('price', 'N/A')}</div>
                    <div><strong>Departs:</strong> {output.get('departure_time', 'N/A')}</div>
                    <div><strong>Arrives:</strong> {output.get('arrival_time', 'N/A')}</div>
                </div>
                <p><strong>Use:</strong> {output.get('recommendation_reason', '')}</p>
            {wrapper_end}
            """
            
        elif "name" in output and "amenities" in output:  # HotelRecommendation
            amenities_html = ", ".join(output.get('amenities', []))
            return f"""
            {wrapper_start}
                <h3>🏨 {output.get('name', 'N/A')}</h3>
                <p style="margin: 0.2rem 0;"><strong>📍 {output.get('location', 'N/A')}</strong></p>
                <p style="margin: 0.2rem 0;"><strong>💲 {output.get('price_per_night', 'N/A')}/night</strong></p>
                <p style="font-size:0.8rem; color:#555; margin: 0.2rem 0;">🛠 {amenities_html}</p>
                <p style="margin-top:0.5rem; font-size:0.85rem;"><em>{output.get('recommendation_reason', '')}</em></p>
            {wrapper_end}
            """
    return str(output)

# ------------------------------------------------------------------
# UI Layout
# ------------------------------------------------------------------

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🌍 Travel Agent</div>
    <div class="hero-subtitle">Design your perfect journey with AI-powered personalized planning</div>
</div>
""", unsafe_allow_html=True)

# Main Form Container
with st.container():
    st.markdown('<div class="form-card" style="padding: 1rem;">', unsafe_allow_html=True)
    
    with st.form("input_form"):
        # Row 1: All Core Details in one line
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 0.8, 0.8])
        with c1:
            origin = st.text_input("Origin", value=st.session_state.user_context.source_destination or "Dallas")
        with c2:
            destination = st.text_input("Destination", value=st.session_state.user_context.target_destination or "Paris")
        with c3:
            start_date = st.text_input("From", value="Dec 25")
        with c4:
            end_date = st.text_input("To", value="Jan 5")

        # Row 2: Budget & Preferences
        c5, c6, c7 = st.columns([1, 1.5, 1.5])
        with c5:
            budget_range = st.slider("Budget ($)", 2000, 20000, (5000, 10000), 500, format="$%d")
        with c6:
            airlines = st.multiselect("Airlines", ["SkyWays", "Delta", "United", "American"], default=st.session_state.user_context.preferred_airlines)
        with c7:
            amenities = st.multiselect("Amenities", ["WiFi", "Pool", "Gym", "Breakfast", "Spa"], default=st.session_state.user_context.hotel_amenities)
            
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨ Plan Trip")
        
    st.markdown('</div>', unsafe_allow_html=True)

# Form Handling & Logic
if submitted:
    if not origin or not destination:
        st.error("⚠️ Origin & Destination required.")
    else:
        # Save Context
        travel_dates = f"{start_date} to {end_date}" if start_date and end_date else "Flexible dates"
        budget_str = f"${budget_range[0]} - ${budget_range[1]}"
        
        st.session_state.user_context.source_destination = origin
        st.session_state.user_context.target_destination = destination
        st.session_state.user_context.travel_dates = travel_dates
        st.session_state.user_context.budget_level = budget_str
        st.session_state.user_context.preferred_airlines = airlines
        st.session_state.user_context.hotel_amenities = amenities
        
        # Prepare Prompt
        prompt = f"Plan a trip from {origin} to {destination} for {travel_dates}. Budget: {budget_str}. Airlines: {', '.join(airlines)}. Amenities: {', '.join(amenities)}."
        
        # Run Agent
        with st.spinner("Creating your perfect itinerary..."):
            try:
                # Direct Agent Call
                result = asyncio.run(Runner.run(
                    travel_agent,
                    prompt, # Simplified input
                    context=st.session_state.user_context
                ))
                st.session_state.latest_plan = result.final_output
                
                # DEBUG: Show raw output
                st.markdown("### 🐛 Debug Output")
                st.write("Result Type:", type(result.final_output))
                st.write("Result Content:", result.final_output)
                if hasattr(result.final_output, "model_dump"):
                     st.json(result.final_output.model_dump())
            except Exception as e:
                st.error(f"Error: {e}")

# ------------------------------------------------------------------
# Results Dashboard (Replacing Chat)
# ------------------------------------------------------------------

if st.session_state.latest_plan:
    output = st.session_state.latest_plan
    if hasattr(output, "model_dump"):
        output = output.model_dump()
        
    if isinstance(output, dict) and "flight_options" in output:
        # Weather Banner
        st.markdown(f"""
        <div style="background:#e0f7fa; padding:1rem; border-radius:12px; margin-bottom:1.5rem; text-align:center; border:1px solid #b2ebf2;">
            <h3 style="margin:0; color:#006064;">🌤 Weather in {output.get('destination')}</h3>
            <p style="margin:0.5rem 0 0 0; color:#00838f;">{output.get('weather_remark', 'Forecast loading...')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🗺️ Itinerary Options")
        
        # Zip options to create paired rows
        flights = output.get('flight_options', [])
        hotels = output.get('hotel_options', [])
        
        # Determine max length to iterate
        max_opts = min(len(flights), len(hotels))
        
        for i in range(max_opts):
            f = flights[i]
            h = hotels[i]
            
            # Combine into a "Row Card"
            total_est = f.get('price', 0) + (h.get('price_per_night', 0) * output.get('duration_days', 5))
            
            st.markdown(f"""
            <div class="output-card" style="margin-bottom:1rem; border-left: 5px solid #0ba360;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <h3 style="margin:0;">Option {i+1}</h3>
                    <span style="background:#e8f5e9; color:#2e7d32; padding:4px 12px; border-radius:20px; font-weight:bold;">
                        Total Est: ${total_est:,.0f}
                    </span>
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1.5rem;">
                    <!-- Flight -->
                    <div style="background:#f8f9fa; padding:1rem; border-radius:8px;">
                        <div style="font-weight:bold; color:#1565c0; margin-bottom:0.5rem;">✈️ Flight: {f.get('airline')}</div>
                        <div style="font-size:0.9rem;">{f.get('departure_time')} ➔ {f.get('arrival_time')}</div>
                        <div style="font-size:0.9rem; color:#666; margin-top:0.3rem;">{f.get('recommendation_reason')}</div>
                        <div style="font-weight:bold; margin-top:0.5rem;">${f.get('price')}</div>
                    </div>
                    
                    <!-- Hotel -->
                    <div style="background:#fff3e0; padding:1rem; border-radius:8px;">
                        <div style="font-weight:bold; color:#e65100; margin-bottom:0.5rem;">🏨 Hotel: {h.get('name')}</div>
                        <div style="font-size:0.9rem;">📍 {h.get('location')}</div>
                        <div style="font-size:0.8rem; color:#666; margin-top:0.3rem;">{", ".join(h.get('amenities', [])[:3])}...</div>
                         <div style="font-weight:bold; margin-top:0.5rem;">${h.get('price_per_night')}/night</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Notes & Activities footer
        st.markdown(f"""
        <div style="margin-top:2rem; padding:1.5rem; background:white; border-radius:12px; border:1px solid #eee;">
            <h4>✨ Recommended Activities</h4>
            <ul style="columns: 2;">
                {"".join([f"<li>{a}</li>" for a in output.get('activities', [])])}
            </ul>
            <hr style="margin:1rem 0; border-top:1px solid #eee;">
            <p style="font-style:italic; color:#666;">📝 Guide's Note: {output.get('notes')}</p>
        </div>
        """, unsafe_allow_html=True)