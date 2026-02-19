<template>
  <div class="chat-window">
    <div class="chat-header">
      <h2 class="chat-title">对话窗口</h2>
      <button 
        class="toggle-subagent-btn" 
        @click="toggleSubagentMessages"
        :title="subagentMessagesCollapsed ? '展开 Subagent 消息' : '折叠 Subagent 消息'"
      >
        {{ subagentMessagesCollapsed ? '展开 Subagent' : '折叠 Subagent' }}
      </button>
    </div>
    
    <div class="messages-container" ref="messagesContainer">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="[
          message.senderType,
          { 'subagent-collapsed': subagentMessagesCollapsed && message.senderType === 'subagent' }
        ]"
        v-show="!(subagentMessagesCollapsed && message.senderType === 'subagent')"
      >
        <div class="message-content">
          <!-- Text content -->
          <div v-if="message.content" class="message-text" v-html="formatMessage(message.content)"></div>
          
          <!-- Images -->
          <div v-if="message.images && message.images.length > 0" class="message-images">
            <img
              v-for="(img, index) in message.images"
              :key="index"
              :src="img"
              alt="Image"
              class="message-image"
              @click="openImageModal(img)"
            />
          </div>
          
          <!-- Files -->
          <div v-if="message.files && message.files.length > 0" class="message-files">
            <a
              v-for="(file, index) in message.files"
              :key="index"
              :href="file.url"
              target="_blank"
              class="message-file"
            >
              <span class="file-icon">📎</span>
              <span class="file-name">{{ file.name || file.url }}</span>
            </a>
          </div>
          
          <!-- Videos -->
          <div v-if="message.videos && message.videos.length > 0" class="message-videos">
            <video
              v-for="(video, index) in message.videos"
              :key="index"
              :src="video"
              controls
              class="message-video"
            >
              您的浏览器不支持视频播放
            </video>
          </div>
          
          <div class="message-meta">
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            <span v-if="message.senderType === 'user'" class="message-status">
              {{ message.user_read_status === 'READ' ? '✓✓' : '✓' }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <!-- Preview area for pending media -->
      <div v-if="pendingImages.length > 0 || pendingFiles.length > 0 || pendingVideos.length > 0" class="preview-area">
        <div v-if="pendingImages.length > 0" class="preview-section">
          <div class="preview-label">待发送图片:</div>
          <div class="preview-images">
            <div v-for="(img, index) in pendingImages" :key="index" class="preview-item">
              <img :src="img" alt="Preview" class="preview-image" />
              <button class="preview-remove" @click="removePendingImage(index)">×</button>
            </div>
          </div>
        </div>
        <div v-if="pendingVideos.length > 0" class="preview-section">
          <div class="preview-label">待发送视频:</div>
          <div class="preview-videos">
            <div v-for="(video, index) in pendingVideos" :key="index" class="preview-item">
              <video :src="video" class="preview-video" controls></video>
              <button class="preview-remove" @click="removePendingVideo(index)">×</button>
            </div>
          </div>
        </div>
        <div v-if="pendingFiles.length > 0" class="preview-section">
          <div class="preview-label">待发送文件:</div>
          <div class="preview-files">
            <div v-for="(file, index) in pendingFiles" :key="index" class="preview-file-item">
              <span class="file-icon">📎</span>
              <span class="file-name">{{ file.name }}</span>
              <button class="preview-remove" @click="removePendingFile(index)">×</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-toolbar">
        <button class="toolbar-btn" @click="triggerImageInput" title="上传图片">
          📷
        </button>
        <button class="toolbar-btn" @click="triggerFileInput" title="上传文件">
          📎
        </button>
        <button class="toolbar-btn" @click="triggerVideoInput" title="上传视频">
          🎥
        </button>
      </div>
      <textarea
        v-model="inputText"
        class="message-input"
        placeholder="输入消息..."
        @keydown.enter.exact.prevent="sendMessage"
        @keydown.shift.enter.exact="inputText += '\n'"
        rows="3"
      ></textarea>
      <div class="input-actions">
        <button class="send-btn" @click="sendMessage" :disabled="!canSend">
          发送
        </button>
      </div>
      
      <!-- Hidden file inputs -->
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        multiple
        style="display: none"
        @change="handleImageSelect"
      />
      <input
        ref="fileInput"
        type="file"
        multiple
        style="display: none"
        @change="handleFileSelect"
      />
      <input
        ref="videoInput"
        type="file"
        accept="video/*"
        multiple
        style="display: none"
        @change="handleVideoSelect"
      />
    </div>
    
    <!-- Image Modal -->
    <div v-if="selectedImage" class="image-modal" @click="selectedImage = null">
      <img :src="selectedImage" alt="Preview" class="modal-image" />
    </div>
  </div>
</template>

<script>
import { messagesAPI } from '../services/api'
import pollingService from '../services/polling'

export default {
  name: 'ChatWindow',
  data() {
    return {
      messages: [],
      inputText: '',
      pendingImages: [],
      pendingFiles: [],
      pendingVideos: [],
      selectedImage: null,
      userId: 'user_' + Date.now(), // Temporary user ID
      subagentMessagesCollapsed: false // Whether subagent messages are collapsed
    }
  },
  computed: {
    canSend() {
      return this.inputText.trim().length > 0 || 
             this.pendingImages.length > 0 || 
             this.pendingFiles.length > 0 ||
             this.pendingVideos.length > 0
    }
  },
  mounted() {
    this.loadMessages()
    this.startPolling()
  },
  beforeUnmount() {
    pollingService.stopPolling('chat-messages')
  },
  methods: {
    async loadMessages() {
      try {
        const response = await messagesAPI.list()
        this.messages = response.data.map(msg => this.formatMessageForDisplay(msg))
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      } catch (error) {
        console.error('Failed to load messages:', error)
      }
    },
    
    startPolling() {
      pollingService.startPolling(
        'chat-messages',
        () => messagesAPI.list(),
        2000,
        (data) => {
          this.messages = data.map(msg => this.formatMessageForDisplay(msg))
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      )
    },
    
    formatMessageForDisplay(msg) {
      // Parse message content to extract images, files, videos
      const content = msg.content || ''
      const images = []
      const files = []
      const videos = []
      
      // Extract image data URLs (base64)
      const imageDataUrlRegex = /data:image\/[^;]+;base64,[^\s]+/gi
      const imageDataMatches = content.match(imageDataUrlRegex)
      if (imageDataMatches) {
        images.push(...imageDataMatches)
      }
      
      // Extract image URLs (http/https)
      const imageUrlRegex = /https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|webp|bmp)/gi
      const imageUrlMatches = content.match(imageUrlRegex)
      if (imageUrlMatches) {
        images.push(...imageUrlMatches)
      }
      
      // Extract file data URLs
      const fileDataUrlRegex = /data:[^;]+;base64,[^\s]+(?=\s*\[File:)/gi
      const fileDataMatches = content.match(fileDataUrlRegex)
      if (fileDataMatches) {
        fileDataMatches.forEach((url, index) => {
          const fileMatch = content.match(/\[File: ([^\]]+)\]/g)
          const fileName = fileMatch && fileMatch[index] ? fileMatch[index].replace(/\[File: |\]/g, '') : 'file'
          files.push({ url, name: fileName })
        })
      }
      
      // Extract file links (http/https)
      const fileUrlRegex = /https?:\/\/[^\s]+\.(pdf|doc|docx|txt|zip|rar|tar|gz)/gi
      const fileUrlMatches = content.match(fileUrlRegex)
      if (fileUrlMatches) {
        fileUrlMatches.forEach(url => {
          files.push({ url, name: url.split('/').pop() })
        })
      }
      
      // Extract video data URLs (base64)
      const videoDataUrlRegex = /data:video\/[^;]+;base64,[^\s]+/gi
      const videoDataMatches = content.match(videoDataUrlRegex)
      if (videoDataMatches) {
        videos.push(...videoDataMatches)
      }
      
      // Extract video URLs (http/https and file://)
      const videoUrlRegex = /(https?:\/\/[^\s]+\.(mp4|webm|ogg|avi|mov)|file:\/\/[^\s]+\.(mp4|webm|ogg|avi|mov))/gi
      const videoUrlMatches = content.match(videoUrlRegex)
      if (videoUrlMatches) {
        videos.push(...videoUrlMatches)
      }
      
      // Remove media URLs from text content
      let textContent = content
      if (images.length > 0 || files.length > 0 || videos.length > 0) {
        textContent = content
          .replace(imageDataUrlRegex, '')
          .replace(imageUrlRegex, '')
          .replace(fileDataUrlRegex, '')
          .replace(fileUrlRegex, '')
          .replace(videoDataUrlRegex, '')
          .replace(videoUrlRegex, '')
          .replace(/\[File: [^\]]+\]/g, '')
          .trim()
      }
      
      // Determine sender type and display class
      const senderType = msg.sender_type || (msg.user_id === this.userId ? 'user' : 'director')
      
      return {
        ...msg,
        content: textContent,
        senderType: senderType,
        images,
        files,
        videos
      }
    },
    
    formatMessage(text) {
      // Simple markdown-like formatting
      return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
    },
    
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      
      return date.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    async sendMessage() {
      if (!this.canSend) return
      
      let content = this.inputText.trim()
      
      // Add images to content (as data URLs)
      if (this.pendingImages.length > 0) {
        const imageText = this.pendingImages.map(img => img).join('\n')
        content = content ? `${content}\n\n${imageText}` : imageText
      }
      
      // Add files to content (as data URLs)
      if (this.pendingFiles.length > 0) {
        const fileText = this.pendingFiles.map(file => `${file.url} [File: ${file.name}]`).join('\n')
        content = content ? `${content}\n\n${fileText}` : fileText
      }
      
      // Add videos to content (as data URLs)
      if (this.pendingVideos.length > 0) {
        const videoText = this.pendingVideos.map(video => video).join('\n')
        content = content ? `${content}\n\n${videoText}` : videoText
      }
      
      if (!content) return
      
      try {
        await messagesAPI.create(content, this.userId)
        this.inputText = ''
        this.pendingImages = []
        this.pendingFiles = []
        this.pendingVideos = []
        this.loadMessages()
      } catch (error) {
        console.error('Failed to send message:', error)
        alert('发送消息失败，请重试')
      }
    },
    
    triggerImageInput() {
      this.$refs.imageInput.click()
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    triggerVideoInput() {
      this.$refs.videoInput.click()
    },
    
    handleImageSelect(event) {
      const files = Array.from(event.target.files)
      files.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.pendingImages.push(e.target.result)
        }
        reader.readAsDataURL(file)
      })
      event.target.value = ''
    },
    
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      files.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.pendingFiles.push({
            url: e.target.result,
            name: file.name
          })
        }
        reader.readAsDataURL(file)
      })
      event.target.value = ''
    },
    
    handleVideoSelect(event) {
      const files = Array.from(event.target.files)
      files.forEach(file => {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.pendingVideos.push(e.target.result)
        }
        reader.readAsDataURL(file)
      })
      event.target.value = ''
    },
    
    openImageModal(imageSrc) {
      this.selectedImage = imageSrc
    },
    
    removePendingImage(index) {
      this.pendingImages.splice(index, 1)
    },
    
    removePendingVideo(index) {
      this.pendingVideos.splice(index, 1)
    },
    
    removePendingFile(index) {
      this.pendingFiles.splice(index, 1)
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    toggleSubagentMessages() {
      this.subagentMessagesCollapsed = !this.subagentMessagesCollapsed
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    }
  }
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #ffffff;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.toggle-subagent-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #ffffff;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-subagent-btn:hover {
  background-color: #f5f5f5;
  border-color: #c0c0c0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #f9f9f9;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
  animation: fadeIn 0.3s;
}

