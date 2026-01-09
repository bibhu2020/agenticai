# main.py
from llm_factory import LLMFactory
import os
import time  # Import time module for measuring processing time

from langchain_core.output_parsers import StrOutputParser

llm = LLMFactory.get_llm(
    provider="ollama"
)

embedding_model = LLMFactory.get_embedding_model(
    provider="huggingface",
)

chain = llm | StrOutputParser()

start_time = time.time()  # Start timer

print(chain.invoke("Explain the factory pattern in one sentence."))

print(embedding_model.embed_query("Explain the factory pattern in one sentence."))

end_time = time.time()  # End timer
processing_time = end_time - start_time  # Calculate elapsed time

print(f"Processing time: {processing_time:.3f} seconds")