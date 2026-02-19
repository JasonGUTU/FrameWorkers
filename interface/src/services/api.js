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
  create: (content, user_id, sender_type = 'user') => api.post('/messages/create', { content, user_id, sender_type }),
  list: (user_id = null) => {
    const params = user_id ? { user_id } : {}
    return api.get('/messages/list', { params })
  },
  get: (msg_id) => api.get(`/messages/${msg_id}`),
  unread: (options = {}) => {
    // options: { sender_type, user_id, target_user_id, check_director_read, check_user_read }
    // user_id: sender user_id (who sent the message)
    // target_user_id: target user_id (for user_read_status check)
    const params = {}
    if (options.sender_type) params.sender_type = options.sender_type
    if (options.user_id) params.user_id = options.user_id
    if (options.target_user_id) params.target_user_id = options.target_user_id
    if (options.check_director_read !== undefined) params.check_director_read = options.check_director_read
    if (options.check_user_read !== undefined) params.check_user_read = options.check_user_read
    return api.get('/messages/unread', { params })
  },
  updateReadStatus: (msg_id, director_read_status = null, user_read_status = null) => {
    const data = {}
    if (director_read_status) data.director_read_status = director_read_status
    if (user_read_status) data.user_read_status = user_read_status
    return api.put(`/messages/${msg_id}/read-status`, data)
  },
  check: (msg_id) => api.get(`/messages/${msg_id}/check`)
}

// Tasks API
export const tasksAPI = {
  create: (description) => api.post('/tasks/create', { description }),
  list: () => api.get('/tasks/list'),
  get: (task_id) => api.get(`/tasks/${task_id}`),
  update: (task_id, data) => api.put(`/tasks/${task_id}`, data),
  delete: (task_id) => api.delete(`/tasks/${task_id}`),
  updateStatus: (task_id, status) => api.put(`/tasks/${task_id}/status`, { status }),
  pushMessage: (task_id, content, user_id) => api.post(`/tasks/${task_id}/messages`, { content, user_id })
}

// Layers API
export const layersAPI = {
  create: (layer_index = null, pre_hook = null, post_hook = null) => {
    const data = {}
    if (layer_index !== null) data.layer_index = layer_index
    if (pre_hook) data.pre_hook = pre_hook
    if (post_hook) data.post_hook = post_hook
    return api.post('/layers/create', data)
  },
  list: () => api.get('/layers/list'),
  get: (layer_index) => api.get(`/layers/${layer_index}`),
  updateHooks: (layer_index, pre_hook = null, post_hook = null) => {
    const data = {}
    if (pre_hook) data.pre_hook = pre_hook
    if (post_hook) data.post_hook = post_hook
    return api.put(`/layers/${layer_index}/hooks`, data)
  },
  addTask: (layer_index, task_id, insert_index = null) => {
    const data = { task_id }
    if (insert_index !== null) data.insert_index = insert_index
    return api.post(`/layers/${layer_index}/tasks`, data)
  },
  removeTask: (layer_index, task_id) => api.delete(`/layers/${layer_index}/tasks/${task_id}`),
  replaceTask: (layer_index, old_task_id, new_task_id) => {
    return api.post(`/layers/${layer_index}/tasks/replace`, { old_task_id, new_task_id })
  }
}

// Execution Pointer API
export const executionPointerAPI = {
  get: () => api.get('/execution-pointer/get'),
  set: (layer_index, task_index, is_executing_pre_hook = false, is_executing_post_hook = false) => {
    return api.put('/execution-pointer/set', {
      layer_index,
      task_index,
      is_executing_pre_hook,
      is_executing_post_hook
    })
  },
  advance: () => api.post('/execution-pointer/advance')
}

// Task Stack API
export const taskStackAPI = {
  get: () => api.get('/task-stack'),
  getNext: () => api.get('/task-stack/next')
}

// Health Check
export const healthCheck = () => api.get('/health', { baseURL: 'http://localhost:5002' })

export default api
