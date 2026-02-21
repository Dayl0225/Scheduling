from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import master_data, scheduling, export, audit

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Campus Scheduling System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(master_data.router, prefix="/api/master-data", tags=["Master Data"])
app.include_router(scheduling.router, prefix="/api/scheduling", tags=["Scheduling"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])

@app.get("/")
def read_root():
    return {"message": "Campus Automated Scheduling System API"}