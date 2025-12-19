from autogen_agentchat.agents import AssistantAgent

def get_job_analyst_reviewer(model_client):
    return AssistantAgent(
        name="Job_Analyst_Reviewer",
        model_client=model_client,
        system_message="""
        You are a Senior HR Reviewer.
        
        Task:
        1. Review the output from the "Job_Analyst".
        2. Verify if the identified skills accurately reflect the JD.
        3. CHECK MATH: Verify that the sum of ALL weights across all categories equals exactly 100.
        4. If the math is wrong or skills are missing, reject and ask for corrections.
        5. If acceptable, output "APPROVED".
        """,
    )
