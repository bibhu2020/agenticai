from autogen_agentchat.agents import AssistantAgent

def get_evaluator(model_client):
    return AssistantAgent(
        name="Evaluator",
        model_client=model_client,
        system_message="""
        You are the Hiring Evaluator.
        
        Inputs:
        1. Context includes "Candidate Summary" (from Candidate_Profiler).
        2. Context includes "Approved JD Analysis" (from Job_Analyst/Reviewer).
        
        Task:
        1. Compare the Candidate's profile against the approved JD requirements across FOUR dimensions:
           - Technical Proficiency
           - Behavioral Fit
           - Situational Judgment & Problem Solving
           - Leadership Potential (Ownership/Influence)
        2. Score the overall fitness (1-10) weighted by the priorities defined in the JD Analysis.
        3. Identify Strengths and Gaps.
        4. List specific areas to probe in the interview.
        
        Output:
        Return a JSON object:
        ```json
        {
          "fitness_score": 8,
          "justification": "...",
          "strengths": ["..."],
          "gaps": ["..."],
          "interview_focus_areas": ["..."]
        }
        ```
        """,
    )
