import os
from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    input_guardrail,
    GuardrailFunctionOutput,
)
from tools.time_tools import TimeTools
from openai import AsyncOpenAI


# ✅ Step 1: Define structured output schema
class UnparliamentaryCheckOutput(BaseModel):
    has_unparliamentary_language: bool
    explanation: str


# ✅ Step 2: Define the LLM guardrail agent
guardrail_agent = Agent(
    name="Unparliamentary language check",
    instructions=(
        "Analyze the user input and determine if it contains any unparliamentary, "
        "offensive, or disrespectful language. "
        "If it does, set has_unparliamentary_language=true and explain briefly why. "
        "Otherwise, set it to false."
    ),
    output_type=UnparliamentaryCheckOutput,
    model="gpt-4o-mini",
)


# ✅ Step 3: Use the input guardrail decorator
@input_guardrail
async def guardrail_against_unparliamentary(ctx, agent, message: str):
    """Guardrail function that blocks messages with unparliamentary words."""
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    has_unparliamentary_language = result.final_output.has_unparliamentary_language

    return GuardrailFunctionOutput(
        output_info={
            "found_unparliamentary_word": result.final_output.model_dump()
        },
        tripwire_triggered=has_unparliamentary_language,
    )
