from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.assistant.workspace.global_memory import GlobalMemory
from src.assistant.workspace.artifact_writer import ArtifactWriter
from src.assistant.workspace.file_manager import FileManager
from src.assistant.workspace.log_manager import LogManager


def _build_artifact_writer(
    fm: FileManager,
    lm: LogManager,
    memory: GlobalMemory | None = None,
) -> ArtifactWriter:
    mem = memory or GlobalMemory("ws_1", fm.runtime_base_path)
    from pathlib import Path

    def _delete_at_path(path: str) -> bool:
        try:
            p = Path(path)
            if p.exists() and p.is_file():
                p.unlink()
                return True
        except OSError:
            pass
        return False

    return ArtifactWriter(
        fm.store_file_at_relative_path,
        lm.add_log,
        fm.read_binary_from_uri,
        register_artifacts=lambda *, execution, artifact_refs: None,
        find_artifact_refs_for_producer=mem.find_by_producer,
        delete_file_at_path=_delete_at_path,
        prune_global_memory_by_paths=mem.prune_by_paths,
    )


def test_file_manager_store_writes_bytes_and_returns_handle(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    a = fm.store_file_at_relative_path("notes/a.txt", b"one", filename="a.txt")
    b = fm.store_file_at_relative_path("notes/b.txt", b"two", filename="b.txt")

    from pathlib import Path
    assert Path(a.path).read_bytes() == b"one"
    assert Path(b.path).read_bytes() == b"two"
    assert a.size_bytes == 3
    assert b.filename == "b.txt"


def test_file_manager_read_binary_from_uri(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(b"abc")

    assert fm.read_binary_from_uri(str(payload_path)) == b"abc"
    assert fm.read_binary_from_uri(str(tmp_path / "missing.bin")) is None


def _make_ref(path: str, caption: str = "test caption", scope: str = "global", mime: str = "application/json", **_kw):
    from src.assistant.workspace.models import ArtifactRef
    return ArtifactRef(caption=caption, scope=scope, path=path, mime=mime)


def test_global_memory_register_then_list(tmp_path):
    mem = GlobalMemory("ws_gm", tmp_path)
    mem.register(
        execution_id="exec_1",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/story.json", caption="story blueprint")],
    )
    entries = mem.list_all()
    assert len(entries) == 1
    assert entries[0].agent_id == "StoryAgent"
    assert entries[0].artifacts[0].caption == "story blueprint"


def test_global_memory_persists_as_markdown(tmp_path):
    mem = GlobalMemory("ws_md", tmp_path)
    mem.register(
        execution_id="exec_1",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/story.json")],
    )
    md_path = tmp_path / "ws_md" / "global_memory.md"
    assert md_path.exists()
    text = md_path.read_text(encoding="utf-8")
    assert "# Global memory" in text
    assert "## Entries" in text
    assert "```json" in text
    assert "exec_1" in text
    assert "StoryAgent" in text


def test_global_memory_round_trip_through_disk(tmp_path):
    mem1 = GlobalMemory("ws_rt", tmp_path)
    mem1.register(
        execution_id="exec_1",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/a.json")],
    )
    mem1.register(
        execution_id="exec_2",
        agent_id="ScreenplayAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/b.json")],
    )
    # New instance reads back the same entries from disk.
    mem2 = GlobalMemory("ws_rt", tmp_path)
    entries = mem2.list_all()
    assert len(entries) == 2
    assert {e.agent_id for e in entries} == {"StoryAgent", "ScreenplayAgent"}


def test_global_memory_legacy_jsonl_fallback(tmp_path):
    """Workspaces written before the rename use ``artifact_registry.jsonl`` —
    GlobalMemory must read them transparently so old runs still load."""
    import json as _json
    wid = "ws_legacy"
    workspace_dir = tmp_path / wid
    workspace_dir.mkdir(parents=True)
    legacy = workspace_dir / "artifact_registry.jsonl"
    legacy.write_text(
        _json.dumps({
            "execution_id": "exec_legacy",
            "agent_id": "LegacyAgent",
            "task_id": "task_legacy",
            "created_at": "2026-01-01T00:00:00+00:00",
            "artifacts": [
                {"caption": "old caption", "scope": "global", "path": "/p/old.json", "mime": "application/json"},
            ],
        }) + "\n",
        encoding="utf-8",
    )

    mem = GlobalMemory(wid, tmp_path)
    entries = mem.list_all()
    assert len(entries) == 1
    assert entries[0].agent_id == "LegacyAgent"
    assert entries[0].artifacts[0].path == "/p/old.json"


