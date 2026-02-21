from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

# ============================================================================
# BUILDINGS
# ============================================================================

@router.post("/buildings/", response_model=schemas.Building, tags=["Buildings"])
def create_building(building: schemas.BuildingCreate, db: Session = Depends(get_db)):
    """Create a new building."""
    db_building = models.Building(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

@router.get("/buildings/", response_model=list[schemas.Building], tags=["Buildings"])
def read_buildings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all buildings with pagination."""
    buildings = db.query(models.Building).offset(skip).limit(limit).all()
    return buildings

@router.get("/buildings/{building_id}", response_model=schemas.Building, tags=["Buildings"])
def read_building(building_id: int, db: Session = Depends(get_db)):
    """Get a specific building by ID."""
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@router.put("/buildings/{building_id}", response_model=schemas.Building, tags=["Buildings"])
def update_building(building_id: int, building: schemas.BuildingCreate, db: Session = Depends(get_db)):
    """Update a building."""
    db_building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not db_building:
        raise HTTPException(status_code=404, detail="Building not found")
    for key, value in building.dict().items():
        setattr(db_building, key, value)
    db.commit()
    db.refresh(db_building)
    return db_building

@router.delete("/buildings/{building_id}", tags=["Buildings"])
def delete_building(building_id: int, db: Session = Depends(get_db)):
    """Delete a building."""
    db_building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not db_building:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(db_building)
    db.commit()
    return {"detail": "Building deleted"}

# ============================================================================
# ROOMS
# ============================================================================

@router.post("/rooms/", response_model=schemas.Room, tags=["Rooms"])
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """Create a new room."""
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/rooms/", response_model=list[schemas.Room], tags=["Rooms"])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all rooms with pagination."""
    rooms = db.query(models.Room).offset(skip).limit(limit).all()
    return rooms

@router.get("/rooms/{room_id}", response_model=schemas.Room, tags=["Rooms"])
def read_room(room_id: int, db: Session = Depends(get_db)):
    """Get a specific room by ID."""
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/rooms/{room_id}", response_model=schemas.Room, tags=["Rooms"])
def update_room(room_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """Update a room."""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    for key, value in room.dict().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/rooms/{room_id}", tags=["Rooms"])
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """Delete a room."""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(db_room)
    db.commit()
    return {"detail": "Room deleted"}

# ============================================================================
# TEACHERS
# ============================================================================

@router.post("/teachers/", response_model=schemas.Teacher, tags=["Teachers"])
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher."""
    db_teacher = models.Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.get("/teachers/", response_model=list[schemas.Teacher], tags=["Teachers"])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all teachers with pagination."""
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers

@router.get("/teachers/{teacher_id}", response_model=schemas.Teacher, tags=["Teachers"])
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get a specific teacher by ID."""
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/teachers/{teacher_id}", response_model=schemas.Teacher, tags=["Teachers"])
def update_teacher(teacher_id: int, teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """Update a teacher."""
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for key, value in teacher.dict().items():
        setattr(db_teacher, key, value)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.delete("/teachers/{teacher_id}", tags=["Teachers"])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Delete a teacher."""
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(db_teacher)
    db.commit()
    return {"detail": "Teacher deleted"}

# ============================================================================
# SECTIONS
# ============================================================================

@router.post("/sections/", response_model=schemas.Section, tags=["Sections"])
def create_section(section: schemas.SectionCreate, db: Session = Depends(get_db)):
    """Create a new section."""
    db_section = models.Section(**section.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.get("/sections/", response_model=list[schemas.Section], tags=["Sections"])
def read_sections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sections with pagination."""
    sections = db.query(models.Section).offset(skip).limit(limit).all()
    return sections

@router.get("/sections/{section_id}", response_model=schemas.Section, tags=["Sections"])
def read_section(section_id: int, db: Session = Depends(get_db)):
    """Get a specific section by ID."""
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.put("/sections/{section_id}", response_model=schemas.Section, tags=["Sections"])
def update_section(section_id: int, section: schemas.SectionCreate, db: Session = Depends(get_db)):
    """Update a section."""
    db_section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    for key, value in section.dict().items():
        setattr(db_section, key, value)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.delete("/sections/{section_id}", tags=["Sections"])
def delete_section(section_id: int, db: Session = Depends(get_db)):
    """Delete a section."""
    db_section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    db.delete(db_section)
    db.commit()
    return {"detail": "Section deleted"}

# ============================================================================
# COURSES
# ============================================================================

@router.post("/courses/", response_model=schemas.Course, tags=["Courses"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/courses/", response_model=list[schemas.Course], tags=["Courses"])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all courses with pagination."""
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses

@router.get("/courses/{course_id}", response_model=schemas.Course, tags=["Courses"])
def read_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/courses/{course_id}", response_model=schemas.Course, tags=["Courses"])
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Update a course."""
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in course.dict().items():
        setattr(db_course, key, value)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/courses/{course_id}", tags=["Courses"])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course."""
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return {"detail": "Course deleted"}

# ============================================================================
# TIMESLOTS
# ============================================================================

@router.post("/timeslots/", response_model=schemas.Timeslot, tags=["Timeslots"])
def create_timeslot(timeslot: schemas.TimeslotCreate, db: Session = Depends(get_db)):
    """Create a new timeslot."""
    db_timeslot = models.Timeslot(**timeslot.dict())
    db.add(db_timeslot)
    db.commit()
    db.refresh(db_timeslot)
    return db_timeslot

@router.get("/timeslots/", response_model=list[schemas.Timeslot], tags=["Timeslots"])
def read_timeslots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all timeslots with pagination."""
    timeslots = db.query(models.Timeslot).offset(skip).limit(limit).all()
    return timeslots

@router.get("/timeslots/{timeslot_id}", response_model=schemas.Timeslot, tags=["Timeslots"])
def read_timeslot(timeslot_id: int, db: Session = Depends(get_db)):
    """Get a specific timeslot by ID."""
    timeslot = db.query(models.Timeslot).filter(models.Timeslot.id == timeslot_id).first()
    if not timeslot:
        raise HTTPException(status_code=404, detail="Timeslot not found")
    return timeslot

@router.put("/timeslots/{timeslot_id}", response_model=schemas.Timeslot, tags=["Timeslots"])
def update_timeslot(timeslot_id: int, timeslot: schemas.TimeslotCreate, db: Session = Depends(get_db)):
    """Update a timeslot."""
    db_timeslot = db.query(models.Timeslot).filter(models.Timeslot.id == timeslot_id).first()
    if not db_timeslot:
        raise HTTPException(status_code=404, detail="Timeslot not found")
    for key, value in timeslot.dict().items():
        setattr(db_timeslot, key, value)
    db.commit()
    db.refresh(db_timeslot)
    return db_timeslot

@router.delete("/timeslots/{timeslot_id}", tags=["Timeslots"])
def delete_timeslot(timeslot_id: int, db: Session = Depends(get_db)):
    """Delete a timeslot."""
    db_timeslot = db.query(models.Timeslot).filter(models.Timeslot.id == timeslot_id).first()
    if not db_timeslot:
        raise HTTPException(status_code=404, detail="Timeslot not found")
    db.delete(db_timeslot)
    db.commit()
    return {"detail": "Timeslot deleted"}