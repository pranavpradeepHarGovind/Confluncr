from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1 import api_v1_router
from app.api.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Production-quality Account & Transaction Management System API.\n\n"
        "Features:\n"
        "- Strict financial data integrity with NUMERIC(18, 2) decimal arithmetic.\n"
        "- Atomic credit/debit transactions with PostgreSQL row-level locking (`FOR UPDATE`).\n"
        "- Immutable transaction log with unique per-account reference IDs.\n"
        "- Deadlock-free atomic transfers between accounts.\n"
        "- Paginated latest-first transaction history.\n"
        "- Standardized, consistent JSON error responses."
    ),
    openapi_tags=[
        {"name": "Accounts", "description": "Account creation, balance lookup, and transactions"},
        {"name": "Transactions", "description": "Direct transaction processing with row locking"},
        {"name": "Transfers", "description": "Atomic cross-account fund transfers"},
    ],
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
register_exception_handlers(app)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
