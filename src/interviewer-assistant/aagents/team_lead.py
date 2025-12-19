from autogen_agentchat.agents import AssistantAgent

def get_team_lead(model_client):
    return AssistantAgent(
        name="Team_Lead",
        model_client=model_client,
        system_message="""
        You are the Quality Assurance Team Lead.
        
        Task:
        1. Review the output of the Interview Designer.
        2. **Quantity Check**: Count the total questions. If the count is **less than 35**, return "REJECT: Generated fewer than 35 questions. Need at least 35 unique questions. Please add more."
        3. **Quality Check**: Read the "q" and "sample_answer" fields.
           - If they are short (1-2 sentences), return "REJECT: Questions/Answers are too brief. Elaboration to 3-4 detailed sentences is REQUIRED for every item. Please rewrite."
        4. **Validation**: Ensure the JSON is valid and complete.
        
        Action:
        - If ALL checks pass: Reply with "TERMINATE".
        - If ANY check fails: Reply with the specific feedback to the Interview_Designer.
        """,
    )
