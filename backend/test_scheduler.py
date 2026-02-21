#!/usr/bin/env python
"""
Test script for Phase 7: Scheduling Algorithm

This script tests the complete scheduling workflow:
1. Create a schedule run
2. Add teaching assignments
3. Run the scheduler
4. Verify the generated schedule
5. Check constraint violations
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.scheduler import CampusScheduler
from app.constraints import ConstraintEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_test_data(db: Session):
    """Create test data for scheduling."""
    logger.info("Setting up test data...")
    
    # Create buildings
    bldg_a = models.Building(code="A", name="Building A")
    bldg_b = models.Building(code="B", name="Building B")
    db.add(bldg_a)
    db.add(bldg_b)
    db.flush()
    
    # Create rooms
    rooms = [
        models.Room(
            building_id=bldg_a.id,
            room_code="A101",
            floor_no=1,
            room_type=models.RoomType.STANDARD,
            capacity=30,
            active=True
        ),
        models.Room(
            building_id=bldg_a.id,
            room_code="A103",
            floor_no=1,
            room_type=models.RoomType.LAB,
            capacity=25,
            active=True
        ),
        models.Room(
            building_id=bldg_b.id,
            room_code="B201",
            floor_no=2,
            room_type=models.RoomType.SHOP,
            capacity=20,
            active=True
        ),
    ]
    db.add_all(rooms)
    db.flush()
    
    # Create teachers with various classifications
    teachers = [
        models.Teacher(
            employee_no="T001",
            full_name="Dr. John Smith",
            title=models.TeacherTitle.INSTRUCTOR_I,
            status=models.TeacherStatus.PERMANENT,
            workload=models.Workload.FULL_TIME,
            is_senior_old=True,
            active=True
        ),
        models.Teacher(
            employee_no="T002",
            full_name="Ms. Jane Doe",
            title=models.TeacherTitle.ASST_PROF_III,
            status=models.TeacherStatus.CONTRACT_OF_SERVICE,
            workload=models.Workload.FULL_TIME,
            is_senior_old=False,
            active=True
        ),
        models.Teacher(
            employee_no="T003",
            full_name="Mr. James Wilson",
            title=models.TeacherTitle.INSTRUCTOR_II,
            status=models.TeacherStatus.PERMANENT,
            workload=models.Workload.PART_TIME,
            is_senior_old=False,
            active=True
        ),
    ]
    db.add_all(teachers)
    db.flush()
    
    # Create sections (student groups)
    sections = [
        models.Section(code="BS-CS-1A", year_level=1, is_first_year=True),
        models.Section(code="BS-CS-2B", year_level=2, is_first_year=False),
        models.Section(code="BS-CE-1C", year_level=1, is_first_year=True),
    ]
    db.add_all(sections)
    db.flush()
    
    # Create courses
    courses = [
        models.Course(
            course_code="CS101",
            course_name="Introduction to Programming",
            units=3.0,
            course_type=models.CourseType.STANDARD,
            default_duration_minutes=90
        ),
        models.Course(
            course_code="CS201",
            course_name="Data Structures Lab",
            units=2.0,
            course_type=models.CourseType.LAB,
            default_duration_minutes=180
        ),
        models.Course(
            course_code="CE101",
            course_name="Engineering Workshop",
            units=2.0,
            course_type=models.CourseType.SHOP,
            default_duration_minutes=180
        ),
    ]
    db.add_all(courses)
    db.flush()
    
    # Create timeslots (Morning and afternoon sessions)
    timeslots = [
        # Monday morning
        models.Timeslot(day_of_week=models.DayOfWeek.MON, start_time="07:30", end_time="10:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.MON, start_time="10:30", end_time="13:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.MON, start_time="14:30", end_time="17:30", is_cwats_slot=False),
        # Tuesday morning
        models.Timeslot(day_of_week=models.DayOfWeek.TUE, start_time="07:30", end_time="10:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.TUE, start_time="10:30", end_time="13:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.TUE, start_time="14:30", end_time="17:30", is_cwats_slot=False),
        # Wednesday
        models.Timeslot(day_of_week=models.DayOfWeek.WED, start_time="07:30", end_time="10:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.WED, start_time="10:30", end_time="13:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.WED, start_time="14:30", end_time="17:30", is_cwats_slot=False),
        # Thursday
        models.Timeslot(day_of_week=models.DayOfWeek.THU, start_time="07:30", end_time="10:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.THU, start_time="10:30", end_time="13:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.THU, start_time="14:30", end_time="17:30", is_cwats_slot=False),
        # Friday
        models.Timeslot(day_of_week=models.DayOfWeek.FRI, start_time="07:30", end_time="10:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.FRI, start_time="10:30", end_time="13:30", is_cwats_slot=False),
        models.Timeslot(day_of_week=models.DayOfWeek.FRI, start_time="14:30", end_time="17:30", is_cwats_slot=False),
        # Saturday (CWATS - for first-year students only)
        models.Timeslot(day_of_week=models.DayOfWeek.SAT, start_time="07:30", end_time="10:30", is_cwats_slot=True),
        models.Timeslot(day_of_week=models.DayOfWeek.SAT, start_time="10:30", end_time="13:30", is_cwats_slot=True),
    ]
    db.add_all(timeslots)
    db.flush()
    
    # Create teaching assignments (term 1)
    term_id = 1
    assignments = [
        models.TeachingAssignment(
            teacher_id=teachers[0].id,
            section_id=sections[0].id,
            course_id=courses[0].id,
            term_id=term_id
        ),
        models.TeachingAssignment(
            teacher_id=teachers[1].id,
            section_id=sections[1].id,
            course_id=courses[1].id,
            term_id=term_id
        ),
        models.TeachingAssignment(
            teacher_id=teachers[2].id,
            section_id=sections[2].id,
            course_id=courses[2].id,
            term_id=term_id
        ),
    ]
    db.add_all(assignments)
    db.commit()
    
    logger.info(f"✅ Test data created: {len(teachers)} teachers, {len(sections)} sections, {len(courses)} courses, {len(timeslots)} timeslots")
    return {
        "term_id": term_id,
        "teachers": teachers,
        "sections": sections,
        "courses": courses,
        "rooms": rooms,
        "timeslots": timeslots,
    }


def test_constraint_engine(db: Session):
    """Test the constraint engine with sample data."""
    logger.info("\n" + "="*80)
    logger.info("TESTING CONSTRAINT ENGINE")
    logger.info("="*80)
    
    engine_instance = ConstraintEngine(db)
    
    # Get sample data
    teacher = db.query(models.Teacher).first()
    course = db.query(models.Course).first()
    section = db.query(models.Section).first()
    timeslot = db.query(models.Timeslot).first()
    room = db.query(models.Room).first()
    
    if all([teacher, course, section, timeslot, room]):
        is_valid, violations = engine_instance.validate_timeslot_for_assignment(
            teacher=teacher,
            course=course,
            section=section,
            timeslot=timeslot,
            room=room
        )
        
        logger.info(f"Teacher: {teacher.full_name}")
        logger.info(f"Course: {course.course_code} ({course.course_type.value})")
        logger.info(f"Section: {section.code}")
        logger.info(f"Timeslot: {timeslot.day_of_week.value} {timeslot.start_time}-{timeslot.end_time}")
        logger.info(f"Room: {room.room_code}")
        logger.info(f"Valid: {is_valid}")
        logger.info(f"Violations: {len(violations)}")
        for violation in violations:
            logger.info(f"  - {violation}")
    else:
        logger.error("Missing sample data for constraint engine test")


def test_scheduler(db: Session, test_data: dict):
    """Test the scheduling algorithm."""
    logger.info("\n" + "="*80)
    logger.info("TESTING SCHEDULING ALGORITHM")
    logger.info("="*80)
    
    term_id = test_data["term_id"]
    
    # Create a schedule run
    schedule_run = models.ScheduleRun(
        term_id=term_id,
        status=models.ScheduleRunStatus.DRAFT,
        created_by="TEST",
        created_at=datetime.now()
    )
    db.add(schedule_run)
    db.commit()
    
    logger.info(f"Created schedule run {schedule_run.id} for term {term_id}")
    
    # Run the scheduler
    scheduler = CampusScheduler(db)
    success, message = scheduler.generate_schedule(schedule_run, term_id, prioritize_senior=True)
    
    logger.info(f"Scheduler result: {success}")
    logger.info(f"Message: {message}")
    
    # Get results
    entries = db.query(models.ScheduleEntry).filter(
        models.ScheduleEntry.schedule_run_id == schedule_run.id
    ).all()
    
    logger.info(f"\n✅ Generated {len(entries)} schedule entries:")
    for i, entry in enumerate(entries, 1):
        teacher = entry.teacher
        course = entry.course
        section = entry.section
        room = entry.room
        timeslot = entry.timeslot
        
        logger.info(f"  {i}. {teacher.full_name} teaches {course.course_code}")
        logger.info(f"     Section: {section.code}, Room: {room.room_code}")
        logger.info(f"     Time: {timeslot.day_of_week.value} {timeslot.start_time}-{timeslot.end_time}")
    
    # Get violations report
    violations_report = scheduler.get_violations_report()
    logger.info(f"\nViolations Report:")
    logger.info(f"  Hard violations: {violations_report['total_hard']}")
    logger.info(f"  Soft violations: {violations_report['total_soft']}")
    logger.info(f"  Objective score: {violations_report['objective_score']:.2f}")
    
    return schedule_run


def main():
    """Main test function."""
    logger.info("Starting Phase 7 Scheduling Algorithm Test")
    logger.info("="*80)
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Setup test data
        test_data = setup_test_data(db)
        
        # Test constraint engine
        test_constraint_engine(db)
        
        # Test scheduler
        schedule_run = test_scheduler(db, test_data)
        
        logger.info("\n" + "="*80)
        logger.info("✅ PHASE 7 TEST COMPLETE")
        logger.info("="*80)
        logger.info(f"Schedule Run Status: {schedule_run.status.value}")
        logger.info(f"Schedule Run ID: {schedule_run.id}")
        logger.info(f"Objective Score: {schedule_run.objective_score}")
        
    except Exception as e:
        logger.exception(f"Test failed: {str(e)}")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
