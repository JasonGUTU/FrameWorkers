# Retrieval Module
# This module handles information retrieval from the workspace file system

from typing import Dict, Any, List, Optional
from .workspace import Workspace


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
        files = self.workspace.search_files(query, file_type=file_types[0] if file_types else None, limit=limit)
        return [
            {
                "id": f.id,
                "filename": f.filename,
                "description": f.description,
                "file_type": f.file_type,
                "file_path": f.file_path,
                "created_at": f.created_at.isoformat(),
                "tags": f.tags
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
        
        # If pattern provided, search in content
        if pattern and pattern.lower() in memory_content.lower():
            # Find context around pattern
            idx = memory_content.lower().find(pattern.lower())
            start = max(0, idx - 100)
            end = min(len(memory_content), idx + len(pattern) + 100)
            result["match_context"] = memory_content[start:end]
        
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
                "id": f.id,
                "filename": f.filename,
                "description": f.description,
                "file_type": f.file_type,
                "file_path": f.file_path,
                "created_at": f.created_at.isoformat(),
                "tags": f.tags,
                "metadata": f.metadata
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
            results['logs'] = [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "operation_type": log.operation_type,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details
                }
                for log in logs
            ]
        
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
        context = {
            "agent_id": agent_id,
            "task_id": task_id,
            "files": [],
            "memory": "",
            "recent_logs": []
        }
        
        # Retrieve specific files if context_keys provided
        if context_keys:
            for file_id in context_keys:
                file_meta = self.workspace.get_file(file_id)
                if file_meta:
                    context["files"].append({
                        "id": file_meta.id,
                        "filename": file_meta.filename,
                        "description": file_meta.description,
                        "file_type": file_meta.file_type,
                        "file_path": file_meta.file_path
                    })
        else:
            # Get recent files created by this agent or related to this task
            agent_files = self.workspace.list_files(
                created_by=agent_id,
                limit=5
            )
            task_files = self.workspace.list_files(
                tags=[task_id],
                limit=5
            )
            # Combine and deduplicate
            all_files = {f.id: f for f in agent_files + task_files}
            context["files"] = [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "description": f.description,
                    "file_type": f.file_type,
                    "file_path": f.file_path
                }
                for f in list(all_files.values())[:10]
            ]
        
        # Retrieve Global Memory (first 2000 chars for context)
        memory_content = self.workspace.read_memory()
        context["memory"] = memory_content[:2000] if memory_content else ""
        
        # Get recent logs related to this agent/task
        recent_logs = self.workspace.get_logs(
            agent_id=agent_id,
            task_id=task_id,
            limit=10
        )
        context["recent_logs"] = [
            {
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id
            }
            for log in recent_logs
        ]
        
        return context
