import os
import asyncio
from appagents.FinancialAgent import FinancialAgent
from appagents.NewsAgent import NewsAgent
from appagents.SearchAgent import SearchAgent
from appagents.InputValidationAgent import input_validation_guardrail
from agents import Agent, OpenAIChatCompletionsModel, InputGuardrail
from openai import AsyncOpenAI


class OrchestratorAgent:
    """
    The OrchestratorAgent coordinates multiple specialized sub-agents
    (Financial, News, and Search) to provide accurate, up-to-date,
    and well-routed market research insights.
    """

    MAX_RETRIES = 2

    # ----------------------------------------------------------
    # MAIN CREATION METHOD
    # ----------------------------------------------------------
    @staticmethod
    def create(model: str = "gpt-4o-mini"):
        """
        Creates and returns a configured Orchestrator agent.
        """

        # --- Sub-agent setup ---
        handoffs = [
            FinancialAgent.create(),
            NewsAgent.create(),
            SearchAgent.create(),
        ]

        # --- Behavioral instructions ---
        instructions = """
        You are the Orchestrator Agent responsible for coordinating specialized sub-agents 
        to generate accurate and well-rounded market research responses.

        **Your Core Responsibilities**
        1. **Task Routing:** Determine which sub-agent (Financial, News, or Search) is best suited 
           to handle each user query based on intent and context.
        2. **Delegation:** Forward the request to the appropriate sub-agent and wait for its result.
        3. **Synthesis:** When multiple agents provide responses, summarize and merge their findings 
           into a clear, concise, and accurate overall answer.
        4. **Recency and Accuracy:** Prioritize the most up-to-date, verifiable data from sub-agents.
        5. **Transparency:** Clearly identify which insights came from which sub-agent when relevant.
        6. **Error Handling:** If a sub-agent fails or provides insufficient data, attempt fallback 
           strategies such as rerouting the query or notifying the user.
        7. **Clarity:** Always present the final response in a professional, well-structured, 
           and easy-to-understand format.

        ⚠️ Do **not** perform the underlying data analysis or external lookup yourself — 
        ALWAYS delegate those tasks to the respective sub-agents.
        """

        # --- Model setup ---
        GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        google_api_key = os.getenv("GOOGLE_API_KEY")
        gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
        gemini_model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=gemini_client
        )

        # --- Create orchestrator agent ---
        agent = Agent(
            name="AI Market Research Assistant",
            handoffs=handoffs,
            instructions=instructions.strip(),
            model=gemini_model,
            # input_guardrails=[
            #     InputGuardrail(
            #         name="Input Validation Guardrail",
            #         guardrail_function=input_validation_guardrail,
            #     )
            # ],
        )

        # Attach orchestration logic
        agent.respond = lambda prompt: OrchestratorAgent.respond(prompt, handoffs, gemini_model)
        return agent

    # ----------------------------------------------------------
    # RESPONSE HANDLING + SELF-CORRECTION
    # ----------------------------------------------------------
    @staticmethod
    async def respond(prompt: str, handoffs: list, model) -> str:
        """
        Routes prompt to the most relevant agent, retries if output seems irrelevant.
        """
        attempted_agents = set()

        for attempt in range(OrchestratorAgent.MAX_RETRIES):
            # Step 1: Route intelligently
            chosen_agent = await OrchestratorAgent._route_to_agent(prompt, handoffs, attempted_agents)
            if not chosen_agent:
                return "⚠️ No available agent could handle this query."

            print(f"🤖 Attempt {attempt+1}: Sending query to {chosen_agent.name}")

            # Step 2: Run agent
            try:
                response = await chosen_agent.run(prompt)
            except Exception as e:
                print(f"⚠️ Agent {chosen_agent.name} failed: {e}")
                attempted_agents.add(chosen_agent.name)
                continue

            # Step 3: Evaluate if relevant
            if await OrchestratorAgent._is_relevant(prompt, response, model):
                return f"✅ {chosen_agent.name} handled this successfully:\n\n{response}"

            print(f"🔁 {chosen_agent.name}'s response deemed irrelevant. Re-routing...")
            attempted_agents.add(chosen_agent.name)

        return "⚠️ Could not find a relevant answer after multiple attempts."

    # ----------------------------------------------------------
    # ROUTING LOGIC
    # ----------------------------------------------------------
    @staticmethod
    async def _route_to_agent(prompt: str, handoffs: list, attempted_agents: set):
        """
        Determines the best-fit agent for the given prompt.
        Avoids previously tried agents.
        """
        lowered = prompt.lower()
        available = [a for a in handoffs if a.name not in attempted_agents]

        if not available:
            return None

        if any(k in lowered for k in ["finance", "stock", "market", "earnings"]):
            return next((a for a in available if "financial" in a.name.lower()), available[0])
        elif any(k in lowered for k in ["news", "headline", "press release"]):
            return next((a for a in available if "news" in a.name.lower()), available[0])
        elif any(k in lowered for k in ["search", "find", "lookup", "discover"]):
            return next((a for a in available if "search" in a.name.lower()), available[0])
        else:
            # fallback — first available agent
            return available[0]

    # ----------------------------------------------------------
    # LLM-BASED EVALUATOR
    # ----------------------------------------------------------
    @staticmethod
    async def _is_relevant(prompt: str, response: str, model) -> bool:
        """
        Uses the model itself to check if the response matches the prompt intent.
        """
        eval_prompt = f"""
        You are an evaluator checking multi-agent responses.
        User asked: "{prompt}"
        Agent responded: "{response}"

        Does this response accurately and completely answer the user's intent?
        Reply with only 'yes' or 'no'.
        """
        try:
            eval_result = await model.run(eval_prompt)
            print(f"🧠 Evaluation result: {eval_result}")
            return "yes" in eval_result.lower()
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            return False
