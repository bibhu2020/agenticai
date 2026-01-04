
from .agents.security import security_agent
from .tools.definitions import log_interaction_db

class MediBoOrchestrator:
    def __init__(self):
        pass

    async def handle_request(self, patient_id, user_text):
        """
        Uses the OpenAI Agents SDK (Swarm pattern) to process the request.
        """
        
        # We start with the Security Agent
        initial_input = [{"role": "user", "content": f"Patient ID: {patient_id}. Message: {user_text}"}]
        
        # Run the Swarm
        try:
            from agents import Runner
            runner = Runner()
            # Use async run because we are already in an async FastAPI event loop
            result = await runner.run(
                starting_agent=security_agent,
                input=initial_input
            )
            
            # The result object likely has a 'output' or 'messages' attribute.
            # Based on inspection, we likely want the final text output.
            
            # Assuming result is RunResult, which has 'output' (final message content)
            # or we iterate items.
            # Let's try to get the output from the result object.
            # Standard agents lib usage: result.output is the final agent's response.
            
            final_response = str(result.final_output)
            
            # Heuristic to capture actions from the conversation history if available
            # We might not have easy access to full history in result.output.
            # But let's check result attributes if possible.
            # For now, we will parse the final text and assume actions were done if mentioned.
            
            actions = []
            urgency = "UNKNOWN"
            
            # Fallback simple parsing of the text for simulation purposes
            if "Appointment Booked" in final_response:
                actions.append("Booked Appointment")
                urgency = "MODERATE"
            if "EMERGENCY" in final_response:
                actions.append("Alerted Emergency Services")
                urgency = "CRITICAL"
            
            action_summary = ", ".join(actions) if actions else "Provided Info/Advice"
            
            # Log it (Learning Module)
            log_interaction_db(patient_id, user_text, final_response, urgency)

            return final_response, action_summary

        except Exception as e:
            print(f"Agent Execution Error: {e}")
            # print stack trace for debugging
            import traceback
            traceback.print_exc()
            return "Broad system error (Agent SDK). Please try again.", "Error"
