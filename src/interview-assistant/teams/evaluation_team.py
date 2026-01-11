from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.agents import UserProxyAgent
from agents.definitions import (
    get_jd_summarizer, 
    get_resume_summarizer, 
    get_evaluator, 
    get_coordinator
)

async def run_evaluation_team(candidate_name: str, job_description: str):
    # Initialize Agents
    jd_agent = get_jd_summarizer()
    resume_agent = get_resume_summarizer()
    evaluator = get_evaluator()
    coordinator = get_coordinator()

    TERMINATION_KEYWORD = "EVALUATION" + "_" + "APPROVED"

    # Define Termination
    # Stop when Coordinator says "EVALUATION_APPROVED"
    termination = TextMentionTermination(TERMINATION_KEYWORD) | MaxMessageTermination(30)

    # Create Team
    # Analysis Flow: JD Agent -> Resume Agent -> Evaluator -> Coordinator -> (Loop)
    team = RoundRobinGroupChat(
        participants=[jd_agent, resume_agent, evaluator, coordinator], 
        termination_condition=termination
    )

    # Initial Prompt
    task = f"""
    PROJECT: Candidate Evaluation
    Candidate Name: {candidate_name}
    Job Description: {job_description}
    
    GOAL: Produce a high-quality, data-driven evaluation JSON.

    PROCESS:
    1. JD_Summarizer, extract key requirements.
    2. Resume_Summarizer, find matches for these requirements for {candidate_name}.
    3. Evaluator, score the candidate (0-10) and analyze Strengths/Weaknesses.
    4. Coordinator, review against the rules.
    
    ITERATION RULES:
    - If the Coordinator REJECTS (due to vague data or bad format), the team must refine the analysis.
    - Continue looping until the quality is perfect.
    - When satisfied, Coordinator outputs the JSON and the signal: "EVALUATION", underscore, "APPROVED".
    """

    print(f"[DEBUG] Starting Evaluation Team for {candidate_name}")
    last_message = ""
    async for message in team.run_stream(task=task):
        if hasattr(message, 'content') and isinstance(message.content, str):
            print(f"[DEBUG] Agent '{message.source}' says: {message.content[:60]}...")
            last_message = message.content
            # Optional: Print stream for debug
            # print(f"{message.source}: {message.content[:50]}...")
    
    print(f"[DEBUG] Evaluation Team finished. Final message length: {len(last_message)}")
    return last_message
