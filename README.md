#  Udaan Translation Microservice

> **Udaan** (उड़ान) means *"flight"* in Hindi — empowering your words to soar across languages.

A lightweight, production-ready **translation microservice** built with **FastAPI** and **Python 3.11+**.  
Supports live translation via the **Google Cloud Translation API** and falls back to a rich **mock dictionary engine** when no API key is configured.

---

##  Features

| Feature | Detail |
|---------|--------|
|  **FastAPI** | High-performance async REST API with auto-generated OpenAPI docs |
|  **Pydantic v2** | Full request / response validation with type hints throughout |
|  **15 Languages** | Hindi, Tamil, Kannada, Bengali, Telugu, Marathi, Gujarati, Malayalam, Punjabi, Urdu, Odia, Assamese, French, German, Spanish |
|  **Dual Engine** | Google Cloud Translation API (live) with automatic mock fallback |
|  **SQLite Logging** | Every request is persisted with latency, engine, and client metadata |
|  **Bulk Endpoint** | Translate up to 50 sentences in a single request |
|  **Health Check** | Liveness probe reporting DB status and active engine |
|  **Modular** | Clean architecture — routes, services, models, database, utils, config |

---

## Project Structure

```
udaan-translation-microservice/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory, middleware, exception handlers
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic BaseSettings (env vars / .env file)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic request/response schemas
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py               # GET /health, GET /info
│   │   ├── translate.py            # POST /translate, POST /translate/bulk
│   │   └── logs.py                 # GET /logs, GET /logs/{id}
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── translation_service.py  # Orchestration: engine selection & fallback
│   │   ├── google_translator.py    # Google Cloud Translation API adapter
│   │   └── mock_translator.py      # Built-in phrase dictionary (13 languages)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # SQLAlchemy engine, session factory, Base
│   │   ├── models.py               # ORM model: TranslationLog
│   │   └── repository.py           # Data-access layer (CRUD operations)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Coloured console logging setup
│       └── helpers.py              # UUID generation, timing, language name map
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures (in-memory SQLite)
│   ├── test_health.py
│   └── test_translate.py
│
├── main.py                         # Entry point: python main.py
├── requirements.txt
├── .env.example                    # Environment variable template
├── .gitignore
└── README.md
```

---

##  Quick Start

### 1. Clone / enter the project directory

```bash
cd "Project udaan translation microservice"
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional)

```bash
# Copy the template
cp .env.example .env
```

Edit `.env` to set your **Google API Key** (leave blank to use the mock engine):

```env
GOOGLE_API_KEY=AIzaSy...   # optional — leave empty for mock mode
DEBUG=False
PORT=8000
```

### 5. Run the server

```bash
# Option A — via uvicorn directly (recommended for production)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option B — via the convenience wrapper
python main.py

# Option C — with hot-reload during development
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**

---

##  API Endpoints

### Base URL: `http://localhost:8000`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message & links |
| `GET` | `/health` | Liveness / readiness probe |
| `GET` | `/info` | Service metadata & supported languages |
| `POST` | `/translate` | Translate a single text |
| `POST` | `/translate/bulk` | Translate multiple texts in one request |
| `GET` | `/logs` | List translation logs (paginated) |
| `GET` | `/logs/{id}` | Get a specific log entry |
| `GET` | `/docs` | Swagger UI (interactive API docs) |
| `GET` | `/redoc` | ReDoc documentation |

---

## 🌍 Supported Languages

| ISO Code | Language |
|----------|----------|
| `hi` | Hindi |
| `ta` | Tamil |
| `kn` | Kannada |
| `bn` | Bengali |
| `te` | Telugu |
| `mr` | Marathi |
| `gu` | Gujarati |
| `ml` | Malayalam |
| `pa` | Punjabi |
| `ur` | Urdu |
| `or` | Odia |
| `as` | Assamese |
| `fr` | French |
| `de` | German |
| `es` | Spanish |

---

##  Request & Response Reference

### `POST /translate`

**Request body:**

```json
{
  "text": "Hello, how are you?",
  "target_language": "hi",
  "source_language": "en"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `text` | string | ✅ | 1–1000 characters, non-blank |
| `target_language` | string | ✅ | Valid ISO 639-1 code |
| `source_language` | string | ❌ | ISO 639-1 code, defaults to `"auto"` |

**Response:**

```json
{
  "success": true,
  "original_text": "Hello, how are you?",
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi",
  "engine": "mock",
  "characters_translated": 19
}
```

---

### `POST /translate/bulk`

**Request body:**

```json
{
  "texts": ["Good morning", "Thank you", "How are you?"],
  "target_language": "ta",
  "source_language": "en"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| `texts` | array of strings | 1–50 items, each 1–1000 chars |
| `target_language` | string | Valid ISO 639-1 code |
| `source_language` | string | Optional, defaults to `"auto"` |

**Response:**

```json
{
  "success": true,
  "target_language": "ta",
  "source_language": "en",
  "engine": "mock",
  "total": 3,
  "succeeded": 3,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "original_text": "Good morning",
      "translated_text": "காலை வணக்கம்",
      "success": true,
      "error": null
    },
    {
      "index": 1,
      "original_text": "Thank you",
      "translated_text": "நன்றி",
      "success": true,
      "error": null
    },
    {
      "index": 2,
      "original_text": "How are you?",
      "translated_text": "நீங்கள் எப்படி இருக்கிறீர்கள்?",
      "success": true,
      "error": null
    }
  ]
}
```

---

### `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "app_name": "Udaan Translation Microservice",
  "version": "1.0.0",
  "translation_engine": "mock",
  "database": "connected",
  "timestamp": "2024-07-08T10:00:00.000000+00:00"
}
```

---

## 🔧 cURL Examples

### Health check
```bash
curl -X GET http://localhost:8000/health
```

### Single translation — Hindi
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "target_language": "hi"}'
```

