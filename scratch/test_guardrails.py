from src.phase2_rag.pipeline import RAGPipeline
import os
from dotenv import load_dotenv
import sys

# Set encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

pipeline = RAGPipeline()
query = "My PAN is ABCDE1234F. What is the lock-in period for ELSS?"

response = pipeline.generate_response(query)
print(f"Query: {query}")
print(f"Response:\n{response}")
