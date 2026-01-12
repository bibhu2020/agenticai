from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from rag.db import get_db
from dotenv import load_dotenv

# Assuming agents/definitions.py is in src/interview-assistant/agents/, root is 3 levels up
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Shared Model Client
# Shared Model Client
# model_client = OpenAIChatCompletionClient(model="gpt-4")

# Groq via OpenAI Compatibility
api_key = os.getenv("GROQ_API_KEY")
print(f"[DEBUG] Loading Groq Client. Key found: {'Yes' if api_key else 'No'}")

model_client = OpenAIChatCompletionClient(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown"
    }
)

# --- Tools ---
# Tools moved to src/interview-assistant/tools/rag_tools.py

# --- Evaluation Agents ---

def get_jd_summarizer():
    return AssistantAgent(
        name="JD_Summarizer",
        model_client=model_client,
        system_message="""You are an expert Talent Acquisition Specialist. 
        Your task is to analyze the Job Description and extract the Critical Skills, Required Experience, and Nice-to-Have attributes. 
        Output a concise summary bullet point list."""
    )

def get_resume_summarizer():
    return AssistantAgent(
        name="Resume_Summarizer",
        model_client=model_client,
        tools=[search_candidate_knowledge_base],
        system_message="""You are a Researcher. Your goal is to find evidence in the candidate's resume that matches the JD requirements.
        Use the `search_candidate_knowledge_base` tool to find skills and experience.
        Summarize what the candidate HAS and what they are MISSING based on the evidence found."""
    )

def get_evaluator():
    return AssistantAgent(
        name="Evaluator",
        model_client=model_client,
        system_message="""You are the Lead Evaluator. 
        You will receive the Job Description and the Candidate's Resume Context.
        
        TASK:
        1. Compare the Candidate's skills/experience against the JD critical requirements.
        2. Identify specific Matches and Gaps.
        3. Assign a Fitness Score (0-10) using the SCORING RUBRIC below.
        
        SCORING RUBRIC (BE STRICT & CONSISTENT):
        - 0-3 (Mismatch): Missing >50% of critical skills or wrong domain (e.g., Java dev for Python role).
        - 4-6 (Partial): Has core skills but lacks seniority, specific framework exp, or key leadership traits.
        - 7-8 (Good): Matches ~80% of requirements. Minor gaps (e.g., missing a nice-to-have).
        - 9-10 (Perfect): 100% match + exceeds expectations (e.g., has bonus skills, higher seniority).
        
        OUTPUT:
        Produce a draft analysis with:
        - Score (Must align with Rubric)
        - Top 3 Strengths (Matches - Be specific)
        - Top 3 Weaknesses (Gaps - Be specific)
        - Brief Summary
        """
    )

def get_coordinator():
    return AssistantAgent(
        name="Coordinator",
        model_client=model_client,
        system_message="""You are the Quality Assurance Manager. Review the Evaluator's output.
        
        CRITICAL OUTPUT RULES:
        1. You must output the Final Evaluation in STRICT JSON format.
        2. The JSON must have these exact keys:
           - "score": Integer (0-10)
           - "key_matches": List[str] (Specific skills/experiences from JD found in Resume)
           - "gaps": List[str] (Specific requirements missing)
           - "summary": str (Brief reasoning)
        
        QUALITY CHECK:
        - Ensure the 'summary' is insightful and not just a restatement.
        - Ensure 'key_matches' and 'gaps' are specific, not generic.
        
        DECISION:
        - If satisfied, output the valid JSON immediately followed by "EVALUATION_APPROVED".
        - If NOT satisfied (e.g., vague analysis, missing JSON, unstructured), REJECT.
           - Provide specific instructions to the Evaluator on what to fix.
           - Do NOT output the termination keyword.
        """
    )

# --- Interview Design Agents (Flow 3) ---

def get_question_generator():
    return AssistantAgent(
        name="Question_Generator",
        model_client=model_client,
        system_message="""You are a Strategy-Driven Senior Interviewer.
        
        PHASE 1: STRATEGY
        - Analyze the JD Role & Seniority (Junior vs Senior vs Architect vs Manager).
        - Determine weights:
           * Developer: Focus on Tech.
           * Architect: Focus on System Design/Tech.
           * Manager: Focus on Leadership/Behavioral.
        
        PHASE 2: GENERATION
        - Generate exactly 20 Interview Questions based on the strategy.
        
        CRITICAL INSTRUCTION:
        - Each Question MUST be detailed and descriptive (approx. 100-200 words). 
        - DO NOT ask simple one-liners. Use scenario-based questions, case studies, or multi-part situational problems to provide deep context.
        
        ORGANIZATION:
        - Group the questions by Category: Present all Technical questions first, then Leadership, then Behavioral.
        
        OUTPUT FORMAT:
        Output the questions as a JSON List of Objects. Each object must have:
        {
          "category": "Technical|Leadership|Behavioral",
          "u_id": int (1-20),
          "question": "The detailed scenario-based question text (100-200 words)",
          "complexity": "Low|Medium|High",
          "likely_answer": "Key points expected in a good answer"
        }
        """
    )

def get_question_reviewer():
    return AssistantAgent(
        name="Question_Reviewer",
        model_client=model_client,
        system_message="""You are the Interview Board Chair. Review the generated questions.
        
        CHECKLIST:
        1. Are there exactly 20 questions?
        2. Do they cover the specific topics identified by the Strategist?
        3. Are the questions SUFFICIENTLY DETAILED (100-200 words each)?
        4. Are the 'likely_answer' keys provided and accurate?
        5. Is the format valid JSON?
        
        DECISION:
        - If satisfied (ALL checks pass), output the final JSON list and then write "GUIDE_APPROVED" on a new line.
        - If NOT satisfied (e.g., questions are too short/simple, missing answer keys, wrong count, or not specific enough), REJECT.
           - Provide specific, actionable feedback on what needs to change.
           - Do NOT output the termination keyword.
        """
    )
