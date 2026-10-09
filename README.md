# Regulatory Compliance Agent

A prototype insurance-policy compliance workflow built with LangGraph, LangChain, OpenAI, and PostgreSQL with pgvector. It retrieves regulatory text, checks a policy against that text, and scores detected violations. The backend and frontend are scaffolds: the graph can produce a human-review result, but the case-review flow is not yet connected end to end.

## Architecture

The project has two paths: an ingestion path that indexes regulatory PDFs, and a runtime path that loads a policy and evaluates it against retrieved rules.

```mermaid
flowchart TD
    subgraph Ingestion["Regulatory document ingestion"]
        PDFs["Data/<state>/*.pdf"] --> Ingest["ingest_regulations.py"]
        Ingest --> Extract["Extract PDF text<br/>pypdf"]
        Extract --> Split["Split into overlapping chunks"]
        Split --> Embed["Create embeddings<br/>OpenAI text-embedding-3-small"]
        Embed --> VectorDB[("PostgreSQL + pgvector<br/>regulatory_embeddings")]
    end

    subgraph Runtime["Policy compliance workflow (LangGraph)"]
        Input["Input state<br/>policy_data.policy_number"] --> Intent["Intent router"]
        Intent --> PAS["PAS lookup<br/>in-memory mock"]
        PAS --> PreGuard["Pre-validation guardrails"]

        PreGuard --> CancelRetrieve["Retrieve cancellation rules"]
        PreGuard --> NonrenewRetrieve["Retrieve non-renewal rules"]
        PreGuard --> UnderwriteRetrieve["Retrieve underwriting rules"]

        VectorDB -. "similarity search" .-> CancelRetrieve
        VectorDB -. "similarity search" .-> NonrenewRetrieve
        VectorDB -. "similarity search" .-> UnderwriteRetrieve

        CancelRetrieve --> CancelValidate["Validate cancellation"]
        NonrenewRetrieve --> NonrenewValidate["Validate non-renewal"]
        UnderwriteRetrieve --> UnderwriteValidate["Validate underwriting"]

        CancelValidate --> Merge["Post-validation guardrails"]
        NonrenewValidate --> Merge
        UnderwriteValidate --> Merge

        Merge --> Reason["Rule reasoner"]
        Reason --> ReasonGuard["Post-reasoning guardrails"]
        ReasonGuard --> Score["Score violations"]
        Score --> Branch{"requires_escalation?"}
        Branch -->|"Yes"| HITL["Human underwriter review"]
        Branch -->|"No"| Response["Compliant response"]
    end

    LLM["OpenAI chat model<br/>gpt-4o-mini"] -. "violation analysis,<br/>reasoning" .-> CancelValidate
    LLM -.-> NonrenewValidate
    LLM -.-> UnderwriteValidate
    LLM -.-> Reason
```

## Requirements

- Python 3.10 or newer
- PostgreSQL with the [pgvector extension](https://github.com/pgvector/pgvector) installed and enabled
- An OpenAI API key
- Node.js and npm (for the frontend)

The application reads `OPENAI_API_KEY` and `PG_CONN_STR` from the environment (or a local `.env` file). `PG_CONN_STR` should be a PostgreSQL connection string usable by psycopg, for example:

```text
PG_CONN_STR=postgresql+psycopg://USER:PASSWORD@localhost:5432/DATABASE
OPENAI_API_KEY=your-openai-api-key
```

Keep credentials private; do not commit `.env`.

## Setup

From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create the PostgreSQL database, enable pgvector in it, and set `PG_CONN_STR` and `OPENAI_API_KEY` in your environment or a local `.env` file. The vector store collection is named `regulatory_embeddings`.

## Ingest regulatory documents

Place state-organized PDF files under `Data/<state>/`, then run:

```powershell
python ingest_regulations.py
```

The script recursively finds PDFs in `Data/`, extracts their text, splits it into overlapping chunks, tags each document with its state code, and stores the chunks in pgvector.

## Run the workflow

Run the sample invocation:

```powershell
python main.py
```

The example uses the mock PAS record `CT-123`. The workflow entry state must include `policy_data.policy_number`; the PAS lookup replaces `policy_data` with the matching mock policy. The intent router defaults a missing intent to `cancellation_compliance`.

The graph retrieves cancellation, non-renewal, and underwriting rules in parallel, validates the policy against each category, reasons over any violations, and scores them. A score below 70 sets `requires_escalation` and routes to human review; otherwise the workflow returns a compliant response. The PAS implementation is an in-memory mock, not a connection to a production policy administration system.

## Run the API

From the repository root, start the FastAPI application with:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:fastapi_app --app-dir backend --reload
```

The API routers are available under `/cases` and `/hitl`. Case storage is currently in memory, so cases are lost when the server restarts and are not shared between worker processes.

Available endpoints are `GET /cases`, `GET /cases/{case_id}`, `POST /hitl/approve`, `POST /hitl/reject`, and `POST /hitl/override`. The backend currently has no endpoint to create or initially evaluate a case, so its in-memory case list starts empty; the HITL endpoints return 404 until a case is created in memory. The HITL endpoints invoke the graph again rather than resume it from a saved pause. Open the interactive API docs at `http://localhost:8000/docs` while the server is running.

## Run the frontend

From the repository root, install the JavaScript dependencies and start the Vite development server:

```powershell
cd frontend
npm install
npm start
```

Open the local URL printed by Vite (usually `http://localhost:5173`). The current UI is a starter dashboard with a placeholder Cases page; it does not yet fetch data from the API. The case-detail components and API client under `frontend/src/` are not yet connected to the app routes.

## Project files

- `agents.py` — shared graph state, retrieval/validation agents, guardrails, reasoning, and scoring.
- `graph.py` — LangGraph nodes, edges, and conditional routing.
- `rag_pgvector.py` — PDF extraction, chunking, embeddings, pgvector storage, and retrieval.
- `ingest_regulations.py` — command-line ingestion of PDFs under `Data/`.
- `pas_mock.py` — in-memory sample policy administration system.
- `main.py` — sample graph invocation.
- `requirements.txt` — Python dependencies.
- `backend/app/` — FastAPI entry point, case/HITL routers, and in-memory case storage.
- `frontend/` — Vite/React starter app and currently unconnected case UI components/API clients.