def test_global_memory_find_by_producer_and_has_run(tmp_path):
    mem = GlobalMemory("ws_p", tmp_path)
    mem.register(
        execution_id="exec_1",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/a.json")],
    )
    mem.register(
        execution_id="exec_2",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/b.json")],
    )
    refs = mem.find_by_producer(task_id="task_1", agent_id="StoryAgent")
    assert {r.path for r in refs} == {"/p/a.json", "/p/b.json"}
    assert mem.has_producer_run(task_id="task_1", agent_id="StoryAgent") is True
    assert mem.has_producer_run(task_id="task_1", agent_id="OtherAgent") is False


def test_global_memory_prune_by_paths_removes_refs_and_empty_entries(tmp_path):
    mem = GlobalMemory("ws_prune", tmp_path)
    mem.register(
        execution_id="exec_1",
        agent_id="StoryAgent",
        task_id="task_1",
        artifacts=[_make_ref("/p/a.json"), _make_ref("/p/b.json")],
    )
    removed = mem.prune_by_paths(["/p/a.json"])
    assert removed == 1
    entries = mem.list_all()
    assert len(entries) == 1
    assert {r.path for r in entries[0].artifacts} == {"/p/b.json"}

    removed_all = mem.prune_by_paths(["/p/b.json"])
    assert removed_all == 1
    assert mem.list_all() == []


def test_log_manager_filter(tmp_path):
    lm = LogManager("ws_1", tmp_path)
    lm.add_log(event="artifact.persisted", details={"msg": "hello"}, agent_id="a1", task_id="t1")
    lm.add_log(event="memory.written", details={"msg": "world"}, agent_id="a2", task_id="t2")

    filtered = lm.get_logs(event="artifact.persisted", agent_id="a1")

    assert len(filtered) == 1
    assert filtered[0].event == "artifact.persisted"


def test_log_manager_requires_event(tmp_path):
    lm = LogManager("ws_1", tmp_path)
    with pytest.raises(ValueError, match="event"):
        lm.add_log(event="")


def test_artifact_writer_hydrate_and_persist_index(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_artifact_writer(fm, lm)

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

    persisted_paths, index = am.persist_execution_from_plan(
        execution,
        assignments=[
            {
                "kind": "json_snapshot",
                "source_key": "",
                "relative_path": "artifacts/AgentA/AgentA_exec_1.json",
            }
        ],
    )
    assert persisted_paths == {}
    assert index is not None
    # Snapshot index now keys producers by agent_id (no asset_key field).
    assert index["agent_id"] == "AgentA"

    hydrated = am.hydrate_indexed_assets({"AgentA": index})
    assert hydrated["AgentA"]["content"]["value"] == 42

    # Snapshot landed at the planned relative path under the workspace runtime root.
    snapshot = tmp_path / "ws_1" / "artifacts" / "AgentA" / "AgentA_exec_1.json"
    assert snapshot.exists()


def test_artifact_writer_persist_rewrites_uris_before_json_snapshot(tmp_path):
    """Media must be written and URIs rewritten before JSON snapshot is serialized."""
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_artifact_writer(fm, lm)

    stale_uri = str(tmp_path / "gone" / "img_001.png")
    execution = SimpleNamespace(
        id="exec_7",
        task_id="task_uri",
        agent_id="KeyFrameAgent",
        results={
            "content": {
                "global_anchors": {
                    "characters": [
                        {
                            "entity_id": "char_001",
                            "image_asset": {
                                "asset_id": "img_char_001_global",
                                "uri": stale_uri,
                                "format": "png",
                            },
                        }
                    ],
                    "locations": [],
                    "props": [],
                },
                "scenes": [],
            },
            "_media_files": {
                "img_char_001_global": {
                    "file_content": b"\x89PNG\r\n",
                    "filename": "img_char_001_global.png",
                    "description": "test",
                },
            },
        },
    )

    am.persist_execution_from_plan(
        execution,
        assignments=[
            {
                "kind": "media",
                "source_key": "img_char_001_global",
                "relative_path": (
                    "artifacts/media/KeyFrameAgent/image/img_char_001_global.png"
                ),
            },
            {
                "kind": "json_snapshot",
                "source_key": "",
                "relative_path": "artifacts/KeyFrameAgent/keyframeagent_exec_7.json",
            },
        ],
    )

    written = (
        tmp_path
        / "ws_1"
        / "artifacts"
        / "KeyFrameAgent"
        / "keyframeagent_exec_7.json"
    )
    assert written.exists()
    text = written.read_text(encoding="utf-8")
    assert stale_uri not in text
    assert "img_char_001_global.png" in text
    assert str(tmp_path / "ws_1") in text or "/ws_1/" in text.replace("\\", "/")


def test_artifact_writer_collect_materialized_files_reads_binary_by_uri(tmp_path):
    fm = FileManager("ws_1", tmp_path)
    lm = LogManager("ws_1", tmp_path)
    am = _build_artifact_writer(fm, lm)

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
