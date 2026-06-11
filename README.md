# Agentic Systems

This repository contains experiments, examples, and implementations related to agentic AI systems. It is a realization of my journey through the **Agentic Systems course at IIT Roorkee**, where I am learning to design and build expert AI agents.

## About This Repository

The projects and code samples here explore various aspects of building AI agents, including:

- Agent design and prompting
- Memory systems (window memory, buffer memory, etc.)
- Retrieval-Augmented Generation (RAG)
- Vector databases for semantic search
- Tool use and agent workflows

Each example is intended to illustrate a concept or technique covered in the course, serving as both a learning artifact and a reference for future agent development.

## Project Structure

```
agentic-systems/
├── chroma_store/               # ChromaDB vector storage
├── vector_search_lab/          # Experiments with vector search and RAG
│   ├── chroma_store/
│   └── support_faq_search.py
├ solutions.md                  # GyanBot AI study assistant design (course assignment)
├ prompt_builder.py             # Product launch advisor agent example
├ window_memory.py              # Window memory implementation for LLMs
├ rag_use_case.md               # RAG design for coaching institute support
├ device_management.sql         # Sample SQL database schema
```

## Key Examples

### 1. GyanBot - AI Study Assistant (`solutions.md`)
A detailed design document for an AI study assistant tailored for Indian engineering students. It covers:
- System prompt with boundaries and tone
- User prompt example (C-I-F-C framework)
- Framework recommendation (LangChain)
- Agent flow for career guidance

### 2. Product Launch Advisor Agent (`prompt_builder.py`)
A simple example of building agent prompts for product evaluation. Demonstrates:
- Role definition
- Task specification
- Instructions and constraints
- Output formatting

### 3. Window Memory (`window_memory.py`)
Implementation of a window memory strategy for LLMs to manage conversation history. Shows:
- System message persistence
- Conversation windowing
- Context truncation
- Memory reporting

### 4. RAG Use Case (`rag_use_case.md`)
Design plan for combining SQL databases with vector databases for a support assistant. Details:
- What data stays in SQL (structured data)
- What goes into vector database (unstructured FAQs)
- Metadata storage
- Query-time flow
- Performance considerations

### 5. Vector Search Lab (`vector_search_lab/`)
Hands-on experiments with ChromaDB and sentence transformers:
- `support_faq_search.py`: Basic CRUD operations and similarity search
- Persistent storage with ChromaDB
- Embedding generation with sentence-transformers

## Getting Started

### Prerequisites
- Python 3.8+
- Structured Query Language
- Required packages: `chromadb`, `sentence-transformers`

### Installation
```bash
pip install chromadb sentence-transformers
```

### Running Examples
1. **Window Memory Demo**:
   ```bash
   python window_memory.py
   ```

2. **Vector Search Demo**:
   ```bash
   cd vector_search_lab
   python support_faq_search.py
   ```

3. **Product Launch Advisor**:
   ```bash
   python prompt_builder.py
   ```

## Contributing

Feel free to submit issues or pull requests to improve the examples or add new agentic system implementations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by various AI agent frameworks and memory systems
- Uses ChromaDB for vector storage
- Uses sentence-transformers for embeddings
- Developed as part of the Agentic Systems course at IIT Roorkee
