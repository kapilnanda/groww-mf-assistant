import chromadb
from pathlib import Path
import os
import sys

# Set encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
db_dir = project_root / "data" / "chroma_db"

client = chromadb.PersistentClient(path=str(db_dir))
collection = client.get_collection(name="mutual_fund_facts")

scheme = "HDFC Mid Cap Fund Direct Growth"
results = collection.get(where={"scheme_name": scheme})

for i, meta in enumerate(results['metadatas']):
    print(f"Metadata {i}: {meta}")
