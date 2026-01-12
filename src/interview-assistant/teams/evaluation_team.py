from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.agents import UserProxyAgent
from agents.definitions import (
    get_evaluator, 
    get_coordinator
)

async def run_evaluation_team(candidate_name: str, job_description: str):
    # PRE-OPTIMIZATION: Fetch context directly to save LLM turns
    from tools.rag_tools import search_candidate_knowledge_base
    print(f"[DEBUG] Pre-fetching context for {candidate_name}...", flush=True)
    resume_context = await search_candidate_knowledge_base(f"Summary and skills for {candidate_name}", candidate_name)

    # Initialize Agents (Reduced Team)
    # We merged JD & Resume analysis into the prompt for the Evaluator
    evaluator = get_evaluator()
    coordinator = get_coordinator()

    TERMINATION_KEYWORD = "EVALUATION" + "_" + "APPROVED"

    # Define Termination
    termination = TextMentionTermination(TERMINATION_KEYWORD) | MaxMessageTermination(10)

    # Create Team (2 Agents)
    # Flow: Evaluator (Analysis) -> Coordinator (Validation) -> Loop
    team = RoundRobinGroupChat(
        participants=[evaluator, coordinator], 
        termination_condition=termination
    )

    # Initial Prompt
    task = f"""
    PROJECT: Candidate Evaluation
    Candidate Name: {candidate_name}
    
    JOB DESCRIPTION:
    {job_description}
    
    RESUME CONTEXT (Pre-retrieved):
    {resume_context}
    
    GOAL: Produce a high-quality, data-driven evaluation JSON.

    PROCESS:
    1. Evaluator: Analyze JD requirements vs Resume Context. Score (0-10) and identify Strengths/Weaknesses.
    2. Coordinator: Review against strict JSON rules.
    
    ITERATION RULES:
    - If Coordinator REJECTS, Evaluator must fix.
    - When satisfied, Coordinator outputs "EVALUATION", underscore, "APPROVED".
    """

    print(f"[DEBUG] Starting Evaluation Team for {candidate_name}")
    last_message = ""
    last_json_message = ""
    
    async for message in team.run_stream(task=task):
        if hasattr(message, 'content') and isinstance(message.content, str):
            content = message.content
            print(f"[DEBUG] Agent '{message.source}' says: {content[:60]}...")
            last_message = content
            
            # Simple heuristic to trap the JSON payload
            # look for keys that MUST be present
            if '"score"' in content and '"key_matches"' in content:
                last_json_message = content
    
    print(f"[DEBUG] Evaluation Team finished. Final message length: {len(last_message)}")
    
    # Prefer the structured JSON message if we found one
    return last_json_message if last_json_message else last_message
