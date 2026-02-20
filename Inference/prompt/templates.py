"""
Prompt Templates - Template system for prompt composition

Provides template system for creating and managing prompt templates.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
import json
import re
from string import Template


class PromptTemplate:
    """
    Prompt template with variable substitution
    
    Supports both Python string formatting and custom template syntax.
    """
    
    def __init__(
        self,
        template: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None
    ):
        """
        Initialize prompt template
        
        Args:
            template: Template string with placeholders
            name: Template name
            description: Template description
            variables: List of variable names (auto-detected if None)
        """
        self.template = template
        self.name = name or "unnamed_template"
        self.description = description
        self.variables = variables or self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from template"""
        # Support {variable} syntax
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.template)
        
        # Support {{variable}} syntax (double braces)
        pattern2 = r'\{\{(\w+)\}\}'
        variables2 = re.findall(pattern2, self.template)
        
        # Support $variable syntax
        pattern3 = r'\$(\w+)'
        variables3 = re.findall(pattern3, self.template)
        
        # Combine and deduplicate
        all_vars = list(set(variables + variables2 + variables3))
        return sorted(all_vars)
    
    def format(
        self,
        **kwargs
    ) -> str:
        """
        Format template with provided variables
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Formatted prompt string
        """
        # Try Python string formatting first ({variable})
        try:
            return self.template.format(**kwargs)
        except KeyError:
            pass
        
        # Try Template class ($variable)
        try:
            template_obj = Template(self.template)
            return template_obj.substitute(**kwargs)
        except KeyError:
            pass
        
        # Manual substitution for {{variable}} syntax
        result = self.template
        for var, value in kwargs.items():
            result = result.replace(f"{{{{{var}}}}}", str(value))
            result = result.replace(f"${{{var}}}", str(value))
        
        return result
    
    def format_safe(
        self,
        default: str = "",
        **kwargs
    ) -> str:
        """
        Format template with safe defaults for missing variables
        
        Args:
            default: Default value for missing variables
            **kwargs: Variable values
            
        Returns:
            Formatted prompt string
        """
        # Fill missing variables with defaults
        filled_kwargs = {var: default for var in self.variables}
        filled_kwargs.update(kwargs)
        return self.format(**filled_kwargs)
    
    def validate(self, **kwargs) -> tuple[bool, List[str]]:
        """
        Validate that all required variables are provided
        
        Args:
            **kwargs: Variable values to validate
            
        Returns:
            Tuple of (is_valid, missing_variables)
        """
        missing = [var for var in self.variables if var not in kwargs]
        return len(missing) == 0, missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "variables": self.variables,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create template from dictionary"""
        return cls(
            template=data["template"],
            name=data.get("name"),
            description=data.get("description"),
            variables=data.get("variables")
        )


class TemplateManager:
    """
    Manager for prompt templates
    
    Provides template storage, retrieval, and composition utilities.
    """
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """
        Initialize Template Manager
        
        Args:
            storage_path: Path to template storage directory
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.templates: Dict[str, PromptTemplate] = {}
        
        # Load templates if storage path exists
        if self.storage_path and self.storage_path.exists():
            self.load()
    
    def register_template(self, template: PromptTemplate):
        """
        Register a template
        
        Args:
            template: PromptTemplate object
        """
        self.templates[template.name] = template
        if self.storage_path:
            self.save()
    
    def create_template(
        self,
        name: str,
        template: str,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> PromptTemplate:
        """
        Create and register a new template
        
        Args:
            name: Template name
            template: Template string
            description: Template description
            variables: List of variable names
            
        Returns:
            Created PromptTemplate object
        """
        prompt_template = PromptTemplate(
            template=template,
            name=name,
            description=description,
            variables=variables
        )
        self.register_template(prompt_template)
        return prompt_template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get template by name
        
        Args:
            name: Template name
            
        Returns:
            PromptTemplate if found, None otherwise
        """
        return self.templates.get(name)
    
    def format_template(
        self,
        name: str,
        **kwargs
    ) -> Optional[str]:
        """
        Format a template by name
        
        Args:
            name: Template name
            **kwargs: Variable values
            
        Returns:
            Formatted prompt string or None if template not found
        """
        template = self.get_template(name)
        if template:
            return template.format(**kwargs)
        return None
    
    def compose(
        self,
        templates: List[Union[str, PromptTemplate]],
        separator: str = "\n\n",
        **kwargs
    ) -> str:
        """
        Compose multiple templates into a single prompt
        
        Args:
            templates: List of template names or PromptTemplate objects
            separator: Separator between templates
            **kwargs: Variable values for all templates
            
        Returns:
            Composed prompt string
        """
        parts = []
        for template in templates:
            if isinstance(template, str):
                # Template name
                template_obj = self.get_template(template)
                if template_obj:
                    parts.append(template_obj.format(**kwargs))
            elif isinstance(template, PromptTemplate):
                parts.append(template.format(**kwargs))
            else:
                parts.append(str(template))
        
        return separator.join(parts)
    
    def compose_messages(
        self,
        templates: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Compose multiple templates into message list
        
        Args:
            templates: List of dicts with 'role' and 'template' keys
            **kwargs: Variable values
            
        Returns:
            List of message dictionaries
        """
        messages = []
        for item in templates:
            role = item.get("role", "user")
            template_name = item.get("template")
            
            if template_name:
                content = self.format_template(template_name, **kwargs)
                if content:
                    messages.append({
                        "role": role,
                        "content": content
                    })
            elif "content" in item:
                # Direct content
                messages.append({
                    "role": role,
                    "content": item["content"]
                })
        
        return messages
    
    def list_templates(self) -> List[str]:
        """
        List all registered template names
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
    
    def remove_template(self, name: str) -> bool:
        """
        Remove a template
        
        Args:
            name: Template name
            
        Returns:
            True if removed, False if not found
        """
        if name in self.templates:
            del self.templates[name]
            if self.storage_path:
                self.save()
            return True
        return False
    
    def save(self, format: str = "json"):
        """
        Save templates to file
        
        Args:
            format: File format ("json")
        """
        if not self.storage_path:
            return
        
        # Ensure directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        templates_data = {
            name: template.to_dict()
            for name, template in self.templates.items()
        }
        
        file_path = self.storage_path / "templates.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)
    
    def load(self, format: str = "json"):
        """
        Load templates from file
        
        Args:
            format: File format ("json")
        """
        if not self.storage_path:
            return
        
        file_path = self.storage_path / "templates.json"
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            self.templates = {
                name: PromptTemplate.from_dict(data)
                for name, data in templates_data.items()
            }
        except Exception as e:
            print(f"Warning: Failed to load templates: {e}")
    
    def export_template(self, name: str, output_path: Union[str, Path]):
        """
        Export a single template to file
        
        Args:
            name: Template name
            output_path: Path to export file
        """
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
    
    def import_template(self, file_path: Union[str, Path]):
        """
        Import a template from file
        
        Args:
            file_path: Path to template file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        template = PromptTemplate.from_dict(data)
        self.register_template(template)
