from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
import xlsxwriter
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/export/{run_id}")
def export_schedule(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Schedule run not found")
    
    entries = db.query(models.ScheduleEntry).filter(models.ScheduleEntry.schedule_run_id == run_id).all()
    
    # Create workbook
    bio = BytesIO()
    workbook = xlsxwriter.Workbook(bio)
    
    # Schedule sheet
    worksheet = workbook.add_worksheet('Schedule')
    worksheet.write('A1', 'Teacher')
    worksheet.write('B1', 'Section')
    worksheet.write('C1', 'Course')
    worksheet.write('D1', 'Room')
    worksheet.write('E1', 'Day')
    worksheet.write('F1', 'Start')
    worksheet.write('G1', 'End')
    
    row = 1
    for entry in entries:
        color = entry.course.color_map.hex_color if entry.course.color_map else '#FFFFFF'
        format = workbook.add_format({'bg_color': color})
        worksheet.write(row, 0, entry.teacher.full_name, format)
        worksheet.write(row, 1, entry.section.code, format)
        worksheet.write(row, 2, entry.course.course_name, format)
        worksheet.write(row, 3, entry.room.room_code, format)
        worksheet.write(row, 4, entry.timeslot.day_of_week.value, format)
        worksheet.write(row, 5, entry.timeslot.start_time, format)
        worksheet.write(row, 6, entry.timeslot.end_time, format)
        row += 1
    
    # Teachers sheet
    teachers_ws = workbook.add_worksheet('Teachers')
    teachers_ws.write('A1', 'Name')
    teachers_ws.write('B1', 'Title')
    teachers_ws.write('C1', 'Status')
    teachers_ws.write('D1', 'Workload')
    teachers_ws.write('E1', 'Senior')
    teachers = db.query(models.Teacher).all()
    row = 1
    for teacher in teachers:
        teachers_ws.write(row, 0, teacher.full_name)
        teachers_ws.write(row, 1, teacher.title.value)
        teachers_ws.write(row, 2, teacher.status.value)
        teachers_ws.write(row, 3, teacher.workload.value)
        teachers_ws.write(row, 4, 'Yes' if teacher.is_senior_old else 'No')
        row += 1
    
    # Sections sheet
    sections_ws = workbook.add_worksheet('Sections')
    sections_ws.write('A1', 'Code')
    sections_ws.write('B1', 'Year Level')
    sections_ws.write('C1', 'First Year')
    sections = db.query(models.Section).all()
    row = 1
    for section in sections:
        sections_ws.write(row, 0, section.code)
        sections_ws.write(row, 1, section.year_level)
        sections_ws.write(row, 2, 'Yes' if section.is_first_year else 'No')
        row += 1
    
    # Rooms sheet
    rooms_ws = workbook.add_worksheet('Rooms')
    rooms_ws.write('A1', 'Code')
    rooms_ws.write('B1', 'Building')
    rooms_ws.write('C1', 'Type')
    rooms_ws.write('D1', 'Capacity')
    rooms = db.query(models.Room).all()
    row = 1
    for room in rooms:
        rooms_ws.write(row, 0, room.room_code)
        rooms_ws.write(row, 1, room.building.name)
        rooms_ws.write(row, 2, room.room_type.value)
        rooms_ws.write(row, 3, room.capacity)
        row += 1
    
    workbook.close()
    bio.seek(0)
    
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=schedule_{run_id}.xlsx"})