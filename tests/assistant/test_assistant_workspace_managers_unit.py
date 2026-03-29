from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.assistant.workspace.asset_manager import AssetManager
from src.assistant.workspace.file_manager import FileManager
from src.assistant.workspace.log_manager import LogManager
from src.assistant.workspace.memory_manager import MemoryManager


def _build_asset_manager(fm: FileManager, lm: LogManager) -> AssetManager:
    return AssetManager(
        fm.store_file_at_relative_path,
        lm.add_log,
        fm.read_binary_from_uri,
        fm.list_files,
        fm.delete_file,
    )


def test_file_manager_list(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    fm.store_file_at_relative_path(
        "notes/a.txt", b"one", "a.txt", "alpha", created_by="u1", tags=["t1", "t2"]
    )
    fm.store_file_at_relative_path(
        "notes/b.txt", b"two", "b.txt", "beta", created_by="u2", tags=["t2"]
    )

    listed = fm.list_files()
    assert len(listed) == 2


def test_file_manager_read_binary_from_uri(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(b"abc")

    assert fm.read_binary_from_uri(str(payload_path)) == b"abc"
    assert fm.read_binary_from_uri(str(tmp_path / "missing.bin")) is None


def test_memory_manager_structured_entries_and_brief(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)

    mm.add_memory_entry(
        content="Last run failed on noisy vocals; lower music bed.",
        task_id="task_1",
        agent_id="AudioAgent",
        execution_result={
            "status": "FAILED",
            "execution_id": "ex_1",
            "error": "boom",
        },
    )

    entries = mm.list_memory_entries(task_id="task_1", limit=5)
    assert len(entries) == 1
    assert {"content", "agent_id", "created_at", "execution_result"}.issubset(entries[0].keys())
    assert entries[0]["execution_result"]["status"] == "FAILED"

    brief = mm.get_memory_brief(task_id="task_1")
    assert len(brief["global_memory"]) >= 1
    ex0 = brief["global_memory"][0]
    assert "content" not in ex0
    assert ex0["agent_id"] == "AudioAgent"
    assert ex0["execution_result"]["status"] == "FAILED"
    assert ex0["execution_result"]["error"] == "boom"

def test_memory_brief_slim_all_entries(tmp_path):
    """Brief omits content and returns all matching rows."""
    mm = MemoryManager("ws_1", tmp_path)
    for i in range(5):
        mm.add_memory_entry(
            content=f"note {i}",
            task_id="task_many",
            agent_id="StoryAgent",
            execution_result={"status": "COMPLETED", "execution_id": f"ex_{i}"},
        )
    full_slim = mm.get_memory_brief(task_id="task_many")
    assert len(full_slim["global_memory"]) == 5
    assert all("content" not in e for e in full_slim["global_memory"])


def test_memory_brief_task_id_unique_no_or_with_agent_id(tmp_path):
    """Workspace single file; querying task_id filters entries."""
    mm = MemoryManager("ws_1", tmp_path)
    mm.add_memory_entry(
        content="Story step done",
        task_id="task_alpha",
        agent_id="StoryAgent",
    )
    mm.add_memory_entry(
        content="Audio mix note",
        task_id="task_beta",
        agent_id="AudioAgent",
    )
    brief = mm.get_memory_brief(
        task_id="task_alpha",
        agent_id=None,
    )
    assert len(brief["global_memory"]) == 1
    assert "content" not in brief["global_memory"][0]
    assert brief["global_memory"][0]["agent_id"] == "StoryAgent"
    full = mm.list_memory_entries(task_id="task_alpha", limit=10)
    assert len(full) == 1
    assert full[0]["content"] == "Story step done"


def test_memory_manager_requires_task_id(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)
    with pytest.raises(ValueError, match="task_id"):
        mm.add_memory_entry(content="hello")


def test_memory_manager_artifact_locations_roundtrip(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)
    mm.add_memory_entry(
        content="done",
        task_id="task_art",
        agent_id="StoryAgent",
        artifact_locations=[
            {"role": "story_blueprint", "path": "/tmp/x.json"},
        ],
    )
    rows = mm.list_memory_entries(task_id="task_art", limit=5)
    assert rows[0].get("artifact_locations")
    assert rows[0]["artifact_locations"][0]["path"] == "/tmp/x.json"
    brief = mm.get_memory_brief(task_id="task_art")
    assert brief["global_memory"][0]["artifact_locations"][0]["role"] == "story_blueprint"


def test_global_memory_md_created_empty_then_sections_after_entry(tmp_path):
    wid = "ws_md"
    mm = MemoryManager(wid, tmp_path)
    tid = "task_init_md"
    path = tmp_path / wid / "global_memory.md"
    assert not path.exists()

    mm.add_memory_entry(content="hello", task_id=tid)
    assert path.exists()
    md_text = path.read_text(encoding="utf-8")
    assert "## File tree" in md_text
    assert "## Entries" in md_text
    assert "```json" in md_text
    assert "<!-- FW_FILE_TREE_BEGIN -->" in md_text
    assert "human-readable snapshot" in md_text.lower() or "not authoritative" in md_text.lower()
    listed = mm.list_memory_entries(limit=10)
    assert len(listed) == 1
    assert listed[0]["content"] == "hello"


def test_log_manager_filter(tmp_path):
    lm = LogManager("ws_1", tmp_path)
    lm.add_log("write", "file", details={"msg": "hello"}, agent_id="a1", task_id="t1")
    lm.add_log("read", "memory", details={"msg": "world"}, agent_id="a2", task_id="t2")

    filtered = lm.get_logs(operation_type="write", agent_id="a1")

    assert len(filtered) == 1
    assert filtered[0].operation_type == "write"


def test_asset_manager_hydrate_and_persist_index(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_asset_manager(fm, lm)

    execution = SimpleNamespace(
        id="exec_001",
        task_id="task_1",
        agent_id="AgentA",
        results={
            "content": {"value": 42},
            "preview": {
                "file_content": b"hello",
                "filename": "preview.txt",
                "description": "preview",
            },
        },
    )

    persisted_paths, index, extra_locs = am.persist_execution_from_plan(
        execution,
        assignments=[
            {
                "kind": "json_snapshot",
                "source_key": "",
                "role": "agent_asset",
                "relative_path": "artifacts/agent_asset/agent_asset_exec_1.json",
            }
        ],
    )
    assert persisted_paths == {}
    assert extra_locs == []
    assert index is not None
    assert index["asset_key"] == "agent_asset"

    hydrated = am.hydrate_indexed_assets({"agent_asset": index})
    assert hydrated["agent_asset"]["content"]["value"] == 42

    files = fm.list_files()
    assert len(files) == 1


def test_asset_manager_collect_materialized_files_reads_binary_by_uri(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_asset_manager(fm, lm)

    media_path = tmp_path / "tmp_asset.png"
    media_path.write_bytes(b"png-bytes")
    media_asset = SimpleNamespace(
        sys_id="img_001",
        extension="png",
        uri_holder={"uri": str(media_path)},
    )

    files = am.collect_materialized_files([media_asset])
    assert files["img_001"]["file_content"] == b"png-bytes"
    assert files["img_001"]["filename"] == "img_001.png"
