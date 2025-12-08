import os
from agents import Agent, OpenAIChatCompletionsModel, Runner, GuardrailFunctionOutput
from pydantic import BaseModel
import json
from openai import AsyncOpenAI

class ValidatedOutput(BaseModel):
    is_valid: bool
    reasoning: str

class InputValidationAgent:
    """
    Encapsulates the AI agent definition for conducting comprehensive web searches and synthesizing information.
    """

    @staticmethod
    def create():
        """
        Returns a configured Agent instance ready for use.
        """

        instructions = """
            You are a highly efficient and specialized **Agent** 🌐. Your sole function is to validate the user inputs.
            
            ## Core Directives & Priorities
            1. You should flag if the user uses unparaliamentary language ONLY.
            2. You MUST give reasoning for the same.
            
            ## Rules
            - If it contains any of these, mark `"is_valid": false` and explain **why** in `"reasoning"`.
            - Otherwise, mark `"is_valid": true` with reasoning like "The input follows respectful communication guidelines."


            ## Output Format (MANDATORY)
            * Return a JSON object with the following structure:
            {
                "is_valid": <boolean>,
                "reasoning": <string>
            }

        """


        GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        google_api_key = os.getenv('GOOGLE_API_KEY')
        gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
        gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client) 

        agent = Agent(
            name="Guardrail Input Validation Agent",
            instructions=instructions,
            model=gemini_model,
            output_type=ValidatedOutput,
        )
        return agent
    
async def input_validation_guardrail(ctx, agent, input_data):
    result = await Runner.run(InputValidationAgent.create(), input_data, context=ctx.context)
    raw_output = result.final_output

    # print("Raw Output from Guardrail Model:", raw_output)

    # Handle different return shapes gracefully
    if isinstance(raw_output, ValidatedOutput):
        final_output = raw_output
        print("Parsed ValidatedOutput:", final_output)
    else:
        final_output = ValidatedOutput(
            is_valid=False,
            reasoning=f"Unexpected output type: {type(raw_output)}"
        )

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_valid,
    )
