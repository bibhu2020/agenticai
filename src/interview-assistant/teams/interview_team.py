from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.agents import UserProxyAgent
from agents.definitions import (
    get_interview_strategist, 
    get_question_generator, 
    get_question_reviewer,
    search_candidate_knowledge_base
)

async def run_interview_generation_team(candidate_name: str, job_description: str):
    # Pre-fetch Context to simplify agent flow
    # We query for the candidate name itself to get a general overview + strengths/weaknesses
    print(f"[DEBUG] Pre-fetching context for {candidate_name}...", flush=True)
    resume_context = await search_candidate_knowledge_base(f"Summary and skills for {candidate_name}", candidate_name)

    # Initialize Agents
    strategist = get_interview_strategist()
    generator = get_question_generator()
    reviewer = get_question_reviewer()

    TERMINATION_KEYWORD = "GUIDE" + "_" + "APPROVED"
    
    # Define Termination
    # Stop when Reviewer says "GUIDE_APPROVED"
    termination = TextMentionTermination(TERMINATION_KEYWORD) | MaxMessageTermination(30)

    # Create Team
    # Analysis Flow: Strategist -> Generator -> Reviewer -> (Loop)
    team = RoundRobinGroupChat(
        participants=[strategist, generator, reviewer], 
        termination_condition=termination
    )

    # Initial Prompt
    task = f"""
    PROJECT: Interview Guide Generation
    Candidate Name: {candidate_name}
    Job Description: {job_description}
    
    RESUME CONTEXT:
    {resume_context}
    
    GOAL: Create a high-quality, detailed Interview Guide.
    
    PROCESS:
    1. Strategist: Analyze and set the plan (Weights/Topics).
    2. Generator: Draft 20 detailed questions (100-200 words each).
    3. Reviewer: Critically review against the checklist (Role fit, Depth, Logic, Format).
    
    ITERATION RULES:
    - If the Reviewer REJECTS, the Strategist must refine parameters or calling out specific fixes, and the Generator must rewrite.
    - Continue this loop until the quality is perfect.
    - ONLY when the Reviewer is 100% satisfied, output the valid JSON list followed by the termination signal: "GUIDE", underscore, "APPROVED".
    """

    print(f"[DEBUG] Starting Interview Generation Team for {candidate_name}", flush=True)
    
    last_json_message = ""
    last_message = ""
    
    async for message in team.run_stream(task=task):
        if hasattr(message, 'content') and isinstance(message.content, str):
            content = message.content
            print(f"[DEBUG] Agent '{message.source}' says: {content[:60]}...", flush=True)
            last_message = content
            
            # Check if this message looks like it contains the questions list
            # We look for a JSON array pattern with at least some content
            if "[" in content and "]" in content and "question" in content:
                last_json_message = content

    print(f"[DEBUG] Interview Generation Team finished.", flush=True)
    
    # Return the last message that had JSON, otherwise fallback to the very last message
    return last_json_message if last_json_message else last_message

async def run_interview_revision(current_questions: str, feedback: str):
    generator = get_question_generator()
    user_proxy = UserProxyAgent("User")
    
    # Simple chat for revision
    team = RoundRobinGroupChat(
        participants=[generator], 
        termination_condition=MaxMessageTermination(5)
    )
    
    task = f"""
    Current Questions (JSON): {current_questions}
    
    User Feedback: {feedback}
    
    TASK: Revise the questions based on the feedback.
    Output the FULL revised list of 20 questions in the same JSON list format.
    """
    
    print(f"[DEBUG] Starting Revision", flush=True)
    last_message = ""
    async for message in team.run_stream(task=task):
        if hasattr(message, 'content') and isinstance(message.content, str):
            print(f"[DEBUG] Revision Agent '{message.source}': {message.content[:60]}...", flush=True)
            last_message = message.content
            
    return last_message
