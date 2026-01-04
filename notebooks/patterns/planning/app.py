import os
from dotenv import load_dotenv
from agents import Agent, Runner

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# 1. Define the Planner Agent
planner_agent = Agent(
    name="PlannerAgent",
    instructions="""
        You are a strategic planner.
        Given a user request, break it down into a sequence of 3 to 5 distinct, actionable steps.
        
        Format your output as a numbered list, where each line is a single step.
        Do not include any introductory or concluding text.
        
        Example Output:
        1. Research the history of the Eiffel Tower.
        2. Identify key architectural features.
        3. Write a summary of its construction process.
    """,
    model="gpt-4o-mini"
)

# 2. Define the Worker Agent
worker_agent = Agent(
    name="WorkerAgent",
    instructions="""
        You are a skilled researcher and writer.
        You will be assigned a specific sub-task associated with a larger project.
        
        You will receive:
        1. The current sub-task to execute.
        2. Context/Results from previous steps (if any).
        
        Execute the sub-task thoroughly. Provide specific facts, code, or content as requested.
    """,
    model="gpt-4o-mini"
)

# 3. Define the Finalizer Agent
finalizer_agent = Agent(
    name="FinalizerAgent",
    instructions="""
        You are a project manager and editor.
        You will receive the original user request and the results from all executed sub-tasks.
        
        Your job is to synthesize this information into a cohesive, final response that directly addresses the user's initial request.
        Ensure the tone is professional and the structure is logical.
    """,
    model="gpt-4o-mini"
)

def planning_pipeline(user_request: str) -> str:
    print(f"\n[DEBUG] Starting Planning Pipeline for: '{user_request}'")
    
    # Step 1: Generate the Plan
    print("[DEBUG] PlannerAgent is creating a plan...")
    plan_result = Runner.run_sync(planner_agent, user_request)
    plan_text = plan_result.final_output
    
    print(f"\n[DEBUG] Plan Generated:\n{plan_text}\n")
    
    # Parse the plan into a list of steps
    # Assumes the agent follows the numbered list format (1. Step one...)
    steps = [line.strip() for line in plan_text.split('\n') if line.strip() and line[0].isdigit()]
    
    if not steps:
        print("[WARN] Could not parse steps. Using raw plan as single step.")
        steps = [plan_text]

    # Step 2: Execute each step
    context = ""
    for i, step in enumerate(steps):
        print(f"[DEBUG] Executing Step {i+1}/{len(steps)}: {step}")
        
        worker_prompt = f"""
        Current Task: {step}
        
        Context from previous steps:
        {context}
        """
        
        step_result = Runner.run_sync(worker_agent, worker_prompt)
        step_output = step_result.final_output
        
        print(f"[DEBUG] Only first 100 chars of result: {step_output[:100]}...")
        
        # Accumulate context for subsequent steps and final synthesis
        context += f"\n\n--- Result of Step: {step} ---\n{step_output}"

    # Step 3: Synthesize Final Response
    print("\n[DEBUG] FinalizerAgent is synthesizing the response...")
    final_prompt = f"""
    Original Request: {user_request}
    
    All Step Results:
    {context}
    """
    
    final_response_result = Runner.run_sync(finalizer_agent, final_prompt)
    return final_response_result.final_output

if __name__ == "__main__":
    request = "Write a comprehensive guide on how to start a vegetable garden for beginners."
    
    final_output = planning_pipeline(request)
    
    print("\n\n================ FINAL RESPONSE ================\n")
    print(final_output)
