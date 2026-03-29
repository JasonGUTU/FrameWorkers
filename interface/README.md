# Task Stack Frontend

Vue 3 frontend for Dynamic Task Stack system.

## Features

- **Chat Window**: Real-time chat interface similar to ChatGPT
  - User messages with text, images, files, and videos
  - Server messages with text, images, file links, and video playback
  - Support for local video file playback
  
- **Task Stack Monitor**: Real-time task execution monitoring
  - Layer-based task visualization
  - Color-coded task status (completed, current, future, failed)
  - Expandable layer view for task details
  
- **System Status**: System status display
  - Current execution information
  - Total task count
  - System state indicators

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build

```bash
npm run build
```

## Configuration

Update the API base URL in `src/services/api.js` if your backend is running on a different port:

```javascript
const API_BASE_URL = 'http://localhost:5002/api'
```

Task message API contract (`tasksAPI.pushMessage`) follows backend fields:
- required: `content`
- optional: `sender_type` (`user` / `director` / `subagent`)

This UI targets the **Task Stack + messages** HTTP API. **Sub-agent execution** (`POST /api/assistant/execute` with `agent_id`, `task_id`, `execute_fields`) is invoked by the **Director** process, not by this client; server-side **`input_bundle_v2`** / **`resolved_inputs`** assembly is documented in `dynamic-task-stack/src/assistant/README.md`.

## Project Structure

```
interface/
├── src/
│   ├── components/
│   │   ├── SystemStatus.vue      # System status module
│   │   ├── TaskStackMonitor.vue  # Task stack monitoring module
│   │   └── ChatWindow.vue        # Chat interface
│   ├── services/
│   │   ├── api.js                # API service
│   │   └── polling.js            # Long polling service
│   ├── App.vue                   # Main app component
│   ├── main.js                   # Entry point
│   └── style.css                 # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Features Details

### Long Polling
The application uses long polling to fetch real-time updates from the backend:
- Messages: Polled every 2 seconds
- Task Stack: Polled every 2-3 seconds
- Execution Pointer: Polled every 2 seconds

### Video Playback
Supports video playback from:
- HTTP/HTTPS URLs
- Local file:// URLs
- Base64 encoded video data

### Task Status Colors
- **Gray**: Completed tasks
- **Green**: Currently executing tasks
- **Blue**: Future/pending tasks
- **Red**: Failed tasks
- **Light Gray**: Cancelled tasks
