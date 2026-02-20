# Example Agent - Template implementation

from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentMetadata, BaseEvaluator


class ExampleEvaluator(BaseEvaluator):
    """Quality evaluator for ExampleAgent.

    Demonstrates how to implement structural checks for an agent's output.
    """

    def check_structure(
        self,
        output: Dict[str, Any],
        upstream: Dict[str, Any] | None = None,
    ) -> List[str]:
        errors: List[str] = []
        if "result" not in output:
            errors.append("missing 'result' field")
        if "timestamp" not in output:
            errors.append("missing 'timestamp' field")
        return errors


class ExampleAgent(BaseAgent):
    """Example Agent - Template for creating new agents.

    This is a template showing how to implement a new agent.
    Copy this file to create your own agent.
    """

    def __init__(self):
        super().__init__()
        self.evaluator = ExampleEvaluator()

    def get_metadata(self) -> AgentMetadata:
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
                    "description": "Input text to process",
                },
                "options": {
                    "type": "object",
                    "required": False,
                    "description": "Optional processing options",
                },
            },
            output_schema={
                "result": {
                    "type": "string",
                    "description": "Processed result",
                },
                "timestamp": {
                    "type": "string",
                    "description": "Processing timestamp",
                },
            },
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_inputs(inputs)

        input_text = inputs.get("input_text", "")
        options = inputs.get("options", {})

        result = f"Processed: {input_text}"
        if options:
            result += f" with options: {options}"

        return {
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
        }
