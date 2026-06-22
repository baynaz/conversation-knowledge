# Conversation Knowledge

## Overview

Conversation Knowledge is a knowledge extraction platform designed to transform Microsoft Teams discussions into a structured technical knowledge base.

Instead of storing isolated messages, the system reconstructs conversation threads, extracts technical knowledge using LLMs, and builds a searchable repository that can later power a Retrieval-Augmented Generation (RAG) assistant.

Typical use cases include:

- IT support conversations
- Troubleshooting discussions
- Firmware and software issues
- Internal technical Q&A
- Operational knowledge retention

---

## Project Goals

The objective is to automatically convert Teams conversations into reusable knowledge objects.

### Example

**Raw Teams conversation**

```text
User A: Firmware update fails with error 0x80070005.
User B: Try running the installer as administrator.
User A: Still failing.
User C: Disable antivirus before updating.
User A: That worked.
```

**Extracted Knowledge Object**

```json
{
  "problem": "Firmware update fails with error 0x80070005",
  "context": "Windows environment",
  "symptoms": [
    "error 0x80070005"
  ],
  "solutions_tried": [
    "Run as administrator"
  ],
  "confirmed_solution": "Disable antivirus before updating",
  "technology": "Firmware X",
  "source": "thread_id_xyz"
}
```

---

# Architecture

```text
Microsoft Teams
        │
        ▼
Power Automate
        │
        ▼
FastAPI Ingestion Layer
        │
        ▼
PostgreSQL (raw messages)
        │
        ▼
LLM Extraction Pipeline
        │
        ▼
Knowledge Objects
        │
        ▼
Embeddings
        │
        ▼
Qdrant / pgvector
        │
        ▼
RAG Assistant
```

---

# Technical Stack
## Architecture Stack

| Component | Technology |
|------------|------------|
| Frontend / Trigger | Microsoft Teams, Power Automate |
| Data Ingestion | FastAPI |
| Raw Data Storage | PostgreSQL |
| Knowledge Storage | PostgreSQL |
| Embedding Storage | Qdrant / pgvector |
| Knowledge Extraction | Ollama + LLMs |
| Semantic Retrieval | Vector Search |
| AI Assistant | RAG Pipeline |
| Deployment | Docker & Docker Compose |

---

# Project Phases

## Phase 1 — Raw Extraction

### Goal

Store Teams conversations exactly as they are.

---

## Phase 2 — Knowledge Extraction Pipeline

### Goal

Transform conversation threads into structured knowledge.

### Challenges

#### 1. Thread Reconstruction

Teams conversations contain nested replies.

The system must reconstruct discussion trees to provide complete context to the LLM.

#### 2. Confirmed Solution Detection

A thread may contain many suggestions.

The system must identify which solution was actually validated.

#### 3. Deduplication

The same issue may appear multiple times.

The system should merge similar knowledge rather than creating duplicates.

---

## Phase 3 — Embeddings & Retrieval

### Goal

Make extracted knowledge searchable.

### Steps

1. Generate embeddings from knowledge objects
2. Store embeddings in Qdrant or pgvector
3. Implement semantic search
4. Build RAG assistant

---

# Local Development Setup

## Prerequisites

- Docker Desktop
- Python 3.11+
- VS Code

### Recommended VS Code Extensions

- SQLTools
- Python
- Docker

---

## Start Services

```bash
docker compose up -d
```

---

## Verify Running Containers

```bash
docker ps
```

---

## Connect to PostgreSQL

```bash
docker exec -it conv-postgres psql -U admin -d knowledge_db
```

If the container already exists:

```bash
docker ps -a --filter "name=conv-postgres"
```

---

## PostgreSQL Commands

### Show all tables

```sql
\dt
```

### Show table structure

```sql
\d table_name
```

Example:

```sql
\d raw_messages
```

### View a Complete Thread

```sql
SELECT *
FROM raw_messages
WHERE thread_id = 'thread_001'
ORDER BY parent_message_id NULLS FIRST, timestamp;
```

---

## pgvector Verification

Verify that the extension is installed:

```sql
SELECT * FROM pg_extension;
```

Expected result:

```text
plpgsql
uuid-ossp
vector
```

---

# FastAPI

Start the API:

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Current MVP Scope

The current MVP focuses on:

- Teams message ingestion
- Raw message storage
- Thread reconstruction preparation
- Knowledge extraction pipeline design

The LLM extraction and RAG layers will be implemented after validating the ingestion pipeline.

---

# Key Design Principle

The chatbot is not the product.

The product is the automatic transformation of unstructured Teams conversations into structured technical knowledge.
