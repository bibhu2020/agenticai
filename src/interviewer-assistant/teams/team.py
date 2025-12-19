import sys
import os
import json
import re
from typing import Dict, Any

from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

# Ensure we can import from parent directory if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import agents
try:
    from ..aagents.job_analyst import get_job_analyst
    from ..aagents.job_analyst_reviewer import get_job_analyst_reviewer
    from ..aagents.candidate_profiler import get_candidate_profiler
    from ..aagents.evaluator import get_evaluator
    from ..aagents.interview_designer import get_interview_designer

except ImportError:
    from aagents.job_analyst import get_job_analyst
    from aagents.job_analyst_reviewer import get_job_analyst_reviewer
    from aagents.candidate_profiler import get_candidate_profiler
    from aagents.evaluator import get_evaluator
    from aagents.interview_designer import get_interview_designer


def get_interview_team(model_client):
    """
    Creates the Interview Team using SelectorGroupChat to enforce order.
    The order is: Profiler -> Job Analyst -> Reviewer -> Evaluator -> Designer
    """
    print(f"[DEBUG] Creating Interview Team")
    
    # 1. Initialize Agents
    profiler = get_candidate_profiler(model_client)
    job_analyst = get_job_analyst(model_client)
    reviewer = get_job_analyst_reviewer(model_client)
    evaluator = get_evaluator(model_client)
    designer = get_interview_designer(model_client)
    
    
    # 2. Define Selector/Transition Logic
    selector_prompt = """
    You are the Team Coordinator. Select the next speaker based on the conversation state:

    - BEGINNING: Select 'Candidate_Profiler' to read the resume/LinkedIn.
    - AFTER 'Candidate_Profiler' provides a JSON summary (look for 'HANDOFF_TO_JOB_ANALYST'): Select 'Job_Analyst'.
    - AFTER 'Job_Analyst' provides a JSON analysis: Select 'Job_Analyst_Reviewer'.
    - AFTER 'Job_Analyst_Reviewer' speaks:
        - If they APPROVE: Select 'Evaluator'.
        - If they REJECT or ask for changes: Select 'Job_Analyst'.
    - AFTER 'Evaluator' provides a JSON score: Select 'Interview_Designer'.
    - AFTER 'Interview_Designer' provides the interview guide: Select 'TERMINATE'.
    """
    
    # Restore full team with Selector
    # team = SelectorGroupChat(
    #     participants=[profiler, job_analyst, reviewer, evaluator, designer],
    #     model_client=model_client,
    #     termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(10),
    #     selector_prompt=selector_prompt,
    #     allow_repeated_speaker=True
    # )
    
    # Use RoundRobin as requested ("Keep it simple like market-analyst")
    # This avoids Selector logic loops. 
    # The agents must be robust enough to handle the sequential flow.
    print(f"[DEBUG] Using RoundRobinGroupChat")
    team = RoundRobinGroupChat(
        participants=[profiler, job_analyst, reviewer, evaluator, designer],
        termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(13)
    )
    print(f"[DEBUG] Team created: {team}")
    
    return team

def extract_json(text: str) -> Dict[str, Any]:
    """Helper to extract JSON from markdown code blocks or raw text."""
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except:
        return {}
