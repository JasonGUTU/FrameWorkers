import axios from 'axios'

const API_BASE_URL = 'http://localhost:5002/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// User Messages API
export const messagesAPI = {
  create: (content, sender_type = 'user') => api.post('/messages/create', { content, sender_type }),
  list: () => api.get('/messages/list')
}

// Tasks API
export const tasksAPI = {
  list: () => api.get('/tasks/list'),
  get: (task_id) => api.get(`/tasks/${task_id}`)
}

// Execution Pointer API
export const executionPointerAPI = {
  get: () => api.get('/execution-pointer/get')
}

// Task Stack API
export const taskStackAPI = {
  get: () => api.get('/task-stack')
}

export default api
