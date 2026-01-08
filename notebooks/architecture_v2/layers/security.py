from typing import Any, Union, List
from agents import InputGuardrail, OutputGuardrail, GuardrailFunctionOutput

def validate_input_fn(ctx, agent, input_data: Union[str, List[Any]]) -> GuardrailFunctionOutput:
    """
    Callback function for Input Guardrail.
    """
    # handle list of inputs if necessary, usually it's a string or list of messages
    text_content = str(input_data).lower()
    
    banned_terms = ["rm -rf", "shutdown", "drop table", "ignore previous instructions"]
    for term in banned_terms:
        if term in text_content:
            return GuardrailFunctionOutput(
                output_info=f"Security Alert: Prohibited content '{term}' detected.",
                tripwire_triggered=True
            )
            
    return GuardrailFunctionOutput(output_info="Input safe", tripwire_triggered=False)

def validate_output_fn(ctx, agent, output_data: Any) -> GuardrailFunctionOutput:
    """
    Callback function for Output Guardrail.
    """
    text_content = str(output_data)
    
    # Simple check for secrets (e.g., OpenAI Key pattern)
    if "sk-" in text_content and len(text_content) > 30:
         return GuardrailFunctionOutput(
                output_info="Security Alert: Potential API Key leak detected.",
                tripwire_triggered=True
            )
            
    return GuardrailFunctionOutput(output_info="Output safe", tripwire_triggered=False)

def get_input_guardrail() -> InputGuardrail:
    return InputGuardrail(
        name="SecurityGuard_Input",
        guardrail_function=validate_input_fn
    )

def get_output_guardrail() -> OutputGuardrail:
    return OutputGuardrail(
        name="SecurityGuard_Output",
        guardrail_function=validate_output_fn
    )
