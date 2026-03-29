# Director Agent - Main orchestration logic

import logging
import time
import json
from typing import Dict, Any, Optional, List

from .api_client import BackendAPIClient
from .reasoning import LlmSubAgentPlanner, ReasoningEngine
from .config import (
    POLLING_INTERVAL,
    DIRECTOR_AGENT_NAME,
)

logger = logging.getLogger(__name__)


def _task_stack_description_to_assistant_text(raw: Any) -> str:
    """Task Stack 里 ``description`` 当前多为 **dict**；Assistant 的 ``execute_fields.text`` 仅为 **str**。

    仅在此处做一层对齐（不在 Assistant 里做结构化解析）。若已是字符串则原样；
    若为 dict 则优先使用常见的 ``goal`` 字符串；否则退回 JSON 文本以便不丢信息。
    """
    if raw is None or raw == "":
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        g = raw.get("goal")
        if isinstance(g, str) and g.strip():
            return g.strip()
        return json.dumps(raw, ensure_ascii=False)
    return str(raw).strip()


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
    
    def __init__(
        self,
        api_client: Optional[BackendAPIClient] = None,
        sub_agent_planner: Optional[LlmSubAgentPlanner] = None,
    ):
        """
        Initialize Director Agent
        
        Args:
            api_client: Backend API client instance (creates new if None)
            sub_agent_planner: LLM router for ``agent_id`` (tests may inject a mock)
        """
        self.api_client = api_client or BackendAPIClient()
        self.reasoning_engine = ReasoningEngine()
        self._sub_agent_planner = sub_agent_planner or LlmSubAgentPlanner()
        self.running = False
        
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
        # Step 1: If any task is still running, wait for completion first.
        if self._has_in_progress_tasks():
            logger.info("Detected running sub-agent execution; defer new planning this cycle")
            return

        # Step 2: Check for new user messages
        new_messages = self._check_new_messages()
        
        # Step 3: Get current task stack status
        task_stack = self._get_task_stack()

        latest_message = new_messages[-1] if new_messages else None
        target_task_id = self._extract_target_task_id(latest_message) if latest_message else None
        task_summary = self._get_latest_task_execution_summary(target_task_id) if target_task_id else None
        memory_brief = self._get_memory_brief_for_task(target_task_id)
        global_memory = memory_brief.get("global_memory", []) if isinstance(memory_brief, dict) else []

        # Step 4: Perform reasoning and planning
        planning_result = self.reasoning_engine.reason_and_plan(
            user_message=latest_message,
            task_stack=task_stack,
            task_summary=task_summary,
            global_memory=global_memory,
        )
        
        # Step 5: Update task stack based on planning
        if planning_result['action'] == 'create_task':
            self._create_tasks_from_planning(planning_result['task_updates'])
        elif planning_result['action'] == 'execute_task' and planning_result.get('target_task_id'):
            self._execute_existing_task_from_planning(planning_result)
            return
        
        # Step 6: Get next task to execute
        next_task_info = self._get_next_task()
        
        if next_task_info:
            # Step 7: Delegate to Assistant Agent
            execution_result = self._delegate_to_assistant(next_task_info)
            
            if execution_result:
                # Step 8: Handle execution summary
                self._handle_execution_summary(execution_result, next_task_info)
                
                # Step 9: Trigger reflection if needed
                if self.reasoning_engine.should_trigger_reflection(execution_result):
                    reflection_result = self._trigger_reflection(execution_result)
                    
                    if reflection_result:
                        # Step 10: Handle reflection summary
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
            new_messages = self.api_client.get_unread_messages(
                sender_type='user',
                check_director_read=True,
                check_user_read=False,
            )
            
            if new_messages:
                logger.info(f"Found {len(new_messages)} new user messages")
                # Mark messages as read
                for msg in new_messages:
                    try:
                        self.api_client.update_message_read_status(
                            msg['id'],
                            director_read_status='READ'
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

    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        try:
            return self.api_client.get_all_tasks()
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
            return []

    def _has_in_progress_tasks(self) -> bool:
        """Whether there is any ongoing task execution."""
        tasks = self._get_all_tasks()
        return any(task.get("status") == "IN_PROGRESS" for task in tasks)

    @staticmethod
    def _extract_target_task_id(message: Optional[Dict[str, Any]]) -> Optional[str]:
        if not message:
            return None
        explicit_task_id = message.get("task_id")
        if explicit_task_id:
            return explicit_task_id
        raw_content = str(message.get("content", "") or "")
        if not raw_content:
            return None
        try:
            parsed = json.loads(raw_content)
        except Exception:
            return None
        if not isinstance(parsed, dict):
            return None
        parsed_task_id = parsed.get("task_id")
        if isinstance(parsed_task_id, str) and parsed_task_id:
            return parsed_task_id
        return None

    def _get_latest_task_execution_summary(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Fetch latest assistant execution summary for one task."""
        try:
            executions = self.api_client.get_executions_by_task(task_id)
        except Exception as e:
            logger.warning("Failed to fetch executions for task %s: %s", task_id, e)
            return None
        if not executions:
            return None
        latest = executions[-1]
        return {
            "task_id": task_id,
            "execution_id": latest.get("id"),
            "status": latest.get("status"),
            "agent_id": latest.get("agent_id"),
            "results": latest.get("results"),
            "error": latest.get("error"),
        }
    
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
                    self.api_client.get_layer(0)
                except:
                    # Layer doesn't exist, create it
                    self.api_client.create_layer(layer_index=0)
                
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

    def _execute_existing_task_from_planning(self, planning_result: Dict[str, Any]) -> None:
        """
        Execute one agent for an existing task from a user follow-up message.

        Expected planning_result payload:
        {
            "target_task_id": "task_xxx",
            "message_content": "..."
        }
        Sub-agent id is chosen by ``LlmSubAgentPlanner`` (catalog + global_memory brief).
        """
        task_id = planning_result.get("target_task_id")
        message_content = str(planning_result.get("message_content", "") or "")

        if not task_id:
            logger.warning("execute_task action missing target_task_id")
            return
        task = self.api_client.get_task(task_id)

        next_task_info = {
            "task_id": task_id,
            "task": task,
        }
        execution_result = self._delegate_to_assistant(
            next_task_info,
            message_content=message_content,
            routing_mode="followup",
        )
        if execution_result:
            self._handle_execution_summary(
                execution_result,
                next_task_info,
                advance_pointer=False,
            )

    def _build_assistant_inputs_for_execution(
        self,
        *,
        task: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Build ``execute_fields`` for Assistant. Global memory is loaded server-side in ``build_execution_inputs``."""
        execute_fields: Dict[str, Any] = {}
        execute_fields["text"] = _task_stack_description_to_assistant_text(task.get("description"))
        return execute_fields or None
    
    def _delegate_to_assistant(
        self,
        next_task_info: Dict[str, Any],
        message_content: str = "",
        *,
        routing_mode: str = "stack",
    ) -> Optional[Dict[str, Any]]:
        """
        Delegate task execution to Assistant Agent.

        ``routing_mode``:
        - ``stack`` — next task from execution pointer; route from task description + sub-agent catalog.
        - ``followup`` — user message tied to ``task_id``; route with catalog + ``global_memory`` brief + latest execution summary.
        """
        task_id = next_task_info.get('task_id')
        if not task_id:
            logger.error("No task_id in next_task_info")
            return None

        task = next_task_info.get("task")
        if not isinstance(task, dict):
            task = None
        if task is None:
            try:
                task = self.api_client.get_task(task_id)
            except Exception as e:
                logger.error("Failed to load task snapshot for assistant: %s", e)
                return None
        next_task_info["task"] = task

        # Update task status to IN_PROGRESS
        try:
            self.api_client.update_task_status(task_id, 'IN_PROGRESS')
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
        
        # Select agent for task
        try:
            available_agents = self.api_client.get_all_agents()
            if not available_agents:
                logger.error("No available sub-agents discovered from Assistant")
                self.api_client.update_task_status(task_id, 'FAILED')
                return None

            task_intent = _task_stack_description_to_assistant_text(task.get("description"))
            if routing_mode == "followup":
                brief = self._get_memory_brief_for_task(task_id)
                gm = brief.get("global_memory") if isinstance(brief, dict) else []
                if not isinstance(gm, list):
                    gm = []
                summary = self._get_latest_task_execution_summary(task_id)
                agent_id = self._sub_agent_planner.choose_for_followup(
                    message_content=message_content,
                    task_intent_text=task_intent,
                    available_agents=available_agents,
                    global_memory=gm,
                    execution_summary=summary,
                )
            else:
                agent_id = self._sub_agent_planner.choose_for_stack_task(
                    task_intent_text=task_intent,
                    available_agents=available_agents,
                )

            if not agent_id:
                logger.error("No suitable agent found for task (LLM routing returned none)")
                self.api_client.update_task_status(task_id, 'FAILED')
                return None
            
            logger.info(f"Delegating task {task_id} to agent {agent_id}")
            self.api_client.push_task_message(
                task_id=task_id,
                sender='director',
                message=f"Delegated to assistant agent {agent_id}"
            )
            assistant_inputs = self._build_assistant_inputs_for_execution(
                task=task,
            )
            
            # Execute agent (using global assistant)
            execution_result = self.api_client.execute_agent(
                agent_id=agent_id,
                task_id=task_id,
                execute_fields=assistant_inputs,
            )

            try:
                executions = self.api_client.get_executions_by_task(task_id)
                if executions:
                    execution_result["execution"] = executions[-1]
            except Exception as e:
                logger.warning("Failed to fetch latest execution detail for task %s: %s", task_id, e)
            
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
        task_info: Dict[str, Any],
        *,
        advance_pointer: bool = True,
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
                if advance_pointer:
                    self.api_client.advance_execution_pointer()
            elif status == 'FAILED':
                self.api_client.update_task_status(task_id, 'FAILED')
                # Advance execution pointer even on failure
                if advance_pointer:
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

    def _get_memory_brief_for_task(
        self,
        task_id: Optional[str],
    ) -> Dict[str, Any]:
        if not task_id:
            return {"global_memory": []}
        try:
            return self.api_client.get_workspace_memory_brief(
                task_id=task_id,
            )
        except Exception as exc:
            logger.warning("Failed to fetch workspace memory brief for task %s: %s", task_id, exc)
            return {"global_memory": []}

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
