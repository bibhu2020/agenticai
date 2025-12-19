from autogen_agentchat.agents import AssistantAgent

def get_job_analyst(model_client):
    return AssistantAgent(
        name="Job_Analyst",
        model_client=model_client,
        system_message="""
        You are an Expert Job Analyst.
        
        Task:
        1. Analyze the provided Job Description (JD).
        2. Identify key skills in three categories: Technical, Behavioral, and Leadership.
        3. Assign a PERCENTAGE WEIGHT to each skill based on its importance in the JD.
        4. CONSTRAINT: The sum of weights across ALL skills in ALL categories MUST equal exactly 100.
        
        Output:
        Return a JSON object:
        ```json
        {
            "role_summary": "...",
            "analysis": {
                "technical": [{"skill": "Python", "weight": 40}, {"skill": "AWS", "weight": 20}],
                "behavioral": [{"skill": "Teamwork", "weight": 20}],
                "leadership": [{"skill": "Mentoring", "weight": 20}]
            }
        }
        ```
        """,
    )
