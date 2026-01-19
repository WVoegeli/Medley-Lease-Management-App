"""
Configuration settings for Medley Lease Management RAG System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
LEASE_CONTRACTS_DIR = BASE_DIR / os.getenv("LEASE_CONTRACTS_DIR", "Lease Contracts")
CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Embedding settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = 1536
EMBEDDING_BATCH_SIZE = 100

# LLM settings
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Chunking settings
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens
MIN_CHUNK_SIZE = 100  # minimum tokens for a chunk

# Search settings
VECTOR_SEARCH_K = 20  # top-k for vector search
BM25_SEARCH_K = 20  # top-k for BM25 search
FINAL_RESULTS_K = 10  # final results after fusion
RRF_K = 60  # RRF constant
VECTOR_WEIGHT = 0.6  # weight for vector search in hybrid
BM25_WEIGHT = 0.4  # weight for BM25 in hybrid

# ChromaDB collection name
COLLECTION_NAME = "medley_leases"

# Supported file extensions
SUPPORTED_EXTENSIONS = [".docx"]
