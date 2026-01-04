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
    from ..aagents.team_lead import get_team_lead

except ImportError:
    from aagents.job_analyst import get_job_analyst
    from aagents.job_analyst_reviewer import get_job_analyst_reviewer
    from aagents.candidate_profiler import get_candidate_profiler
    from aagents.evaluator import get_evaluator
    from aagents.interview_designer import get_interview_designer
    from aagents.team_lead import get_team_lead


from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

class LinearInterviewTeam:
    def __init__(self, model_client):
        self.model_client = model_client # Save for resets
        self.profiler = get_candidate_profiler(model_client)
        self.job_analyst = get_job_analyst(model_client)
        self.reviewer = get_job_analyst_reviewer(model_client)
        self.evaluator = get_evaluator(model_client)
        self.designer = get_interview_designer(model_client)
        self.lead = get_team_lead(model_client)

    async def run_stream(self, task: str):
        # 1. Profiler
        print("[DEBUG] LinearTeam: Running Profiler")
        msg = TextMessage(content=task, source="user")
        res = await self.profiler.on_messages([msg], cancellation_token=CancellationToken())
        profiler_msg = res.chat_message
        yield profiler_msg
        
        # 2. Analyst
        print("[DEBUG] LinearTeam: Running Analyst")
        res = await self.job_analyst.on_messages([profiler_msg], cancellation_token=CancellationToken())
        analyst_msg = res.chat_message
        yield analyst_msg
        
        # 3. Reviewer Loop
        approved_analysis_msg = analyst_msg
        for i in range(3):
             print(f"[DEBUG] LinearTeam: Running Reviewer Attempt {i+1}")
             res = await self.reviewer.on_messages([approved_analysis_msg], cancellation_token=CancellationToken())
             review_msg = res.chat_message
             yield review_msg
             
             if "APPROVE" in review_msg.content:
                 print("[DEBUG] Analysis Approved")
                 break
             
             # Re-run Analyst
             print("[DEBUG] Review Rejected. Re-running Analyst.")
             res = await self.job_analyst.on_messages([review_msg], cancellation_token=CancellationToken())
             approved_analysis_msg = res.chat_message
             yield approved_analysis_msg
             
        # 4. Evaluator (Pass Profiler + Analysis context)
        print("[DEBUG] LinearTeam: Running Evaluator")
        res = await self.evaluator.on_messages([profiler_msg, approved_analysis_msg], cancellation_token=CancellationToken())
        eval_msg = res.chat_message
        yield eval_msg
        
        # 5. Designer (Pass Analysis + Evaluation context)
        print("[DEBUG] LinearTeam: Running Designer")
        res = await self.designer.on_messages([approved_analysis_msg, eval_msg], cancellation_token=CancellationToken())
        designer_msg = res.chat_message
        yield designer_msg
        
        # 6. Team Lead Loop (QA)
        current_design_msg = designer_msg
        for i in range(3):
            print(f"[DEBUG] LinearTeam: Running Team Lead QA Attempt {i+1}")
            res = await self.lead.on_messages([current_design_msg], cancellation_token=CancellationToken())
            lead_msg = res.chat_message
            yield lead_msg
            
            if "TERMINATE" in lead_msg.content:
                print("[DEBUG] Process Terminated Successfully")
                break
                
            # Re-run Designer with feedback
            print("[DEBUG] Design Rejected. Clearing history and Re-running Designer.")
            
            # Reset Designer to prevent context overflow (Draft 1 is huge)
            self.designer = get_interview_designer(self.model_client)
            
            # Create a fresh instruction including the feedback
            retry_instruction = f"""
            The Team Lead reviewed your previous draft and provided this feedback:
            {lead_msg.content}
            
            Please regenerate the ENTIRE interview guide (JSON) from scratch, ensuring you address the feedback above.
            Use the original Job Analysis and Evaluation context provided.
            """
            retry_msg = TextMessage(content=retry_instruction, source="user")
            
            # Pass original context + retry instruction
            res = await self.designer.on_messages([approved_analysis_msg, eval_msg, retry_msg], cancellation_token=CancellationToken())
            current_design_msg = res.chat_message
            yield current_design_msg

def get_interview_team(model_client):
    return LinearInterviewTeam(model_client)

def extract_json(text: str) -> Dict[str, Any]:
    """Helper to extract JSON from markdown code blocks or raw text."""
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except:
        return {}