### Single translation — Tamil
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "good morning", "target_language": "ta", "source_language": "en"}'
```

### Single translation — Kannada
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "thank you", "target_language": "kn"}'
```

### Bulk translation
```bash
curl -X POST http://localhost:8000/translate/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Good morning", "Thank you", "How are you?", "Sorry"],
    "target_language": "bn"
  }'
```

### View translation logs
```bash
curl -X GET "http://localhost:8000/logs?limit=10&target_language=hi"
```

### Get a specific log entry
```bash
curl -X GET http://localhost:8000/logs/1
```

### Service info
```bash
curl -X GET http://localhost:8000/info
```

---

##  Postman Collection

Import the following JSON into Postman (**File → Import → Raw Text**):

```json
{
  "info": {
    "name": "Udaan Translation Microservice",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    },
    {
      "name": "Service Info",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/info"
      }
    },
    {
      "name": "Translate Single (Hindi)",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/translate",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"text\": \"Hello, how are you?\", \"target_language\": \"hi\", \"source_language\": \"en\"}"
        }
      }
    },
    {
      "name": "Translate Single (Tamil)",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/translate",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"text\": \"good morning\", \"target_language\": \"ta\"}"
        }
      }
    },
    {
      "name": "Translate Bulk",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/translate/bulk",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"texts\": [\"Good morning\", \"Thank you\", \"How are you?\"], \"target_language\": \"bn\"}"
        }
      }
    },
    {
      "name": "List Logs",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/logs?limit=10&skip=0",
          "query": [
            {"key": "limit", "value": "10"},
            {"key": "skip", "value": "0"}
          ]
        }
      }
    }
  ]
}
```

---

##  Running Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

##  Enabling Google Translate (Live Mode)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **Cloud Translation API**
3. Create an **API Key** under _Credentials_
4. Set it in your `.env` file:
   ```env
   GOOGLE_API_KEY=AIzaSy...
   ```
5. Uncomment `google-cloud-translate` in `requirements.txt` and reinstall:
   ```bash
   pip install google-cloud-translate
   ```

The service auto-detects the key on startup and switches to the Google engine.

---

##  Configuration Reference

All settings can be set via environment variables or the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Udaan Translation Microservice` | Display name |
| `APP_VERSION` | `1.0.0` | Version string |
| `DEBUG` | `False` | Enable debug logging & SQL echo |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listening port |
| `GOOGLE_API_KEY` | _(empty)_ | Google Cloud API key (blank = mock mode) |
| `DATABASE_URL` | `sqlite:///./udaan_logs.db` | SQLAlchemy DB URL |
| `MAX_TEXT_LENGTH` | `1000` | Max characters per single translate request |
| `MAX_BULK_SENTENCES` | `50` | Max items per bulk request |

---

##  Error Handling

The API returns structured JSON errors for all failure cases:

| HTTP Code | Scenario |
|-----------|----------|
| `400` | Unsupported language / translation engine error |
| `404` | Log entry not found |
| `422` | Pydantic validation failure (missing fields, bad types, constraints) |
| `500` | Unexpected internal server error |

**Example error response:**
```json
{
  "success": false,
  "error": "Language 'xx' is not supported.",
  "detail": null
}
```

---

##  Database Schema

The SQLite database stores one row per translated text:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `request_id` | TEXT | UUID shared across a bulk request |
| `original_text` | TEXT | Input text |
| `translated_text` | TEXT | Output text |
| `source_language` | TEXT | Source language code |
| `target_language` | TEXT | Target language code |
| `engine` | TEXT | `google` or `mock` |
| `success` | BOOLEAN | Whether translation succeeded |
| `error_message` | TEXT | Error detail (nullable) |
| `characters` | INTEGER | Character count of input |
| `latency_ms` | REAL | Translation latency in milliseconds |
| `is_bulk` | BOOLEAN | True for bulk endpoint requests |
| `created_at` | DATETIME | UTC timestamp |
| `client_host` | TEXT | IP address of the caller |

---

##  License

MIT — use freely, contribute back!
