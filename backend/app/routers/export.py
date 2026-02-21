from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..excel_exporter import ExcelExporter
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/export/{run_id}")
def export_schedule(run_id: int, institution_name: str = "Campus Scheduling System", db: Session = Depends(get_db)):
    """
    Export a schedule run to Excel with three views:
    1. Teacher View - Schedule per teacher with gaps
    2. Section View - Schedule per course/section
    3. Room View - Schedule by room and building
    4. Checklist - Validation of all input data
    
    Args:
        run_id: Schedule run ID
        institution_name: Name of institution (for headers)
    
    Returns:
        Excel file with all views
    """
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    
    try:
        exporter = ExcelExporter(db)
        excel_bytes = exporter.export_schedule(run_id, institution_name)
        
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=schedule_{run_id}_{models.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")