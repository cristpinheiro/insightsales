# Insight Sales (Production)

## Purpose

Insight Sales is a **read-only, production-grade natural language analytics API**. It translates user questions into **strictly validated SQL** and executes them safely against PostgreSQL.

LLMs are used only for **query generation**. They have no execution authority.

---

## Production Architecture

### API Layer (FastAPI)

* No authentication
* No IP-based restrictions
* No rate limiting
* Request size limits
* Structured error responses
* Correlation IDs for tracing

### NLP → SQL Service

* Deterministic prompt templates
* Explicit schema injection
* Bounded retries (fail-fast)
* No conversational state

### SQL Validation Layer

Hard guarantees:

* `SELECT` only
* No subqueries touching system catalogs
* No DDL / DML / functions
* No comments, CTE abuse, or UNION escalation
* Column/table allow-listing

Invalid SQL is rejected before execution.

### Database Access

* Dedicated **read-only DB role**
* Connection pooling (async)
* Statement timeout enforced
* Row/column-level security supported

---

## Data Model

Tables:

* `seller`
* `customer` (FK → seller)
* `product`
* `order` (FK → seller, customer)
* `order_product`

Schema is versioned and must stay in sync with the LLM context.

---

## API Contract

### Endpoint

`POST /api/query`

```json
{
  "query": "Total sales by seller last quarter"
}
```

### Execution Flow

1. Input validation
2. SQL generation
3. SQL policy validation
4. Timed execution
5. Structured JSON response

Failures are explicit and non-retriable unless marked.

---

## Deployment

### Requirements

* Python ≥ 3.10
* PostgreSQL ≥ 13
* Ollama (local or remote)
* Docker (recommended)

### Environment

Example `.env.example`

### Run

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## Security Guarantees

* No authentication or network-level restrictions
* Read-only DB credentials
* SQL allow-list + parser-based validation
* No raw string execution
* TLS for DB connections (recommended)
* Audit logging (SQL hash, latency)

**LLM output is untrusted input.**

---

## Observability

* Structured logs (JSON)
* Request latency metrics
* SQL execution timing
* Validation failure counters

Integrates cleanly with Prometheus / OpenTelemetry.

---

## Operational Limits

* Max query execution time enforced
* Max result size capped
* No joins beyond schema graph

---

## Ollama Model Setup

### Create the model

```bash
ollama create insightsales-model -f Modelfile
```

### Verify the model

```bash
ollama list
```

Ensure `insightsales-model` appears in the list.

### Test the model

```bash
ollama run insightsales-model "Show all sellers"
```

Expected output:

```sql
SELECT id, name FROM seller ORDER BY name;
```

### Application configuration

The API uses this model via environment configuration:

```env
OLLAMA_MODEL=insightsales-model
```

### Update the model

```bash
ollama rm insightsales-model
ollama create insightsales-model -f Modelfile
```

### Alternative base models

Change the `FROM` line in `Modelfile` if needed:

* `codellama`
* `llama3`
* `mistral`
* `phi`

After changing, recreate the model with `ollama create`.

---

## License

MIT
