# Director Agent - Main orchestration logic

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .api_client import BackendAPIClient
from .reasoning import ReasoningEngine
from .config import (
    POLLING_INTERVAL,
    ASSISTANT_ID,
    DIRECTOR_AGENT_NAME
)

logger = logging.getLogger(__name__)


class DirectorAgent:
    """
    Director Agent - Responsible for reasoning, planning, and task orchestration
    
    The Director Agent:
    1. Monitors user messages and task stack
    2. Performs reasoning and planning
    3. Delegates tasks to Assistant Agent
    4. Receives execution summaries
    5. Triggers reflection phase
    6. Updates task stack based on results
    """
    
    def __init__(self, api_client: Optional[BackendAPIClient] = None):
        """
        Initialize Director Agent
        
        Args:
            api_client: Backend API client instance (creates new if None)
        """
        self.api_client = api_client or BackendAPIClient()
        self.reasoning_engine = ReasoningEngine()
        self.running = False
        self.last_message_check_time: Optional[datetime] = None
        
        logger.info(f"{DIRECTOR_AGENT_NAME} initialized")
    
    def start(self):
        """Start the Director Agent main loop"""
        logger.info(f"{DIRECTOR_AGENT_NAME} starting...")
        self.running = True
        
        # Health check
        try:
            health = self.api_client.health_check()
            logger.info(f"Backend health check: {health}")
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            logger.error("Make sure the backend is running on the configured URL")
            return
        
        # Main loop
        while self.running:
            try:
                self._cycle()
                time.sleep(POLLING_INTERVAL)
            except KeyboardInterrupt:
                logger.info(f"{DIRECTOR_AGENT_NAME} stopping...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(POLLING_INTERVAL)
    
    def stop(self):
        """Stop the Director Agent"""
        logger.info(f"{DIRECTOR_AGENT_NAME} stopping...")
        self.running = False
    
    def _cycle(self):
        """
        Single cycle of the Director Agent
        
        This implements the main flow:
        1. Check for new user messages
        2. Check current task stack status
        3. Perform reasoning and planning
        4. Update task stack
        5. Get next task
        6. Delegate to Assistant Agent
        7. Handle execution summary
        8. Trigger reflection if needed
        9. Handle reflection summary
        """
        # Step 1: Check for new user messages
        new_messages = self._check_new_messages()
        
        # Step 2: Get current task stack status
        task_stack = self._get_task_stack()
        execution_pointer = self._get_execution_pointer()
        
        # Step 3: Perform reasoning and planning
        planning_result = self.reasoning_engine.reason_and_plan(
            user_message=new_messages[0] if new_messages else None,
            task_stack=task_stack,
            current_task=None  # Will be updated when we get next task
        )
        
        # Step 4: Update task stack based on planning
        if planning_result['action'] == 'create_task':
            self._create_tasks_from_planning(planning_result['task_updates'])
        
        # Step 5: Get next task to execute
        next_task_info = self._get_next_task()
        
        if next_task_info:
            # Step 6: Delegate to Assistant Agent
            execution_result = self._delegate_to_assistant(next_task_info)
            
            if execution_result:
                # Step 7: Handle execution summary
                self._handle_execution_summary(execution_result, next_task_info)
                
                # Step 8: Trigger reflection if needed
                if self.reasoning_engine.should_trigger_reflection(execution_result):
                    reflection_result = self._trigger_reflection(execution_result)
                    
                    if reflection_result:
                        # Step 9: Handle reflection summary
                        self._handle_reflection_summary(reflection_result)
                        
                        # Re-plan based on reflection
                        planning_result = self.reasoning_engine.reason_and_plan(
                            reflection_summary=reflection_result,
                            task_stack=task_stack
                        )
                        
                        # Update task stack based on reflection
                        if planning_result['action'] == 'update_plan':
                            self._update_task_stack_from_reflection(planning_result)
    
    def _check_new_messages(self) -> List[Dict[str, Any]]:
        """
        Check for new unread user messages
        
        Returns:
            List of new user messages
        """
        try:
            messages = self.api_client.get_user_messages()
            new_messages = [
                msg for msg in messages
                if msg.get('worker_read_status') == 'UNREAD'
            ]
            
            if new_messages:
                logger.info(f"Found {len(new_messages)} new user messages")
                # Mark messages as read
                for msg in new_messages:
                    try:
                        self.api_client.update_message_read_status(
                            msg['id'],
                            worker_read_status='READ'
                        )
                    except Exception as e:
                        logger.error(f"Failed to mark message {msg['id']} as read: {e}")
            
            return new_messages
        except Exception as e:
            logger.error(f"Error checking messages: {e}")
            return []
    
    def _get_task_stack(self) -> List[Dict[str, Any]]:
        """Get current task stack"""
        try:
            return self.api_client.get_task_stack()
        except Exception as e:
            logger.error(f"Error getting task stack: {e}")
            return []
    
    def _get_execution_pointer(self) -> Optional[Dict[str, Any]]:
        """Get current execution pointer"""
        try:
            return self.api_client.get_execution_pointer()
        except Exception as e:
            logger.error(f"Error getting execution pointer: {e}")
            return None
    
    def _get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task to execute"""
        try:
            return self.api_client.get_next_task()
        except Exception as e:
            logger.error(f"Error getting next task: {e}")
            return None
    
    def _create_tasks_from_planning(self, task_updates: List[Dict[str, Any]]):
        """
        Create tasks based on planning result
        
        Args:
            task_updates: List of task descriptions to create
        """
        for task_desc in task_updates:
            try:
                # Create task
                task = self.api_client.create_task(task_desc['description'])
                task_id = task['id']
                logger.info(f"Created task: {task_id}")
                
                # Create or get layer 0
                try:
                    layer = self.api_client.get_layer(0)
                except:
                    # Layer doesn't exist, create it
                    layer = self.api_client.create_layer(layer_index=0)
                
                # Add task to layer
                self.api_client.add_task_to_layer(0, task_id)
                logger.info(f"Added task {task_id} to layer 0")
                
                # Set execution pointer if not set
                pointer = self._get_execution_pointer()
                if not pointer:
                    self.api_client.set_execution_pointer(0, 0)
                    logger.info("Set execution pointer to layer 0, task 0")
                
            except Exception as e:
                logger.error(f"Error creating task: {e}")
    
    def _delegate_to_assistant(
        self,
        next_task_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Delegate task execution to Assistant Agent
        
        Args:
            next_task_info: Information about the next task to execute
            
        Returns:
            Execution result or None if failed
        """
        task_id = next_task_info.get('task_id')
        task = next_task_info.get('task')
        
        if not task_id:
            logger.error("No task_id in next_task_info")
            return None
        
        # Update task status to IN_PROGRESS
        try:
            self.api_client.update_task_status(task_id, 'IN_PROGRESS')
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
        
        # Select agent for task
        try:
            available_agents = self.api_client.get_all_agents()
            agent_id = self.reasoning_engine.select_agent_for_task(
                task or {},
                available_agents
            )
            
            if not agent_id:
                logger.error("No suitable agent found for task")
                self.api_client.update_task_status(task_id, 'FAILED')
                return None
            
            logger.info(f"Delegating task {task_id} to agent {agent_id}")
            
            # Execute agent
            execution_result = self.api_client.execute_agent(
                assistant_id=ASSISTANT_ID,
                agent_id=agent_id,
                task_id=task_id
            )
            
            logger.info(f"Task {task_id} execution completed: {execution_result.get('status')}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error delegating to assistant: {e}")
            try:
                self.api_client.update_task_status(task_id, 'FAILED')
            except:
                pass
            return None
    
    def _handle_execution_summary(
        self,
        execution_result: Dict[str, Any],
        task_info: Dict[str, Any]
    ):
        """
        Handle execution summary from Assistant Agent
        
        Args:
            execution_result: Result from task execution
            task_info: Information about the executed task
        """
        task_id = task_info.get('task_id')
        status = execution_result.get('status')
        
        logger.info(f"Handling execution summary for task {task_id}: {status}")
        
        # Update task status based on execution result
        try:
            if status == 'COMPLETED':
                self.api_client.update_task_status(task_id, 'COMPLETED')
                # Advance execution pointer
                self.api_client.advance_execution_pointer()
            elif status == 'FAILED':
                self.api_client.update_task_status(task_id, 'FAILED')
                # Advance execution pointer even on failure
                self.api_client.advance_execution_pointer()
        except Exception as e:
            logger.error(f"Error handling execution summary: {e}")
    
    def _trigger_reflection(
        self,
        execution_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger reflection phase
        
        Args:
            execution_result: Result from task execution
            
        Returns:
            Reflection result or None if failed
        """
        logger.info("Triggering reflection phase...")
        
        # Placeholder: Reflection is handled by Assistant Agent
        # In the actual implementation, this would call a reflection endpoint
        # For now, we'll simulate it by checking execution results
        
        task_id = execution_result.get('task_id') or execution_result.get('results', {}).get('task_id')
        
        if not task_id:
            logger.warning("No task_id in execution result, skipping reflection")
            return None
        
        # Get execution details for reflection
        try:
            executions = self.api_client.get_executions_by_task(task_id)
            if executions:
                # Use the latest execution
                latest_execution = executions[-1]
                
                # Create reflection summary
                reflection_summary = {
                    'task_id': task_id,
                    'execution_id': latest_execution.get('id'),
                    'status': latest_execution.get('status'),
                    'evaluation': 'Execution completed successfully' if latest_execution.get('status') == 'COMPLETED' else 'Execution failed',
                    'recommendations': []
                }
                
                logger.info(f"Reflection completed for task {task_id}")
                return reflection_summary
        except Exception as e:
            logger.error(f"Error triggering reflection: {e}")
        
        return None
    
    def _handle_reflection_summary(self, reflection_summary: Dict[str, Any]):
        """
        Handle reflection summary
        
        Args:
            reflection_summary: Summary from reflection phase
        """
        logger.info(f"Handling reflection summary: {reflection_summary.get('evaluation')}")
        
        # Reflection summary is used in the next reasoning cycle
        # This is handled in the main _cycle method
    
    def _update_task_stack_from_reflection(self, planning_result: Dict[str, Any]):
        """
        Update task stack based on reflection results
        
        Args:
            planning_result: Planning result from reasoning engine
        """
        logger.info("Updating task stack based on reflection")
        
        # Placeholder: Implement task stack updates based on reflection
        # This could involve creating new tasks, updating existing tasks, etc.
        
        if planning_result.get('task_updates'):
            self._create_tasks_from_planning(planning_result['task_updates'])
