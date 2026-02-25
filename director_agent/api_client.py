# HTTP API Client for interacting with backend

import requests
import logging
from typing import Dict, Any, Optional, List
from .config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)


class BackendAPIError(RuntimeError):
    """Raised when backend response is invalid or unexpected."""


class BackendAPIClient:
    """HTTP client for interacting with Task Stack and Assistant backend"""
    
    def __init__(self, base_url: str = BACKEND_BASE_URL, timeout: float = 30.0):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make HTTP request to backend
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data (dict/list/scalar)
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as exc:
                raise BackendAPIError(
                    f"Non-JSON response from backend: {method} {endpoint}"
                ) from exc
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise
    
    # Task Stack API methods
    
    def get_user_messages(self) -> List[Dict[str, Any]]:
        """Get all user messages"""
        response = self._request('GET', '/api/messages/list')
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/messages/list")
    
    def get_user_message(self, msg_id: str) -> Dict[str, Any]:
        """Get a specific user message"""
        return self._request('GET', f'/api/messages/{msg_id}')

    def get_unread_messages(
        self,
        sender_type: Optional[str] = None,
        check_director_read: bool = True,
        check_user_read: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get unread messages with route-level filtering."""
        params: Dict[str, Any] = {
            "check_director_read": str(check_director_read).lower(),
            "check_user_read": str(check_user_read).lower(),
        }
        if sender_type:
            params["sender_type"] = sender_type
        response = self._request('GET', '/api/messages/unread', params=params)
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/messages/unread")
    
    def check_user_message(self, msg_id: str) -> Dict[str, Any]:
        """Check user message (data structure, read status, is new task)"""
        return self._request('GET', f'/api/messages/{msg_id}/check')
    
    def update_message_read_status(
        self,
        msg_id: str,
        director_read_status: Optional[str] = None,
        user_read_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update message read status"""
        data = {}
        if director_read_status:
            data['director_read_status'] = director_read_status
        if user_read_status:
            data['user_read_status'] = user_read_status
        return self._request('PUT', f'/api/messages/{msg_id}/read-status', data=data)
    
    def get_task_stack(self) -> List[Dict[str, Any]]:
        """Get all layers in task stack"""
        response = self._request('GET', '/api/task-stack')
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/task-stack")
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task to execute"""
        response = self._request('GET', '/api/task-stack/next')
        if 'message' in response and 'No tasks' in response['message']:
            return None
        return response
    
    def get_execution_pointer(self) -> Optional[Dict[str, Any]]:
        """Get current execution pointer"""
        response = self._request('GET', '/api/execution-pointer/get')
        if 'message' in response and 'No execution pointer' in response['message']:
            return None
        return response
    
    def set_execution_pointer(
        self,
        layer_index: int,
        task_index: int,
        is_executing_pre_hook: bool = False,
        is_executing_post_hook: bool = False
    ) -> Dict[str, Any]:
        """Set execution pointer"""
        data = {
            'layer_index': layer_index,
            'task_index': task_index,
            'is_executing_pre_hook': is_executing_pre_hook,
            'is_executing_post_hook': is_executing_post_hook
        }
        return self._request('PUT', '/api/execution-pointer/set', data=data)
    
    def advance_execution_pointer(self) -> Dict[str, Any]:
        """Advance execution pointer to next task"""
        return self._request('POST', '/api/execution-pointer/advance')
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a task by ID"""
        return self._request('GET', f'/api/tasks/{task_id}')
    
    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """Update task status"""
        data = {'status': status}
        return self._request('PUT', f'/api/tasks/{task_id}/status', data=data)
    
    def create_task(self, description: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        data = {'description': description}
        return self._request('POST', '/api/tasks/create', data=data)

    def push_task_message(
        self,
        task_id: str,
        sender: str,
        message: str
    ) -> Dict[str, Any]:
        """Push progress/message entry into task."""
        data = {"sender": sender, "message": message}
        return self._request('POST', f'/api/tasks/{task_id}/messages', data=data)
    
    def create_layer(
        self,
        layer_index: Optional[int] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new task layer"""
        data = {}
        if layer_index is not None:
            data['layer_index'] = layer_index
        if pre_hook:
            data['pre_hook'] = pre_hook
        if post_hook:
            data['post_hook'] = post_hook
        return self._request('POST', '/api/layers/create', data=data)
    
    def add_task_to_layer(
        self,
        layer_index: int,
        task_id: str,
        insert_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add a task to a layer"""
        data = {'task_id': task_id}
        if insert_index is not None:
            data['insert_index'] = insert_index
        return self._request('POST', f'/api/layers/{layer_index}/tasks', data=data)
    
    def get_layer(self, layer_index: int) -> Dict[str, Any]:
        """Get a specific layer"""
        return self._request('GET', f'/api/layers/{layer_index}')

    def insert_layer_with_tasks(
        self,
        insert_layer_index: int,
        task_ids: Optional[List[str]] = None,
        pre_hook: Optional[Dict[str, Any]] = None,
        post_hook: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Insert layer and optionally attach tasks atomically."""
        data: Dict[str, Any] = {"insert_layer_index": insert_layer_index}
        if task_ids is not None:
            data["task_ids"] = task_ids
        if pre_hook is not None:
            data["pre_hook"] = pre_hook
        if post_hook is not None:
            data["post_hook"] = post_hook
        return self._request('POST', '/api/task-stack/insert-layer', data=data)

    def modify_task_stack(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform atomic batch task-stack modifications."""
        return self._request('POST', '/api/task-stack/modify', data={"operations": operations})
    
    # Assistant API methods
    
    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        additional_inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent for a task
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            additional_inputs: Optional additional inputs
        """
        data = {
            'agent_id': agent_id,
            'task_id': task_id
        }
        if additional_inputs:
            data['additional_inputs'] = additional_inputs
        return self._request('POST', '/api/assistant/execute', data=data)
    
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution by ID"""
        return self._request('GET', f'/api/assistant/executions/{execution_id}')
    
    def get_executions_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all executions for a task"""
        response = self._request('GET', f'/api/assistant/executions/task/{task_id}')
        if isinstance(response, list):
            return response
        raise BackendAPIError(f"Expected list from /api/assistant/executions/task/{task_id}")
    
    def get_assistant(self) -> Dict[str, Any]:
        """
        Get the global assistant instance
        """
        return self._request('GET', '/api/assistant')
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents as a flat list."""
        response = self._request('GET', '/api/assistant/sub-agents')
        if isinstance(response, dict):
            agents = response.get('agents')
            if isinstance(agents, list):
                return agents
        if isinstance(response, list):
            return response
        raise BackendAPIError("Unexpected response shape from /api/assistant/sub-agents")

    def get_sub_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get metadata for one sub-agent."""
        response = self._request('GET', f'/api/assistant/sub-agents/{agent_id}')
        if isinstance(response, dict):
            return response
        raise BackendAPIError(f"Expected object from /api/assistant/sub-agents/{agent_id}")

    def get_agent_inputs(self, agent_id: str) -> Dict[str, Any]:
        """Get input contract for one sub-agent."""
        response = self._request('GET', f'/api/assistant/agents/{agent_id}/inputs')
        if isinstance(response, dict):
            return response
        raise BackendAPIError(f"Expected object from /api/assistant/agents/{agent_id}/inputs")

    # Workspace API helpers
    def get_workspace_summary(self) -> Dict[str, Any]:
        """Get assistant workspace summary."""
        response = self._request('GET', '/api/assistant/workspace/summary')
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from /api/assistant/workspace/summary")

    def get_workspace(self) -> Dict[str, Any]:
        """Get assistant workspace summary alias endpoint."""
        response = self._request('GET', '/api/assistant/workspace')
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from /api/assistant/workspace")

    def get_workspace_files(
        self,
        file_type: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List files in assistant workspace."""
        params: Dict[str, Any] = {}
        if file_type:
            params["file_type"] = file_type
        if created_by:
            params["created_by"] = created_by
        if limit is not None:
            params["limit"] = limit
        if tags:
            params["tags"] = tags
        response = self._request('GET', '/api/assistant/workspace/files', params=params or None)
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/assistant/workspace/files")

    def get_workspace_memory(self) -> Dict[str, Any]:
        """Read assistant workspace memory."""
        response = self._request('GET', '/api/assistant/workspace/memory')
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from /api/assistant/workspace/memory")

    def get_workspace_file(self, file_id: str) -> Dict[str, Any]:
        """Get one workspace file metadata by id."""
        response = self._request('GET', f'/api/assistant/workspace/files/{file_id}')
        if isinstance(response, dict):
            return response
        raise BackendAPIError(f"Expected object from /api/assistant/workspace/files/{file_id}")

    def search_workspace_files(
        self,
        query: str,
        file_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search workspace files by textual query."""
        params: Dict[str, Any] = {"query": query, "limit": limit}
        if file_type:
            params["file_type"] = file_type
        response = self._request('GET', '/api/assistant/workspace/files/search', params=params)
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/assistant/workspace/files/search")

    def write_workspace_memory(self, content: str, append: bool = False) -> Dict[str, Any]:
        """Write assistant workspace memory."""
        response = self._request(
            'POST',
            '/api/assistant/workspace/memory',
            data={"content": content, "append": append},
        )
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from POST /api/assistant/workspace/memory")

    def get_workspace_logs(
        self,
        operation_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get workspace logs with optional filters."""
        params: Dict[str, Any] = {}
        if operation_type:
            params["operation_type"] = operation_type
        if resource_type:
            params["resource_type"] = resource_type
        if agent_id:
            params["agent_id"] = agent_id
        if task_id:
            params["task_id"] = task_id
        if limit is not None:
            params["limit"] = limit
        response = self._request('GET', '/api/assistant/workspace/logs', params=params or None)
        if isinstance(response, list):
            return response
        raise BackendAPIError("Expected list from /api/assistant/workspace/logs")

    def search_workspace(
        self,
        query: str,
        types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run comprehensive workspace search across files/memory/logs."""
        params: Dict[str, Any] = {"query": query}
        if types:
            params["types"] = types
        response = self._request('GET', '/api/assistant/workspace/search', params=params)
        if isinstance(response, dict):
            return response
        raise BackendAPIError("Expected object from /api/assistant/workspace/search")
    
    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return self._request('GET', '/health')
