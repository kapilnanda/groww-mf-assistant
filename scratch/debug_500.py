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
query = "what is the minimum investment required for HDFC Flexi Cap Direct Plan Growth"

try:
    response = pipeline.generate_response(query)
    print(f"Query: {query}")
    print(f"Response:\n{response}")
except Exception as e:
    import traceback
    traceback.print_exc()
