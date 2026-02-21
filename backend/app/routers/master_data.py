from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

# Buildings
@router.post("/buildings/", response_model=schemas.Building)
def create_building(building: schemas.BuildingCreate, db: Session = Depends(get_db)):
    db_building = models.Building(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

@router.get("/buildings/", response_model=list[schemas.Building])
def read_buildings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    buildings = db.query(models.Building).offset(skip).limit(limit).all()
    return buildings

# Rooms
@router.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/rooms/", response_model=list[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = db.query(models.Room).offset(skip).limit(limit).all()
    return rooms

# Teachers
@router.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = models.Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.get("/teachers/", response_model=list[schemas.Teacher])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers

# Sections
@router.post("/sections/", response_model=schemas.Section)
def create_section(section: schemas.SectionCreate, db: Session = Depends(get_db)):
    db_section = models.Section(**section.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.get("/sections/", response_model=list[schemas.Section])
def read_sections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sections = db.query(models.Section).offset(skip).limit(limit).all()
    return sections

# Courses
@router.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/courses/", response_model=list[schemas.Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses

# Timeslots
@router.post("/timeslots/", response_model=schemas.Timeslot)
def create_timeslot(timeslot: schemas.TimeslotCreate, db: Session = Depends(get_db)):
    db_timeslot = models.Timeslot(**timeslot.dict())
    db.add(db_timeslot)
    db.commit()
    db.refresh(db_timeslot)
    return db_timeslot

@router.get("/timeslots/", response_model=list[schemas.Timeslot])
def read_timeslots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    timeslots = db.query(models.Timeslot).offset(skip).limit(limit).all()
    return timeslots