// API Service for Scheduling System
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * API client for the Campus Scheduling System
 * All endpoints return JSON or throw errors on failure
 */
export const api = {
  // ===== TEACHERS =====
  getTeachers: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/teachers/`);
    if (!response.ok) throw new Error('Failed to fetch teachers');
    return response.json();
  },

  createTeacher: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/teachers/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create teacher');
    }
    return response.json();
  },

  getTeacher: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/teachers/${id}`);
    if (!response.ok) throw new Error('Failed to fetch teacher');
    return response.json();
  },

  updateTeacher: async (id: number, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/teachers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update teacher');
    }
    return response.json();
  },

  deleteTeacher: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/teachers/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete teacher');
    }
    return response.json();
  },

  // ===== COURSES =====
  getCourses: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/courses/`);
    if (!response.ok) throw new Error('Failed to fetch courses');
    return response.json();
  },

  createCourse: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/courses/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create course');
    }
    return response.json();
  },

  getCourse: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/courses/${id}`);
    if (!response.ok) throw new Error('Failed to fetch course');
    return response.json();
  },

  updateCourse: async (id: number, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/courses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update course');
    }
    return response.json();
  },

  deleteCourse: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/courses/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete course');
    }
    return response.json();
  },

  // ===== SECTIONS =====
  getSections: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/sections/`);
    if (!response.ok) throw new Error('Failed to fetch sections');
    return response.json();
  },

  createSection: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/sections/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create section');
    }
    return response.json();
  },

  updateSection: async (id: number, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/sections/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update section');
    }
    return response.json();
  },

  deleteSection: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/sections/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete section');
    }
    return response.json();
  },

  // ===== ROOMS =====
  getRooms: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/rooms/`);
    if (!response.ok) throw new Error('Failed to fetch rooms');
    return response.json();
  },

  createRoom: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/rooms/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create room');
    }
    return response.json();
  },

  updateRoom: async (id: number, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/rooms/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update room');
    }
    return response.json();
  },

  deleteRoom: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/rooms/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete room');
    }
    return response.json();
  },

  // ===== BUILDINGS =====
  getBuildings: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/buildings/`);
    if (!response.ok) throw new Error('Failed to fetch buildings');
    return response.json();
  },

  createBuilding: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/buildings/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create building');
    }
    return response.json();
  },

  // ===== TIMESLOTS =====
  getTimeslots: async () => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/timeslots/`);
    if (!response.ok) throw new Error('Failed to fetch timeslots');
    return response.json();
  },

  createTimeslot: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/master-data/timeslots/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create timeslot');
    }
    return response.json();
  },
};
