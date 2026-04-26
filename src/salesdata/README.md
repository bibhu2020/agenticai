# InsightPulse — Enterprise SQL Sales Agent

InsightPulse is a production-grade **Hybrid Sales Intelligence Agent** that bridges the gap between natural language interaction and relational database analytics.

This version is powered by a **PostgreSQL (Neon) Database** with a professional **Northwind-Lite Schema**, featuring complex SQL joins and semantic discovery over product documentation.

## 🚀 Key Features

- **Natural Language SQL**: Transparent and accurate querying of a 6-table relational schema using LlamaIndex's `NLSQLTableQueryEngine`.
- **SQL-Backed Semantic Discovery**: Maps fuzzy product features (e.g., "ergonomic mechanical gear") to exact `productid`s using a vector index built from long-form SQL metadata.
- **Deterministic Accuracy**: Zero hallucination on numbers. All metrics, trends, and comparisons are calculated via real-time SQL execution.
- **Enterprise Dashboard**: A premium, wide-screen Streamlit interface powered by live SQL visualizations.

## 🏗️ Architecture

- **Engine**: LlamaIndex (ReAct Agent + NLSQL)
- **LLM**: Gemini 2.0 Flash
- **Data Layer**: PostgreSQL (Northwind-Lite Schema: Orders, Products, Customers, Employees, etc.)
- **Frontend**: Streamlit
- **Host**: Neon DB (Cloud PostgreSQL)

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+
- `uv` (recommended)
- Google Gemini API Key

### 2. Setup
1. Clone the repository.
2. Create a `.env` file with `GOOGLE_API_KEY=your_key_here`.
3. Install dependencies: `uv sync`.

### 3. Run the System
1. **Provision & Populate Database**:
   ```bash
   uv run python src/salesdata/dummy_data.py
   ```
2. **Build the Index**:
   ```bash
   uv run python src/salesdata/index.py
   ```
3. **Start Backend API**:
   ```bash
   uv run uvicorn src.salesdata.api:app --reload --port 8080
   ```
4. **Start Streamlit UI**:
   ```bash
   streamlit run src/salesdata/app.py
   ```

## 🧠 Northwind-Lite Schema
- `categories`: Metadata for product groups.
- `products`: Deep descriptions (Manuals) for semantic search.
- `customers`: Enterprise/SME segments with regional tagging.
- `employees`: Regional sales performance and ratings.
- `orders`: Transactional headers.
- `order_details`: Line-item revenue and quantity data.

## 💬 Example Queries
- "Which Enterprise customer in the North region spent the most on ergonomic work gear in 2024?"
- "Compare total revenue between Alice Zhang and Bob Smith."
- "What is the average order value per category in 2025?"
- "Which customer spent the most on communication gear in 2024?"

---
*Built with ❤️ for professional agentic SQL intelligence.*