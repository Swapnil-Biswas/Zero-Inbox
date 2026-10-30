# ZERO-INBOX: Production Deployment Guide

This guide details local execution, Docker orchestration, and cloud deployment options for ZERO-INBOX.

---

## 1. Local Python & Node Execution

### Backend Setup
```bash
cd zero-inbox/backend
pip install -r requirements.txt
python run_server.py
```
*Backend runs on `http://127.0.0.1:8010` (Swagger UI at `/docs`).*

### Frontend Setup
```bash
cd zero-inbox/frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5174`.*

---

## 2. Docker Compose Deployment

```bash
cd zero-inbox/docker
docker-compose up -d --build
```
- Backend: `http://localhost:8010`
- Frontend: `http://localhost:3000`

---

## 3. Persistent Storage

ZERO-INBOX uses an SQLite WAL database for job idempotency, article deduplication, and user preferences. Ensure the data directory (`data/`) is mounted on a persistent storage volume when deploying in containerized environments.

