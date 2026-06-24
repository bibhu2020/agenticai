import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DB_NAME = 'healthcare_db'
DIRECTORY_NAME = "healthcare"

class Retriever:
    def __init__(self,  
                        file_path:str = os.path.join(os.getcwd(), "data"), 
                        db_path:str = os.path.join(os.getcwd(), "db") ):
        self.directory_path = os.path.join(file_path, DIRECTORY_NAME)
        self.db_path = os.path.join(db_path, DB_NAME)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=300,
            length_function=len,
            # separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            is_separator_regex=False,
        )
        self.retriever = None

    def load_knowledge_base(self):
        if os.path.exists(self.db_path):
            self.retriever = FAISS.load_local(
                self.db_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            ).as_retriever()
        else:
            self.retriever = self._create_knowledge_base()

    def _create_knowledge_base(self):
        documents = self._load_documents()
        chunks = self._split_documents(documents)
        # embeddings = self._embed_documents(texts)
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(self.db_path)
        return vectorstore.as_retriever()

    def _load_documents(self):
        documents = []
        loader = DirectoryLoader(
            self.directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        documents = loader.load()
        return documents

    def _split_documents(self, documents):
        chunks = []
        for doc in documents:
            chunks.extend(self.text_splitter.split_documents([doc]))
        return chunks

    # def _embed_documents(self, texts):
    #     return [self.embeddings.embed_query(text.page_content) for text in texts]   

    def retrieve(self, query, k=4):
        """Retrieve documents without scores (backward compatible)"""
        if not self.retriever:
            self.load_knowledge_base()
        return self.retriever.invoke(query)
    
    def retrieve_with_scores(self, query, k=4):
        """Retrieve documents with similarity scores"""
        if not self.retriever:
            self.load_knowledge_base()
        
        # Get the underlying vectorstore from the retriever
        vectorstore = self.retriever.vectorstore
        
        # Use similarity_search_with_score to get scores
        # Note: FAISS returns L2 distance, lower is better
        results = vectorstore.similarity_search_with_score(query, k=k)
        
        return results


    def update_knowledge_base(self):
        self._create_knowledge_base()

    def delete_knowledge_base(self):
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path) 

    # No cleanup needed for VectorStoreRetriever
    