/* User messages: right side, green bubble */
.message-item.user {
  justify-content: flex-end;
}

.message-item.user .message-content {
  background-color: #4CAF50;
  color: white;
  border-bottom-right-radius: 4px;
}

/* Director messages: left side, light blue background */
.message-item.director {
  justify-content: flex-start;
}

.message-item.director .message-content {
  background-color: #E3F2FD;
  color: #333;
  border: 1px solid #BBDEFB;
  border-bottom-left-radius: 4px;
}

/* Subagent messages: left side, gray background */
.message-item.subagent {
  justify-content: flex-start;
}

.message-item.subagent .message-content {
  background-color: #F5F5F5;
  color: #333;
  border: 1px solid #E0E0E0;
  border-bottom-left-radius: 4px;
}

/* Worker messages: left side, default style (for backward compatibility) */
.message-item.worker {
  justify-content: flex-start;
}

.message-item.worker .message-content {
  background-color: #ffffff;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message-text {
  line-height: 1.6;
  margin-bottom: 8px;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.message-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}

.message-image {
  max-width: 300px;
  max-height: 300px;
  border-radius: 8px;
  cursor: pointer;
  object-fit: contain;
}

.message-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 8px 0;
}

.message-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s;
}

.message-file:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.file-icon {
  font-size: 18px;
}

.file-name {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-videos {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 8px 0;
}

.message-video {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  background-color: #000;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.7;
}

.message-time {
  color: inherit;
}

.message-status {
  margin-left: 8px;
}

.input-area {
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  background-color: #ffffff;
}

.preview-area {
  margin-bottom: 12px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.preview-section {
  margin-bottom: 12px;
}

.preview-section:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.preview-images,
.preview-videos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-item {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.preview-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  display: block;
}

.preview-video {
  width: 200px;
  max-height: 150px;
  display: block;
}

.preview-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.preview-remove:hover {
  background-color: rgba(0, 0, 0, 0.9);
}

.preview-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  position: relative;
}

.preview-file-item .file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.input-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.toolbar-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #ffffff;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background-color: #f5f5f5;
  border-color: #c0c0c0;
}

.message-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #4A90E2;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.send-btn {
  padding: 10px 24px;
  background-color: #4A90E2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-btn:hover:not(:disabled) {
  background-color: #357ABD;
}

.send-btn:disabled {
  background-color: #c0c0c0;
  cursor: not-allowed;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: pointer;
}

.modal-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
