from agents import Agent, RunContextWrapper, Runner, function_tool, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from output_types.budget_analysis import BudgetAnalysis

# --- Guardrails ---

budget_analysis_agent = Agent(
    name="Budget Analyzer",
    instructions="""
    You analyze travel budgets to determine if they are realistic for the destination and duration.
    Consider factors like:
    - Average hotel costs in the destination
    - Flight costs
    - Food and entertainment expenses
    - Local transportation
    
    Provide a clear analysis of whether the budget is realistic and why.
    If the budget is not realistic, suggest a more appropriate budget.
    Don't be harsh at all, lean towards it being realistic unless it's really crazy.
    If no budget was mentioned, just assume it is realistic.
    """,
    output_type=BudgetAnalysis,
    model='gpt-4o-mini'
)

async def budget_guardrail(ctx, agent, input_data):
    """Check if the user's travel budget is realistic."""
    # Parse the input to extract destination, duration, and budget
    try:
        analysis_prompt = f"The user is planning a trip and said: {input_data}.\nAnalyze if their budget is realistic for a trip to their destination for the length they mentioned."
        result = await Runner.run(budget_analysis_agent, analysis_prompt, context=ctx.context)
        final_output = result.final_output_as(BudgetAnalysis)

        if not final_output.is_realistic:
            print(f"Your budget for your trip may not be realistic. {final_output.reasoning}" if not final_output.is_realistic else None)
        
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_realistic,
        )
    except Exception as e:
        # Handle any errors gracefully
        return GuardrailFunctionOutput(
            output_info=BudgetAnalysis(is_realistic=True, reasoning=f"Error analyzing budget: {str(e)}"),
            tripwire_triggered=False
        )