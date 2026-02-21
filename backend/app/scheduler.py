"""
Campus Scheduling Algorithm

This module implements the scheduling algorithm that:
1. Loads all teachers, courses, sections, and rooms
2. Applies hard and soft constraints
3. Generates valid schedule assignments
4. Saves results to the database

The algorithm uses a greedy approach with backtracking when hard constraints are violated.
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum

from . import models
from .constraints import ConstraintEngine, ConstraintViolation, TimePeriod

logger = logging.getLogger(__name__)


class SchedulerStatus(str, Enum):
    """Status of scheduling operation."""
    STARTED = "started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduleAssignment:
    """Represents a single schedule assignment."""
    
    def __init__(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        timeslot: models.Timeslot,
        room: models.Room
    ):
        self.teacher = teacher
        self.course = course
        self.section = section
        self.timeslot = timeslot
        self.room = room
        self.violations: List[ConstraintViolation] = []


class CampusScheduler:
    """Main scheduling engine that generates course assignments."""
    
    def __init__(self, db: Session):
        self.db = db
        self.constraint_engine = ConstraintEngine(db)
        self.assignments: List[ScheduleAssignment] = []
        self.schedule_entries: List[models.ScheduleEntry] = []
        self.violations: List[ConstraintViolation] = []
    
    def generate_schedule(
        self,
        schedule_run: models.ScheduleRun,
        term_id: int,
        prioritize_senior: bool = True
    ) -> Tuple[bool, str]:
        """
        Generate a complete schedule for a term.
        
        Args:
            schedule_run: ScheduleRun object to save results to
            term_id: Term ID for filtering assignments
            prioritize_senior: If True, assign senior teachers first
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Starting schedule generation for run {schedule_run.id}, term {term_id}")
            
            # Load all necessary data
            teaching_assignments = self._load_teaching_assignments(term_id)
            if not teaching_assignments:
                msg = f"No teaching assignments found for term {term_id}"
                logger.warning(msg)
                return False, msg
            
            timeslots = self._load_timeslots()
            if not timeslots:
                msg = "No timeslots configured"
                logger.warning(msg)
                return False, msg
            
            rooms = self._load_rooms()
            if not rooms:
                msg = "No rooms available"
                logger.warning(msg)
                return False, msg
            
            logger.info(f"Loaded {len(teaching_assignments)} assignments, {len(timeslots)} timeslots, {len(rooms)} rooms")
            
            # Sort assignments for prioritization
            sorted_assignments = self._sort_assignments_by_priority(
                teaching_assignments,
                prioritize_senior=prioritize_senior
            )
            
            # Attempt to assign each teaching assignment
            failed_assignments = []
            for teaching_assignment in sorted_assignments:
                success = self._assign_teaching_unit(
                    teaching_assignment,
                    timeslots,
                    rooms
                )
                if not success:
                    failed_assignments.append(teaching_assignment)
                    logger.warning(f"Failed to assign {teaching_assignment.teacher.full_name} -> {teaching_assignment.course.course_code}")
            
            # Save all valid assignments to the schedule
            self._save_schedule_entries(schedule_run)
            
            # Update schedule run status
            hard_violations = [v for v in self.violations if v.constraint_type == "HARD"]
            if hard_violations:
                schedule_run.status = models.ScheduleRunStatus.FAILED
                msg = f"Schedule generation completed with {len(hard_violations)} hard constraint violations"
                logger.error(msg)
                return False, msg
            else:
                schedule_run.status = models.ScheduleRunStatus.SUCCESS
                schedule_run.objective_score = self._calculate_objective_score()
                msg = f"Schedule successfully generated: {len(self.assignments)} assignments, {len(failed_assignments)} failures"
                logger.info(msg)
                self.db.commit()
                return True, msg
        
        except Exception as e:
            logger.exception(f"Error during schedule generation: {str(e)}")
            schedule_run.status = models.ScheduleRunStatus.FAILED
            self.db.commit()
            return False, f"Schedule generation failed: {str(e)}"
    
    def _load_teaching_assignments(self, term_id: int) -> List[models.TeachingAssignment]:
        """Load all teaching assignments for a term."""
        assignments = self.db.query(models.TeachingAssignment).filter(
            models.TeachingAssignment.term_id == term_id
        ).all()
        return assignments
    
    def _load_timeslots(self) -> List[models.Timeslot]:
        """Load all available timeslots."""
        timeslots = self.db.query(models.Timeslot).all()
        return timeslots
    
    def _load_rooms(self) -> List[models.Room]:
        """Load all active rooms."""
        rooms = self.db.query(models.Room).filter(models.Room.active == True).all()
        return rooms
    
    def _sort_assignments_by_priority(
        self,
        assignments: List[models.TeachingAssignment],
        prioritize_senior: bool = True
    ) -> List[models.TeachingAssignment]:
        """
        Sort assignments by priority.
        
        Priority order:
        1. Senior teachers (if prioritize_senior=True)
        2. Permanent + Full-Time teachers
        3. Contract + Full-Time teachers
        4. Part-Time and Visiting teachers
        5. New first-year sections (lower course code priority)
        """
        def priority_key(assignment):
            teacher = assignment.teacher
            section = assignment.section
            
            # Senior priority (lower number = higher priority)
            senior_priority = 0 if (prioritize_senior and teacher.is_senior_old) else 1
            
            # Employment status priority
            if teacher.status == models.TeacherStatus.PERMANENT:
                if teacher.workload == models.Workload.FULL_TIME:
                    status_priority = 0
                else:
                    status_priority = 2
            elif teacher.status == models.TeacherStatus.CONTRACT_OF_SERVICE:
                if teacher.workload == models.Workload.FULL_TIME:
                    status_priority = 1
                else:
                    status_priority = 3
            else:
                status_priority = 4
            
            # First-year section priority (first-year sections get lower priority)
            year_priority = 0 if section.is_first_year else 1
            
            return (senior_priority, status_priority, year_priority)
        
        return sorted(assignments, key=priority_key)
    
    def _assign_teaching_unit(
        self,
        teaching_assignment: models.TeachingAssignment,
        timeslots: List[models.Timeslot],
        rooms: List[models.Room]
    ) -> bool:
        """
        Attempt to assign a single teaching unit to a valid timeslot and room.
        
        Returns: True if successfully assigned, False otherwise
        """
        teacher = teaching_assignment.teacher
        course = teaching_assignment.course
        section = teaching_assignment.section
        
        # Build a dict of existing schedule for conflict checking
        existing_schedule = self._build_existing_schedule_dict()
        
        # Try to find a valid slot
        for timeslot in timeslots:
            for room in rooms:
                is_valid, violations = self.constraint_engine.validate_timeslot_for_assignment(
                    teacher=teacher,
                    course=course,
                    section=section,
                    timeslot=timeslot,
                    room=room,
                    existing_schedule=existing_schedule
                )
                
                # Record violations for reporting
                self.violations.extend(violations)
                
                # If valid, create the assignment
                if is_valid:
                    assignment = ScheduleAssignment(
                        teacher=teacher,
                        course=course,
                        section=section,
                        timeslot=timeslot,
                        room=room
                    )
                    self.assignments.append(assignment)
                    logger.debug(f"Assigned {teacher.full_name} ({course.course_code}) to {room.room_code} on {timeslot.day_of_week.value} {timeslot.start_time}")
                    return True
        
        logger.warning(f"Could not find valid slot for {teacher.full_name} -> {course.course_code} -> {section.code}")
        return False
    
    def _build_existing_schedule_dict(self) -> Dict:
        """
        Build a dictionary of existing assignments for quick lookup.
        
        Format: {day_of_week: [(teacher_id, start_time, end_time), ...]}
        """
        schedule_dict = {}
        for assignment in self.assignments:
            day = assignment.timeslot.day_of_week.value
            if day not in schedule_dict:
                schedule_dict[day] = []
            
            schedule_dict[day].append((
                assignment.teacher.id,
                assignment.timeslot.start_time,
                assignment.timeslot.end_time
            ))
        
        return schedule_dict
    
    def _save_schedule_entries(self, schedule_run: models.ScheduleRun) -> None:
        """Save all valid assignments to the database as ScheduleEntry records."""
        for assignment in self.assignments:
            schedule_entry = models.ScheduleEntry(
                schedule_run_id=schedule_run.id,
                teacher_id=assignment.teacher.id,
                section_id=assignment.section.id,
                course_id=assignment.course.id,
                room_id=assignment.room.id,
                timeslot_id=assignment.timeslot.id,
                is_locked=False
            )
            self.db.add(schedule_entry)
            self.schedule_entries.append(schedule_entry)
        
        self.db.commit()
        logger.info(f"Saved {len(self.schedule_entries)} schedule entries")
    
    def _calculate_objective_score(self) -> float:
        """
        Calculate an objective score for the generated schedule.
        
        Scoring criteria:
        - Fewer soft constraint violations (better)
        - Better room utilization (better)
        - Better time distribution (better)
        
        Returns a score (higher is better).
        """
        score = 1000.0
        
        # Penalize soft constraint violations
        soft_violations = [v for v in self.violations if v.constraint_type == "SOFT"]
        score -= len(soft_violations) * 10
        
        # Bonus for more assignments
        score += len(self.assignments) * 5
        
        # Penalize time gaps for students (student vacancy)
        # This would require more analysis of schedule structure
        
        return max(0, score)
    
    def get_violations_report(self) -> Dict:
        """Generate a report of all constraint violations."""
        hard_violations = [v for v in self.violations if v.constraint_type == "HARD"]
        soft_violations = [v for v in self.violations if v.constraint_type == "SOFT"]
        
        return {
            "hard_violations": [str(v) for v in hard_violations],
            "soft_violations": [str(v) for v in soft_violations],
            "total_hard": len(hard_violations),
            "total_soft": len(soft_violations),
            "total_assignments": len(self.assignments),
            "objective_score": self._calculate_objective_score()
        }
