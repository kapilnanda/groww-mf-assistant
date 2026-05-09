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
query = "What is the NAV of HDFC Mid-Cap Opportunities Fund?"

# Manually trigger the steps to see what's happening
target_scheme = pipeline.extract_intent(query)
print(f"Extracted Scheme: {target_scheme}")

context_data = pipeline.retrieve_context(target_scheme, query)
print(f"Context found: {context_data is not None}")
if context_data:
    print(f"Context Text:\n{context_data['text']}")

response = pipeline.generate_response(query)
print(f"Final Response:\n{response}")
