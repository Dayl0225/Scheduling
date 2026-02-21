import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import type { 
  Teacher, 
  Course, 
  Section,
  TeachingAssignment,
  TeacherFormState,
  CourseFormState,
  SectionFormState,
  AssignmentFormState 
} from '../types';

const MasterData: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'teachers' | 'courses' | 'sections' | 'assignments'>('teachers');
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // ==================== TEACHER STATE ====================
  const [teacherForm, setTeacherForm] = useState<TeacherFormState>({
    full_name: '',
    title: '',
    status: '',
    workload: '',
    is_senior_old: false,
  });

  const { data: teachers, isLoading: loadingTeachers } = useQuery({
    queryKey: ['teachers'],
    queryFn: () => api.getTeachers(),
    staleTime: 5 * 60 * 1000,
  });

  const createTeacherMutation = useMutation({
    mutationFn: (data: Omit<Teacher, 'id'>) => api.createTeacher(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
      setTeacherForm({ full_name: '', title: '', status: '', workload: '', is_senior_old: false });
      setShowForm(false);
      setSuccess('✅ Teacher added successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to create teacher';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  const deleteTeacherMutation = useMutation({
    mutationFn: (id: number) => api.deleteTeacher(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
      setSuccess('✅ Teacher deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to delete teacher';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  // ==================== COURSE STATE ====================
  const [courseForm, setCourseForm] = useState<CourseFormState>({
    course_code: '',
    course_name: '',
    units: '',
    course_type: '',
  });

  const { data: courses, isLoading: loadingCourses } = useQuery({
    queryKey: ['courses'],
    queryFn: () => api.getCourses(),
    staleTime: 5 * 60 * 1000,
  });

  const createCourseMutation = useMutation({
    mutationFn: (data: Omit<Course, 'id'>) => api.createCourse(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setCourseForm({ course_code: '', course_name: '', units: '', course_type: '' });
      setShowForm(false);
      setSuccess('✅ Course added successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to create course';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  const deleteCourseMutation = useMutation({
    mutationFn: (id: number) => api.deleteCourse(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setSuccess('✅ Course deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to delete course';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  // ==================== SECTION STATE ====================
  const [sectionForm, setSectionForm] = useState<SectionFormState>({
    code: '',
    year_level: '',
    is_first_year: false,
  });

  const { data: sections, isLoading: loadingSections } = useQuery({
    queryKey: ['sections'],
    queryFn: () => api.getSections(),
    staleTime: 5 * 60 * 1000,
  });

  const createSectionMutation = useMutation({
    mutationFn: (data: Omit<Section, 'id'>) => api.createSection(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections'] });
      setSectionForm({ code: '', year_level: '', is_first_year: false });
      setShowForm(false);
      setSuccess('✅ Section added successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to create section';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  const deleteSectionMutation = useMutation({
    mutationFn: (id: number) => api.deleteSection(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sections'] });
      setSuccess('✅ Section deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to delete section';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  // ==================== ASSIGNMENT STATE ====================
  const [assignmentForm, setAssignmentForm] = useState<AssignmentFormState>({
    teacher_id: '',
    course_id: '',
    section_id: '',
  });

  const { data: assignments, isLoading: loadingAssignments } = useQuery({
    queryKey: ['assignments'],
    queryFn: () => api.getAssignments(),
    staleTime: 5 * 60 * 1000,
  });

  const createAssignmentMutation = useMutation({
    mutationFn: (data: any) => {
      // Note: Assignments might need a different structure than teaching_assignments
      return Promise.resolve({ id: 1, ...data }); // Placeholder for now
    },
    onSuccess: () => {
      // queryClient.invalidateQueries({ queryKey: ['assignments'] });
      setAssignmentForm({ teacher_id: '', course_id: '', section_id: '' });
      setShowForm(false);
      setSuccess('✅ Assignment created successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to create assignment';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  const deleteAssignmentMutation = useMutation({
    mutationFn: (id: number) => Promise.resolve({}), // Placeholder
    onSuccess: () => {
      // queryClient.invalidateQueries({ queryKey: ['assignments'] });
      setSuccess('✅ Assignment deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
    },
    onError: (error: any) => {
      const message = error?.message || 'Failed to delete assignment';
      setError(`❌ ${message}`);
      setTimeout(() => setError(null), 5000);
    },
  });

  // ==================== HANDLERS ====================

  const handleAddTeacher = (e: React.FormEvent) => {
    e.preventDefault();
    if (teacherForm.title && teacherForm.status && teacherForm.workload) {
      createTeacherMutation.mutate({
        full_name: teacherForm.full_name,
        title: teacherForm.title as any,
        status: teacherForm.status as any,
        workload: teacherForm.workload as any,
        is_senior_old: teacherForm.is_senior_old,
      });
    }
  };

  const handleAddCourse = (e: React.FormEvent) => {
    e.preventDefault();
    if (courseForm.course_type && courseForm.units) {
      createCourseMutation.mutate({
        course_code: courseForm.course_code,
        course_name: courseForm.course_name,
        units: Number(courseForm.units),
        course_type: courseForm.course_type as any,
      });
    }
  };

  const handleAddSection = (e: React.FormEvent) => {
    e.preventDefault();
    if (sectionForm.year_level) {
      createSectionMutation.mutate({
        code: sectionForm.code,
        year_level: Number(sectionForm.year_level),
        is_first_year: sectionForm.is_first_year,
      });
    }
  };

  const handleAddAssignment = (e: React.FormEvent) => {
    e.preventDefault();
    if (assignmentForm.teacher_id && assignmentForm.course_id && assignmentForm.section_id) {
      createAssignmentMutation.mutate({
        teacher_id: Number(assignmentForm.teacher_id),
        course_id: Number(assignmentForm.course_id),
        section_id: Number(assignmentForm.section_id),
      });
    }
  };

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6">
        <div className="container mx-auto">
          <h1 className="text-3xl font-bold mb-2">Scheduling Officer Dashboard</h1>
          <p className="text-blue-100">Manage teachers, courses, sections, and assignments</p>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 m-4 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 m-4 rounded">
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="container mx-auto p-4">
        <div className="flex gap-2 mb-6 border-b border-gray-300">
          <button
            onClick={() => { setActiveTab('teachers'); setShowForm(false); }}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'teachers'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            👨‍🏫 Teachers {teachers?.length > 0 && `(${teachers.length})`}
          </button>
          <button
            onClick={() => { setActiveTab('courses'); setShowForm(false); }}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'courses'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📚 Courses {courses?.length > 0 && `(${courses.length})`}
          </button>
          <button
            onClick={() => { setActiveTab('sections'); setShowForm(false); }}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'sections'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            📖 Sections {sections?.length > 0 && `(${sections.length})`}
          </button>
          <button
            onClick={() => { setActiveTab('assignments'); setShowForm(false); }}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'assignments'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            🎓 Assignments {assignments?.length > 0 && `(${assignments.length})`}
          </button>
        </div>

        {/* TEACHERS TAB */}
        {activeTab === 'teachers' && (
          <div>
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                className="mb-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition"
              >
                + Add Teacher
              </button>
            ) : (
              <div className="bg-white p-6 rounded shadow-md mb-6">
                <h2 className="text-xl font-bold mb-4">Add New Teacher</h2>
                <form onSubmit={handleAddTeacher}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                      <input
                        type="text"
                        value={teacherForm.full_name}
                        onChange={(e) => setTeacherForm({...teacherForm, full_name: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="Dr. John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                      <select
                        value={teacherForm.title}
                        onChange={(e) => setTeacherForm({...teacherForm, title: e.target.value as any})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Title</option>
                        <option value="INSTRUCTOR_I">Instructor I</option>
                        <option value="INSTRUCTOR_II">Instructor II</option>
                        <option value="ASST_PROF_III">Assistant Professor III</option>
                        <option value="ASST_PROF_IV">Assistant Professor IV</option>
                        <option value="ASSOC_PROF_V">Associate Professor V</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Employment Status *</label>
                      <select
                        value={teacherForm.status}
                        onChange={(e) => setTeacherForm({...teacherForm, status: e.target.value as any})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Status</option>
                        <option value="CONTRACT_OF_SERVICE">Contract of Service</option>
                        <option value="PERMANENT">Permanent</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Time Status *</label>
                      <select
                        value={teacherForm.workload}
                        onChange={(e) => setTeacherForm({...teacherForm, workload: e.target.value as any})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Workload</option>
                        <option value="FULL_TIME">Full Time</option>
                        <option value="PART_TIME">Part Time</option>
                        <option value="VISITING">Visiting</option>
                      </select>
                    </div>
                    <div className="md:col-span-2">
                      <label className="flex items-center text-sm font-medium text-gray-700">
                        <input
                          type="checkbox"
                          checked={teacherForm.is_senior_old}
                          onChange={(e) => setTeacherForm({...teacherForm, is_senior_old: e.target.checked})}
                          className="mr-2 w-4 h-4 rounded"
                        />
                        Senior/Old Teacher (Requires priority routing to Building A)
                      </label>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button
                      type="submit"
                      disabled={createTeacherMutation.isPending}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded font-semibold transition"
                    >
                      {createTeacherMutation.isPending ? 'Adding...' : 'Add Teacher'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded font-semibold transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Teachers List */}
            {loadingTeachers ? (
              <div className="text-center text-gray-500">Loading teachers...</div>
            ) : teachers?.length === 0 ? (
              <div className="text-center text-gray-500 py-8">No teachers added yet</div>
            ) : (
              <div className="grid gap-4">
                {teachers.map((teacher: Teacher) => (
                  <div key={teacher.id} className="bg-white p-4 rounded shadow hover:shadow-md transition">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800">{teacher.full_name}</h3>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Title:</span> {teacher.title.replace(/_/g, ' ')}
                          </div>
                          <div>
                            <span className="font-medium">Status:</span> {teacher.status.replace(/_/g, ' ')}
                          </div>
                          <div>
                            <span className="font-medium">Workload:</span> {teacher.workload.replace(/_/g, ' ')}
                          </div>
                          {teacher.is_senior_old && (
                            <div className="text-amber-600 font-medium">🏛️ Senior Teacher</div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => deleteTeacherMutation.mutate(teacher.id!)}
                        className="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded text-sm transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* COURSES TAB */}
        {activeTab === 'courses' && (
          <div>
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                className="mb-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition"
              >
                + Add Course
              </button>
            ) : (
              <div className="bg-white p-6 rounded shadow-md mb-6">
                <h2 className="text-xl font-bold mb-4">Add New Course</h2>
                <form onSubmit={handleAddCourse}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Course Code *</label>
                      <input
                        type="text"
                        value={courseForm.course_code}
                        onChange={(e) => setCourseForm({...courseForm, course_code: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="CS101"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Course Name *</label>
                      <input
                        type="text"
                        value={courseForm.course_name}
                        onChange={(e) => setCourseForm({...courseForm, course_name: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="Introduction to Programming"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Units/Hours *</label>
                      <input
                        type="number"
                        step="0.5"
                        value={courseForm.units}
                        onChange={(e) => setCourseForm({...courseForm, units: e.target.value ? parseFloat(e.target.value) : ''})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="3"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Room Type *</label>
                      <select
                        value={courseForm.course_type}
                        onChange={(e) => setCourseForm({...courseForm, course_type: e.target.value as any})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Room Type</option>
                        <option value="STANDARD">Standard Classroom</option>
                        <option value="LAB">Lab</option>
                        <option value="SHOP">Shop</option>
                        <option value="SCIENCE_LAB">Science Lab</option>
                        <option value="CWATS">CWATS</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button
                      type="submit"
                      disabled={createCourseMutation.isPending}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded font-semibold transition"
                    >
                      {createCourseMutation.isPending ? 'Adding...' : 'Add Course'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded font-semibold transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Courses List */}
            {loadingCourses ? (
              <div className="text-center text-gray-500">Loading courses...</div>
            ) : courses?.length === 0 ? (
              <div className="text-center text-gray-500 py-8">No courses added yet</div>
            ) : (
              <div className="grid gap-4">
                {courses.map((course: Course) => (
                  <div key={course.id} className="bg-white p-4 rounded shadow hover:shadow-md transition">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {course.course_code} - {course.course_name}
                        </h3>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Units:</span> {course.units}
                          </div>
                          <div>
                            <span className="font-medium">Room Type:</span> {course.course_type.replace(/_/g, ' ')}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => deleteCourseMutation.mutate(course.id!)}
                        className="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded text-sm transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* SECTIONS TAB */}
        {activeTab === 'sections' && (
          <div>
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                className="mb-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition"
              >
                + Add Section
              </button>
            ) : (
              <div className="bg-white p-6 rounded shadow-md mb-6">
                <h2 className="text-xl font-bold mb-4">Add New Section</h2>
                <form onSubmit={handleAddSection}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Section Code *</label>
                      <input
                        type="text"
                        value={sectionForm.code}
                        onChange={(e) => setSectionForm({...sectionForm, code: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="CS101-1A"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Year Level *</label>
                      <select
                        value={sectionForm.year_level}
                        onChange={(e) => setSectionForm({...sectionForm, year_level: e.target.value ? parseInt(e.target.value) : ''})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Year</option>
                        <option value="1">1st Year</option>
                        <option value="2">2nd Year</option>
                        <option value="3">3rd Year</option>
                        <option value="4">4th Year</option>
                      </select>
                    </div>
                    <div className="md:col-span-2">
                      <label className="flex items-center text-sm font-medium text-gray-700">
                        <input
                          type="checkbox"
                          checked={sectionForm.is_first_year}
                          onChange={(e) => setSectionForm({...sectionForm, is_first_year: e.target.checked})}
                          className="mr-2 w-4 h-4 rounded"
                        />
                        Is 1st Year (Requires Saturday CWATS vacancy)
                      </label>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button
                      type="submit"
                      disabled={createSectionMutation.isPending}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded font-semibold transition"
                    >
                      {createSectionMutation.isPending ? 'Adding...' : 'Add Section'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded font-semibold transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Sections List */}
            {loadingSections ? (
              <div className="text-center text-gray-500">Loading sections...</div>
            ) : sections?.length === 0 ? (
              <div className="text-center text-gray-500 py-8">No sections added yet</div>
            ) : (
              <div className="grid gap-4">
                {sections.map((section: Section) => (
                  <div key={section.id} className="bg-white p-4 rounded shadow hover:shadow-md transition">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800">{section.code}</h3>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Year Level:</span> {section.year_level}
                          </div>
                          {section.is_first_year && (
                            <div className="text-amber-600 font-medium">📅 1st Year (CWATS Required)</div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => deleteSectionMutation.mutate(section.id!)}
                        className="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded text-sm transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ASSIGNMENTS TAB */}
        {activeTab === 'assignments' && (
          <div>
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                className="mb-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition"
              >
                + Create Assignment
              </button>
            ) : (
              <div className="bg-white p-6 rounded shadow-md mb-6">
                <h2 className="text-xl font-bold mb-4">Create Teaching Assignment</h2>
                <form onSubmit={handleAddAssignment}>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Teacher *</label>
                      <select
                        value={assignmentForm.teacher_id}
                        onChange={(e) => setAssignmentForm({...assignmentForm, teacher_id: e.target.value ? parseInt(e.target.value) : ''})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Teacher</option>
                        {teachers?.map((teacher: Teacher) => (
                          <option key={teacher.id} value={teacher.id}>
                            {teacher.full_name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Course *</label>
                      <select
                        value={assignmentForm.course_id}
                        onChange={(e) => setAssignmentForm({...assignmentForm, course_id: e.target.value ? parseInt(e.target.value) : ''})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Course</option>
                        {courses?.map((course: Course) => (
                          <option key={course.id} value={course.id}>
                            {course.course_code}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Section *</label>
                      <select
                        value={assignmentForm.section_id}
                        onChange={(e) => setAssignmentForm({...assignmentForm, section_id: e.target.value ? parseInt(e.target.value) : ''})}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Section</option>
                        {sections?.map((section: Section) => (
                          <option key={section.id} value={section.id}>
                            {section.code}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button
                      type="submit"
                      disabled={createAssignmentMutation.isPending || !assignmentForm.teacher_id || !assignmentForm.course_id || !assignmentForm.section_id}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded font-semibold transition"
                    >
                      {createAssignmentMutation.isPending ? 'Creating...' : 'Create Assignment'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowForm(false)}
                      className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded font-semibold transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Assignments List */}
            {loadingAssignments ? (
              <div className="text-center text-gray-500">Loading assignments...</div>
            ) : assignments?.length === 0 ? (
              <div className="text-center text-gray-500 py-8">No assignments created yet</div>
            ) : (
              <div className="grid gap-4">
                {assignments.map((assignment: TeachingAssignment) => (
                  <div key={assignment.id} className="bg-white p-4 rounded shadow hover:shadow-md transition">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {assignment.teacher?.full_name} - {assignment.course?.course_code}
                        </h3>
                        <div className="grid grid-cols-3 gap-2 mt-2 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Teacher:</span> {assignment.teacher?.full_name}
                          </div>
                          <div>
                            <span className="font-medium">Course:</span> {assignment.course?.course_name}
                          </div>
                          <div>
                            <span className="font-medium">Section:</span> {assignment.section?.code}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => deleteAssignmentMutation.mutate(assignment.id!)}
                        className="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded text-sm transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MasterData;