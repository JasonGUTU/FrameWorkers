from __future__ import annotations

from src.assistant.workspace.file_manager import FileManager
from src.assistant.workspace.log_manager import LogManager
from src.assistant.workspace.memory_manager import MemoryManager


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


def test_memory_manager_append_and_info(tmp_path):
    mm = MemoryManager("ws_1", tmp_path)
    mm.write_memory("hello")
    mm.append_memory("world")
    content = mm.read_memory()
    info = mm.get_memory_info()

    assert "hello" in content and "world" in content
    assert info["length"] == len(content)
    assert info["max_length"] == mm.MAX_MEMORY_LENGTH


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
