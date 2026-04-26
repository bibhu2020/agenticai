# LlamaIndex

> 🔗 [llamaindex.ai](https://www.llamaindex.ai/)

LlamaIndex is an open-source data framework that helps you connect Large Language Models (LLMs) to your own data. Think of it as a **bridge between your data and an LLM**.

## The Problem

LLMs (like GPT models) are powerful, but they don't automatically know about:

- Your internal documents
- Your database records (structured data)
- Your PDFs, emails, logs, or SharePoint files (unstructured data)

## How LlamaIndex Helps

LlamaIndex solves this by providing a pipeline to:

1. **Ingest** your data
2. **Index** it for efficient search
3. **Retrieve** relevant chunks
4. **Feed** them into the LLM
5. **Generate** accurate, context-aware answers

## Key Concepts

### Data Connectors

LlamaIndex provides connectors for various data sources, including:

- **Unstructured data**: PDFs, text files, Word documents, Markdown files, emails, Slack messages, Notion pages
- **Structured data**: SQL databases, CSV files, JSON files, Parquet files
- **APIs**: REST APIs, GraphQL APIs, WebSocket APIs
- **Cloud storage**: Amazon S3, Google Cloud Storage, Azure Blob Storage
- **NoSQL databases**: MongoDB, Cassandra, Redis
- **Vector databases**: Pinecone, Weaviate, Milvus, Chroma

### Indexing

LlamaIndex supports various indexing strategies, including:

- **Vector indexing**: Creates vector embeddings of your data for efficient semantic search
- **Tree indexing**: Creates a hierarchical index of your data for efficient retrieval of relevant information
- **Keyword indexing**: Creates a keyword index of your data for efficient retrieval of relevant information
- **Graph indexing**: Creates a knowledge graph of your data for efficient retrieval of relevant information


### Embeddings

#### Why Embeddings?

Computers cannot compare the *meaning* of text directly — they can only compare numbers. Embeddings solve this by converting text into a list of numbers (a **vector**) that captures its semantic meaning.

```
"heart attack symptoms"  →  [0.21, -0.84, 0.53, ...]
"myocardial infarction"  →  [0.22, -0.81, 0.55, ...]  ← similar numbers = similar meaning
"chocolate cake recipe"  →  [-0.63, 0.12, -0.44, ...]  ← very different
```

Two texts with similar meanings produce vectors that are **close together in space** — even if they use completely different words. This enables **semantic search**.

#### Why Not Just Use Keyword Search?

| Keyword Search | Semantic Search (Embeddings) |
|---|---|
| Matches exact words | Matches meaning |
| `"heart attack"` won't find `"myocardial infarction"` | ✅ Will find it |
| Fast, no model needed | Slightly slower, requires embedding model |
| Good for known, fixed terms | Good for natural language questions |

#### When and Where Are Embeddings Generated?

Embeddings are needed in exactly **two places** in the RAG pipeline:

```
┌──────────────────────────────────────────────────────┐
│  OFFLINE — run once (or when documents change)        │
│  Load docs → Chunk → EMBED chunks → Store in DB      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  ONLINE — every user request (cheap, one small text)  │
│  User query → EMBED query → Search DB → LLM answer   │
└──────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> Never re-embed documents on every query. Pre-compute them once at ingestion time to save cost and time.

#### How to Configure the Embedding Model

LlamaIndex defaults to **OpenAI `text-embedding-ada-002`**, but you can swap it easily:

```python
from llama_index.core import Settings

# Use Azure OpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
Settings.embed_model = AzureOpenAIEmbedding(model="text-embedding-ada-002")

# Use a free local HuggingFace model
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

#### Which Index Types Use Embeddings?

| Index Type | Creates Embeddings? |
|---|---|
| `VectorStoreIndex` | ✅ Yes — core to how it works |
| `TreeIndex` | ❌ No — uses LLM summarization |
| `KeywordTableIndex` | ❌ No — uses keyword extraction |
| `KnowledgeGraphIndex` | ❌ No — uses graph structure |

### Retrieval


LlamaIndex supports various retrieval strategies, including:

- **Vector retrieval**: Retrieves relevant information based on vector similarity
- **Tree retrieval**: Retrieves relevant information based on hierarchical structure
- **Keyword retrieval**: Retrieves relevant information based on keyword matching
- **Graph retrieval**: Retrieves relevant information based on graph relationships

### Querying

LlamaIndex supports various querying strategies, including:

- **Simple querying**: Retrieves relevant information based on a single query
- **Complex querying**: Retrieves relevant information based on multiple queries
- **Iterative querying**: Retrieves relevant information based on iterative queries
- **Hybrid querying**: Retrieves relevant information based on a combination of strategies

## Use Cases

Not every use case needs both embeddings and indexing. Here is when you need each:

### 🔵 Embedding Only (No Indexing)

You only need embeddings when comparing or classifying text — no storage or retrieval involved.

| Use Case | Why embedding only |
|---|---|
| **Text similarity / deduplication** | Compare two pieces of text to see if they mean the same thing |
| **Sentiment / intent classification** | Embed text and classify it against known category vectors |
| **Clustering documents** | Group documents by meaning without storing them for later retrieval |
| **Recommendation systems** | Find similar items based on description similarity |
| **Re-ranking search results** | Embed candidates and re-score them against the query |

```python
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()
vec1 = embed_model.get_text_embedding("heart attack symptoms")
vec2 = embed_model.get_text_embedding("myocardial infarction signs")
# Compare vec1 and vec2 — no index needed
```

---

### 🟡 Indexing Only (No Embeddings)

You only need indexing when you want structured retrieval by keywords, hierarchy, or graph — not by meaning.

| Use Case | Why indexing only |
|---|---|
| **Keyword search over docs** | Exact term matching — no semantic understanding needed |
| **Hierarchical summarization** | TreeIndex summarizes docs layer by layer using the LLM, no embeddings |
| **Knowledge graph Q&A** | Graph traversal to answer questions — relationships, not vectors |
| **Structured data lookup** | Query SQL/JSON by rules, not by meaning |

```python
# TreeIndex uses LLM summarization — no embedding model needed
from llama_index.core import TreeIndex

index = TreeIndex.from_documents(documents)
```

---

### 🟢 Embedding + Indexing (Both)

The most common RAG pattern — you need both to store and semantically search your data.

| Use Case | Why both |
|---|---|
| **Document Q&A / chatbot over your data** | Index chunks + embed them so the right chunks are retrieved by meaning |
| **Enterprise knowledge base search** | Employees ask natural language questions, system finds relevant docs |
| **Clinical / legal document search** | Semantic matches across complex, domain-specific terminology |
| **Multi-document summarization** | Retrieve the most relevant docs first, then summarize |
| **Agentic RAG** | Agent retrieves context from indexed, embedded knowledge to reason |

```python
# Both happen automatically with VectorStoreIndex
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
# ↑ chunks docs, embeds each chunk, stores vectors in index
```


### 🗄️ Real-World Example: Sales Database (PostgreSQL)

With a PostgreSQL sales database, the approach depends on what kind of questions you want to answer.

#### Approach 1: Natural Language → SQL

Ask questions like *"What were total sales in Q4 by region?"* — LlamaIndex translates them directly to SQL and runs against Postgres.

**Needs:** Indexing Only (LlamaIndex reads the schema, not the data rows — no embeddings needed)

```python
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/salesdb")
sql_database = SQLDatabase(engine, include_tables=["orders", "customers", "products"])

query_engine = NLSQLTableQueryEngine(sql_database=sql_database)
response = query_engine.query("What were total sales in Q4 2024 by region?")
# → LlamaIndex generates SQL → runs it → returns a natural language answer
```

#### Approach 2: Semantic Search Over Text Columns

If your DB has unstructured text — customer notes, sales call summaries, product descriptions — you need embeddings too.

**Needs:** Embedding + Indexing

```python
import psycopg2
from llama_index.core import VectorStoreIndex, Document

conn = psycopg2.connect("postgresql://user:pass@localhost/salesdb")
cur = conn.cursor()
cur.execute("SELECT id, notes FROM sales_calls")

documents = [Document(text=row[1], metadata={"id": row[0]}) for row in cur.fetchall()]
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("Which customers mentioned budget concerns?")
```

#### Decision Guide for a Sales DB

| Question Type | Approach | Embedding? | Indexing? |
|---|---|---|---|
| "Total sales last month?" | NL → SQL | ❌ | ✅ Schema only |
| "Which customers churned?" | NL → SQL | ❌ | ✅ Schema only |
| "Find customers who mentioned pricing issues" | Semantic search on notes | ✅ | ✅ |
| "Summarize all sales call notes for Q1" | Embed notes + retrieve | ✅ | ✅ |

> [!TIP]
> Start with **NL-to-SQL** for analytics questions (no embedding needed). Add embeddings only if you have free-text columns you want to search semantically.


### 🌐 Real-World Example: Retrieving Data from APIs

LlamaIndex provides three approaches for working with API data, depending on how the API is used and how fresh the data needs to be.

#### Approach 1: Built-in API Connector (LlamaHub)

For popular services like Notion, Slack, GitHub, Confluence, Jira — use a pre-built loader from [LlamaHub](https://llamahub.ai/).

**Needs:** Embedding + Indexing

```python
from llama_index.readers.notion import NotionPageReader
from llama_index.core import VectorStoreIndex

reader = NotionPageReader(integration_token="your-token")
documents = reader.load_data(page_ids=["page-id-1", "page-id-2"])

index = VectorStoreIndex.from_documents(documents)  # embeds + indexes
query_engine = index.as_query_engine()
response = query_engine.query("What decisions were made in the Q4 planning doc?")
```

#### Approach 2: Custom REST API Loader

For any API not in LlamaHub, build a custom `BaseReader` that fetches data and returns `Document` objects.

**Needs:** Embedding + Indexing

```python
import requests
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader
from llama_index.core import VectorStoreIndex

class SalesAPIReader(BaseReader):
    def load_data(self, endpoint: str) -> list[Document]:
        records = requests.get(endpoint, headers={"Authorization": "Bearer token"}).json()["data"]
        return [
            Document(
                text=f"Customer: {r['name']}\nNotes: {r['notes']}",
                metadata={"id": r["id"], "region": r["region"]}
            )
            for r in records
        ]

documents = SalesAPIReader().load_data("https://api.yourcrm.com/customers")
index = VectorStoreIndex.from_documents(documents)  # embeds + indexes
```

#### Approach 3: Agent Calls API Live (On-Demand)

Let the agent call the API at query time — best when data changes frequently and freshness matters more than speed.

**Needs:** Neither embedding nor indexing

```python
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
import requests

def get_sales_data(region: str) -> str:
    """Fetch latest sales data for a given region from the API."""
    return str(requests.get(f"https://api.yourcrm.com/sales?region={region}").json())

agent = OpenAIAgent.from_tools([FunctionTool.from_defaults(fn=get_sales_data)])
response = agent.chat("What are the latest sales numbers for the West region?")
```

#### Decision Guide for API Data

| Scenario | Approach | Embedding? | Indexing? |
|---|---|---|---|
| Notion, Slack, GitHub, Jira, Confluence | Built-in LlamaHub loader | ✅ | ✅ |
| Any custom REST API, data is stable | Custom loader + VectorStoreIndex | ✅ | ✅ |
| Structured JSON API (analytics/aggregations) | Custom loader, NL-to-SQL style | ❌ | ❌ |
| Data changes frequently, freshness critical | Agent live API calls | ❌ | ❌ |

> [!TIP]
> Pre-index when API data is stable — faster and cheaper at query time. Use live agent calls when you always need the freshest data.

## Getting Started



To get started with LlamaIndex, you can follow these steps:

1. **Install LlamaIndex**

```bash
pip install llama-index
```

2. **Create a data index**

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# Load data from a directory
documents = SimpleDirectoryReader("data").load_data()

# Create a vector index
index = VectorStoreIndex.from_documents(documents)
```

3. **Query the index**

```python
# Create a query engine
query_engine = index.as_query_engine()

# Query the index
response = query_engine.query("What is LlamaIndex?")

# Print the response
print(response)
```

## Storage

By default, LlamaIndex stores the index **in memory** — it is lost when the program exits. There are several persistence options:

| Storage Option | Best For |
|---|---|
| **In-memory** (default) | Prototyping and quick tests |
| **Local disk** | Simple single-machine apps |
| **External vector database** | Production, scalable apps |
| **Cloud object storage** | Distributed / multi-machine setups |

### In-Memory (Default)

```python
index = VectorStoreIndex.from_documents(documents)
# Lost when program exits
```

### Local Disk

LlamaIndex serializes the index to a folder as JSON files:

```python
# Save
index.storage_context.persist(persist_dir="./storage")

# Load later
from llama_index.core import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

Files created inside `./storage/`:

| File | Contents |
|---|---|
| `docstore.json` | Raw document chunks |
| `index_store.json` | Index metadata and structure |
| `vector_store.json` | Vector embeddings |

### External Vector Database

When you plug in a vector store (Pinecone, Chroma, Azure AI Search, etc.), embeddings are stored there instead of locally:

```python
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context  # backed by external vector DB
)
```

### Cloud Object Storage (S3, GCS, Azure Blob)

The local JSON files can be synced to cloud storage for distributed setups.

## Advanced Features


LlamaIndex also supports advanced features, including:

- **Multi-modal data**: Support for images, audio, and video data
- **Real-time data**: Support for real-time data streams
- **Distributed indexing**: Support for distributed indexing across multiple machines
- **Multi-model support**: Support for multiple LLM models
- **Fine-tuning**: Support for fine-tuning LLM models on your specific data
- **Evaluation**: Support for evaluating LLM model performance on your specific data
- **Monitoring**: Support for monitoring LLM model performance on your specific data
- **Security**: Support for secure data handling and access control
- **Scalability**: Support for scaling to large datasets and high query volumes
- **Extensibility**: Support for extending with custom data sources, indexes, and retrieval strategies

## Community

LlamaIndex has a vibrant community of developers and users who are actively contributing to the framework. You can join the community by:

- **Joining the Discord server**: https://discord.gg/llama-index
- **Contributing to the GitHub repository**: https://github.com/run-llama/llama_index
- **Following on Twitter**: https://twitter.com/llama_index
- **Subscribing to the newsletter**: https://llama.ai/newsletter
- **Attending meetups and events**: https://llama.ai/events

## Competitors

These are frameworks that, like LlamaIndex, help build RAG pipelines and connect LLMs to external data:

| Tool | Description |
|---|---|
| **[LangChain](https://www.langchain.com/)** | LLM application framework with RAG, data loaders, and chain orchestration |
| **[Haystack](https://haystack.deepset.ai/)** | Open-source NLP framework focused on RAG pipelines and document search |
| **[DSPy](https://dspy.ai/)** | Stanford's framework for programming LLMs with structured data retrieval |

## Comparisons

### LlamaIndex vs Azure AI Search

**Azure AI Search is not a competitor** — it is a managed search/vector store service that plugs into LlamaIndex as a backend component.

| LlamaIndex Stage | Azure AI Search |
|---|---|
| **Ingest** data | ❌ Not covered — LlamaIndex handles data loaders |
| **Index** documents + embeddings | ✅ Stores and indexes documents with vector embeddings |
| **Retrieve** relevant chunks | ✅ Performs hybrid search (keyword + semantic/vector) |
| **Feed** context to LLM | ❌ Not covered — LlamaIndex handles this |
| **Generate** answer | ❌ Not covered — done by the LLM |

Azure AI Search sits in the same category as Pinecone, Weaviate, and Chroma — it is a **vector store backend** that LlamaIndex can use, not a replacement for it.

```python
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore

vector_store = AzureAISearchVectorStore(
    search_or_index_client=index_client,
    index_name="my-index",
)
```

---

### LlamaIndex vs LangChain

Both are open-source Python frameworks for building LLM-powered applications, but they have different strengths:

| Feature | LlamaIndex | LangChain |
|---|---|---|
| **Primary focus** | Data ingestion, indexing & RAG | General LLM orchestration & chaining |
| **Best for** | Knowledge-base Q&A over your own data | Multi-step agent workflows and tool use |
| **Data connectors** | 100+ built-in data loaders (strong focus) | Available but less extensive |
| **Indexing strategies** | Vector, tree, keyword, graph indexes | Mostly vector store integrations |
| **Agents** | Supported but secondary | First-class, highly flexible |
| **Abstractions** | Higher-level, simpler RAG out of the box | Lower-level, more customizable chains |
| **Learning curve** | Easier for RAG-specific use cases | Steeper, but more flexible |
| **Community** | Smaller but RAG-focused | Larger, broader ecosystem |

> [!TIP]
> They are often used **together** — LlamaIndex for indexing/retrieval and LangChain for agent orchestration and tooling around it.

---

## Conclusion

LlamaIndex is a powerful data framework that helps you connect LLMs to your own data, enabling them to answer questions about your specific data. It provides a simple and efficient way to ingest, index, retrieve, and query your data, enabling you to build intelligent applications that can answer questions about your specific data.