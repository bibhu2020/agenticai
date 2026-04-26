"""
agent.py — SQL-Powered Sales Agent

Responsibility:
    - Perform relational joins and calculations using PostgreSQL
    - Map fuzzy descriptions to ProductIDs via semantic index
    - Use LlamaIndex NLSQLTableQueryEngine for robust SQL operations
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from llama_index.core import PromptTemplate

from dotenv import load_dotenv
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.google_genai import GoogleGenAI

try:
    from index import get_index
except ImportError:
    from src.salesdata.index import get_index

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Environment ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = GoogleGenAI(model_name="models/gemini-2.0-flash", api_key=GOOGLE_API_KEY)

# ── Database ──────────────────────────────────────────────────────────────────
DB_URL = "postgresql://neondb_owner:npg_h4FkSJfs9taC@ep-young-brook-a8mnh7la-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DB_URL)
sql_database = SQLDatabase(engine)

def semantic_mapping(query: str) -> str:
    """
    Map fuzzy descriptions (e.g. 'ergonomic gear') to specific productids using manuals.
    Returns exact productid and productname for use in SQL queries.
    """
    index = get_index()
    # Use top-3 results for breadth
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(query)
    
    results = []
    for node in nodes:
        pid = node.metadata.get("product_id")
        pname = node.metadata.get("product_name")
        results.append(f"- ID: {pid} (Name: {pname})")
    
    if not results:
        return "No specific products found for this description."
    
    return "Relational Mapping Results:\n" + "\n".join(set(results))


# ── PostgreSQL Specific SQL Prompt ───────────────────────────────────────────
POSTGRES_PROMPT_STR = (
    "Given an input question, first create a syntactically correct {dialect} "
    "query to run, then look at the results of the query and return the answer. "
    "You can order the results by a relevant column to return the most "
    "interesting examples in the database.\n\n"
    "Never query for all the columns from a specific table, only ask for a "
    "few relevant columns given the question.\n\n"
    "Crucially, for PostgreSQL:\n"
    "- Use `EXTRACT(YEAR FROM column)` for years.\n"
    "- Use `EXTRACT(MONTH FROM column)` for months (1-12).\n"
    "- For specific month/year (e.g. 'Jan 2025'), use `DATE_TRUNC('month', column)` or `TO_CHAR(column, 'YYYY-MM')`.\n"
    "- IMPORTANT: In GROUP BY clauses, always repeat the expression (e.g. GROUP BY EXTRACT(MONTH FROM column)) rather than using a SELECT alias.\n"
    "- Use standard double quotes for table/column names if they are reserved words.\n"
    "- Use `SUM(unit_price * quantity)` for revenue calculations from `order_details`.\n\n"
    "Only use the tables listed below.\n"
    "{schema}\n\n"
    "Question: {query_str}\n"
    "SQLQuery: (Create the SQL query ONLY, no markdown, no dialect prefix)"
)
POSTGRES_PROMPT = PromptTemplate(POSTGRES_PROMPT_STR)


# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a SQL-Powered Sales Intelligence Agent for 'InsightPulse'. You analyze the 'Northwind-Lite' PostgreSQL database.

DATABASE SCHEMA:
- `categories`: category_id, category_name, description
- `products`: product_id, product_name, category_id, unit_price, product_manual
- `customers`: customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax, type
- `employees`: employee_id, last_name, first_name, title, birth_date, hire_date, address, city, region, country, reports_to
- `orders`: order_id, customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, ship_name, ship_address, ship_city, ship_region, ship_postal_code, ship_country
- `order_details`: order_id, product_id, unit_price, quantity, discount

POSTGRESQL DIALECT HINTS:
- REVENUE: SUM(unit_price * quantity).
- DATE FILTERING: Use `EXTRACT(YEAR FROM o.order_date)` and `EXTRACT(MONTH FROM o.order_date)`. 
  - Jan 2026 example: `WHERE EXTRACT(YEAR FROM o.order_date) = 2026 AND EXTRACT(MONTH FROM o.order_date) = 1`.
- EMPTY RESULTS: If the tool returns NO data or NULL, report it as "No sales found for this period" or "No records match your search." 
- PERIODS: Orders span from 2004 to 2026.
- MULTI-YEAR AGGREGATION: If asked for 'which month' or 'monthly sales', clarify if the user wants an aggregate across all years (e.g. 'Average Jan') or a specific month/year (e.g. 'Jan 2025'). Generally, specific month/year is safer in `sql_analytics_tool`.

CRITICAL: 
- FOR ALL NOUNS/TYPES (e.g. 'coffee', 'laptops', 'dairy'): You MUST use `semantic_mapping_tool` first to find `product_id`s. Do NOT guess names in SQL.
- AFTER getting IDs, use `sql_analytics_tool` for the final calculation.
- ALWAYS use `sql_analytics_tool` for numbers and trends.
- Treat empty SQL results as valid logic (0 results) and report it clearly as 'No sales recorded for this criteria'.
"""

def get_agent() -> ReActAgent:
    """Build the SQL-backed agent."""
    
    # Text-to-SQL Query Engine
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        llm=llm,
        tables=["categories", "products", "customers", "employees", "orders", "order_details"],
        text_to_sql_prompt=POSTGRES_PROMPT
    )

    analytics_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        name="sql_analytics_tool",
        description="Executes complex SQL joins and math on the database. Input should be a natural language question about the data."
    )

    mapping_tool = FunctionTool.from_defaults(
        fn=semantic_mapping,
        name="semantic_mapping_tool",
        description="Maps feature descriptions (e.g. 'ergonomic') to specific productids using product manuals."
    )

    agent = ReActAgent(
        tools=[mapping_tool, analytics_tool],
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        verbose=True,
    )
    return agent
