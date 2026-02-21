// Teacher Classifications
export type TeacherTitle = 
  | 'INSTRUCTOR_I'
  | 'INSTRUCTOR_II'
  | 'ASST_PROF_III'
  | 'ASST_PROF_IV'
  | 'ASSOC_PROF_V';

export type EmploymentStatus = 'CONTRACT_OF_SERVICE' | 'PERMANENT';

export type TimeStatus = 'FULL_TIME' | 'PART_TIME' | 'VISITING';

export type CourseType = 'STANDARD' | 'LAB' | 'SHOP' | 'SCIENCE_LAB' | 'CWATS';

// API Models
export interface Teacher {
  id?: number;
  full_name: string;
  title: TeacherTitle;
  status: EmploymentStatus;
  workload: TimeStatus;
  is_senior_old: boolean;
  active?: boolean;
}

export interface Course {
  id?: number;
  course_code: string;
  course_name: string;
  units: number;
  course_type: CourseType;
}

export interface Section {
  id?: number;
  code: string;
  year_level: number;
  is_first_year: boolean;
}

export interface TeachingAssignment {
  id?: number;
  teacher_id: number;
  course_id: number;
  section_id: number;
  term_id: number;
  teacher?: Teacher;
  course?: Course;
  section?: Section;
}

export interface Room {
  id?: number;
  room_code: string;
  building_id: number;
  floor_no: number;
  room_type: CourseType;
  capacity: number;
  active?: boolean;
}

export interface Building {
  id?: number;
  code: string;
  name: string;
}

export interface Timeslot {
  id?: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  is_cwats_slot: boolean;
}

// Form State
export interface TeacherFormState {
  full_name: string;
  title: TeacherTitle | '';
  status: EmploymentStatus | '';
  workload: TimeStatus | '';
  is_senior_old: boolean;
}

export interface CourseFormState {
  course_code: string;
  course_name: string;
  units: number | '';
  course_type: CourseType | '';
}

export interface SectionFormState {
  code: string;
  year_level: number | '';
  is_first_year: boolean;
}

export interface AssignmentFormState {
  teacher_id: number | '';
  course_id: number | '';
  section_id: number | '';
}

// API Response
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}
