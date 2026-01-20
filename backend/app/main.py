from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import diaries
from app.core.firebase import initialize_firebase

# Initialize Firebase
initialize_firebase()

app = FastAPI(
    title="AI Diary API",
    description="Backend API for AI-powered diary application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diaries.router, prefix="/diaries", tags=["diaries"])

@app.get("/")
async def root():
    return {
        "message": "AI Diary API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

