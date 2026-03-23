"""Workspace context boundary for Assistant execution inputs.

This module only retrieves and shapes context from Workspace. It does not
execute agents or persist execution results.
"""

from typing import Any, Dict, List, Optional

from .response_serializers import (
    context_log_item_to_dict,
    file_brief_to_dict,
    file_search_item_to_dict,
    log_search_item_to_dict,
)
from .workspace import Workspace


class WorkspaceContextBuilder:
    """
    Retrieves information from the workspace file system.

    The assistant uses this module to search and retrieve information
    from the shared workspace, then distributes it to agents.
    """

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

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
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve files from workspace based on query."""
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
        pattern: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve structured memory info and optional matched entries."""
        memory_info = self.workspace.get_memory_info()
        matched_entries = []
        if pattern:
            matched_entries = self.workspace.memory_manager.search_memory_entries(pattern, limit=10)
        brief = self.workspace.get_memory_brief(short_term_limit=6)

        result = {
            "info": memory_info,
            "brief": brief,
        }
        if matched_entries:
            result["matches"] = matched_entries
        return result

    def search_workspace(
        self,
        query: str,
        search_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Comprehensive search across workspace."""
        search_types = search_types or ["files", "memory", "logs"]
        results = {}

        if "files" in search_types:
            results["files"] = self.retrieve_files(query)

        if "memory" in search_types:
            memory_result = self.retrieve_memory(pattern=query)
            if memory_result and memory_result.get("matches"):
                results["memory"] = memory_result

        if "logs" in search_types:
            logs = self.workspace.log_manager.search_logs(query)
            results["logs"] = [log_search_item_to_dict(log) for log in logs]

        return results

    def get_context_for_agent(
        self,
        agent_id: str,
        task_id: str,
        context_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get relevant context from workspace for a specific agent."""
        context: Dict[str, Any] = {
            "agent_id": agent_id,
            "task_id": task_id,
            "files": self._get_context_files(agent_id, task_id, context_keys),
            "memory_brief": {},
            "recent_logs": [],
        }

        context["memory_brief"] = self.workspace.get_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
            short_term_limit=6,
        )

        recent_logs = self.workspace.get_logs(
            agent_id=agent_id,
            task_id=task_id,
            limit=10,
        )
        context["recent_logs"] = [context_log_item_to_dict(log) for log in recent_logs]

        return context

