from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from . import models
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def run_solver(run_id: int, db: Session):
    # Load data
    run = db.query(models.ScheduleRun).filter(models.ScheduleRun.id == run_id).first()
    if not run:
        logger.error(f"Schedule run {run_id} not found")
        return
    
    term_id = run.term_id
    
    # Load teaching assignments
    assignments = db.query(models.TeachingAssignment).filter(models.TeachingAssignment.term_id == term_id).all()
    
    # Load timeslots
    timeslots = db.query(models.Timeslot).all()
    
    # Load rooms
    rooms = db.query(models.Room).filter(models.Room.active == True).all()
    
    # Load teachers, sections, courses from assignments
    teachers = {a.teacher_id: a.teacher for a in assignments}
    sections = {a.section_id: a.section for a in assignments}
    courses = {a.course_id: a.course for a in assignments}
    
    # Create model
    model = cp_model.CpModel()
    
    # Variables: for each assignment, room, timeslot
    variables = {}
    for assignment in assignments:
        for room in rooms:
            for timeslot in timeslots:
                var_name = f"assign_{assignment.id}_{room.id}_{timeslot.id}"
                variables[(assignment.id, room.id, timeslot.id)] = model.NewBoolVar(var_name)
    
    # Hard Constraints
    
    # 1. Each assignment must be assigned exactly once
    for assignment in assignments:
        model.Add(sum(variables[(assignment.id, r.id, t.id)] for r in rooms for t in timeslots) == 1)
    
    # 2. No teacher overlap
    for teacher_id in teachers:
        teacher_assignments = [a for a in assignments if a.teacher_id == teacher_id]
        for timeslot in timeslots:
            model.Add(sum(variables[(a.id, r.id, timeslot.id)] for a in teacher_assignments for r in rooms) <= 1)
    
    # 3. No section overlap
    for section_id in sections:
        section_assignments = [a for a in assignments if a.section_id == section_id]
        for timeslot in timeslots:
            model.Add(sum(variables[(a.id, r.id, timeslot.id)] for a in section_assignments for r in rooms) <= 1)
    
    # 4. No room overlap
    for room in rooms:
        for timeslot in timeslots:
            model.Add(sum(variables[(a.id, room.id, timeslot.id)] for a in assignments) <= 1)
    
    # 5. Room type matching
    for assignment in assignments:
        course = courses[assignment.course_id]
        allowed_rooms = [r for r in rooms if r.room_type == course.course_type or course.course_type == models.CourseType.STANDARD]
        for room in rooms:
            if room not in allowed_rooms:
                for timeslot in timeslots:
                    model.Add(variables[(assignment.id, room.id, timeslot.id)] == 0)
    
    # 6. End-of-day limits
    for assignment in assignments:
        teacher = teachers[assignment.teacher_id]
        for timeslot in timeslots:
            end_time = datetime.strptime(timeslot.end_time, "%H:%M")
            if teacher.status == models.TeacherStatus.PERMANENT and teacher.workload == models.Workload.FULL_TIME:
                if end_time > datetime.strptime("15:30", "%H:%M"):
                    for room in rooms:
                        model.Add(variables[(assignment.id, room.id, timeslot.id)] == 0)
            elif teacher.status == models.TeacherStatus.CONTRACT_OF_SERVICE and teacher.workload == models.Workload.FULL_TIME:
                if end_time > datetime.strptime("17:30", "%H:%M"):
                    for room in rooms:
                        model.Add(variables[(assignment.id, room.id, timeslot.id)] == 0)
    
    # 7. Senior teacher room preference (hard for seniors)
    senior_rooms = ["A103", "A104", "A203"]
    for assignment in assignments:
        teacher = teachers[assignment.teacher_id]
        if teacher.is_senior_old:
            allowed_rooms = [r for r in rooms if r.room_code in senior_rooms]
            for room in rooms:
                if room not in allowed_rooms:
                    for timeslot in timeslots:
                        model.Add(variables[(assignment.id, room.id, timeslot.id)] == 0)
    
    # 8. CWATS for first-year sections
    for section_id in sections:
        section = sections[section_id]
        if section.is_first_year:
            cwats_assignments = [a for a in assignments if a.section_id == section_id and courses[a.course_id].course_type == models.CourseType.CWATS]
            cwats_slots = [t for t in timeslots if t.is_cwats_slot and t.day_of_week == models.DayOfWeek.SAT]
            # At least one CWATS slot assigned
            if cwats_assignments:
                model.Add(sum(variables[(a.id, r.id, t.id)] for a in cwats_assignments for r in rooms for t in cwats_slots) >= 1)
    
    # 9. Saturday-Weekday Swap (simplified penalty in objective)
    sat_penalties = []
    for teacher_id in teachers:
        teacher_assignments = [a for a in assignments if a.teacher_id == teacher_id]
        sat_slots = [t for t in timeslots if t.day_of_week == models.DayOfWeek.SAT]
        has_sat = model.NewBoolVar(f"has_sat_{teacher_id}")
        model.Add(has_sat == (sum(variables[(a.id, r.id, t.id)] for a in teacher_assignments for r in rooms for t in sat_slots) > 0))
        # Penalty if has_sat and no full vacant weekday (simplified)
        sat_penalties.append(has_sat * 100)  # High penalty
    
    # 10. Lunch logic (simplified - ensure no classes during lunch)
    lunch_slots = [t for t in timeslots if "11:30" in t.start_time or "14:30" in t.start_time]  # Assuming lunch slots
    for teacher_id in teachers:
        teacher_assignments = [a for a in assignments if a.teacher_id == teacher_id]
        for lunch_slot in lunch_slots:
            # If teacher has early start, block lunch
            # Simplified: penalize lunch assignments
            pass
    
    # Soft Constraints - Objective
    objective_terms = sat_penalties
    
    # Minimize student gaps (gravity rule)
    for section_id in sections:
        section_assignments = [a for a in assignments if a.section_id == section_id]
        # Sort timeslots by day and time
        sorted_slots = sorted(timeslots, key=lambda t: (t.day_of_week.value, t.start_time))
        for i in range(len(sorted_slots) - 1):
            t1 = sorted_slots[i]
            t2 = sorted_slots[i+1]
            if t1.day_of_week == t2.day_of_week:
                gap_hours = (datetime.strptime(t2.start_time, "%H:%M") - datetime.strptime(t1.end_time, "%H:%M")).seconds / 3600
                if gap_hours > 0:
                    # Penalize gaps
                    gap_penalty = int(gap_hours * 10)
                    # If both assigned, add penalty
                    assigned_t1 = sum(variables[(a.id, r.id, t1.id)] for a in section_assignments for r in rooms)
                    assigned_t2 = sum(variables[(a.id, r.id, t2.id)] for a in section_assignments for r in rooms)
                    objective_terms.append(assigned_t1 * assigned_t2 * gap_penalty)
    
    # 2-unit clustering (prefer small rooms for 2-unit)
    small_rooms = [r for r in rooms if r.capacity < 50]  # Assume small
    for assignment in assignments:
        course = courses[assignment.course_id]
        if course.units == 2:
            # Bonus for small rooms
            for room in small_rooms:
                for timeslot in timeslots:
                    # Negative weight for small rooms
                    objective_terms.append(-variables[(assignment.id, room.id, timeslot.id)] * 5)
    
    # Objective
    model.Minimize(sum(objective_terms))
    
    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Save results
        for (assign_id, room_id, ts_id), var in variables.items():
            if solver.Value(var):
                entry = models.ScheduleEntry(
                    schedule_run_id=run_id,
                    teacher_id=assignments[assign_id-1].teacher_id,
                    section_id=assignments[assign_id-1].section_id,
                    course_id=assignments[assign_id-1].course_id,
                    room_id=room_id,
                    timeslot_id=ts_id
                )
                db.add(entry)
        run.status = models.ScheduleRunStatus.SUCCESS
        run.objective_score = solver.ObjectiveValue()
    else:
        run.status = models.ScheduleRunStatus.FAILED
        # Generate conflict report (placeholder)
        run.objective_score = None
    
    db.commit()
    logger.info(f"Solver completed for run {run_id} with status {run.status}")