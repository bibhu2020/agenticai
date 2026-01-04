# Tool Use Pattern

This project demonstrates the **Tool Use** (or Function Calling) pattern in agentic AI.

## What is Tool Use?

Tool use allows an AI agent to interact with external systems, databases, or APIs to perform actions or retrieve information that is not part of its training data. By providing the agent with a set of executable functions ("tools"), it can dynamically decide when to call them to satisfy a user request.

## How It Works

1.  **Tool Definition**: You define standard Python functions (e.g., `get_weather`) that perform specific tasks.
2.  **Agent Logic**: You inspect the agent's query. If the agent determines it needs external data, it generates a "tool call" instead of a text response.
3.  **Execution**: The system detects this request, runs the actual Python function, and feeds the return value back to the agent.
4.  **Final Response**: The agent uses the tool's output to generate a final, informed answer for the user.

## Flow Diagram

```mermaid
graph TD
    Start([Start]) --> UserQuery[User: Ask Question]
    UserQuery --> Agent[Agent: Analyze Request]
    Agent --> Decision{Needs Tools?}
    Decision -- Yes --> Select[Select Tool (Weather/Time)]
    Select --> Execute[Execute Python Function]
    Execute --> Result[Return Result to Agent]
    Result --> Agent
    Decision -- No --> FinalRes[Generate Final Response]
    FinalRes --> End([End])
```

## Code Structure

-   `app.py`: Contains the entire demo.
    -   Defines two mock tools: `get_weather` and `get_local_time`.
    -   Initializes an `Agent` with `tools=[get_weather, get_local_time]`.
    -   Runs the agent with multiple scenarios to demonstrate dynamic tool selection:
        1.  **Weather only**: Agent selects `get_weather`.
        2.  **Time only**: Agent selects `get_local_time`.
        3.  **Combined**: Agent selects both tools to answer a complex query.
        4.  **Parallel**: Agent calls `get_weather` three times simultaneously for different cities.

## Usage

Run the application to see the agent intelligently switch between tools:

```bash
python app.py
```
