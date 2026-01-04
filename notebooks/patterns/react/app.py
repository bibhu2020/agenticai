import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# --- Define Tools for a Multi-Hop Knowledge Chain ---

@function_tool
def get_author(book_title: str) -> str:
    """Returns the author of a given book."""
    print(f"\n[Action] Looking up author for: {book_title}")
    db = {"Frankenstein": "Mary Shelley", "The Raven": "Edgar Allan Poe"}
    return db.get(book_title, "Unknown Author")

@function_tool
def get_mother(person_name: str) -> str:
    """Returns the mother's name of a given person."""
    print(f"\n[Action] Looking up mother of: {person_name}")
    db = {"Mary Shelley": "Mary Wollstonecraft", "Edgar Allan Poe": "Elizabeth Arnold Hopkins Poe"}
    return db.get(person_name, "Unknown Mother")

@function_tool
def get_life_dates(person_name: str) -> str:
    """Returns birth and death years for a person."""
    print(f"\n[Action] Looking up life dates for: {person_name}")
    db = {
        "Mary Wollstonecraft": "1759-1797",
        "Elizabeth Arnold Hopkins Poe": "1787-1811"
    }
    return db.get(person_name, "Unknown Dates")

@function_tool
def calculate_age(start_year: int, end_year: int) -> int:
    """Calculates age or duration given two years."""
    print(f"\n[Action] Calculating: {end_year} - {start_year}")
    return int(end_year) - int(start_year)

# --- Define the ReAct Agent ---

react_agent = Agent(
    name="ReActAgent",
    instructions="""
        You are a generic reasoning agent.
        
        To answer the user's question, you must "Reason" and then "Act".
        
        Strictly follow this format for your output:
        
        Thought: [Your reasoning about what to do next based on what you know so far]
        Action: [The tool call you need to make]
        
        Once the tool results returns:
        Observation: [The result of the tool]
        Thought: [Your new reasoning based on the observation]
        ...
        
        Final Answer: [The answer to the user's question]
        
        Do not try to guess. Use the tools step-by-step.
    """,
    model="gpt-4o-mini",
    tools=[get_author, get_mother, get_life_dates, calculate_age]
)

if __name__ == "__main__":
    # A multi-hop question that requires sequential dependencies.
    # The agent CANNOT call `get_life_dates` until it knows WHO the mother is.
    # The agent CANNOT call `get_mother` until it knows WHO the author is.
    # This dependency chain enforces the ReAct pattern over simple parallel tool use.
    
    question = "How old was the mother of the author of 'Frankenstein' when she died?"
    print(f"User Question: {question}")
    
    result = Runner.run_sync(react_agent, question)

    print("\n\n================ FINAL RESPONSE ================\n")
    print(result.final_output)
