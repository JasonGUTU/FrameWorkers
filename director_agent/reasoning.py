# Reasoning and Planning Module for Director Agent

import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

MESSAGE_KEYWORD_TO_AGENT = {
    "story": "StoryAgent",
    "screenplay": "ScreenplayAgent",
    "script": "ScreenplayAgent",
    "storyboard": "StoryboardAgent",
    "keyframe": "KeyFrameAgent",
    "image": "KeyFrameAgent",
    "video": "VideoAgent",
    "audio": "AudioAgent",
    "voice": "AudioAgent",
    "music": "AudioAgent",
}


class ReasoningEngine:
    """
    Reasoning engine for Director Agent
    
    This module handles reasoning and planning logic.
    Currently contains placeholder implementations.
    """

    def reason_and_plan(
        self,
        user_message: Optional[Dict[str, Any]] = None,
        task_stack: Optional[List[Dict[str, Any]]] = None,
        current_task: Optional[Dict[str, Any]] = None,
        task_summary: Optional[Dict[str, Any]] = None,
        reflection_summary: Optional[Dict[str, Any]] = None,
        short_term_memory: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Main reasoning and planning function
        
        This is a placeholder that will be implemented with actual reasoning logic.
        
        Args:
            user_message: Current user message (if any)
            task_stack: Current task stack state
            current_task: Current task being executed
            task_summary: Summary from task execution
            reflection_summary: Summary from reflection phase
            
        Returns:
            Dictionary containing planning decisions:
            {
                'action': str,  # 'create_task', 'execute_task', 'wait', etc.
                'task_updates': List[Dict],  # Tasks to create/update
                'agent_id': Optional[str],  # Agent to use for execution
                'reasoning': str  # Explanation of the decision
            }
        """
        logger.info("Reasoning and planning...")
        
        # Placeholder logic
        # TODO: Implement actual reasoning logic
        
        # If we have a user message, create a task
        if user_message:
            message_content = str(user_message.get("content", "") or "")
            explicit_task_id = user_message.get("task_id")
            parsed_content = self._parse_message_content_as_json(message_content)
            target_task_id = explicit_task_id or parsed_content.get("task_id")

            if target_task_id:
                preferred_agent = self._resolve_preferred_agent(
                    message_content=message_content,
                    parsed_content=parsed_content,
                    task_summary=task_summary,
                    short_term_memory=short_term_memory or [],
                )
                return {
                    "action": "execute_task",
                    "task_updates": [],
                    "agent_id": None,
                    "target_task_id": target_task_id,
                    "preferred_agent_id": preferred_agent,
                    "message_content": message_content,
                    "reasoning": (
                        "User message linked to existing task; execute selected agent "
                        "with short-term memory hints and let Director decide overwrite "
                        "based on existing assets"
                    ),
                }

            return {
                'action': 'create_task',
                'task_updates': [
                    {
                        'description': {
                            'overall_description': user_message.get('content', ''),
                            'input': {},
                            'requirements': [],
                            'additional_notes': ''
                        }
                    }
                ],
                'agent_id': None,
                'reasoning': 'User message received, creating task'
            }
        
        # If we have a current task, execute it
        if current_task:
            return {
                'action': 'execute_task',
                'task_updates': [],
                'agent_id': None,  # Will be determined based on task requirements
                'reasoning': 'Task ready for execution'
            }
        
        # If we have a reflection summary, decide next steps
        if reflection_summary:
            return {
                'action': 'update_plan',
                'task_updates': [],
                'agent_id': None,
                'reasoning': 'Reflection received, updating plan'
            }
        
        # Default: wait
        return {
            'action': 'wait',
            'task_updates': [],
            'agent_id': None,
            'reasoning': 'No action needed, waiting'
        }
    
    def select_agent_for_task(
        self,
        task: Dict[str, Any],
        available_agents: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Select appropriate agent for a task
        
        Args:
            task: Task to execute
            available_agents: List of available agents
            
        Returns:
            Agent ID or None if no suitable agent found
        """
        # Placeholder: return first available agent
        # TODO: Implement agent selection logic based on task requirements
        if available_agents:
            task_description = task.get("description", {}) if isinstance(task, dict) else {}
            preferred_agent_id = (
                task_description.get("preferred_agent_id")
                if isinstance(task_description, dict)
                else None
            )
            if preferred_agent_id and any(
                a.get("id") == preferred_agent_id for a in available_agents
            ):
                return preferred_agent_id
            return available_agents[0].get('id')
        return None
    
    def should_trigger_reflection(
        self,
        execution_result: Dict[str, Any]
    ) -> bool:
        """
        Determine if reflection should be triggered
        
        Args:
            execution_result: Result from task execution
            
        Returns:
            True if reflection should be triggered
        """
        # Placeholder: always trigger reflection after execution
        # TODO: Implement logic to determine when reflection is needed
        return True

    @staticmethod
    def _parse_message_content_as_json(content: str) -> Dict[str, Any]:
        if not content:
            return {}
        try:
            parsed = json.loads(content)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _resolve_preferred_agent(
        self,
        *,
        message_content: str,
        parsed_content: Dict[str, Any],
        task_summary: Optional[Dict[str, Any]] = None,
        short_term_memory: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        explicit_agent = parsed_content.get("preferred_agent_id")
        if isinstance(explicit_agent, str) and explicit_agent.strip():
            return explicit_agent.strip()
        explicit_agents = parsed_content.get("rerun_agents")
        if isinstance(explicit_agents, list) and explicit_agents:
            first = str(explicit_agents[0]).strip()
            if first:
                return first
        lowered = message_content.lower()
        for keyword, mapped_agent in MESSAGE_KEYWORD_TO_AGENT.items():
            if keyword in lowered:
                return mapped_agent
        memory_suggestion = self._resolve_agent_from_short_term_memory(short_term_memory or [])
        if memory_suggestion:
            return memory_suggestion
        if isinstance(task_summary, dict):
            latest_agent = task_summary.get("agent_id")
            if isinstance(latest_agent, str) and latest_agent:
                return latest_agent
        return None

    def _resolve_agent_from_short_term_memory(
        self,
        entries: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Infer preferred next agent from recent short-term memory entries."""
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            metadata = entry.get("metadata")
            if isinstance(metadata, dict):
                suggested = metadata.get("suggested_next_agent")
                if isinstance(suggested, str) and suggested:
                    return suggested
            applies_to_agents = entry.get("applies_to_agents")
            if isinstance(applies_to_agents, list) and applies_to_agents:
                first = str(applies_to_agents[0]).strip()
                if first:
                    return first
        return None
