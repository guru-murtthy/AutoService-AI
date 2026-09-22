# AutoService AI - Deployment Guide

## Overview
- **Frontend**: Vercel / Netlify / Cloudflare Pages compatible
- **Backend**: Render / Railway / Fly.io / AWS ECS compatible
- **Database**: Supabase / Neon / PostgreSQL compatible

## Docker Deployment

Build and start all services locally or in production:
```bash
docker compose up -d --build
```

Health check endpoints:
- Backend Health: `http://localhost:8000/health`
- Backend Ready: `http://localhost:8000/ready`
- Dashboard UI: `http://localhost:3000`
