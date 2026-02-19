<template>
  <div class="app-container">
    <!-- Left Sidebar -->
    <div class="sidebar">
      <!-- System Status Module -->
      <SystemStatus />
      
      <!-- Task Stack Monitor Module -->
      <TaskStackMonitor />
    </div>
    
    <!-- Right Chat Area -->
    <div class="chat-container">
      <ChatWindow />
    </div>
  </div>
</template>

<script>
import SystemStatus from './components/SystemStatus.vue'
import TaskStackMonitor from './components/TaskStackMonitor.vue'
import ChatWindow from './components/ChatWindow.vue'

export default {
  name: 'App',
  components: {
    SystemStatus,
    TaskStackMonitor,
    ChatWindow
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: #ffffff;
}

.sidebar {
  width: 350px;
  background-color: #fafafa;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden;
}
</style>
