"""
Constraint Validation Engine for Campus Scheduling System

This module implements hard and soft constraint checking based on Master Rules Document:
- Hard Constraints: Non-negotiable rules that MUST be followed
- Soft Constraints: Preferences and priorities that optimize the schedule
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from enum import Enum

from . import models


class ConstraintViolation:
    """Represents a constraint violation with details."""
    
    def __init__(self, constraint_type: str, severity: str, message: str):
        self.constraint_type = constraint_type  # "HARD" or "SOFT"
        self.severity = severity  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
        self.message = message
    
    def __repr__(self):
        return f"[{self.constraint_type}-{self.severity}] {self.message}"


class TimePeriod:
    """Represents a time period within a day."""
    
    def __init__(self, start_time: str, end_time: str):
        """
        Initialize a time period.
        
        Args:
            start_time: Time in "HH:MM" format (e.g., "07:30")
            end_time: Time in "HH:MM" format (e.g., "10:30")
        """
        self.start_time = datetime.strptime(start_time, "%H:%M").time()
        self.end_time = datetime.strptime(end_time, "%H:%M").time()
        self.duration_minutes = int(
            (datetime.combine(datetime.today(), self.end_time) - 
             datetime.combine(datetime.today(), self.start_time)).total_seconds() / 60
        )
    
    def overlaps_with(self, other: 'TimePeriod') -> bool:
        """Check if this period overlaps with another."""
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def __repr__(self):
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class ConstraintEngine:
    """
    Main constraint validation engine.
    
    Takes a teacher, course, timeslot, and room, then validates all constraints.
    """
    
    # Lunch break rules
    EARLY_START_THRESHOLD = "10:30"  # If class starts before this, lunch at 11:30
    EARLY_START_LUNCH = "11:30"      # Lunch start for early classes
    LATE_START_LUNCH = "14:30"       # Lunch start for 10:30 AM or later
    LUNCH_DURATION_MINUTES = 90      # 1.5 hours
    
    # Time limits based on employment classification
    TIME_LIMITS = {
        ("CONTRACT_OF_SERVICE", "FULL_TIME"): "17:30",  # 5:30 PM
        ("PERMANENT", "FULL_TIME"): "15:30",             # 3:30 PM
        ("PART_TIME",): "20:00",                         # No specific limit, use 8 PM
        ("VISITING",): "20:00",                          # No specific limit, use 8 PM
    }
    
    # Senior teacher room codes
    SENIOR_ROOMS = ["A103", "A104", "A203"]
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_timeslot_for_assignment(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        timeslot: models.Timeslot,
        room: models.Room,
        existing_schedule: Optional[Dict] = None
    ) -> Tuple[bool, List[ConstraintViolation]]:
        """
        Validate if a teacher-course-section-timeslot-room combination is valid.
        
        Args:
            teacher: Teacher object
            course: Course object
            section: Section object
            timeslot: Timeslot object
            room: Room object
            existing_schedule: Dict of existing schedule entries for conflict checking
                              Format: {day: [(teacher_id, start_time, end_time), ...]}
        
        Returns:
            Tuple[bool, List[ConstraintViolation]]: (is_valid, violations)
            - is_valid: True if all hard constraints pass, False otherwise
            - violations: List of all violations (hard and soft)
        """
        violations: List[ConstraintViolation] = []
        
        # HARD CONSTRAINTS
        hard_violations = self._check_hard_constraints(
            teacher, course, section, timeslot, room, existing_schedule
        )
        violations.extend(hard_violations)
        
        # If hard constraints fail, return immediately
        if hard_violations:
            return False, violations
        
        # SOFT CONSTRAINTS (only checked if hard constraints pass)
        soft_violations = self._check_soft_constraints(
            teacher, course, section, timeslot, room
        )
        violations.extend(soft_violations)
        
        return True, violations
    
    def _check_hard_constraints(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        timeslot: models.Timeslot,
        room: models.Room,
        existing_schedule: Optional[Dict]
    ) -> List[ConstraintViolation]:
        """Check all hard constraints."""
        violations: List[ConstraintViolation] = []
        
        # 1. Room Type Matching
        violations.extend(self._check_room_type_matching(course, room))
        
        # 2. Time Limit Constraint
        violations.extend(self._check_time_limit(teacher, timeslot))
        
        # 3. Teacher Lunch Break Constraint
        violations.extend(self._check_teacher_lunch_break(timeslot))
        
        # 4. Max 5 Days Per Week Constraint
        violations.extend(self._check_max_teaching_days(teacher, timeslot, existing_schedule))
        
        # 5. Saturday Compensation Constraint
        violations.extend(self._check_saturday_compensation(teacher, timeslot, existing_schedule))
        
        # 6. 1st Year CWATS Saturday Vacancy Constraint
        violations.extend(self._check_first_year_cwats_vacancy(section, timeslot))
        
        # 7. Room Availability (No Maintenance Block)
        violations.extend(self._check_room_maintenance_blocks(room, timeslot))
        
        # 8. No Teacher/Section/Room Overlap
        violations.extend(self._check_no_overlap(teacher, section, room, timeslot, existing_schedule))
        
        return violations
    
    def _check_soft_constraints(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        timeslot: models.Timeslot,
        room: models.Room
    ) -> List[ConstraintViolation]:
        """Check all soft constraints (preferences & priorities)."""
        violations: List[ConstraintViolation] = []
        
        # 1. Senior Teacher Priority - Building A (1st or 2nd floor)
        violations.extend(self._check_senior_priority(teacher, room))
        
        # 2. 2-Hour Course Grouping
        violations.extend(self._check_2hour_course_grouping(course, room))
        
        return violations
    
    # ==================== HARD CONSTRAINTS ====================
    
    def _check_room_type_matching(
        self,
        course: models.Course,
        room: models.Room
    ) -> List[ConstraintViolation]:
        """
        Constraint: Course room type must match room type.
        
        Example: Lab course must be in a Lab room.
        """
        violations = []
        
        # STANDARD courses can be in any room
        if course.course_type == models.CourseType.STANDARD:
            return violations
        
        # Specific course types must match room types
        if room.room_type != course.course_type:
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"Course type {course.course_type.value} requires {course.course_type.value} room, "
                f"but {room.room_code} is {room.room_type.value}"
            ))
        
        return violations
    
    def _check_time_limit(
        self,
        teacher: models.Teacher,
        timeslot: models.Timeslot
    ) -> List[ConstraintViolation]:
        """
        Constraint: End of day time limits based on employment status.
        
        Rules:
        - Contract of Service + Full-Time: max 5:30 PM
        - Permanent + Full-Time: max 3:30 PM
        - Part-Time/Visiting: no strict limit
        """
        violations = []
        
        end_time = datetime.strptime(timeslot.end_time, "%H:%M").time()
        
        # Get the applicable time limit
        key = (teacher.status.value, teacher.workload.value)
        if key not in self.TIME_LIMITS:
            # Fall back for Part-Time/Visiting without specific time status
            if teacher.workload.value in self.TIME_LIMITS:
                key = (teacher.workload.value,)
            else:
                return violations  # No time limit
        
        max_time_str = self.TIME_LIMITS[key]
        max_time = datetime.strptime(max_time_str, "%H:%M").time()
        
        if end_time > max_time:
            limit_str = max_time_str
            if teacher.status == models.TeacherStatus.PERMANENT and \
               teacher.workload == models.Workload.FULL_TIME:
                limit_str = "3:30 PM"
            elif teacher.status == models.TeacherStatus.CONTRACT_OF_SERVICE and \
                 teacher.workload == models.Workload.FULL_TIME:
                limit_str = "5:30 PM"
            
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"{teacher.full_name} ({teacher.status.value}/{teacher.workload.value}) "
                f"cannot work past {limit_str}, but timeslot ends at {timeslot.end_time}"
            ))
        
        return violations
    
    def _check_teacher_lunch_break(
        self,
        timeslot: models.Timeslot
    ) -> List[ConstraintViolation]:
        """
        Constraint: Mandatory 1.5-hour teacher lunch break.
        
        Rules:
        - If class starts before 10:30 AM: lunch at 11:30 AM
        - If class starts 10:30 AM or later: lunch at 2:30 PM
        
        This validates that the timeslot doesn't conflict with lunch.
        """
        violations = []
        
        start_time = datetime.strptime(timeslot.start_time, "%H:%M").time()
        end_time = datetime.strptime(timeslot.end_time, "%H:%M").time()
        
        early_threshold = datetime.strptime(self.EARLY_START_THRESHOLD, "%H:%M").time()
        
        # Determine lunch period
        if start_time < early_threshold:
            lunch_start = datetime.strptime(self.EARLY_START_LUNCH, "%H:%M").time()
        else:
            lunch_start = datetime.strptime(self.LATE_START_LUNCH, "%H:%M").time()
        
        lunch_end_minutes = self.LUNCH_DURATION_MINUTES
        lunch_end = datetime.combine(datetime.today(), lunch_start)
        lunch_end = (lunch_end + timedelta(minutes=lunch_end_minutes)).time()
        
        lunch_period = TimePeriod(
            lunch_start.strftime("%H:%M"),
            lunch_end.strftime("%H:%M")
        )
        
        timeslot_period = TimePeriod(timeslot.start_time, timeslot.end_time)
        
        if timeslot_period.overlaps_with(lunch_period):
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"Timeslot {timeslot_period} conflicts with mandatory lunch break {lunch_period}"
            ))
        
        return violations
    
    def _check_max_teaching_days(
        self,
        teacher: models.Teacher,
        timeslot: models.Timeslot,
        existing_schedule: Optional[Dict]
    ) -> List[ConstraintViolation]:
        """
        Constraint: Teachers can teach maximum 5 days per week.
        
        If scheduled on Saturday, they must be given a full vacant weekday.
        """
        violations = []
        
        if not existing_schedule:
            return violations
        
        # Count unique teaching days for this teacher
        teaching_days = set()
        for day, sessions in existing_schedule.items():
            for teacher_id, _, _ in sessions:
                if teacher_id == teacher.id:
                    teaching_days.add(day)
        
        # Add the current timeslot's day
        teaching_days.add(timeslot.day_of_week.value)
        
        # Check if exceeds 5 days
        if len(teaching_days) > 5:
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"{teacher.full_name} would teach {len(teaching_days)} days/week, exceeding maximum of 5 days"
            ))
        
        # If Saturday is involved, check for compensation day
        if timeslot.day_of_week == models.DayOfWeek.SAT and len(teaching_days) == 5:
            # Saturday + 4 weekdays = 5 days. Need to verify at least 1 weekday is blocked
            weekdays = {d for d in teaching_days if d != "SAT"}
            if len(weekdays) != 4:
                violations.append(ConstraintViolation(
                    "HARD",
                    "HIGH",
                    f"{teacher.full_name} scheduled on Saturday but doesn't have exactly 4 weekdays"
                ))
        
        return violations
    
    def _check_saturday_compensation(
        self,
        teacher: models.Teacher,
        timeslot: models.Timeslot,
        existing_schedule: Optional[Dict]
    ) -> List[ConstraintViolation]:
        """
        Constraint: If scheduled on Saturday, must have one full vacant weekday.
        
        This is enforced via TeacherDayBlock with AUTO_SATURDAY_COMP_OFF source.
        """
        violations = []
        
        if timeslot.day_of_week != models.DayOfWeek.SAT:
            return violations
        
        # Query for blocked days from AUTO_SATURDAY_COMP_OFF
        blocked_days = self.db.query(models.TeacherDayBlock).filter(
            models.TeacherDayBlock.teacher_id == teacher.id,
            models.TeacherDayBlock.source == models.BlockSource.AUTO_SATURDAY_COMP_OFF,
            models.TeacherDayBlock.is_blocked == True
        ).all()
        
        if not blocked_days:
            violations.append(ConstraintViolation(
                "HARD",
                "HIGH",
                f"{teacher.full_name} scheduled on Saturday but has no blocked compensation day"
            ))
        
        return violations
    
    def _check_first_year_cwats_vacancy(
        self,
        section: models.Section,
        timeslot: models.Timeslot
    ) -> List[ConstraintViolation]:
        """
        Constraint: 1st-year sections must have Saturday CWATS vacancy.
        
        Specific times: 7:30-10:30 AM or 10:30-1:30 PM
        """
        violations = []
        
        if not section.is_first_year:
            return violations
        
        if timeslot.day_of_week != models.DayOfWeek.SAT:
            return violations
        
        # Check if timeslot is a valid CWATS slot
        if not timeslot.is_cwats_slot:
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"1st-year section {section.code} scheduled on Saturday, "
                f"but timeslot {timeslot.start_time}-{timeslot.end_time} is not a CWATS slot. "
                f"Valid CWATS times: 7:30-10:30 AM or 10:30-1:30 PM"
            ))
        
        return violations
    
    def _check_room_maintenance_blocks(
        self,
        room: models.Room,
        timeslot: models.Timeslot
    ) -> List[ConstraintViolation]:
        """
        Constraint: Room cannot be scheduled during maintenance.
        """
        violations = []
        
        # Get maintenance blocks for this room
        maintenance_blocks = self.db.query(models.RoomMaintenanceBlock).filter(
            models.RoomMaintenanceBlock.room_id == room.id
        ).all()
        
        # Create datetime objects for comparison (assuming current date for simplicity)
        today = datetime.today()
        timeslot_start = datetime.combine(today, datetime.strptime(timeslot.start_time, "%H:%M").time())
        timeslot_end = datetime.combine(today, datetime.strptime(timeslot.end_time, "%H:%M").time())
        
        for block in maintenance_blocks:
            if not (timeslot_end <= block.start_datetime or timeslot_start >= block.end_datetime):
                violations.append(ConstraintViolation(
                    "HARD",
                    "CRITICAL",
                    f"Room {room.room_code} has maintenance scheduled during timeslot "
                    f"{timeslot.start_time}-{timeslot.end_time}: {block.reason}"
                ))
        
        return violations
    
    def _check_no_overlap(
        self,
        teacher: models.Teacher,
        section: models.Section,
        room: models.Room,
        timeslot: models.Timeslot,
        existing_schedule: Optional[Dict]
    ) -> List[ConstraintViolation]:
        """
        Constraint: No overlapping assignments for teacher, section, or room.
        """
        violations = []
        
        if not existing_schedule:
            return violations
        
        day_key = timeslot.day_of_week.value
        timeslot_period = TimePeriod(timeslot.start_time, timeslot.end_time)
        
        if day_key not in existing_schedule:
            return violations
        
        for scheduled_teacher_id, scheduled_start, scheduled_end in existing_schedule[day_key]:
            scheduled_period = TimePeriod(scheduled_start, scheduled_end)
            
            if timeslot_period.overlaps_with(scheduled_period):
                if scheduled_teacher_id == teacher.id:
                    violations.append(ConstraintViolation(
                        "HARD",
                        "CRITICAL",
                        f"{teacher.full_name} already scheduled at {scheduled_period} on {day_key}"
                    ))
        
        # Check room overlap (simplified - would need more detailed schedule lookup)
        room_entries = self.db.query(models.ScheduleEntry).filter(
            models.ScheduleEntry.room_id == room.id,
            models.ScheduleEntry.timeslot_id == timeslot.id
        ).all()
        
        if room_entries:
            violations.append(ConstraintViolation(
                "HARD",
                "CRITICAL",
                f"Room {room.room_code} already occupied at {timeslot_period} on {day_key}"
            ))
        
        return violations
    
    # ==================== SOFT CONSTRAINTS ====================
    
    def _check_senior_priority(
        self,
        teacher: models.Teacher,
        room: models.Room
    ) -> List[ConstraintViolation]:
        """
        Soft Constraint: Senior/Old teachers should be assigned to Building A.
        
        Preferred rooms: A103, A104 (1st floor), A203 (2nd floor)
        """
        violations = []
        
        if not teacher.is_senior_old:
            return violations
        
        if room.room_code not in self.SENIOR_ROOMS:
            violations.append(ConstraintViolation(
                "SOFT",
                "MEDIUM",
                f"Senior teacher {teacher.full_name} assigned to {room.room_code}, "
                f"but should prefer Building A rooms: {', '.join(self.SENIOR_ROOMS)}"
            ))
        
        return violations
    
    def _check_2hour_course_grouping(
        self,
        course: models.Course,
        room: models.Room
    ) -> List[ConstraintViolation]:
        """
        Soft Constraint: 2-hour/2-unit courses should be back-to-back.
        
        This is a preference for room consistency to prevent time-wasting.
        """
        violations = []
        
        if course.units != 2.0:
            return violations
        
        # This is a soft constraint about placement strategy
        # Could recommend small rooms or specific buildings
        if room.capacity > 100:
            violations.append(ConstraintViolation(
                "SOFT",
                "LOW",
                f"2-unit course {course.course_code} assigned to large room {room.room_code} "
                f"(capacity {room.capacity}). Consider smaller room for efficiency."
            ))
        
        return violations
    
    # ==================== UTILITY METHODS ====================
    
    def find_valid_timeslots(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        available_rooms: Optional[List[models.Room]] = None,
        existing_schedule: Optional[Dict] = None
    ) -> Dict[models.Timeslot, List[models.Room]]:
        """
        Find all valid timeslot-room combinations for a teacher-course-section.
        
        Returns: {timeslot: [rooms], ...} of valid combinations
        """
        if available_rooms is None:
            available_rooms = self.db.query(models.Room).filter(
                models.Room.active == True
            ).all()
        
        valid_combinations: Dict[models.Timeslot, List[models.Room]] = {}
        
        timeslots = self.db.query(models.Timeslot).all()
        
        for timeslot in timeslots:
            valid_rooms_for_slot = []
            
            for room in available_rooms:
                is_valid, _ = self.validate_timeslot_for_assignment(
                    teacher, course, section, timeslot, room, existing_schedule
                )
                
                if is_valid:
                    valid_rooms_for_slot.append(room)
            
            if valid_rooms_for_slot:
                valid_combinations[timeslot] = valid_rooms_for_slot
        
        return valid_combinations
    
    def find_constraint_violations_for_assignment(
        self,
        teacher: models.Teacher,
        course: models.Course,
        section: models.Section,
        timeslot: models.Timeslot,
        room: models.Room
    ) -> Dict[str, List[ConstraintViolation]]:
        """
        Get detailed violation report for a specific assignment.
        
        Returns: {"HARD": [...], "SOFT": [...]}
        """
        _, violations = self.validate_timeslot_for_assignment(
            teacher, course, section, timeslot, room
        )
        
        return {
            "HARD": [v for v in violations if v.constraint_type == "HARD"],
            "SOFT": [v for v in violations if v.constraint_type == "SOFT"]
        }
