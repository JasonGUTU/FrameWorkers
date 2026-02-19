# Base Agent Abstract Class

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMetadata:
    """Metadata for an agent"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    Abstract base class for all agents
    
    Every agent must inherit from this class and implement the required methods.
    Each agent should be placed in its own folder under src/assistant/agents/
    
    Example structure:
    src/assistant/agents/
    ├── storyboard_agent/
    │   ├── __init__.py
    │   └── agent.py  # StoryboardAgent(BaseAgent)
    ├── transcript_agent/
    │   ├── __init__.py
    │   └── agent.py  # TranscriptAgent(BaseAgent)
    └── ...
    """
    
    def __init__(self):
        """Initialize the agent"""
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> AgentMetadata:
        """
        Return agent metadata
        
        Returns:
            AgentMetadata: Metadata describing this agent
            
        Example:
            return AgentMetadata(
                id="storyboard_agent",
                name="Storyboard Agent",
                description="Creates storyboards for video projects",
                capabilities=["storyboard_generation", "visual_design"],
                input_schema={
                    "script": {"type": "string", "required": True},
                    "style": {"type": "string", "required": False}
                },
                output_schema={
                    "storyboard": {"type": "array", "items": {"type": "object"}}
                }
            )
        """
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with given inputs
        
        Args:
            inputs: Input data dictionary matching the agent's input_schema
            
        Returns:
            Dict[str, Any]: Output data matching the agent's output_schema
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If execution fails
            
        Example:
            def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
                script = inputs.get("script")
                if not script:
                    raise ValueError("script is required")
                
                # Process the script and generate storyboard
                storyboard = self._generate_storyboard(script)
                
                return {
                    "storyboard": storyboard,
                    "status": "completed"
                }
        """
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate inputs against the agent's input_schema
        
        Args:
            inputs: Input data to validate
            
        Returns:
            bool: True if inputs are valid
            
        Raises:
            ValueError: If inputs are invalid
        """
        schema = self.metadata.input_schema
        if not schema:
            return True
        
        # Check required fields
        for field_name, field_spec in schema.items():
            if isinstance(field_spec, dict):
                required = field_spec.get("required", False)
                if required and field_name not in inputs:
                    raise ValueError(f"Required field '{field_name}' is missing")
        
        return True
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the input schema for this agent
        
        Returns:
            Dict[str, Any]: Input schema definition
        """
        return self.metadata.input_schema
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the output schema for this agent
        
        Returns:
            Dict[str, Any]: Output schema definition
        """
        return self.metadata.output_schema
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List[str]: List of capability strings
        """
        return self.metadata.capabilities
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get complete information about this agent
        
        Returns:
            Dict[str, Any]: Complete agent information
        """
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "capabilities": self.metadata.capabilities,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat()
        }
