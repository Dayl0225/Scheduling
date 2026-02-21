from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from .. import models, schemas
from ..scheduler import CampusScheduler
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ScheduleGenerationRequest(BaseModel):
    """Request to generate a schedule."""
    term_id: int
    prioritize_senior: bool = True


class ScheduleGenerationResponse(BaseModel):
    """Response from schedule generation."""
    run_id: int
    status: str
    message: str
    assignments_count: int = 0
    violations_count: int = 0


@router.post("/schedule-runs/", response_model=schemas.ScheduleRun)
def create_schedule_run(schedule_run: schemas.ScheduleRunCreate, db: Session = Depends(get_db)):
    """Create a new schedule run (draft status)."""
    from datetime import datetime
    db_run = models.ScheduleRun(
        term_id=schedule_run.term_id,
        status=schedule_run.status,
        objective_score=schedule_run.objective_score,
        created_by=schedule_run.created_by,
        created_at=datetime.now()
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    logger.info(f"Created schedule run {db_run.id} for term {db_run.term_id}")
    return db_run


@router.get("/schedule-runs/", response_model=list[schemas.ScheduleRun])
def read_schedule_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all schedule runs with pagination."""
    runs = db.query(models.ScheduleRun).offset(skip).limit(limit).all()
    return runs


@router.get("/schedule-runs/{run_id}", response_model=schemas.ScheduleRun)
def read_schedule_run(run_id: int, db: Session = Depends(get_db)):
    """Get details of a specific schedule run."""
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    return run


@router.post("/schedule-runs/{run_id}/generate")
def generate_schedule(
    run_id: int,
    request: ScheduleGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ScheduleGenerationResponse:
    """
    Trigger schedule generation for a term.
    
    This endpoint:
    1. Creates a new ScheduleRun
    2. Starts the scheduling algorithm in the background
    3. Returns immediately with the run ID
    
    The algorithm will:
    - Load all teachers, courses, sections, rooms, timeslots
    - Apply hard and soft constraints
    - Generate valid schedule assignments
    - Save results to the database
    
    Args:
        run_id: The schedule run ID
        request: Generation request with term_id and prioritize_senior
        background_tasks: FastAPI background task handler
        db: Database session
    
    Returns:
        ScheduleGenerationResponse with status and run_id
    """
    # Validate schedule run exists
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    
    # Check if term_id in request matches the run's term
    if run.term_id != request.term_id:
        raise HTTPException(
            status_code=400,
            detail=f"Term mismatch: run is for term {run.term_id}, request is for {request.term_id}"
        )
    
    # Verify there are teaching assignments for this term
    assignment_count = db.query(models.TeachingAssignment).filter(
        models.TeachingAssignment.term_id == request.term_id
    ).count()
    
    if assignment_count == 0:
        raise HTTPException(
            status_code=400,
            detail=f"No teaching assignments found for term {request.term_id}"
        )
    
    # Update run status to RUNNING
    run.status = models.ScheduleRunStatus.RUNNING
    db.commit()
    
    logger.info(f"Starting schedule generation for run {run_id}, term {request.term_id}")
    
    # Start the scheduler in the background
    background_tasks.add_task(
        _run_scheduler_task,
        run_id,
        request.term_id,
        request.prioritize_senior
    )
    
    return ScheduleGenerationResponse(
        run_id=run_id,
        status="RUNNING",
        message=f"Schedule generation started for {assignment_count} teaching assignments",
        assignments_count=assignment_count
    )


def _run_scheduler_task(run_id: int, term_id: int, prioritize_senior: bool) -> None:
    """
    Background task to run the scheduler.
    
    This is executed asynchronously so the HTTP endpoint can return immediately.
    """
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
        if not run:
            logger.error(f"Schedule run {run_id} not found")
            return
        
        scheduler = CampusScheduler(db)
        success, message = scheduler.generate_schedule(run, term_id, prioritize_senior)
        
        if success:
            logger.info(f"Schedule generation successful for run {run_id}: {message}")
        else:
            logger.error(f"Schedule generation failed for run {run_id}: {message}")
    
    except Exception as e:
        logger.exception(f"Unexpected error in schedule generation task: {str(e)}")
    
    finally:
        db.close()


@router.get("/schedule-runs/{run_id}/violations")
def get_schedule_violations(run_id: int, db: Session = Depends(get_db)):
    """Get constraint violations report for a schedule run."""
    from ..scheduler import CampusScheduler
    
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    
    # Query violations from schedule entries (any entries that exist)
    entries = db.query(models.ScheduleEntry).filter(
        models.ScheduleEntry.schedule_run_id == run_id
    ).all()
    
    return {
        "run_id": run_id,
        "status": run.status.value,
        "total_entries": len(entries),
        "objective_score": float(run.objective_score) if run.objective_score else 0,
        "message": "Violation report available after schedule generation"
    }


@router.get("/schedule-entries/", response_model=list[schemas.ScheduleEntry])
def read_schedule_entries(run_id: int = None, db: Session = Depends(get_db)):
    """
    Get schedule entries (actual assignments) for a run.
    
    Args:
        run_id: Filter by specific schedule run (optional)
    
    Returns:
        List of schedule entries
    """
    query = db.query(models.ScheduleEntry)
    if run_id:
        query = query.filter(models.ScheduleEntry.schedule_run_id == run_id)
    entries = query.all()
    return entries


@router.get("/schedule-entries/{entry_id}", response_model=schemas.ScheduleEntry)
def read_schedule_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific schedule entry."""
    entry = db.query(models.ScheduleEntry).filter(models.ScheduleEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
    return entry