# AutoService AI - Production PostgreSQL Database Guide

## Overview
AutoService AI supports dual persistence:
- **SQLite**: Local single-file development & testing (`sqlite:///./autoservice.db`).
- **PostgreSQL**: Production persistent relational database via `DATABASE_URL=postgresql://user:password@host:5432/dbname`.

---

## 1. Connection Pooling & Configuration
In `backend/app/core/database.py`, connection pooling for PostgreSQL is managed using SQLAlchemy's `QueuePool`:
- `pool_size`: 10 persistent connections
- `max_overflow`: 20 connections
- `pool_pre_ping`: True (verifies connection health before handing to requests)

---

## 2. Database Migrations (Alembic)

Before starting the backend in production (`ENVIRONMENT=production`), run Alembic migrations:
```bash
source backend/venv/bin/activate
cd backend
alembic upgrade head
```

To create a new migration script when modifying models:
```bash
alembic revision --autogenerate -m "Add new business fields"
```

To rollback the last migration:
```bash
alembic downgrade -1
```

---

## 3. Database Health Check Endpoint
- **URL**: `GET /ready`
- **Behavior**: Executes a lightweight `SELECT 1` query to verify active connection pool health.
- **Sample Output**:
```json
{
  "status": "ready",
  "database": "connected",
  "database_dialect": "postgresql"
}
```

---

## 4. Automated Backup Recommendation
For production PostgreSQL (e.g. Supabase, Neon, AWS RDS, Managed Postgres):
- **Daily Automated Snapshots**: Retain 30 days of daily backups.
- **Manual Backup**:
```bash
pg_dump -U postgres_user -h postgres-host autoservice_prod > backup_$(date +%Y%m%d).sql
```
