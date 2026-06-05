# Vectorless RAG

## Shortcoming of Traditional RAG

- Embedding is done on random size chunk (no science behind it.). It may so happen that your content is broken into 2 separate chunks, and on query you may not get both returned by the simillarity search.

- User query must has matching keyword for simillarity search to query the vector and find the matching content. 

- Say a chunk has a referral to another content. Technically, the RAG should read the referral content also, But it does not.
E.g. A law book paragraph/chunk says "Refer to Rule 6.3.7a to decide the current situation". RAG does not dig into referred rule.

- RAG relies on semantic similarity rather than true relevance. But similarity ≠ relevance — what we truly need in retrieval is relevance, and that requires reasoning. When working with professional documents that demand domain expertise and multi-step reasoning, similarity search often falls short. 

- Pipeline goes like this: Documents -> Chunks -> Embeddings -> VectorDB -> Simillarity Search -> Answer


## What is PagenIndex?

**PageIndex** is a vectorless, reasoning-based RAG approach that retrieves answers from long documents without using embedding, chunking, or a vector database. 

Instead of relying on semantic simillarity search, PageIndex builds a **Hierarchical Table of Content (TOC)** tree from a document and uses a Large Language Model (LLM) to reason over that structure. The model first identifies the most relevant section using the documents' hierarchy, then navigates to the section to generate a precise, cited answer.

PageIndex Pipeline goes like this: Documents -> Hierarchical Index -> Reasoning-Based Retrieval -> Answer

![pageIndex](https://camo.githubusercontent.com/e9c3f93a4039fa4743b0655dc7a08eddd0eeb24ed1bfddfb03b6a0bf3c87cbdc/68747470733a2f2f646f63732e70616765696e6465782e61692f696d616765732f636f6f6b626f6f6b2f766563746f726c6573732d7261672e706e67)

### Source Code
https://github.com/VectifyAI/PageIndex

### Core Features

- **No Vector DB:** Uses document structure and LLM reasoning for retrieval, instead of vector similarity search.

- **No Chunking:** Documents are organized into natural sections, not artificial chunks.

- **Human-like Retrieval:** Simulates how human experts navigate and extract knowledge from complex documents.

- **Better Explainability and Traceability:** Retrieval is based on reasoning — traceable and interpretable, with page and section references. No more opaque, approximate vector search (“vibe retrieval”).

