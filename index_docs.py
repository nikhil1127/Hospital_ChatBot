#!/usr/bin/env python3
"""
Hospital Knowledge Base Indexer
==============================
Run this script after adding PDFs/TXT files to data/documents/

Usage:
    python index_docs.py

This will:
1. Load all documents from data/documents/
2. Split them into chunks
3. Create embeddings
4. Store in ChromaDB for the bot to search
"""

import sys
from app.core.rag_service import index_documents_cli

if __name__ == "__main__":
    print("🏥 Hospital Knowledge Base Indexer\n")
    index_documents_cli()
