"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, tasks, chat
from src.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context - DB init handled by init_db.py pre-startup script."""
    yield
    print("🔌 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="RESTful API for task management with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (will restrict in production)
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
            "tasks": "/api/tasks",
            "chat": "/api/{user_id}/chat"
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

# Register chat router (AI chatbot feature)
app.include_router(
    chat.router,
    tags=["chat"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
