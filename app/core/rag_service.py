"""
RAG (Retrieval-Augmented Generation) Service
=============================================
This module handles document ingestion, embedding generation,
and semantic search for the hospital knowledge base.

Usage:
1. Place PDFs/TXT files in `data/documents/` folder
2. Run: python -m app.core.rag_service (to index documents)
3. The bot will automatically use this for relevant queries
"""

import os
from typing import List, Optional
from pathlib import Path

# Vector database
import chromadb
from chromadb.utils import embedding_functions

# Document loaders
try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG dependencies not fully installed. Run: pip install langchain-community pypdf")


class HospitalRAGService:
    """
    RAG Service for Hospital Knowledge Base.
    Indexes documents and provides semantic search for the AI.
    """

    def __init__(self, data_dir: str = "data/documents"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="data/chroma_db")

        # Use default embedding function (all-MiniLM-L6-v2)
        self.embedding_func = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="hospital_knowledge",
            embedding_function=self.embedding_func
        )

        print(f"📚 RAG Service initialized")
        print(f"   📁 Documents folder: {self.data_dir.absolute()}")
        print(f"   📊 Indexed documents: {self.collection.count()}")

    def index_documents(self) -> int:
        """
        Load all PDFs and TXT files from data/documents/ and index them.
        Returns number of chunks indexed.
        """
        if not RAG_AVAILABLE:
            print("❌ RAG dependencies not available. Install: pip install langchain-community pypdf")
            return 0

        # Supported file types
        documents = []

        # Load PDFs
        pdf_files = list(self.data_dir.glob("*.pdf"))
        txt_files = list(self.data_dir.glob("*.txt"))
        md_files = list(self.data_dir.glob("*.md"))

        if not (pdf_files or txt_files or md_files):
            print("⚠️ No documents found in data/documents/")
            print("   Add PDFs, TXT, or MD files and run again.")
            return 0

        print(f"📄 Found {len(pdf_files)} PDFs, {len(txt_files)} TXTs, {len(md_files)} MDs")

        # Process PDFs
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_path))
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = pdf_path.name
                    doc.metadata["type"] = "pdf"
                documents.extend(docs)
                print(f"   ✅ Loaded: {pdf_path.name}")
            except Exception as e:
                print(f"   ❌ Error loading {pdf_path.name}: {e}")

        # Process TXT and MD files
        for text_path in list(txt_files) + list(md_files):
            try:
                loader = TextLoader(str(text_path), encoding='utf-8')
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = text_path.name
                    doc.metadata["type"] = "text"
                documents.extend(docs)
                print(f"   ✅ Loaded: {text_path.name}")
            except Exception as e:
                print(f"   ❌ Error loading {text_path.name}: {e}")

        if not documents:
            return 0

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)
        print(f"✂️ Split into {len(chunks)} chunks")

        # Clear existing collection and add new documents
        self.collection.delete(where={})  # Clear all

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            ids = [f"chunk_{i + j}" for j in range(len(batch))]
            texts = [chunk.page_content for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]

            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )

        print(f"🎉 Successfully indexed {len(chunks)} chunks from {len(documents)} pages")
        return len(chunks)

    def search(self, query: str, n_results: int = 3) -> List[dict]:
        """
        Search the knowledge base for relevant information.
        Returns top N matching chunks with metadata.
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'source': results['metadatas'][0][i].get('source', 'Unknown'),
                'distance': results['distances'][0][i]
            })

        return formatted_results

    def get_relevant_context(self, query: str, max_chars: int = 1000) -> str:
        """
        Get relevant context from documents for a given query.
        Returns formatted string to add to AI prompt.
        """
        results = self.search(query, n_results=3)

        if not results:
            return ""

        context_parts = []
        for result in results:
            context_parts.append(f"[{result['source']}] {result['content']}")

        context = "\n\n".join(context_parts)

        # Truncate if too long
        if len(context) > max_chars:
            context = context[:max_chars] + "..."

        return context

    def has_documents(self) -> bool:
        """Check if any documents are indexed."""
        return self.collection.count() > 0


def index_documents_cli():
    """
    CLI command to index documents.
    Run this after adding PDFs to data/documents/
    """
    print("🏥 Hospital Knowledge Base - Document Indexer")
    print("=" * 50)

    rag = HospitalRAGService()
    count = rag.index_documents()

    if count > 0:
        print("\n✅ Indexing complete!")
        print("   Your bot can now answer questions from these documents.")
    else:
        print("\n⚠️ No documents indexed.")
        print("   Add PDFs/TXTs to 'data/documents/' and run again.")


# Singleton instance for the application
rag_service = HospitalRAGService()

if __name__ == "__main__":
    index_documents_cli()
