import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.rate_limiter import SimpleRateLimiterMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.api.routes import auth, enquiries, leads, quotations, followups, dashboard, reports, admin, pricing, public_chat, settings as settings_router

logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Attach Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimiterMiddleware, max_requests=60, window_seconds=60)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Error Handler: Suppresses stack traces and internal secrets in production
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    if settings.ENVIRONMENT.lower() == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred. Please try again later."}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )

# Mount Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(enquiries.router, prefix=settings.API_V1_STR)
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(quotations.router, prefix=settings.API_V1_STR)
app.include_router(followups.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(pricing.router, prefix=settings.API_V1_STR)
app.include_router(public_chat.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    from app.services.emergency_stop import is_emergency_stop_active
    from app.models.all_models import SystemHealth
    
    recent_health = db.query(SystemHealth).order_by(SystemHealth.checked_at.desc()).first()
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": settings.APP_MODE,
        "env": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "emergency_stop_active": is_emergency_stop_active(db),
        "worker_health": recent_health.status if recent_health else "active"
    }

@app.get("/ready")
def ready_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        dialect = db.bind.dialect.name if db.bind else "unknown"
        return {"status": "ready", "database": "connected", "database_dialect": dialect}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}

@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    from app.models.all_models import Lead, AgentTask
    total_leads = db.query(Lead).count()
    failed_tasks = db.query(AgentTask).filter(AgentTask.status == "FAILED").count()
    return {
        "active_mode": settings.APP_MODE,
        "demo_mode": settings.DEMO_MODE,
        "spending_limit_daily": settings.DAILY_SPENDING_LIMIT,
        "spending_limit_monthly": settings.MONTHLY_SPENDING_LIMIT,
        "total_leads_processed": total_leads,
        "failed_tasks_count": failed_tasks
    }
