from pydantic import BaseModel
from typing import Optional
from .models import RoomType, TeacherTitle, TeacherStatus, Workload, DayOfWeek, BlockSource, CourseType, ScheduleRunStatus
from datetime import datetime

# Buildings
class BuildingBase(BaseModel):
    code: str
    name: str

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True

# Rooms
class RoomBase(BaseModel):
    building_id: int
    room_code: str
    floor_no: int
    room_type: RoomType
    capacity: int
    active: bool = True

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    building: Building

    class Config:
        from_attributes = True

# Teachers
class TeacherBase(BaseModel):
    employee_no: Optional[str] = None
    full_name: str
    title: TeacherTitle
    status: TeacherStatus
    workload: Workload
    is_senior_old: bool = False
    active: bool = True

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int

    class Config:
        from_attributes = True

# Sections
class SectionBase(BaseModel):
    code: str
    year_level: int
    is_first_year: bool = False

class SectionCreate(SectionBase):
    pass

class Section(SectionBase):
    id: int

    class Config:
        from_attributes = True

# Courses
class CourseBase(BaseModel):
    course_code: str
    course_name: str
    units: float
    course_type: CourseType
    default_duration_minutes: int

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int

    class Config:
        from_attributes = True

# Timeslots
class TimeslotBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: str
    end_time: str
    is_cwats_slot: bool = False

class TimeslotCreate(TimeslotBase):
    pass

class Timeslot(TimeslotBase):
    id: int

    class Config:
        from_attributes = True

# Schedule Runs
class ScheduleRunBase(BaseModel):
    term_id: int
    status: ScheduleRunStatus = ScheduleRunStatus.DRAFT
    objective_score: Optional[float] = None
    created_by: str

class ScheduleRunCreate(ScheduleRunBase):
    pass

class ScheduleRun(ScheduleRunBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schedule Entries
class ScheduleEntryBase(BaseModel):
    schedule_run_id: int
    teacher_id: int
    section_id: int
    course_id: int
    room_id: int
    timeslot_id: int
    is_locked: bool = False

class ScheduleEntryCreate(ScheduleEntryBase):
    pass

class ScheduleEntry(ScheduleEntryBase):
    id: int

    class Config:
        from_attributes = True

# Audit Logs
class AuditLogBase(BaseModel):
    actor_id: str
    action_type: str
    entity_type: str
    entity_id: int
    payload_json: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True