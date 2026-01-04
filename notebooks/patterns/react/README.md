# ReAct Pattern (Reason + Act)

This project demonstrates the **ReAct Pattern**, a paradigm where Large Language Models are used to generate both **reasoning traces** and **task-specific actions** in an interleaved manner.

## What is the ReAct Pattern?

ReAct stands for **Re**asoning and **Act**ing. It allows models to create dynamic plans that can be updated in real-time based on new information contained in the context.

*   **Reasoning (Thought)**: The model analyzes the current state and decides what to do next.
*   **Acting (Action)**: The model performs a step (calling a tool/function).
*   **Observation**: The model receives the result of that action.
*   **Repeat**: The loop continues until the model can form a final answer.

## ReAct vs. Standard Tool Use

**Standard Tool Use** (Function Calling) is often optimized for **parallelism**. If you ask "What's the weather in Tokyo and Paris?", the model will call `get_weather("Tokyo")` and `get_weather("Paris")` simultaneously.

**ReAct** is optimized for **dependency chains**. If you ask "Who is the mother of the author of X?", the model **cannot** know who the mother is until it first finds the author.
1.  **Thought**: "I need to find the author first." -> **Action**: `get_author`
2.  **Observation**: "Mary Shelley"
3.  **Thought**: "Now I need HER mother." -> **Action**: `get_mother`

This explicit "Stop, Think, Act, Observe" loop is what defines ReAct.

## Code Structure

-   `app.py`:
    -   Defines a chain of tools: `get_author`, `get_mother`, `get_life_dates`, `calculate_age`.
    -   Demonstrates a **4-step dependency chain**: Book -> Author -> Mother -> Dates -> Age.
    -   Forces the agent to reason slightly at each step rather than guessing or trying to parallelize impossible tasks.

## Usage

Run the demo to observe the interleaved reasoning and action steps:

```bash
python app.py
```
