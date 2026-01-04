import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# --- 1. Tool A: Public Ontology (Wikidata) ---
@function_tool
def consult_wikidata(concept: str) -> str:
    """
    Queries Wikidata (Public 3rd Party) for standard components of a general concept (e.g., dish ingredients, album tracks).
    Use this for GENERAL KNOWLEDGE questions.
    """
    print(f"\n[Ontology: Public] Connecting to Wikidata for: '{concept}'...")
    try:
        # Search for Entity
        headers = {"User-Agent": "AgenticAIDemo/1.0"}
        search_params = urllib.parse.urlencode({"action": "wbsearchentities", "search": concept, "language": "en", "format": "json", "limit": 1})
        req = urllib.request.Request(f"https://www.wikidata.org/w/api.php?{search_params}", headers=headers)
        with urllib.request.urlopen(req) as response:
            search_data = json.loads(response.read().decode())
        
        if not search_data.get("search"): return f"No entry found in Wikidata for {concept}."
        entity_id = search_data["search"][0]["id"]
        entity_label = search_data["search"][0]["label"]
        print(f"[Ontology: Public] Identified: {entity_label} ({entity_id})")

        # Query "has part" (P527)
        sparql_query = f"""SELECT ?itemLabel WHERE {{ wd:{entity_id} wdt:P527 ?item . SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}"""
        sparql_params = urllib.parse.urlencode({"query": sparql_query, "format": "json"})
        req = urllib.request.Request(f"https://query.wikidata.org/sparql?{sparql_params}", headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        parts = [b["itemLabel"]["value"] for b in data["results"]["bindings"]]
        if not parts: return f"Wikidata has no 'parts' listed for {entity_label}."
        
        return f"Standard Parts/Ingredients for {entity_label}: " + ", ".join(parts)
    except Exception as e: return f"Error: {str(e)}"

# --- 2. Tool B: Private Ontology (Corporate Policy) ---

# This is the "User Defined Graph" - You define your business logic here.
USER_DEFINED_GRAPH = {
    "AI Model Launch": {
        "steps": [
            "1. Data Privacy Impact Assessment (DPIA)", 
            "2. Model Bias Audit", 
            "3. Security Review", 
            "4. Executive Sign-off"
        ],
        "required_docs": ["Form A1", "Audit Report"]
    },
    "New Employee Onboarding": {
        "steps": [
            "1. Create Email Account", 
            "2. Assign Mentor", 
            "3. Security Training", 
            "4. Hardware Provisioning"
        ],
        "required_docs": ["HR Contract"]
    },
    "Cloud Resource Provisioning": {
        "steps": [
            "1. Cost Estimate", 
            "2. Architecture Review", 
            "3. Terraform Apply", 
            "4. Tagging Compliance Check"
        ],
        "required_docs": ["Jira Ticket"]
    }
}

@function_tool
def consult_corporate_policy(process_name: str) -> str:
    """
    Queries the Internal Knowledge Graph for company-specific procedures.
    Use this for ENTERPRISE/INTERNAL questions.
    """
    print(f"\n[Ontology: Private] 🔍 Searching USER_DEFINED_GRAPH for: '{process_name}'...")
    
    # Smart fuzzy match logic (Token-based)
    process_tokens = set(process_name.lower().split())
    
    for key, value in USER_DEFINED_GRAPH.items():
        key_tokens = set(key.lower().split())
        
        # Check if the words overlap significantly (Subset in either direction)
        # This handles "Launch AI Model" (input) matching "AI Model Launch" (key)
        if key_tokens.issubset(process_tokens) or process_tokens.issubset(key_tokens):
            steps_str = "\n".join(value['steps'])
            docs_str = ", ".join(value['required_docs'])
            
            result = f"FOUND Standard Corporate Procedure for '{key}':\n\nREQUIRED STEPS:\n{steps_str}\n\nREQUIRED DOCS: {docs_str}"
            print(f"[Ontology: Private] ✅ Found Match! Returning strict process steps.")
            return result
            
    print("[Ontology: Private] ❌ No matching process found in User Graph.")
    return "No standard procedure found in corporate graph."

# --- 3. Execution Tools ---
@function_tool
def perform_task(task_name: str) -> str:
    """Simulates executing a task."""
    print(f"\n[Executor] Performing: {task_name}...")
    return "Done."

# --- 4. Agents ---

# Smart Planner that chooses the right ontology
planner_agent = Agent(
    name="HybridPlanner",
    instructions="""
        You are a smart planner.
        
        Determine if the user's request is General Knowledge or Internal Business.
        1. If General (e.g., 'Ingredients of X'), consult 'consult_wikidata'.
        2. If Internal (e.g., 'Launch AI Model'), consult 'consult_corporate_policy'.
        
        Then, create a step-by-step execution plan based strictly on the ontology's response.
    """,
    model="gpt-4o-mini",
    tools=[consult_wikidata, consult_corporate_policy]
)

executor_agent = Agent(
    name="UniversalExecutor",
    instructions="Execute the plan using 'perform_task'.",
    model="gpt-4o-mini",
    tools=[perform_task]
)

def run_scenario(scenario_name, request):
    print(f"\n\n>>> SCENARIO: {scenario_name}")
    print(f"Request: {request}")
    
    print("\n--- PHASE 1: PLANNING ---")
    plan = Runner.run_sync(planner_agent, request).final_output
    print(f"\n[Plan Generated]:\n{plan}")
    
    print("\n--- PHASE 2: EXECUTION ---")
    Runner.run_sync(executor_agent, f"Execute this plan:\n{plan}")

if __name__ == "__main__":
    # Scenario 1: User Defined Graph (Internal)
    run_scenario("Corporate Compliance", "I need to launch a new AI Model. What is the process?")
    
    # Scenario 2: 3rd Party Graph (External)
    run_scenario("General Knowledge", "What are the ingredients in a Mojito?")
