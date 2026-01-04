import streamlit as st

def render_sidebar(cookie_manager):
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("Interview Prep")
        
        # Mode Selection
        mode = st.radio("Select Persona", ["Interviewer", "Candidate"], index=0, horizontal=True)
        
        # Initialize Defaults from Cookies
        # Note: cookie_manager.get can vary in timing, but usually fine.
        cookie_jd = cookie_manager.get(cookie="job_description")
        
        job_description = None
        uploaded_resume = None
        
        if mode == "Interviewer":
            st.info("Upload JD and Resume to generate a structured interview guide.")
            st.markdown("---")
            st.subheader("1. Job Description")
            default_jd = cookie_jd if cookie_jd else ""
            job_description = st.text_area("Paste JD Text", value=default_jd, height=200, placeholder="Paste the full Job Description here...", key="jd_input")

            st.subheader("2. Candidate Resume")
            uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx", "txt"])
            
            st.markdown("---")
            # State Initialization
            if "analyzing" not in st.session_state:
                st.session_state.analyzing = False
            if "generated_report" not in st.session_state:
                st.session_state.generated_report = None
            if "generated_pdf" not in st.session_state:
                st.session_state.generated_pdf = None

            def start_btn_click():
                st.session_state.analyzing = True
                st.session_state.generated_report = None # Clear previous
                st.session_state.generated_pdf = None
                # Save cookies when button is clicked
                if st.session_state.get("jd_input"):
                     cookie_manager.set("job_description", st.session_state.jd_input, key="set_jd")

            if st.session_state.analyzing:
                # Disable button while running
                btn_disabled = True
            else:
                btn_disabled = False

            st.button("🚀 Generate Interview Guide", type="primary", use_container_width=True, on_click=start_btn_click, disabled=btn_disabled)
        
        else:
            # Candidate Mode Sidebar
            st.info("Switch to 'Interviewer' to generate guides.")
            st.success("Candidate Practice Mode active.")
            
        return {
            "mode": mode,
            "job_description": job_description,
            "uploaded_resume": uploaded_resume
        }
