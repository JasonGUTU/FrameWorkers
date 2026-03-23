from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.assistant.workspace.asset_manager import AssetManager
from src.assistant.workspace.file_manager import FileManager
from src.assistant.workspace.log_manager import LogManager
from src.assistant.workspace.memory_manager import MemoryManager


def _build_asset_manager(fm: FileManager, lm: LogManager) -> AssetManager:
    return AssetManager(
        fm.store_file,
        lm.add_log,
        fm.read_binary_from_uri,
        fm.list_files,
        fm.delete_file,
    )


def test_file_manager_filter_and_search(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    fm.store_file(b"one", "a.txt", "alpha", created_by="u1", tags=["t1", "t2"])
    fm.store_file(b"two", "b.txt", "beta", created_by="u2", tags=["t2"])

    only_u1 = fm.list_files(created_by="u1")
    with_tag = fm.list_files(tags=["t2"])
    searched = fm.search_files("alpha")

    assert len(only_u1) == 1
    assert len(with_tag) == 2
    assert len(searched) == 1
    assert searched[0].description == "alpha"


def test_file_manager_read_binary_from_uri(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(b"abc")

    assert fm.read_binary_from_uri(str(payload_path)) == b"abc"
    assert fm.read_binary_from_uri(str(tmp_path / "missing.bin")) is None


def test_memory_manager_info_and_split_files(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)
    mm.add_memory_entry(
        content="Short note",
        tier="short_term",
        kind="note",
    )
    info = mm.get_memory_info()

    assert info["short_term_entries_count"] == 1
    assert info["long_term_entries_count"] == 0
    assert "entries_count" in info


def test_memory_manager_structured_entries_and_brief(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)

    mm.add_memory_entry(
        content="Last run failed on noisy vocals; lower music bed.",
        tier="short_term",
        kind="failure_pattern",
        task_id="task_1",
        agent_id="AudioAgent",
        priority=4,
        metadata={"suggested_next_agent": "AudioAgent"},
    )

    short_entries = mm.list_memory_entries(tier="short_term", task_id="task_1", limit=5)
    assert len(short_entries) == 1
    assert short_entries[0]["kind"] == "failure_pattern"

    brief = mm.get_memory_brief(task_id="task_1", agent_id="AudioAgent", short_term_limit=3)
    assert len(brief["short_term"]) >= 1
    assert brief["long_term"] == []
    assert brief["short_term"][0]["task_id"] == "task_1"


def test_memory_manager_rejects_long_term_tier(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)
    with pytest.raises(ValueError, match="long_term"):
        mm.add_memory_entry(content="nope", tier="long_term", kind="note")


def test_log_manager_filter_and_search(tmp_path):
    lm = LogManager("ws_1", tmp_path)
    lm.add_log("write", "file", details={"msg": "hello"}, agent_id="a1", task_id="t1")
    lm.add_log("read", "memory", details={"msg": "world"}, agent_id="a2", task_id="t2")

    filtered = lm.get_logs(operation_type="write", agent_id="a1")
    searched = lm.search_logs("world")

    assert len(filtered) == 1
    assert filtered[0].operation_type == "write"
    assert len(searched) == 1
    assert searched[0].resource_type == "memory"


def test_log_manager_strategy_insights(tmp_path):
    lm = LogManager("ws_1", tmp_path)
    lm.add_log(
        "write",
        "execution",
        details={"event_type": "execution_started", "status": "IN_PROGRESS"},
        agent_id="a1",
        task_id="t1",
    )
    lm.add_log(
        "write",
        "execution",
        details={"event_type": "execution_failed", "status": "FAILED", "error": "boom"},
        agent_id="a1",
        task_id="t1",
    )
    lm.add_log(
        "write",
        "asset",
        details={"event_type": "asset_persisted", "asset_status": "ready"},
        agent_id="a1",
        task_id="t1",
    )

    insights = lm.get_strategy_insights()

    assert insights["totals"]["execution_event_count"] == 2
    assert insights["totals"]["execution_failed"] == 1
    assert insights["totals"]["execution_fail_rate"] == 0.5
    assert any(item["key"] == "execution_failed" for item in insights["breakdown"]["by_event_type"])
    assert insights["failure_hotspots"]["by_agent"][0]["key"] == "a1"


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

    index = am.persist_execution_json_snapshot(execution, asset_key="agent_asset")
    assert index is not None
    assert index["asset_key"] == "agent_asset"

    hydrated = am.hydrate_indexed_assets({"agent_asset": index})
    assert hydrated["agent_asset"]["content"]["value"] == 42

    persisted_paths = am.persist_execution_assets(execution)
    assert persisted_paths == {}
    files = fm.list_files()
    assert len(files) == 2


def test_asset_manager_build_pipeline_asset_value(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_asset_manager(fm, lm)

    indexed = am.build_pipeline_asset_value(
        execution_results={
            "_asset_index": {
                "asset_key": "story_blueprint",
                "json_uri": "/tmp/story.json",
                "file_id": "file_123",
            }
        },
        descriptor_asset_key="story_blueprint",
        execution_id="exec_100",
    )
    assert indexed == {
        "asset_key": "story_blueprint",
        "json_uri": "/tmp/story.json",
        "file_id": "file_123",
        "execution_id": "exec_100",
    }

    fallback = am.build_pipeline_asset_value(
        execution_results={"content": {"logline": "x"}, "_meta": "skip"},
        descriptor_asset_key="story_blueprint",
        execution_id="exec_101",
    )
    assert fallback == {"content": {"logline": "x"}}


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
