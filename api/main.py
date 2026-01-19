"""
FastAPI REST API for Medley Lease Analysis & Management System

Provides programmatic access to:
- RAG query engine
- Lease database
- Financial analytics
- Expiration tracking
- Portfolio insights
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.search.query_engine import QueryEngine
from src.database.sql_store import SQLStore
from src.analytics.lease_analytics import LeaseAnalytics
from config.settings import Settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medley Lease Analysis & Management API",
    description="REST API for lease document analysis, financial analytics, and portfolio management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
settings = Settings()
query_engine = QueryEngine(settings)
sql_store = SQLStore()
analytics = LeaseAnalytics(sql_store)


# ==================== Request/Response Models ====================

class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., description="Natural language question about leases")
    tenant_filter: Optional[str] = Field(None, description="Filter results to specific tenant")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return", ge=1, le=20)


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    answer: str
    sources: List[Dict[str, Any]]
    query_time_ms: float
    result_count: int


class LeaseCreate(BaseModel):
    """Request model for creating a lease."""
    tenant_name: str
    lease_file: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    term_months: Optional[int] = None
    square_footage: Optional[float] = None
    base_rent: Optional[float] = None
    rent_frequency: Optional[str] = "monthly"
    security_deposit: Optional[float] = None
    renewal_options: Optional[str] = None
    special_provisions: Optional[str] = None


class LeaseUpdate(BaseModel):
    """Request model for updating a lease."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    base_rent: Optional[float] = None
    status: Optional[str] = None


class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    timestamp: str
    services: Dict[str, str]


# ==================== Health & Info Endpoints ====================

@app.get("/", tags=["Info"])
async def root():
    """API root endpoint."""
    return {
        "name": "Medley Lease Analysis & Management API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "query": "/api/query",
            "leases": "/api/leases",
            "analytics": "/api/analytics",
            "alerts": "/api/alerts"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_engine": "operational",
            "database": "operational",
            "analytics": "operational"
        }
    }


# ==================== RAG Query Endpoints ====================

