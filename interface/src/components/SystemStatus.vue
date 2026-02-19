<template>
  <div class="system-status">
    <div class="logo-section">
      <div class="logo">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="8" fill="#4A90E2"/>
          <path d="M20 10L30 20L20 30L10 20L20 10Z" fill="white"/>
        </svg>
      </div>
      <h2 class="title">FrameWorkers</h2>
    </div>
    
    <div class="status-section">
      <div class="status-item">
        <span class="status-label">系统状态:</span>
        <span class="status-value" :class="statusClass">{{ systemStatus }}</span>
      </div>
      <div class="status-item" v-if="executionInfo">
        <span class="status-label">当前执行:</span>
        <span class="status-value">Layer {{ executionInfo.current_layer_index }}, Task {{ executionInfo.current_task_index }}</span>
      </div>
      <div class="status-item" v-if="totalTasks > 0">
        <span class="status-label">总任务数:</span>
        <span class="status-value">{{ totalTasks }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { taskStackAPI, executionPointerAPI } from '../services/api'
import pollingService from '../services/polling'

export default {
  name: 'SystemStatus',
  data() {
    return {
      systemStatus: '等待中',
      executionInfo: null,
      totalTasks: 0
    }
  },
  computed: {
    statusClass() {
      const status = this.systemStatus.toLowerCase()
      if (status.includes('执行')) return 'status-running'
      if (status.includes('等待')) return 'status-waiting'
      if (status.includes('完成')) return 'status-completed'
      return 'status-default'
    }
  },
  mounted() {
    this.startPolling()
  },
  beforeUnmount() {
    pollingService.stopPolling('system-status')
  },
  methods: {
    startPolling() {
      // Poll execution pointer
      pollingService.startPolling(
        'execution-pointer',
        () => executionPointerAPI.get(),
        2000,
        (data) => {
          if (data && !data.message) {
            this.executionInfo = data
            this.systemStatus = '正在执行'
          } else {
            this.executionInfo = null
            this.systemStatus = '等待中'
          }
        }
      )

      // Poll task stack
      pollingService.startPolling(
        'task-stack',
        () => taskStackAPI.get(),
        3000,
        (data) => {
          if (Array.isArray(data)) {
            let count = 0
            data.forEach(layer => {
              count += layer.tasks ? layer.tasks.length : 0
            })
            this.totalTasks = count
          }
        }
      )
    }
  }
}
</script>

<style scoped>
.system-status {
  padding: 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  min-height: 180px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.status-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.status-label {
  color: #666;
  font-weight: 500;
}

.status-value {
  color: #333;
  font-weight: 600;
}

.status-value.status-running {
  color: #4CAF50;
}

.status-value.status-waiting {
  color: #FF9800;
}

.status-value.status-completed {
  color: #2196F3;
}

.status-value.status-default {
  color: #666;
}
</style>
