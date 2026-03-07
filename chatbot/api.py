"""
FastAPI Backend for RAG Chatbot - Energy Assistant
Exposes the RAG chatbot as REST endpoints for Sparky-Mcsparkface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os

# Import RAG functions
from rag_engine import (
    chat_with_rag,
    retrieve_from_pinecone,
    store_in_pinecone,
    clear_database,
    ingest_directory,
    ingest_text_file,
    ingest_pdf_file,
    get_database_stats
)

app = FastAPI(title="Sparky Energy Assistant API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    contexts: Optional[List[str]] = None

class IngestRequest(BaseModel):
    directory: Optional[str] = None
    file_path: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    chunks_added: int
    files_processed: Optional[List[str]] = None

class StatusResponse(BaseModel):
    status: str
    message: str
    database_stats: Optional[dict] = None


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Sparky Energy Assistant API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    try:
        stats = get_database_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "vector_count": stats.get('total_vector_count', 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat with the energy assistant"""
    try:
        # Get relevant contexts for transparency
        contexts = retrieve_from_pinecone(request.message, top_k=3)
        
        # Generate response
        response = chat_with_rag(request.message, request.user_context or "")
        
        return ChatResponse(
            response=response,
            contexts=contexts if contexts else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/ingest", response_model=IngestResponse)
def ingest_files(request: IngestRequest):
    """Ingest files into the knowledge base"""
    try:
        if request.directory:
            if not os.path.exists(request.directory):
                raise HTTPException(status_code=404, detail="Directory not found")
            
            chunks, files = ingest_directory(request.directory)
            return IngestResponse(
                status="success",
                chunks_added=chunks,
                files_processed=files
            )
        
        elif request.file_path:
            if not os.path.exists(request.file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            if request.file_path.endswith('.txt'):
                chunks = ingest_text_file(request.file_path)
            elif request.file_path.endswith('.pdf'):
                chunks = ingest_pdf_file(request.file_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            return IngestResponse(
                status="success",
                chunks_added=chunks,
                files_processed=[os.path.basename(request.file_path)]
            )
        
        else:
            raise HTTPException(status_code=400, detail="Either directory or file_path required")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")


@app.get("/stats")
def get_stats():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        return {
            "status": "success",
            "database_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.delete("/database", response_model=StatusResponse)
def clear_db():
    """Clear the entire database (use with caution!)"""
    try:
        clear_database()
        return StatusResponse(
            status="success",
            message="Database cleared successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@app.post("/store")
def store_text(text: str, metadata: Optional[dict] = None):
    """Store a single text snippet"""
    try:
        vector_id = store_in_pinecone(text, metadata)
        return {
            "status": "success",
            "vector_id": vector_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