@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
async def query_leases(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Query lease documents using natural language.

    Supports questions like:
    - "What is Summit Coffee's monthly rent?"
    - "Which leases expire in 2025?"
    - "Compare rent rates for cafe tenants"
    """
    try:
        start_time = datetime.now()

        # Execute RAG query
        result = query_engine.query(
            question=request.question,
            tenant_filter=request.tenant_filter,
            max_results=request.max_results
        )

        end_time = datetime.now()
        query_time_ms = (end_time - start_time).total_seconds() * 1000

        # Log query in background
        background_tasks.add_task(
            sql_store.log_query,
            request.question,
            request.tenant_filter,
            len(result['sources']),
            query_time_ms
        )

        return {
            "answer": result['answer'],
            "sources": result['sources'],
            "query_time_ms": round(query_time_ms, 2),
            "result_count": len(result['sources'])
        }

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/api/query/popular", tags=["Query"])
async def get_popular_queries(limit: int = Query(10, ge=1, le=50)):
    """Get most frequently asked questions."""
    try:
        popular = sql_store.get_popular_queries(limit=limit)
        return {"queries": popular, "count": len(popular)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Lease Management Endpoints ====================

@app.get("/api/leases", tags=["Leases"])
async def get_all_leases(status: Optional[str] = Query(None, description="Filter by status")):
    """Get all leases, optionally filtered by status."""
    try:
        leases = sql_store.get_all_leases(status=status)
        return {"leases": leases, "count": len(leases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leases/{lease_id}", tags=["Leases"])
async def get_lease(lease_id: int):
    """Get lease details by ID."""
    try:
        lease = sql_store.get_lease(lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail=f"Lease {lease_id} not found")
        return lease
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leases", tags=["Leases"])
async def create_lease(lease: LeaseCreate):
    """Create a new lease."""
    try:
        lease_id = sql_store.add_lease(
            tenant_name=lease.tenant_name,
            lease_file=lease.lease_file,
            start_date=lease.start_date,
            end_date=lease.end_date,
            term_months=lease.term_months,
            square_footage=lease.square_footage,
            base_rent=lease.base_rent,
            rent_frequency=lease.rent_frequency,
            security_deposit=lease.security_deposit,
            renewal_options=lease.renewal_options,
            special_provisions=lease.special_provisions
        )
        return {"lease_id": lease_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/leases/{lease_id}", tags=["Leases"])
async def update_lease(lease_id: int, update: LeaseUpdate):
    """Update lease information."""
    try:
        # Build update dict excluding None values
        update_data = {k: v for k, v in update.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        success = sql_store.update_lease(lease_id, **update_data)

        if not success:
            raise HTTPException(status_code=404, detail=f"Lease {lease_id} not found")

        return {"lease_id": lease_id, "status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leases/tenant/{tenant_name}", tags=["Leases"])
async def get_leases_by_tenant(tenant_name: str):
    """Get all leases for a specific tenant."""
    try:
        leases = sql_store.get_leases_by_tenant(tenant_name)
        return {"tenant": tenant_name, "leases": leases, "count": len(leases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Tenants Endpoints ====================

@app.get("/api/tenants", tags=["Tenants"])
async def get_all_tenants():
    """Get all tenants."""
    try:
        tenants = sql_store.get_all_tenants()
        return {"tenants": tenants, "count": len(tenants)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tenants/{tenant_name}", tags=["Tenants"])
async def get_tenant(tenant_name: str):
    """Get tenant information."""
    try:
        tenant = sql_store.get_tenant(tenant_name)
        if not tenant:
            raise HTTPException(status_code=404, detail=f"Tenant '{tenant_name}' not found")
        return tenant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Analytics Endpoints ====================

@app.get("/api/analytics/summary", tags=["Analytics"])
async def get_financial_summary():
    """Get overall financial summary."""
    try:
        summary = sql_store.get_financial_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/revenue-projection", tags=["Analytics"])
async def get_revenue_projection(months: int = Query(12, ge=1, le=36)):
    """Get revenue projections for the next N months."""
    try:
        projection = analytics.project_revenue(months_ahead=months)
        return projection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/portfolio-health", tags=["Analytics"])
async def get_portfolio_health():
    """Calculate portfolio health score and recommendations."""
    try:
        health = analytics.calculate_portfolio_health_score()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/risk-assessment", tags=["Analytics"])
async def get_risk_assessment():
    """Assess portfolio risks."""
    try:
        risk = analytics.assess_portfolio_risk()
        return risk
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/benchmarks", tags=["Analytics"])
async def get_benchmarks():
    """Get tenant benchmarks across portfolio."""
    try:
        benchmarks = analytics.get_tenant_benchmarks()
        return benchmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/optimization", tags=["Analytics"])
async def get_optimization_opportunities():
    """Get rent optimization opportunities."""
    try:
        opportunities = analytics.get_optimization_opportunities()
        return {"opportunities": opportunities, "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/expiration-timeline", tags=["Analytics"])
async def get_expiration_timeline(months: int = Query(24, ge=1, le=60)):
    """Get lease expiration timeline."""
    try:
        timeline = analytics.analyze_expiration_timeline(months_ahead=months)
        return timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/compare-tenants", tags=["Analytics"])
async def compare_tenants(tenant_names: List[str]):
    """Compare multiple tenants across key metrics."""
    try:
        if not tenant_names or len(tenant_names) < 2:
            raise HTTPException(status_code=400, detail="Provide at least 2 tenant names")

        comparison = analytics.compare_tenants(tenant_names)
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/lease-value/{lease_id}", tags=["Analytics"])
async def get_lease_value(lease_id: int):
    """Calculate total value metrics for a lease."""
    try:
        value = analytics.calculate_lease_value(lease_id)
        if not value:
            raise HTTPException(status_code=404, detail=f"Lease {lease_id} not found")
        return value
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Alerts Endpoints ====================

@app.get("/api/alerts", tags=["Alerts"])
async def get_active_alerts(days_ahead: int = Query(30, ge=0, le=365)):
    """Get active lease alerts for the next N days."""
    try:
        alerts = sql_store.get_active_alerts(days_ahead=days_ahead)
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/expiring", tags=["Alerts"])
async def get_expiring_leases(days_ahead: int = Query(90, ge=0, le=365)):
    """Get leases expiring within the next N days."""
    try:
        expiring = sql_store.get_expiring_leases(days_ahead=days_ahead)
        return {"leases": expiring, "count": len(expiring)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alerts/{alert_id}/dismiss", tags=["Alerts"])
async def dismiss_alert(alert_id: int):
    """Dismiss an alert."""
    try:
        sql_store.dismiss_alert(alert_id)
        return {"alert_id": alert_id, "status": "dismissed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
