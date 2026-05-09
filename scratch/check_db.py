import chromadb
from pathlib import Path
import os

project_root = Path(__file__).resolve().parent.parent
db_dir = project_root / "data" / "chroma_db"

print(f"Checking DB at: {db_dir}")

if not db_dir.exists():
    print("Error: DB directory does not exist!")
    exit(1)

client = chromadb.PersistentClient(path=str(db_dir))
try:
    collection = client.get_collection(name="mutual_fund_facts")
except Exception as e:
    print(f"Error getting collection: {e}")
    print("Available collections:", client.list_collections())
    exit(1)

print(f"Collection count: {collection.count()}")

results = collection.get()
schemes = set()
for metadata in results['metadatas']:
    schemes.add(metadata['scheme_name'])

print("\nSchemes in database:")
for s in schemes:
    print(f"- {s}")

print("\nSample document content:")
if results['documents']:
    print(results['documents'][0][:500])
