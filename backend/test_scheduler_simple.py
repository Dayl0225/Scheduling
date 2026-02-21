#!/usr/bin/env python
"""
Simple test of scheduling algorithm with compatible data.
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.scheduler import CampusScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create tables
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # Clear existing data
    db.query(models.ScheduleEntry).delete()
    db.query(models.TeachingAssignment).delete()
    db.query(models.Timeslot).delete()
    db.query(models.Course).delete()
    db.query(models.Section).delete()
    db.query(models.Teacher).delete()
    db.query(models.Room).delete()
    db.query(models.Building).delete()
    db.query(models.ScheduleRun).delete()
    db.commit()
    
    logger.info("Creating test data...")
    
    # Building & Rooms (all STANDARD)
    bldg = models.Building(code="A", name="Building A")
    db.add(bldg)
    db.flush()
    
    rooms = [
        models.Room(building_id=bldg.id, room_code="A101", floor_no=1, room_type=models.RoomType.STANDARD, capacity=30),
        models.Room(building_id=bldg.id, room_code="A102", floor_no=1, room_type=models.RoomType.STANDARD, capacity=30),
        models.Room(building_id=bldg.id, room_code="A103", floor_no=1, room_type=models.RoomType.STANDARD, capacity=30),
    ]
    db.add_all(rooms)
    db.flush()
    
    # Teachers
    teachers = [
        models.Teacher(employee_no="T001", full_name="Teacher A", title=models.TeacherTitle.INSTRUCTOR_I,
                      status=models.TeacherStatus.PERMANENT, workload=models.Workload.FULL_TIME, is_senior_old=False),
        models.Teacher(employee_no="T002", full_name="Teacher B", title=models.TeacherTitle.INSTRUCTOR_II,
                      status=models.TeacherStatus.CONTRACT_OF_SERVICE, workload=models.Workload.FULL_TIME, is_senior_old=False),
    ]
    db.add_all(teachers)
    db.flush()
    
    # Sections
    sections = [
        models.Section(code="BS-CS-1A", year_level=1, is_first_year=True),
        models.Section(code="BS-CS-2B", year_level=2, is_first_year=False),
    ]
    db.add_all(sections)
    db.flush()
    
    # Courses (all STANDARD)
    courses = [
        models.Course(course_code="CS101", course_name="Programming", units=3.0,
                     course_type=models.CourseType.STANDARD, default_duration_minutes=90),
        models.Course(course_code="CS102", course_name="Databases", units=3.0,
                     course_type=models.CourseType.STANDARD, default_duration_minutes=90),
    ]
    db.add_all(courses)
    db.flush()
    
    # Timeslots
    timeslots = [
        models.Timeslot(day_of_week=models.DayOfWeek.MON, start_time="07:30", end_time="10:30"),
        models.Timeslot(day_of_week=models.DayOfWeek.MON, start_time="10:30", end_time="13:30"),
        models.Timeslot(day_of_week=models.DayOfWeek.TUE, start_time="07:30", end_time="10:30"),
        models.Timeslot(day_of_week=models.DayOfWeek.TUE, start_time="10:30", end_time="13:30"),
        models.Timeslot(day_of_week=models.DayOfWeek.WED, start_time="07:30", end_time="10:30"),
        models.Timeslot(day_of_week=models.DayOfWeek.WED, start_time="10:30", end_time="13:30"),
    ]
    db.add_all(timeslots)
    db.flush()
    
    # Teaching assignments
    assignments = [
        models.TeachingAssignment(teacher_id=teachers[0].id, section_id=sections[0].id, course_id=courses[0].id, term_id=1),
        models.TeachingAssignment(teacher_id=teachers[1].id, section_id=sections[1].id, course_id=courses[1].id, term_id=1),
    ]
    db.add_all(assignments)
    db.commit()
    
    # Create schedule run
    schedule_run = models.ScheduleRun(term_id=1, status=models.ScheduleRunStatus.DRAFT, created_by="TEST", created_at=datetime.now())
    db.add(schedule_run)
    db.commit()
    
    logger.info(f"Test data created. Running scheduler for run {schedule_run.id}...")
    
    # Run scheduler
    scheduler = CampusScheduler(db)
    success, message = scheduler.generate_schedule(schedule_run, term_id=1, prioritize_senior=True)
    
    logger.info(f"Success: {success}")
    logger.info(f"Message: {message}")
    
    # Show results
    entries = db.query(models.ScheduleEntry).filter(models.ScheduleEntry.schedule_run_id == schedule_run.id).all()
    logger.info(f"\n✅ Generated {len(entries)} assignments:")
    for entry in entries:
        logger.info(f"  - {entry.teacher.full_name} ({entry.course.course_code}) -> {entry.room.room_code} / {entry.timeslot.day_of_week.value} {entry.timeslot.start_time}")
    
    # Show violations
    report = scheduler.get_violations_report()
    logger.info(f"\nViolations: Hard={report['total_hard']}, Soft={report['total_soft']}, Score={report['objective_score']:.1f}")
    
finally:
    db.close()
