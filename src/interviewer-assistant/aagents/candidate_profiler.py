from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool

# Import tools
import sys
import os

# Ensure we can import from parent directory if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from tools.resume_tools import read_local_file, scrape_web_page

def get_candidate_profiler(model_client):
    
    # Wrap tools
    read_tool = FunctionTool(read_local_file, description="Reads a local file (PDF, DOCX, or TXT) and returns its text content.")
    scrape_tool = FunctionTool(scrape_web_page, description="Fetches the content of a web page (e.g., LinkedIn public profile) and returns the text.")

    return AssistantAgent(
        name="Candidate_Profiler",
        model_client=model_client,
        tools=[read_tool, scrape_tool],
        system_message="""
        You are an expert Candidate Profiler.
        
        Task:
        1. Read the candidate's resume (using `read_local_file` if path provided) and/or LinkedIn profile (using `scrape_web_page` if URL provided).
        2. Summarize the candidate's professional profile, key skills, years of experience, and notable achievements.
        3. Do NOT evaluate the candidate against any job description yet. Just provide a factual, comprehensive summary.
        
        IMPORTANT: 
        - If you have the Resume content, that is sufficient. exact LinkedIn data is secondary. 
        - Do not retry scraping if it fails or returns empty/short content. Proceed with the Resume only.
        - Output the results in the JSON format below.
        - After outputting the JSON, do not perform further actions.
        
        Output:
        Return a JSON object:
        ```json
        {
          "candidate_summary": "...",
          "key_skills": ["..."],
          "years_of_experience": "...",
          "recent_roles": ["..."]
        }
        ```
        
        End your message with: HANDOFF_TO_JOB_ANALYST
        """,
    )
