import os
from dotenv import load_dotenv
from agents import Agent, Runner

# Load variables from .env into environment
load_dotenv()

# Optional: validate required variables early
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# Define Agents
answer_agent = Agent(
    name="AnswerAgent",
    instructions="""
        You are a knowledgeable assistant.
        Answer the user's question clearly, accurately, and concisely.
        """,
    model="gpt-4o-mini"
)

reflection_agent = Agent(
    name="ReflectionAgent",
    instructions="""
        You are a critical reviewer of AI-generated answers.

        Your task:
        - Identify logical flaws
        - Point out missing details
        - Note unclear or vague explanations
        - Suggest concrete improvements

        If the answer is high quality and needs no further improvement, start your response with "SATISFIED".
        Otherwise, provide your critique below.

        Be precise and constructive.
        """,
    model="gpt-4o"
)

improvement_agent = Agent(
    name="ImprovementAgent",
    instructions="""
        You are an expert editor.

        Rewrite the answer by fully addressing the critique.
        Produce a higher-quality, well-structured final response.
        """,
    model="gpt-4o-mini"
)


def reflection_pipeline(question: str, max_reflections: int = 3) -> str:
    print(f"\n[DEBUG] Starting reflection pipeline for question: '{question}'")

    # Step 1: Initial answer
    print("[DEBUG] Generating initial answer...")
    answer_result = Runner.run_sync(
        answer_agent,
        question
    )
    answer = answer_result.final_output
    print(f"[DEBUG] Initial answer generated (length: {len(answer)} chars).")
    print(f"[DEBUG] Initial Answer Snippet: {answer[:100]}...")

    for i in range(max_reflections):
        print(f"\n[DEBUG] --- Reflection Cycle {i + 1}/{max_reflections} ---")

        # Step 2: Reflect / critique
        print("[DEBUG] Generating critique...")
        critique_prompt = f"""
            Question:
            {question}

            Answer:
            {answer}
            """
        critique_result = Runner.run_sync(
            reflection_agent,
            critique_prompt
        )
        critique = critique_result.final_output
        print(f"[DEBUG] Critique generated (length: {len(critique)} chars).")
        print(f"[DEBUG] Critique Snippet: {critique[:100]}...")

        if "SATISFIED" in critique:
            print("[DEBUG] ReflectionAgent is satisfied. Exiting loop.")
            break

        # Step 3: Improve
        print("[DEBUG] Generating improved answer based on critique...")
        improve_prompt = f"""
            Question:
            {question}

            Original Answer:
            {answer}

            Critique:
            {critique}
            """
        improved_result = Runner.run_sync(
            improvement_agent,
            improve_prompt
        )
        answer = improved_result.final_output
        print(f"[DEBUG] Improved answer generated (length: {len(answer)} chars).")
        print(f"[DEBUG] Improved Answer Snippet: {answer[:100]}...")

    print("\n[DEBUG] Reflection pipeline complete.")
    return answer


if __name__ == "__main__":
    question = "Explain the Reflection Pattern in agentic AI."
    print(f"User Question: {question}")

    final_answer = reflection_pipeline(
        question=question,
        max_reflections=3
    )

    print("\nFINAL ANSWER:\n")
    print(final_answer)
