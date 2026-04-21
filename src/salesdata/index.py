"""
index.py — PostgreSQL-Based Metadata Indexing

Responsibility:
    - Load unique product manuals from PostgreSQL 'products' table
    - Use SentenceSplitter for granular semantic coverage
    - Enable the agent to map fuzzy queries to ProductIDs via embeddings
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Environment ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ── Database Config ──────────────────────────────────────────────────────────
DB_URL = "postgresql://neondb_owner:npg_h4FkSJfs9taC@ep-young-brook-a8mnh7la-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DB_URL)

# ── Index Config ──────────────────────────────────────────────────────────────
MODULE_DIR = Path(__file__).parent
INDEX_STORAGE_DIR = MODULE_DIR / "sql_index_storage"

# ── Embedding Model ───────────────────────────────────────────────────────────
embed_model = GoogleGenAIEmbedding(
    model_name="models/gemini-embedding-001",
    api_key=GOOGLE_API_KEY,
)


def _load_sql_product_metadata() -> list[Document]:
    """Fetch product manuals directly from PostgreSQL."""
    logger.info("Fetching product metadata from PostgreSQL...")
    
    query = """
        SELECT p.product_id, p.product_name, c.category_name, p.product_manual 
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
    """
    
    documents = []
    with engine.connect() as conn:
        result = conn.execute(text(query))
        for row in result:
            # Contextual text for better embedding
            text_content = f"Product: {row.product_name}. Category: {row.category_name}. Manual: {row.product_manual}"
            
            metadata = {
                "product_id": str(row.product_id),
                "product_name": row.product_name,
                "category": row.category_name
            }
            documents.append(Document(text=text_content, metadata=metadata))
            
    logger.info(f"Loaded {len(documents)} products from database.")
    return documents


def _build_index() -> VectorStoreIndex:
    """Build and persist the vector index from SQL metadata."""
    logger.info("Building SQL metadata index...")
    documents = _load_sql_product_metadata()
    
    # Granular splitting for long manuals
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        transformations=[splitter],
    )
    
    INDEX_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(INDEX_STORAGE_DIR))
    logger.info(f"SQL Metadata index persisted to {INDEX_STORAGE_DIR}")
    return index


def _load_index() -> VectorStoreIndex:
    """Load the index from disk."""
    logger.info(f"Loading existing SQL index from {INDEX_STORAGE_DIR}")
    storage_context = StorageContext.from_defaults(persist_dir=str(INDEX_STORAGE_DIR))
    return load_index_from_storage(storage_context, embed_model=embed_model)


def get_index() -> VectorStoreIndex:
    """Public access point for the vector index."""
    if INDEX_STORAGE_DIR.exists() and any(INDEX_STORAGE_DIR.iterdir()):
        try:
            return _load_index()
        except Exception as e:
            logger.warning(f"Failed to load index: {e}. Rebuilding...")
    return _build_index()

if __name__ == "__main__":
    # Test builder
    get_index()
