<template>
  <div class="task-stack-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">任务执行监控</h3>
    </div>
    
    <div class="layers-container">
      <div
        v-for="layer in layers"
        :key="layer.layer_index"
        class="layer-item"
      >
        <div class="layer-header">
          <span class="layer-index">Layer {{ layer.layer_index }}</span>
          <span class="layer-task-count">{{ layer.tasks ? layer.tasks.length : 0 }} tasks</span>
        </div>
        
        <div class="layer-tasks">
          <div
            v-for="(taskEntry, index) in layer.tasks"
            :key="taskEntry.task_id"
            class="task-item"
            :class="getTaskStatusClass(taskEntry.task_id)"
            @click="toggleTask(taskEntry.task_id)"
          >
            <div class="task-header">
              <span class="task-id">Task {{ index }}</span>
              <span class="task-toggle">{{ expandedTasks.has(taskEntry.task_id) ? '−' : '+' }}</span>
            </div>
            <div class="task-status-badge">{{ getTaskStatus(taskEntry.task_id) }}</div>
            <div
              v-if="expandedTasks.has(taskEntry.task_id)"
              class="task-details"
            >
              <div class="task-description" v-if="getTaskDescription(taskEntry.task_id)">
                <strong>描述:</strong> {{ getTaskDescription(taskEntry.task_id) }}
              </div>
              <div class="task-progress" v-if="getTaskProgress(taskEntry.task_id)">
                <strong>进度:</strong> {{ JSON.stringify(getTaskProgress(taskEntry.task_id)) }}
              </div>
              <div class="task-results" v-if="getTaskResults(taskEntry.task_id)">
                <strong>结果:</strong> {{ JSON.stringify(getTaskResults(taskEntry.task_id)) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="layers.length === 0" class="empty-state">
        <p>暂无任务</p>
      </div>
    </div>
  </div>
</template>

<script>
import { taskStackAPI, tasksAPI, executionPointerAPI } from '../services/api'
import pollingService from '../services/polling'

export default {
  name: 'TaskStackMonitor',
  data() {
    return {
      layers: [],
      tasks: {},
      executionPointer: null,
      expandedTasks: new Set()
    }
  },
  mounted() {
    this.startPolling()
  },
  beforeUnmount() {
    pollingService.stopPolling('task-stack-monitor')
  },
  methods: {
    startPolling() {
      // Poll task stack
      pollingService.startPolling(
        'task-stack-monitor',
        () => taskStackAPI.get(),
        2000,
        async (data) => {
          if (Array.isArray(data)) {
            this.layers = data
            
            // Fetch task details for all tasks
            for (const layer of data) {
              if (layer.tasks) {
                for (const taskEntry of layer.tasks) {
                  if (!this.tasks[taskEntry.task_id]) {
                    try {
                      const response = await tasksAPI.get(taskEntry.task_id)
                      this.$set(this.tasks, taskEntry.task_id, response.data)
                    } catch (error) {
                      console.error(`Failed to fetch task ${taskEntry.task_id}:`, error)
                    }
                  }
                }
              }
            }
          }
        }
      )

      // Poll execution pointer
      pollingService.startPolling(
        'execution-pointer-monitor',
        () => executionPointerAPI.get(),
        2000,
        (data) => {
          if (data && !data.message) {
            this.executionPointer = data
          } else {
            this.executionPointer = null
          }
        }
      )
    },
    
    toggleTask(taskId) {
      if (this.expandedTasks.has(taskId)) {
        this.expandedTasks.delete(taskId)
      } else {
        this.expandedTasks.add(taskId)
      }
    },
    
    getTaskProgress(taskId) {
      const task = this.tasks[taskId]
      if (!task || !task.progress) return null
      return task.progress
    },
    
    getTaskResults(taskId) {
      const task = this.tasks[taskId]
      if (!task || !task.results) return null
      return task.results
    },
    
    getTaskStatus(taskId) {
      const task = this.tasks[taskId]
      if (!task) return 'UNKNOWN'
      return task.status || 'PENDING'
    },
    
    getTaskDescription(taskId) {
      const task = this.tasks[taskId]
      if (!task || !task.description) return ''
      return task.description.overall_description || ''
    },
    
    getTaskStatusClass(taskId) {
      const task = this.tasks[taskId]
      if (!task) return 'task-unknown'
      
      const status = task.status
      const isCurrent = this.isCurrentTask(taskId)
      
      if (isCurrent) return 'task-current'
      if (status === 'COMPLETED') return 'task-completed'
      if (status === 'FAILED') return 'task-failed'
      if (status === 'CANCELLED') return 'task-cancelled'
      if (status === 'IN_PROGRESS') return 'task-in-progress'
      if (this.isFutureTask(taskId)) return 'task-future'
      return 'task-pending'
    },
    
    isCurrentTask(taskId) {
      if (!this.executionPointer) return false
      
      const layer = this.layers[this.executionPointer.current_layer_index]
      if (!layer || !layer.tasks) return false
      
      const currentTask = layer.tasks[this.executionPointer.current_task_index]
      return currentTask && currentTask.task_id === taskId
    },
    
    isFutureTask(taskId) {
      if (!this.executionPointer) return false
      
      const execLayer = this.executionPointer.current_layer_index
      const execTask = this.executionPointer.current_task_index
      
      for (let i = 0; i < this.layers.length; i++) {
        const layer = this.layers[i]
        if (!layer.tasks) continue
        
        for (let j = 0; j < layer.tasks.length; j++) {
          if (layer.tasks[j].task_id === taskId) {
            if (i > execLayer) return true
            if (i === execLayer && j > execTask) return true
            return false
          }
        }
      }
      return false
    }
  }
}
</script>

<style scoped>
.task-stack-monitor {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #ffffff;
}

.monitor-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.monitor-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.layers-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.layer-item {
  margin-bottom: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #ffffff;
  overflow: hidden;
}

.layer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #e0e0e0;
}

.layer-index {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.layer-task-count {
  font-size: 12px;
  color: #666;
}

.layer-tasks {
  padding: 8px;
}

.task-item {
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 4px;
  border-left: 3px solid;
  background-color: #fafafa;
  transition: all 0.2s;
  cursor: pointer;
}

.task-item:hover {
  background-color: #f5f5f5;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.task-toggle {
  font-size: 16px;
  color: #666;
  font-weight: bold;
  width: 20px;
  text-align: center;
}

.task-status-badge {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.task-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #666;
}

.task-details > div {
  margin-bottom: 6px;
}

.task-progress,
.task-results {
  word-break: break-all;
  max-height: 100px;
  overflow-y: auto;
}

.task-item.task-completed {
  border-left-color: #9e9e9e;
  background-color: #f5f5f5;
  opacity: 0.7;
}

.task-item.task-current {
  border-left-color: #4CAF50;
  background-color: #e8f5e9;
  font-weight: 600;
}

.task-item.task-future {
  border-left-color: #2196F3;
  background-color: #e3f2fd;
}

.task-item.task-failed {
  border-left-color: #f44336;
  background-color: #ffebee;
}

.task-item.task-cancelled {
  border-left-color: #9e9e9e;
  background-color: #f5f5f5;
  text-decoration: line-through;
  opacity: 0.5;
}

.task-item.task-in-progress {
  border-left-color: #4CAF50;
  background-color: #e8f5e9;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.task-id {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.task-status {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.task-description {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
}
</style>
