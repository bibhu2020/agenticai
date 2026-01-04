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

from tools.resume_tools import read_local_file

def get_candidate_profiler(model_client):
    
    # Wrap tools
    read_tool = FunctionTool(read_local_file, description="Reads a local file (PDF, DOCX, or TXT) and returns its text content.")

    return AssistantAgent(
        name="Candidate_Profiler",
        model_client=model_client,
        tools=[read_tool],
        system_message="""
        You are an expert Candidate Profiler.
        
        Task:
        1. Read the candidate's resume (using `read_local_file` if path provided).
        2. Summarize the candidate's professional profile, key skills, years of experience, and notable achievements.
        3. Do NOT evaluate the candidate against any job description yet. Just provide a factual, comprehensive summary. Also extract the Candidate's Name if available.
        
        IMPORTANT: 
        - Extract the Candidate's Name if available.
        - Output the results in the JSON format below.
        
        Output:
        Return a JSON object:
        ```json
        {
          "candidate_name": "...",
          "candidate_summary": "...",
          "key_skills": ["..."],
          "years_of_experience": "...",
          "recent_roles": ["..."]
        }
        ```
        
        After the JSON, you MUST write exactly: HANDOFF_TO_JOB_ANALYST
        """,
    )
