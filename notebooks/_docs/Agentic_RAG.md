# Retrieval-Augmented Generation (RAG)
RAG is a technique that combines the power of large language models (LLMs) with the ability to retrieve relevant information from a knowledge base. It is a way to improve the accuracy and relevance of LLM outputs by providing them with additional context.

- Reduce Hallucination
- Improve Accuracy
- Provide Context
- Reduce Cost
- Real-time Adaptability

# Agentic RAG
Agentic RAG is an advanced AI framework integrating autonomous agents into traditional RAG pipelines. These agents can make decisions, collaborate with each other, and retrieve relevant information from multiple knowledge bases.

## Key Features

### 1. Autonomous Decision Making

### 2. Expert Agent Collaboration

### 3. Smart Retrieval

## Limitations

- Slower Response: Multiple agents and tools can increase response time
- Complex Integration: Integrating multiple agents and tools can be complex
- Conflicting Information: Agents may retrieve conflicting information from multiple knowledge bases

## Benefits over Traditional RAG

- Context-Awareness: Traditional RAG lacks context-awareness, while Agentic RAG can understand the context from conversation history and user preferences.
- Retrieval Strategy: Traditional RAG uses a single retrieval strategy, while Agentic RAG can use multiple retrieval strategies.
- Scalability: Traditional RAG can be scaled to multiple knowledge bases, while Agentic RAG can be scaled to multiple knowledge bases and tools.
- Accuracy: Agentic RAG can achieve higher accuracy than traditional RAG by self-reflection and self-correction.

# Adaptive RAG
Adaptive RAG is an advanced AI framework that dynamically adjusts its retrieval strategy based on the user's query, optimizing both efficiency and accuracy.

## Key Features

### 1. Retriever: 
Uses advanced and dense retrievers with ability of query adaptive embeddings.

### 2. Generator: 
Employees transformer models (GPT, T5)

### 3. Feedback Mechanism: 
Uses feedback from the users, output of the generator to improve the retriever

### 4. Dynamic Indexing: 
Uses dynamic indexing to improve the retriever

### 5. Hybrid Search: 
Inetrgrates semantic search with lexical search for more accurate context matching.

# Type of Agentic RAG (BASED ON FUNCTION)

## 1. Routing Agent: 
Employs a lightweight LLM to classify the user's intent and route the query to the most appropriate specialized agent or tool.

## 2. Query Planning Agent: 
Breaks down complex queries into a sequence of smaller, manageable sub-queries. It distributes them to other agents for execution. 
It acts like a task manager. It collects response from other agents and synthesizes them to generate the final response.

## 3. Tools Use Agent: 
It enriches user queries by fetching additional contexts from external tools like APIs and databases, before passing the enhanced query to the LLM within the RAG framework.

## 4. ReAct Agent: 
ReAct (Reasoning + Action) agent combines reasoning, tool use and planning in an iterative loop to solve complex queries.

## 5. Self-Reflective Agent: 
Uses self-reflection to improve the retrieved information.

## 6. Dynamic Planning and Execution Agent: 
It separates high-level planning from execution by using a planner to map out steps and an executor to carry them out, enabling efficient, scalable handling of complex queries in production environments. 