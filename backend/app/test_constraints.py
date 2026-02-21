"""
Test and demonstration of the Constraint Engine.

This shows how to use the constraint validation engine with real scenarios.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.constraints import ConstraintEngine


def demonstrate_constraint_checks(db: Session):
    """
    Demonstrates constraint engine usage with sample data.
    """
    
    # Initialize constraint engine
    engine = ConstraintEngine(db)
    
    print("\n" + "="*80)
    print("CONSTRAINT ENGINE DEMONSTRATION")
    print("="*80)
    
    # ========== SCENARIO 1: Check Room Type Matching ==========
    print("\n[SCENARIO 1] Room Type Matching Constraint")
    print("-" * 80)
    
    # Get sample data (assumes data exists in DB)
    lab_course = db.query(models.Course).filter(
        models.Course.course_type == models.CourseType.LAB
    ).first()
    
    standard_room = db.query(models.Room).filter(
        models.Room.room_type == models.RoomType.STANDARD
    ).first()
    
    teacher = db.query(models.Teacher).first()
    section = db.query(models.Section).first()
    timeslot = db.query(models.Timeslot).first()
    
    if lab_course and standard_room and teacher and section and timeslot:
        print(f"Testing: {teacher.full_name} teaches {lab_course.course_code} (LAB)")
        print(f"         in {standard_room.room_code} (STANDARD room)")
        print(f"         at {timeslot.start_time}-{timeslot.end_time}")
        
        is_valid, violations = engine.validate_timeslot_for_assignment(
            teacher, lab_course, section, timeslot, standard_room
        )
        
        print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'}")
        for v in violations:
            print(f"  {v}")
    
    # ========== SCENARIO 2: Check Time Limit Constraint ==========
    print("\n[SCENARIO 2] Time Limit Constraint (Permanent + Full-Time)")
    print("-" * 80)
    
    permanent_ft_teacher = db.query(models.Teacher).filter(
        models.Teacher.status == models.TeacherStatus.PERMANENT,
        models.Teacher.workload == models.Workload.FULL_TIME
    ).first()
    
    late_timeslot = db.query(models.Timeslot).filter(
        models.Timeslot.end_time > "16:00"  # After 3:30 PM limit
    ).first()
    
    if permanent_ft_teacher and late_timeslot:
        standard_course = db.query(models.Course).filter(
            models.Course.course_type == models.CourseType.STANDARD
        ).first()
        
        if standard_course:
            print(f"Testing: {permanent_ft_teacher.full_name} (Permanent + Full-Time)")
            print(f"         Teaching at {late_timeslot.start_time}-{late_timeslot.end_time}")
            print(f"         Time limit for this classification: 3:30 PM")
            
            is_valid, violations = engine.validate_timeslot_for_assignment(
                permanent_ft_teacher, standard_course, section, late_timeslot, standard_room
            )
            
            print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'}")
            for v in violations:
                print(f"  {v}")
    
    # ========== SCENARIO 3: Check Teacher Lunch Break ==========
    print("\n[SCENARIO 3] Teacher Lunch Break Constraint")
    print("-" * 80)
    
    lunch_conflict_timeslot = db.query(models.Timeslot).filter(
        models.Timeslot.start_time >= "11:00",
        models.Timeslot.start_time <= "12:30"
    ).first()
    
    if lunch_conflict_timeslot and teacher and standard_course:
        print(f"Testing: {teacher.full_name}")
        print(f"         Teaching at {lunch_conflict_timeslot.start_time}-{lunch_conflict_timeslot.end_time}")
        print(f"         Potential lunch break conflict")
        
        is_valid, violations = engine.validate_timeslot_for_assignment(
            teacher, standard_course, section, lunch_conflict_timeslot, standard_room
        )
        
        print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'}")
        for v in violations:
            print(f"  {v}")
    
    # ========== SCENARIO 4: Check 1st Year CWATS Vacancy ==========
    print("\n[SCENARIO 4] 1st Year CWATS Saturday Vacancy Constraint")
    print("-" * 80)
    
    first_year_section = db.query(models.Section).filter(
        models.Section.is_first_year == True
    ).first()
    
    cwats_timeslot = db.query(models.Timeslot).filter(
        models.Timeslot.day_of_week == models.DayOfWeek.SAT,
        models.Timeslot.is_cwats_slot == True
    ).first()
    
    if first_year_section and cwats_timeslot and teacher and standard_course:
        print(f"Testing: 1st-year section {first_year_section.code}")
        print(f"         Teaching at {cwats_timeslot.start_time}-{cwats_timeslot.end_time} on Saturday")
        print(f"         CWATS slot: {cwats_timeslot.is_cwats_slot}")
        
        is_valid, violations = engine.validate_timeslot_for_assignment(
            teacher, standard_course, first_year_section, cwats_timeslot, standard_room
        )
        
        print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'}")
        for v in violations:
            print(f"  {v}")
    
    # ========== SCENARIO 5: Senior Teacher Priority (Soft Constraint) ==========
    print("\n[SCENARIO 5] Senior Teacher Priority (Soft Constraint)")
    print("-" * 80)
    
    senior_teacher = db.query(models.Teacher).filter(
        models.Teacher.is_senior_old == True
    ).first()
    
    non_senior_room = db.query(models.Room).filter(
        models.Room.room_code.notin_(["A103", "A104", "A203"])
    ).first()
    
    if senior_teacher and non_senior_room and standard_course and timeslot:
        print(f"Testing: {senior_teacher.full_name} (Senior Teacher)")
        print(f"         Assigned to room: {non_senior_room.room_code}")
        print(f"         Preferred rooms: A103, A104, A203")
        
        is_valid, violations = engine.validate_timeslot_for_assignment(
            senior_teacher, standard_course, section, timeslot, non_senior_room
        )
        
        print(f"\nResult: {'✓ VALID' if is_valid else '✗ INVALID'} (hard constraints)")
        
        hard_vios = [v for v in violations if v.constraint_type == "HARD"]
        soft_vios = [v for v in violations if v.constraint_type == "SOFT"]
        
        print(f"Hard Violations: {len(hard_vios)}")
        for v in hard_vios:
            print(f"  {v}")
        
        print(f"\nSoft Violations (preferences): {len(soft_vios)}")
        for v in soft_vios:
            print(f"  {v}")
    
    # ========== SCENARIO 6: Find Valid Timeslots ==========
    print("\n[SCENARIO 6] Find Valid Timeslots for Assignment")
    print("-" * 80)
    
    if teacher and standard_course and section:
        print(f"Finding valid timeslots for:")
        print(f"  Teacher: {teacher.full_name}")
        print(f"  Course: {standard_course.course_code}")
        print(f"  Section: {section.code}")
        
        valid_combinations = engine.find_valid_timeslots(
            teacher, standard_course, section
        )
        
        if valid_combinations:
            print(f"\nFound {len(valid_combinations)} valid timeslot combinations:")
            for i, (timeslot, rooms) in enumerate(list(valid_combinations.items())[:5], 1):
                print(f"  {i}. {timeslot.day_of_week.value} {timeslot.start_time}-{timeslot.end_time}")
                print(f"     Available rooms: {', '.join([r.room_code for r in rooms[:3]])}")
        else:
            print("\nNo valid timeslots found for this assignment.")
    
    print("\n" + "="*80)
    print("END OF DEMONSTRATION")
    print("="*80 + "\n")


# Usage in API endpoint
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.constraints import ConstraintEngine

router = APIRouter()

@router.post("/validate-assignment")
def validate_assignment(
    teacher_id: int,
    course_id: int,
    section_id: int,
    timeslot_id: int,
    room_id: int,
    db: Session = Depends(get_db)
):
    '''Validate if an assignment is valid given all constraints.'''
    
    teacher = db.query(models.Teacher).get(teacher_id)
    course = db.query(models.Course).get(course_id)
    section = db.query(models.Section).get(section_id)
    timeslot = db.query(models.Timeslot).get(timeslot_id)
    room = db.query(models.Room).get(room_id)
    
    if not all([teacher, course, section, timeslot, room]):
        return {"error": "Invalid IDs"}
    
    engine = ConstraintEngine(db)
    is_valid, violations = engine.validate_timeslot_for_assignment(
        teacher, course, section, timeslot, room
    )
    
    return {
        "is_valid": is_valid,
        "hard_violations": [
            {"message": v.message} for v in violations if v.constraint_type == "HARD"
        ],
        "soft_violations": [
            {"message": v.message} for v in violations if v.constraint_type == "SOFT"
        ]
    }

@router.get("/find-valid-slots")
def find_valid_slots(
    teacher_id: int,
    course_id: int,
    section_id: int,
    db: Session = Depends(get_db)
):
    '''Find all valid timeslot-room combinations.'''
    
    teacher = db.query(models.Teacher).get(teacher_id)
    course = db.query(models.Course).get(course_id)
    section = db.query(models.Section).get(section_id)
    
    if not all([teacher, course, section]):
        return {"error": "Invalid IDs"}
    
    engine = ConstraintEngine(db)
    valid_combinations = engine.find_valid_timeslots(teacher, course, section)
    
    return {
        "valid_combinations": [
            {
                "timeslot": {
                    "id": ts.id,
                    "day": ts.day_of_week.value,
                    "start_time": ts.start_time,
                    "end_time": ts.end_time,
                    "is_cwats_slot": ts.is_cwats_slot
                },
                "rooms": [{"id": r.id, "code": r.room_code, "capacity": r.capacity} for r in rooms]
            }
            for ts, rooms in valid_combinations.items()
        ]
    }
"""
