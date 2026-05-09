import os
import json
from pathlib import Path

def create_chunks():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    cleaned_data_dir = project_root / "data" / "cleaned"
    chunks_dir = project_root / "data" / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    print("Starting Subphase 1.3: Chunking Strategy")
    
    all_chunks = []
    
    for file_path in cleaned_data_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        scheme_name = data["sections"]["Core Details"]["Fund Name"]
        source_url = data["source_url"]
        last_updated = data["last_updated"]
        
        # We use section-based chunking as requested in Architecture
        for section_name, section_facts in data["sections"].items():
            # Build the chunk content
            chunk_content = f"Scheme: {scheme_name}\nSection: {section_name}\n\n"
            for key, value in section_facts.items():
                 chunk_content += f"- {key}: {value}\n"
                 
            # Build metadata attached to every chunk
            metadata = {
                "scheme_name": scheme_name,
                "section": section_name,
                "source_url": source_url,
                "last_updated_date": last_updated
            }
            
            chunk = {
                "page_content": chunk_content.strip(),
                "metadata": metadata
            }
            all_chunks.append(chunk)
            
        print(f"  -> Created chunks for {scheme_name}")
        
    # Save all chunks to a single JSONL file for easy embedding ingestion
    out_path = chunks_dir / "all_chunks.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    print(f"Chunking complete. Total {len(all_chunks)} chunks saved to {out_path}")

if __name__ == "__main__":
    create_chunks()
