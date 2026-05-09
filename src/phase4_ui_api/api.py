import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.phase2_rag.pipeline import RAGPipeline
import os

# Initialize FastAPI app
app = FastAPI(title="Groww MF Facts Assistant API")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RAG Pipeline
pipeline = RAGPipeline()

# Mount static files (ensure the path is absolute)
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(static_dir, "style.css"))

@app.get("/script.js")
async def serve_js():
    return FileResponse(os.path.join(static_dir, "script.js"))


# Simple in-memory rate limiter
# Stores IP -> [timestamps]
rate_limit_store = {}
RATE_LIMIT = 20  # requests
WINDOW = 60      # seconds

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    
    # Filter out timestamps outside the window
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < WINDOW]
    
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return True
    
    rate_limit_store[ip].append(now)
    return False

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    # 1. Rate Limiting Check
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a minute.")
    
    # 2. Input Length Check
    if len(chat_req.message) > 500:
        raise HTTPException(status_code=400, detail="Query is too long. Please limit to 500 characters.")
    
    try:
        # 3. Process query via RAG Pipeline
        response_text = pipeline.generate_response(chat_req.message)
        
        return {
            "response": response_text,
            "status": "success"
        }
    except Exception as e:
        print(f"API Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred while processing your query.", "status": "error"}
        )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Groww MF Facts Assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
