import asyncio
import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.utility.autogen_model_factory import AutoGenModelFactory
from aagents.candidate_profiler import get_candidate_profiler

# Load env (assuming .env in project root, but we can rely on env vars being set in shell)
load_dotenv()

async def main():
    print("DEBUG: Starting standalone profiler test.")
    
    # 1. Setup Dummy Resume
    resume_path = os.path.join(os.getcwd(), "dummy_resume.txt")
    with open(resume_path, "w") as f:
        f.write("Jane Doe. Experienced Software Engineer. Python, Azure, AI. 10 years experience.")
    
    print(f"DEBUG: Created dummy resume at {resume_path}")

    # 2. Setup Agent
    try:
        model_client = AutoGenModelFactory.get_model(
            provider="openai", 
            model_name="gpt-4-turbo", 
            model_info={"vision": False, "function_calling": True, "json_output": False}
        )
        profiler = get_candidate_profiler(model_client)
        print("DEBUG: Profiler agent created.")
    except Exception as e:
        print(f"ERROR: Failed to create agent: {e}")
        return

    # 3. Run Agent
    task_msg = f"Candidate Resume File Path: {resume_path} (Please use `read_local_file` to read this)."
    
    print(f"DEBUG: Sending task: {task_msg}")
    
    try:
        # Run directly against agent usually requires a team context for proper tool loop handling in 0.4
        # But let's try calling on_messages or similar if supported, 
        # OR just wrap in a minimal RoundRobin team like in the app.
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.conditions import MaxMessageTermination
        
        team = RoundRobinGroupChat(
            participants=[profiler],
            termination_condition=MaxMessageTermination(5)
        )
        
        print("DEBUG: Running team stream...")
        async for message in team.run_stream(task=task_msg):
            source = getattr(message, 'source', 'Unknown')
            content = getattr(message, 'content', '')
            print(f"STREAM: {source}: {str(content)[:100]}")
            
    except Exception as e:
        print(f"ERROR during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
