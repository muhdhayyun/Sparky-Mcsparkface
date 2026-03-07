# -*- coding: utf-8 -*-
"""
RAG Chatbot Engine for Sparky-Mcsparkface Energy Dashboard
==========================================================
Provides AI-powered energy assistant capabilities using RAG
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from pypdf import PdfReader
import time

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "energy-assistant")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_DIMENSIONS = int(os.getenv("EMBED_DIMENSIONS", "1024"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Validate required API keys
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env file")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to index
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIMENSIONS,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    time.sleep(10)

pinecone_index = pc.Index(INDEX_NAME)


def create_embedding(text):
    """Convert text to embedding vector using OpenAI's API"""
    response = openai_client.embeddings.create(
        input=text,
        model=EMBED_MODEL
    )
    return response.data[0].embedding


def store_in_pinecone(text, metadata=None):
    """Store text in Pinecone vector database"""
    if metadata is None:
        metadata = {}
    
    embedding = create_embedding(text)
    vector_id = f"doc_{hash(text)}"
    metadata['text'] = text
    
    pinecone_index.upsert(vectors=[(vector_id, embedding, metadata)])
    return vector_id


def retrieve_from_pinecone(query, top_k=3):
    """Retrieve relevant documents from Pinecone"""
    query_embedding = create_embedding(query)
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    contexts = []
    for match in results['matches']:
        if 'text' in match['metadata']:
            contexts.append(match['metadata']['text'])
    
    return contexts


def chat_with_rag(user_message, system_context=""):
    """Generate response using RAG"""
    # Retrieve relevant context
    contexts = retrieve_from_pinecone(user_message, top_k=3)
    
    # Build context string
    context_str = "\n\n".join(contexts) if contexts else "No relevant context found."
    
    # Default system context for energy assistant
    if not system_context:
        system_context = """You are an AI energy assistant for Sparky-Mcsparkface, 
        a smart energy dashboard. You help users understand their energy consumption, 
        provide energy-saving tips, and answer questions about renewable energy and 
        sustainability. Be friendly, helpful, and focus on practical advice."""
    
    # Create messages for chat
    messages = [
        {"role": "system", "content": system_context},
        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {user_message}"}
    ]
    
    # Generate response
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks


def ingest_text_file(file_path):
    """Ingest a text file into the knowledge base"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    metadata = {'source': os.path.basename(file_path), 'type': 'text'}
    
    for i, chunk in enumerate(chunks):
        chunk_metadata = {**metadata, 'chunk': i}
        store_in_pinecone(chunk, chunk_metadata)
    
    return len(chunks)


def ingest_pdf_file(file_path):
    """Ingest a PDF file into the knowledge base"""
    reader = PdfReader(file_path)
    full_text = ""
    
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    chunks = chunk_text(full_text)
    metadata = {'source': os.path.basename(file_path), 'type': 'pdf'}
    
    for i, chunk in enumerate(chunks):
        chunk_metadata = {**metadata, 'chunk': i}
        store_in_pinecone(chunk, chunk_metadata)
    
    return len(chunks)


def ingest_directory(directory_path):
    """Ingest all supported files from a directory"""
    total_chunks = 0
    ingested_files = []
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        try:
            if filename.endswith('.txt'):
                chunks = ingest_text_file(file_path)
                total_chunks += chunks
                ingested_files.append(filename)
            elif filename.endswith('.pdf'):
                chunks = ingest_pdf_file(file_path)
                total_chunks += chunks
                ingested_files.append(filename)
        except Exception as e:
            print(f"Error ingesting {filename}: {str(e)}")
    
    return total_chunks, ingested_files


def clear_database():
    """Clear all vectors from the database"""
    pinecone_index.delete(delete_all=True)
    return True


def get_database_stats():
    """Get statistics about the database"""
    stats = pinecone_index.describe_index_stats()
    return stats
