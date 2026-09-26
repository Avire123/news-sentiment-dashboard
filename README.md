# 📰 News Sentiment Monitor

A real-time, end-to-end data pipeline that ingests RSS news feeds, performs sentiment analysis using VADER NLP, stores normalized records in SQLite/PostgreSQL, and serves interactive telemetry through a Streamlit dashboard and FastAPI REST endpoints.

---

## 🏛️ High-Level Architecture

```plaintext
                                +-----------------------------+
                                | News APIs / RSS Feed Seeds  |
                                +--------------+--------------+
                                               |
                                               v
+-----------------------+       +--------------+--------------+
| Scheduler / Cron      | ----> | Ingestion & Deduplication   |
| (APScheduler / Loop)  |       | (requests / BeautifulSoup)  |
+-----------------------+       +--------------+--------------+
                                               |
                                               v
                                +--------------+--------------+
                                | NLP & Sentiment Engine      |
                                | (VADER Sentiment Analysis)  |
                                +--------------+--------------+
                                               |
                                               v
                                +--------------+--------------+
                                | Relational Database          |
                                | (SQLite / PostgreSQL)       |
                                +--------------+--------------+
                                               |
                                +--------------+--------------+
                                |                             |
                                v                             v
                 +--------------+--------------+ +------------+----------------+
                 | Streamlit Live Dashboard    | | FastAPI REST Endpoints         |
                 | (Charts, Filters, Feed)     | | (/api/v1/articles, etc.)     |
                 +-----------------------------+ +------------------------------+
```

---

## 📁 Repository Structure

```plaintext
news-sentiment-dashboard/
├── config/
│   ├── settings.py           # Database paths, timeouts, and execution parameters
│   └── seeds.json            # Target RSS feed URLs and category definitions
├── data/
│   └── app_database.db       # Persistent SQLite database storage
├── src/
│   ├── __init__.py
│   ├── ingest.py             # Resilient RSS fetcher with exponential backoff
│   ├── transform.py          # Text cleaning and VADER sentiment scoring logic
│   ├── db.py                 # SQLAlchemy ORM schema and atomic UPSERT operations
│   └── utils.py              # Structured logging and UTC date parsing helpers
├── app.py                    # Streamlit interactive analytics dashboard
├── main.py                   # FastAPI REST service and OpenAPI endpoint documentation
├── scheduler.py              # Background job orchestrator (runs ETL periodically)
├── Dockerfile                # Single-container execution setup
├── docker-compose.yml        # Multi-service container orchestration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- Git Bash / Terminal

### 2. Clone Repository & Setup Environment
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/news-sentiment-dashboard.git
cd news-sentiment-dashboard

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Pipeline Components

Open separate terminal sessions with the virtual environment activated to run each component:

#### **A. Background ETL Scheduler**
Triggers an immediate fetch cycle and schedules pipeline runs every 15 minutes:
```bash
python scheduler.py
```

#### **B. Streamlit Live Dashboard**
Launches the web UI at `http://localhost:8501`:
```bash
streamlit run app.py
```

#### **C. FastAPI REST Service**
Launches the REST API server at `http://127.0.0.1:8000`:
```bash
uvicorn main:app --reload
```
* Access interactive Swagger API documentation at: **`http://127.0.0.1:8000/docs`**

---

## 🐳 Docker Deployment

To spin up all services simultaneously with Docker Compose:

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | GET | API Health Status |
| `/api/v1/articles` | GET | Retrieve processed articles (Filters: `category`, `sentiment`, `limit`) |
| `/api/v1/summary` | GET | Aggregate metrics on total articles and positive/neutral/negative ratios |