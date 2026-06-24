"""Content Policy Guardrail — blocks unparliamentary language before it reaches the orchestrator."""
from agents import Agent, GuardrailFunctionOutput, Runner, input_guardrail
from pydantic import BaseModel

from model_factory import get_model

model = get_model("google", "gemini-2.5-flash")

_INSTRUCTIONS = """
You are the **Content Policy Guardrail**. Your sole job is to decide whether a
user message violates the content policy.

## Policy
Flag the message as invalid (`is_valid: false`) ONLY if it contains:
- Profanity or unparliamentary / abusive language directed at people.

All other messages — questions, commands, opinions, technical requests — are valid.

## Output (JSON, mandatory)
{
    "is_valid": <true|false>,
    "reasoning": "<one sentence explanation>"
}
"""


class ContentValidationResult(BaseModel):
    is_valid: bool
    reasoning: str


def create_guardrail(m=None):
    """Return (policy_agent, guardrail_fn) using the supplied model (default: Gemini)."""
    _model = m or model
    policy_agent = Agent(
        name="Content Policy Guardrail",
        model=_model,
        output_type=ContentValidationResult,
        instructions=_INSTRUCTIONS,
    )
    policy_agent.description = (
        "Screens user input for unparliamentary language and blocks policy-violating messages."
    )

    @input_guardrail
    async def _enforce(ctx, agent, input_data):
        result = await Runner.run(policy_agent, input_data, context=ctx.context)
        raw = result.final_output
        if isinstance(raw, ContentValidationResult):
            validated = raw
        else:
            validated = ContentValidationResult(
                is_valid=False,
                reasoning=f"Unexpected guardrail output type: {type(raw)}",
            )
        return GuardrailFunctionOutput(
            output_info=validated,
            tripwire_triggered=not validated.is_valid,
        )

    return policy_agent, _enforce


# Module-level defaults (backwards compat / tests)
content_policy_agent, enforce_content_policy = create_guardrail(model)
