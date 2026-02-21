from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric, Enum, Text, func
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class RoomType(enum.Enum):
    STANDARD = "STANDARD"
    LAB = "LAB"
    SHOP = "SHOP"
    SCIENCE_LAB = "SCIENCE_LAB"

class TeacherTitle(enum.Enum):
    INSTRUCTOR_I = "INSTRUCTOR_I"
    INSTRUCTOR_II = "INSTRUCTOR_II"
    ASST_PROF_III = "ASST_PROF_III"
    ASST_PROF_IV = "ASST_PROF_IV"
    ASSOC_PROF_V = "ASSOC_PROF_V"

class TeacherStatus(enum.Enum):
    CONTRACT_OF_SERVICE = "CONTRACT_OF_SERVICE"
    PERMANENT = "PERMANENT"

class Workload(enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    VISITING = "VISITING"

class DayOfWeek(enum.Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"

class BlockSource(enum.Enum):
    MANUAL = "MANUAL"
    AUTO_SATURDAY_COMP_OFF = "AUTO_SATURDAY_COMP_OFF"

class CourseType(enum.Enum):
    STANDARD = "STANDARD"
    LAB = "LAB"
    SHOP = "SHOP"
    SCIENCE_LAB = "SCIENCE_LAB"
    CWATS = "CWATS"

class ScheduleRunStatus(enum.Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)

    rooms = relationship("Room", back_populates="building")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"))
    room_code = Column(String, unique=True, index=True)
    floor_no = Column(Integer)
    room_type = Column(Enum(RoomType))
    capacity = Column(Integer)
    active = Column(Boolean, default=True)

    building = relationship("Building", back_populates="rooms")
    maintenance_blocks = relationship("RoomMaintenanceBlock", back_populates="room")
    schedule_entries = relationship("ScheduleEntry", back_populates="room")

class RoomMaintenanceBlock(Base):
    __tablename__ = "room_maintenance_blocks"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    reason = Column(String)
    created_by = Column(String)

    room = relationship("Room", back_populates="maintenance_blocks")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String, nullable=True)
    full_name = Column(String)
    title = Column(Enum(TeacherTitle))
    status = Column(Enum(TeacherStatus))
    workload = Column(Enum(Workload))
    is_senior_old = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    day_blocks = relationship("TeacherDayBlock", back_populates="teacher")
    teaching_assignments = relationship("TeachingAssignment", back_populates="teacher")
    schedule_entries = relationship("ScheduleEntry", back_populates="teacher")

class TeacherDayBlock(Base):
    __tablename__ = "teacher_day_blocks"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    day_of_week = Column(Enum(DayOfWeek))
    is_blocked = Column(Boolean, default=False)
    source = Column(Enum(BlockSource), default=BlockSource.MANUAL)

    teacher = relationship("Teacher", back_populates="day_blocks")

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    year_level = Column(Integer)
    is_first_year = Column(Boolean, default=False)

    teaching_assignments = relationship("TeachingAssignment", back_populates="section")
    schedule_entries = relationship("ScheduleEntry", back_populates="section")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String)
    units = Column(Numeric(precision=3, scale=1))
    course_type = Column(Enum(CourseType))
    default_duration_minutes = Column(Integer)

    teaching_assignments = relationship("TeachingAssignment", back_populates="course")
    schedule_entries = relationship("ScheduleEntry", back_populates="course")
    color_map = relationship("SubjectColorMap", back_populates="course", uselist=False)

class TeachingAssignment(Base):
    __tablename__ = "teaching_assignments"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    term_id = Column(Integer)  # Assuming term is an integer ID

    teacher = relationship("Teacher", back_populates="teaching_assignments")
    section = relationship("Section", back_populates="teaching_assignments")
    course = relationship("Course", back_populates="teaching_assignments")

class Timeslot(Base):
    __tablename__ = "timeslots"
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Enum(DayOfWeek))
    start_time = Column(String)  # e.g., "07:30"
    end_time = Column(String)    # e.g., "10:30"
    is_cwats_slot = Column(Boolean, default=False)

    schedule_entries = relationship("ScheduleEntry", back_populates="timeslot")

class ScheduleRun(Base):
    __tablename__ = "schedule_runs"
    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer)
    status = Column(Enum(ScheduleRunStatus), default=ScheduleRunStatus.DRAFT)
    objective_score = Column(Numeric(precision=10, scale=2), nullable=True)
    created_by = Column(String)
    created_at = Column(DateTime, default=func.now)

    schedule_entries = relationship("ScheduleEntry", back_populates="schedule_run")

class ScheduleEntry(Base):
    __tablename__ = "schedule_entries"
    id = Column(Integer, primary_key=True, index=True)
    schedule_run_id = Column(Integer, ForeignKey("schedule_runs.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    timeslot_id = Column(Integer, ForeignKey("timeslots.id"))
    is_locked = Column(Boolean, default=False)

    schedule_run = relationship("ScheduleRun", back_populates="schedule_entries")
    teacher = relationship("Teacher", back_populates="schedule_entries")
    section = relationship("Section", back_populates="schedule_entries")
    course = relationship("Course", back_populates="schedule_entries")
    room = relationship("Room", back_populates="schedule_entries")
    timeslot = relationship("Timeslot", back_populates="schedule_entries")

class SubjectColorMap(Base):
    __tablename__ = "subject_color_map"
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    hex_color = Column(String)

    course = relationship("Course", back_populates="color_map")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(String)
    action_type = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    payload_json = Column(Text)
    created_at = Column(DateTime, default=func.now)