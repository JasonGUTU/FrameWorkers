# Example Agent - Template implementation

from typing import Dict, Any
from datetime import datetime

# Import BaseAgent from the helper module
from ..base_agent import BaseAgent, AgentMetadata


class ExampleAgent(BaseAgent):
    """
    Example Agent - Template for creating new agents
    
    This is a template showing how to implement a new agent.
    Copy this file to create your own agent.
    """
    
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        return AgentMetadata(
            id="example_agent",
            name="Example Agent",
            description="An example agent template for demonstration",
            version="1.0.0",
            author="Frameworkers",
            capabilities=["example_processing", "template"],
            input_schema={
                "input_text": {
                    "type": "string",
                    "required": True,
                    "description": "Input text to process"
                },
                "options": {
                    "type": "object",
                    "required": False,
                    "description": "Optional processing options"
                }
            },
            output_schema={
                "result": {
                    "type": "string",
                    "description": "Processed result"
                },
                "timestamp": {
                    "type": "string",
                    "description": "Processing timestamp"
                }
            }
        )
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with given inputs
        
        Args:
            inputs: Input data dictionary
            
        Returns:
            Dict containing execution results
        """
        # Validate inputs
        self.validate_inputs(inputs)
        
        # Extract inputs
        input_text = inputs.get("input_text", "")
        options = inputs.get("options", {})
        
        # Process the input (example logic)
        result = f"Processed: {input_text}"
        if options:
            result += f" with options: {options}"
        
        # Return results
        return {
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
