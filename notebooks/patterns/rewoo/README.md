# ReWOO Pattern (Reasoning with Open Ontology)
This project demonstrates the **ReWOO Pattern**, which enhances agent planning by leveraging an external domain ontology (Knowledge Graph).

## What is ReWOO?

**ReWOO** (Reasoning with Open Ontology) solves the problem of "blind planning". Instead of relying on the LLM's potentially hallucinated or outdated training data to create a plan, the agent first queries a curated **Ontology** or **Knowledge Graph**.

1.  **Ontology Query**: The Planner asks the Knowledge Graph "What are the standard steps for X?".
2.  **Semantic Plan**: The Planner creates a plan based on the trusted structure returned by the ontology.
3.  **Execution**: The Executor follows this verified plan.

## Key Differences

| Feature | Standard Planning | ReWOO (Ontology) |
| :--- | :--- | :--- |
| **Source of Truth** | LLM Training Data (Internal) | Knowledge Graph (External) |
| **Robustness** | Prone to hallucinations of non-existent naming conventions | Adheres to strict, defined processes |
| **Ideal Use** | Creative writing, general advice | Enterprise processes (Deployment, Compliance, Medical) |

## Where does the Ontology come from?

It can be either, depending on the use case. This demo specifically implements **both**:

1.  **Business Defined (Internal)**:
    *   **Tool**: `consult_corporate_policy`
    *   **Source**: A python dictionary (`USER_DEFINED_GRAPH`) mimicking a private database.
    *   **Use Case**: "Launch an AI Model". Because LLMs don't know your private SOPs, they must query this graph to get the correct compliance steps (e.g., "Form A1").

2.  **3rd Party (External)**:
    *   **Tool**: `consult_wikidata`
    *   **Source**: Live query to **Wikidata** (using `urllib`).
    *   **Use Case**: "Ingredients in a Mojito". The agent fetches canonical facts from the public web instead of guessing.

## Code Structure

*   `app.py`:
    *   **HybridPlanner**: A smart agent that classifies the request ("Internal" vs "General") and selects the correct ontology tool.
    *   **UniversalExecutor**: Executes the plan derived from the ontology.
    *   **Scenarios**: Two distinct runs in the `__main__` block demonstrate the switch between private and public data sources.

## Flow Diagram

```mermaid
graph TD
    Start([User Request]) --> Router{Hybrid Planner:<br>Internal or General?}
    
    Router -- Internal --> PrivateOntology[Tool: consult_corporate_policy<br>(Private User Graph)]
    Router -- General --> PublicOntology[Tool: consult_wikidata<br>(Live 3rd Party API)]
    
    PrivateOntology --> Plan[Generated Plan]
    PublicOntology --> Plan
    
    Plan --> Executor[Executor Agent]
    Executor --> Result([Final Execution])
```

## Usage

Run the dual-scenario demo:

```bash
python app.py
```
