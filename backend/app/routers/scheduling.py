from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..solver import run_solver

router = APIRouter()

@router.post("/schedule-runs/", response_model=schemas.ScheduleRun)
def create_schedule_run(schedule_run: schemas.ScheduleRunCreate, db: Session = Depends(get_db)):
    db_run = models.ScheduleRun(**schedule_run.dict())
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

@router.get("/schedule-runs/", response_model=list[schemas.ScheduleRun])
def read_schedule_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(models.ScheduleRun).offset(skip).limit(limit).all()
    return runs

@router.post("/schedule-runs/{run_id}/run-solver")
def run_schedule_solver(run_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    
    # Update status to RUNNING
    run.status = models.ScheduleRunStatus.RUNNING
    db.commit()
    
    # Run solver in background
    background_tasks.add_task(run_solver, run_id, db)
    
    return {"message": "Solver started"}

@router.get("/schedule-entries/", response_model=list[schemas.ScheduleEntry])
def read_schedule_entries(run_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.ScheduleEntry)
    if run_id:
        query = query.filter(models.ScheduleEntry.schedule_run_id == run_id)
    entries = query.all()
    return entries