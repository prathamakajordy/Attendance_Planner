import axios from 'axios';

// Base URL is loaded from the .env file (VITE_API_BASE_URL).
// TRD Section 15 defines this variable. Default to localhost for development.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Semester ──────────────────────────────────────────────────────────────
export const createSemester = (data) => apiClient.post('/semesters', data);
export const getSemester = (semesterId) => apiClient.get(`/semesters/${semesterId}`);
export const updateSemester = (semesterId, data) => apiClient.put(`/semesters/${semesterId}`, data);

// ── Subjects ──────────────────────────────────────────────────────────────
export const createSubject = (semesterId, data) =>
  apiClient.post(`/semesters/${semesterId}/subjects`, data);
export const updateSubject = (subjectId, data) => apiClient.put(`/subjects/${subjectId}`, data);
export const deleteSubject = (subjectId) => apiClient.delete(`/subjects/${subjectId}`);

// ── Timetable ─────────────────────────────────────────────────────────────
export const createTimetableSlot = (semesterId, data) =>
  apiClient.post(`/semesters/${semesterId}/timetable`, data);
export const updateTimetableSlot = (slotId, data) => apiClient.put(`/timetable/${slotId}`, data);
export const deleteTimetableSlot = (slotId) => apiClient.delete(`/timetable/${slotId}`);

// ── Event Types ───────────────────────────────────────────────────────────
export const getEventTypes = () => apiClient.get('/event-types');

// ── Semester Events ───────────────────────────────────────────────────────
export const createSemesterEvent = (semesterId, data) =>
  apiClient.post(`/semesters/${semesterId}/events`, data);
export const getSemesterEvents = (semesterId) =>
  apiClient.get(`/semesters/${semesterId}/events`);
export const updateSemesterEvent = (eventId, data) => apiClient.put(`/events/${eventId}`, data);
export const deleteSemesterEvent = (eventId) => apiClient.delete(`/events/${eventId}`);

export default apiClient;
