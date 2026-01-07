
import os
import json
from agents import Agent, OpenAIChatCompletionsModel, Runner, GuardrailFunctionOutput
from pydantic import BaseModel
from openai import AsyncOpenAI
from core.model import get_model_client

class ValidatedOutput(BaseModel):
    is_valid: bool
    reasoning: str

input_validation_agent = Agent(
    name="Guardrail Input Validation Agent",
    instructions="""
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
    """,
    model=get_model_client(),
    output_type=ValidatedOutput,
)
input_validation_agent.description = "A guardrail agent that validates user input for unparliamentary language."

async def input_validation_guardrail(ctx, agent, input_data):
    result = await Runner.run(input_validation_agent, input_data, context=ctx.context)
    raw_output = result.final_output

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

__all__ = ["input_validation_agent", "input_validation_guardrail", "ValidatedOutput"]
