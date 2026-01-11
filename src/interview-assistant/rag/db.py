import chromadb
import uuid
import os
import shutil

# Check if we should use OpenAI embeddings (optional, sticking to default for now for ease of setup)
# from chromadb.utils import embedding_functions

# Define Base Directory (src/interview-assistant/data)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "interview_rag_db")
COLLECTION_NAME = "candidates"

class RAGDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        # Using default embedding function (Sentence Transformers)
        # This requires 'sentence-transformers' installed.
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def add_documents(self, processed_docs):
        """
        Adds processed documents to the vector store.
        processed_docs: List of {'text': str, 'metadata': dict}
        """
        ids = []
        documents = []
        metadatas = []

        for doc in processed_docs:
            full_text = doc['text']
            base_metadata = doc['metadata']
            
            # Simple chunking strategy: 1000 characters with 200 overlap
            chunk_size = 1000
            overlap = 200
            
            for i in range(0, len(full_text), chunk_size - overlap):
                chunk = full_text[i:i + chunk_size]
                if len(chunk) < 50: # Skip tiny chunks
                    continue
                
                # Add chunk index to metadata maybe?
                chunk_metadata = base_metadata.copy()
                chunk_metadata['chunk_index'] = i
                
                ids.append(str(uuid.uuid4()))
                documents.append(chunk)
                metadatas.append(chunk_metadata)

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        return False

    def query(self, query_text, candidate_name=None, n_results=5):
        """
        Query the database.
        If candidate_name is provided, filters results to that candidate.
        """
        where_filter = None
        if candidate_name:
            where_filter = {"candidate_name": candidate_name}
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )
        return results

    def reset(self):
        """
        Deletes the collection and recreates it.
        """
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        # Verify empty
        print(f"Collection {COLLECTION_NAME} reset. Count: {self.collection.count()}")

# Singleton instance access
_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = RAGDatabase()
    return _db_instance
