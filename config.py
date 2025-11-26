"""Configuration settings for Travel-Pro System"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", " ")

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", " ")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "")
PINECONE_HOST = os.getenv("PINECONE_HOST", "")
PINECONE_DIMENSIONS = 1536  # text-embedding-3-small produces 1536-dimensional vectors
PINECONE_METRIC = "cosine"

# RapidAPI Configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "")  # Using gpt-4o-mini as gpt-4o-nano doesn't exist
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "")

# Budget Configuration
MAX_REOPTIMIZATION_ATTEMPTS = os.getenv("MAX_REOPTIMIZATION_ATTEMPTS", "")
BUDGET_TOLERANCE = os.getenv("BUDGET_TOLERANCE", "")  # 5% tolerance for budget validation

