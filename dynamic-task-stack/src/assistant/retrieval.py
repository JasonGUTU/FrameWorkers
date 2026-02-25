"""Workspace retrieval boundary for Assistant.

This module only retrieves and shapes context from Workspace. It does not
execute agents or persist execution results.
"""

from typing import Dict, Any, List, Optional
from .workspace import Workspace
from .serializers import (
    file_brief_to_dict,
    file_search_item_to_dict,
    log_search_item_to_dict,
    context_log_item_to_dict,
)


class WorkspaceRetriever:
    """
    Retrieves information from the workspace file system
    
    The assistant uses this module to search and retrieve information
    from the shared workspace, then distributes it to agents.
    """
    
    def __init__(self, workspace: Workspace):
        """
        Initialize the retriever with a workspace
        
        Args:
            workspace: The global workspace instance
        """
        self.workspace = workspace

    @staticmethod
    def _memory_match_context(memory_content: str, pattern: str) -> Optional[str]:
        if not pattern:
            return None
        lower_memory = memory_content.lower()
        lower_pattern = pattern.lower()
        if lower_pattern not in lower_memory:
            return None
        idx = lower_memory.find(lower_pattern)
        start = max(0, idx - 100)
        end = min(len(memory_content), idx + len(pattern) + 100)
        return memory_content[start:end]

    def _get_context_files(
        self,
        agent_id: str,
        task_id: str,
        context_keys: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        if context_keys:
            files: List[Dict[str, Any]] = []
            for file_id in context_keys:
                file_meta = self.workspace.get_file(file_id)
                if file_meta:
                    files.append(file_brief_to_dict(file_meta))
            return files

        # Default path: use recent files by agent + task tag.
        agent_files = self.workspace.list_files(created_by=agent_id, limit=5)
        task_files = self.workspace.list_files(tags=[task_id], limit=5)
        all_files = {f.id: f for f in agent_files + task_files}
        return [file_brief_to_dict(f) for f in list(all_files.values())[:10]]
    
    def retrieve_files(
        self,
        query: str,
        file_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve files from workspace based on query
        
        Args:
            query: Search query string
            file_types: Optional file type filter ('image', 'video', 'text', 'other')
            limit: Maximum number of results to return
        
        Returns:
            List of file information dictionaries
        """
        files = self.workspace.search_files(
            query,
            file_type=file_types[0] if file_types else None,
            limit=limit,
        )
        return [
            {
                **file_search_item_to_dict(f),
                "tags": f.tags,
            }
            for f in files
        ]
    
    def retrieve_memory(
        self,
        key: str = None,
        pattern: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve Global Memory
        
        Args:
            key: Not used (for compatibility)
            pattern: Optional pattern to search in memory
        
        Returns:
            Memory data dictionary
        """
        memory_content = self.workspace.read_memory()
        memory_info = self.workspace.get_memory_info()
        
        result = {
            "content": memory_content,
            "info": memory_info
        }
        
        match_context = self._memory_match_context(memory_content, pattern or "")
        if match_context:
            result["match_context"] = match_context
        
        return result
    
    def retrieve_assets(
        self,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve assets (files) from workspace
        
        Args:
            asset_type: Optional file type filter ('image', 'video', 'text', 'other')
            tags: Optional list of tags to filter
        
        Returns:
            List of asset dictionaries
        """
        files = self.workspace.list_files(file_type=asset_type, tags=tags)
        return [
            {
                **file_search_item_to_dict(f),
                "tags": f.tags,
                "metadata": f.metadata,
            }
            for f in files
        ]
    
    def search_workspace(
        self,
        query: str,
        search_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive search across workspace
        
        Args:
            query: Search query string
            search_types: Optional list of types to search ['files', 'memory', 'logs']
        
        Returns:
            Dictionary containing search results from different sources
        """
        search_types = search_types or ['files', 'memory', 'logs']
        results = {}
        
        if 'files' in search_types:
            results['files'] = self.retrieve_files(query)
        
        if 'memory' in search_types:
            memory_result = self.retrieve_memory(pattern=query)
            if memory_result and query.lower() in memory_result['content'].lower():
                results['memory'] = memory_result
        
        if 'logs' in search_types:
            logs = self.workspace.log_manager.search_logs(query)
            results['logs'] = [log_search_item_to_dict(log) for log in logs]
        
        return results
    
    def get_context_for_agent(
        self,
        agent_id: str,
        task_id: str,
        context_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get relevant context from workspace for a specific agent
        
        The assistant uses this method to retrieve relevant information
        from the workspace and prepare it for distribution to agents.
        
        Args:
            agent_id: ID of the agent that needs context
            task_id: ID of the task being executed
            context_keys: Optional list of specific file IDs to retrieve
        
        Returns:
            Dictionary containing context information for the agent
        """
        context: Dict[str, Any] = {
            "agent_id": agent_id,
            "task_id": task_id,
            "files": self._get_context_files(agent_id, task_id, context_keys),
            "memory": "",
            "recent_logs": []
        }
        
        # Retrieve Global Memory (first 2000 chars for context)
        memory_content = self.workspace.read_memory()
        context["memory"] = memory_content[:2000] if memory_content else ""
        
        # Get recent logs related to this agent/task
        recent_logs = self.workspace.get_logs(
            agent_id=agent_id,
            task_id=task_id,
            limit=10
        )
        context["recent_logs"] = [context_log_item_to_dict(log) for log in recent_logs]
        
        return context
