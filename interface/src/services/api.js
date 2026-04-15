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

// Plan Steps API
export const stepsAPI = {
  list: () => api.get('/steps/list'),
  get: (step_id) => api.get(`/steps/${step_id}`)
}

// Execution Pointer API
export const executionPointerAPI = {
  get: () => api.get('/execution-pointer/get')
}

// Plan Stack API
export const planStackAPI = {
  get: () => api.get('/plan-stack')
}

export default api
