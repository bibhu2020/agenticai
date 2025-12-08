# Import the necessary Libraries
import os
from pathlib import Path
from langchain.utility.llm_factory2 import LLMFactory
from utility.embedding_factory import EmbeddingFactory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings.sentence_transformer import ( SentenceTransformerEmbeddings)


class RAG:
    def __init__(self, pdf_folder, db_path):
        self.pdf_folder = pdf_folder
        self.db_path = db_path
        self.dB = None
        self.llm = LLMFactory.get_llm("openai")
        self.embedding = EmbeddingFactory.get_llm("openai")

    def __split_docs_into_chunks(self):
        # Convert relative path to absolute path
        absolute_pdf_folder = Path(self.pdf_folder).resolve()
        print(f"Absolute path: {absolute_pdf_folder}")

        # Check if the directory exists
        if not absolute_pdf_folder.is_dir():
            raise ValueError(f"Invalid directory: {absolute_pdf_folder}")
        
        pdf_files = [f for f in os.listdir(absolute_pdf_folder) if f.endswith('.pdf')]
        if not pdf_files:
            raise ValueError(f"No PDFs found in the folder: {absolute_pdf_folder}")
        print(f"Found PDFs: {pdf_files}")
        
        # Load the directory to pdf_loader
        pdf_loader = PyPDFDirectoryLoader(absolute_pdf_folder)
        
        # Create text_splitter
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name='cl100k_base',
            chunk_size=512,
            chunk_overlap=16
        )

        # Load and split the documents into chunks
        report_chunks = pdf_loader.load_and_split(text_splitter)
        
        if not report_chunks:
            raise ValueError("No chunks were created from the documents.")
        
        # print(report_chunks)
        # print(f"A chunk sample: {report_chunks[0]}")
        
        return report_chunks
    
    def build_vector_db(self):

        #Name of colelction in dB
        collection_name = 'reports_collection'

        # Initiate the embedding momdel 'thenlper/gte-large'
        embedding_model = self.embedding  #SentenceTransformerEmbeddings(model_name='thenlper/gte-large')

        report_chunks = self.__split_docs_into_chunks()

        # Create the vector Database
        vectorstore = Chroma.from_documents(
            report_chunks,
            embedding_model,
            collection_name=collection_name,
            persist_directory=self.db_path
        )

        # Persist the DB
        # vectorstore.persist()

        self.__load_vector_db()

        print('Pdf document embedddings stored into vector dB.')

    def __load_vector_db(self):
        #Create a Colelction Name
        collection_name = 'reports_collection'

        # Initiate the embedding momdel 'thenlper/gte-large'
        embedding_model = self.embedding  #SentenceTransformerEmbeddings(model_name='thenlper/gte-large')

        # Load the persisted DB
        self.dB = Chroma(
            collection_name=collection_name,
            persist_directory=self.db_path,
            embedding_function=embedding_model
        )

        return self.dB;

    def test_query(self, user_question, document_path):
        if self.dB == None:
            self.__load_vector_db()

        # Perform similarity search on the user_question
        # You must add an extra parameter to the similarity search  function so that you can filter the response based on the 'source'  in the metadata of the doc
        # The filter can be added as a parameter to the similarity search function
        # This will allow you to retrieve chunks from a particular document
        # Use the same format to filter your response based on the company.
        docs = self.dB.similarity_search(user_question, k=5, filter = {"source":document_path})
        # docs = self.dB.similarity_search(user_question, k=5)

        return docs

    def get_context(self, user_question, document_path = ""):
        if self.dB == None:
            self.__load_vector_db()

        # Create context for query by joining page_content and page number of the retrieved docs
        if document_path == "":
            relevant_document_chunks = self.dB.similarity_search(user_question, k=5)
        else:
            relevant_document_chunks = self.dB.similarity_search(user_question, k=5, filter = {"source": document_path} )

        context_list = [d.page_content + "\n ###Page: " + str(d.metadata['page']) + "\n\n " for d in relevant_document_chunks]
        context_for_query = ". ".join(context_list)

        print(context_for_query) # Print the whole context_for_query (after joining all the chunks. It should contain page number of every chunk)

        return context_for_query


    def question_and_answer(self, user_question, document_path = ""):
        # Create a system message for the LLM
        qna_system_message = """
            You are an assistant to a Financial Analyst. Your task is to summarize and provide relevant information to the financial analyst's question based on the provided context.

            User input will include the necessary context for you to answer their questions. This context will begin with the token: ###Context.
            The context contains references to specific portions of documents relevant to the user's query, along with page number from the report.
            The source for the context will begin with the token ###Page

            When crafting your response:
            1. Select only context relevant to answer the question.
            2. Include the source links in your response.
            3. User questions will begin with the token: ###Question.
            4. If the question is irrelevant or if the context is empty - "Sorry, this is out of my knowledge base"

            Please adhere to the following guidelines:
            - Your response should only be about the question asked and nothing else.
            - Answer only using the context provided.
            - Do not mention anything about the context in your final answer.
            - If the answer is not found in the context, it is very very important for you to respond with "Sorry, this is out of my knowledge base"
            - If NO CONTEXT is provided, it is very important for you to respond with "Sorry, this is out of my knowledge base"

            Here is an example of how to structure your response:

            Answer:
            [Answer]

            Page:
            [Page number]
        """

        # Create a message template
        qna_user_message_template = """
            ###Context
            Here are some documents and their page number that are relevant to the question mentioned below.
            {context}

            ###Question
            {question}
        """

        context_for_query = self.get_context(user_question, document_path)


        from langchain_core.output_parsers import StrOutputParser
        parser = StrOutputParser()

        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate([
            ("system", qna_system_message),
            ("human", qna_user_message_template),
        ])

        chain = prompt | self.llm | parser

        response = chain.invoke({"context": context_for_query, "question": user_question},
                config={"temperature": 0, "max_tokens": 5, "model_name": "gpt-4o"})

        return response 


