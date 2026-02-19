# HTTP API Client for interacting with backend

import requests
import logging
from typing import Dict, Any, Optional, List
from .config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """HTTP client for interacting with Task Stack and Assistant backend"""
    
    def __init__(self, base_url: str = BACKEND_BASE_URL):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url.rstrip('/')
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
    ) -> Dict[str, Any]:
        """
        Make HTTP request to backend
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
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
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise
    
    # Task Stack API methods
    
    def get_user_messages(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all user messages"""
        params = {'user_id': user_id} if user_id else None
        return self._request('GET', '/api/messages/list', params=params)
    
    def get_user_message(self, msg_id: str) -> Dict[str, Any]:
        """Get a specific user message"""
        return self._request('GET', f'/api/messages/{msg_id}')
    
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
        return self._request('GET', '/api/task-stack')
    
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
    
    # Assistant API methods
    
    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        additional_inputs: Optional[Dict[str, Any]] = None,
        assistant_id: Optional[str] = None  # Deprecated: kept for backward compatibility
    ) -> Dict[str, Any]:
        """
        Execute an agent for a task
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            additional_inputs: Optional additional inputs
            assistant_id: Deprecated - no longer needed (global assistant is used)
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
        return self._request('GET', f'/api/assistant/executions/task/{task_id}')
    
    def get_assistant(self, assistant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the global assistant instance
        
        Args:
            assistant_id: Deprecated - no longer needed (global assistant is used)
        """
        return self._request('GET', '/api/assistant')
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents"""
        return self._request('GET', '/api/assistant/sub-agents')
    
    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return self._request('GET', '/health')
