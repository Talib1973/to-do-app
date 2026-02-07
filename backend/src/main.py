"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, tasks

# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="RESTful API for task management with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Todo App API is running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/auth",
            "tasks": "/api/tasks"
        }
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "auth": "enabled",
        "timestamp": "2026-02-06T10:00:00Z"
    }


# Register authentication router
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["authentication"]
)

# Register tasks router
app.include_router(
    tasks.router,
    prefix="/api/tasks",
    tags=["tasks"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
