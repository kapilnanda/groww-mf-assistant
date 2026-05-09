import os
import json
import chromadb
from pathlib import Path

def generate_embeddings():
    print("Starting Subphase 1.4: Embedding Generation & Storage")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    chunks_file = project_root / "data" / "chunks" / "all_chunks.jsonl"
    db_dir = project_root / "data" / "chroma_db"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    if not chunks_file.exists():
        print(f"Error: Chunks file not found at {chunks_file}")
        return
        
    # Initialize ChromaDB Persistent Client
    # ChromaDB will automatically use the default 'all-MiniLM-L6-v2' model for embeddings
    client = chromadb.PersistentClient(path=str(db_dir))
    
    # Create or get the collection
    collection = client.get_or_create_collection(
        name="mutual_fund_facts",
        metadata={"hnsw:space": "cosine"} # Cosine similarity works best for semantic search
    )
    
    documents = []
    metadatas = []
    ids = []
    
    with open(chunks_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
                
            chunk = json.loads(line)
            content = chunk["page_content"]
            metadata = chunk["metadata"]
            
            # Generate a distinct ID for each chunk based on the scheme and section
            chunk_id = f"{metadata['scheme_name'].replace(' ', '_')}_{metadata['section'].replace(' ', '_')}"
            
            documents.append(content)
            metadatas.append(metadata)
            ids.append(chunk_id)
            
    print(f"Loaded {len(documents)} chunks from JSONL.")
    
    # Add to ChromaDB (this generates embeddings locally and saves them to disk)
    print("Generating embeddings and saving to ChromaDB. This may take a moment...")
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    # Verify count
    count = collection.count()
    print(f"Successfully stored {count} vectorized documents in the 'mutual_fund_facts' collection at data/chroma_db/")

if __name__ == "__main__":
    generate_embeddings()
