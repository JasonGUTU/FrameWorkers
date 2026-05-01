"""Diagnostic: replay InputResolver's KeyFrameAgent label routing once.

Reuses the workspace produced by smoke3b's intake_img_01 run, but
**truncates global_memory.md to the state right before KeyFrameAgent
ran** (otherwise KF's own dozens of "Global character reference image
for char_001..." entries pollute the LLM's view and make the rerun
non-equivalent).

Then it instantiates a fresh InputResolver against that truncated
state and asks "what would you have selected for KeyFrameAgent now?"

Output: full LLM response (selections + rationale), plus a one-line
verdict on whether the fixture image was routed to any of
character_reference / location_reference / prop_reference / style_reference.

Read-only on the original workspace; writes a temp workspace under /tmp.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = REPO_ROOT / "plan-stack-backend"
for p in (str(REPO_ROOT), str(PKG_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from inference.config.config_loader import ConfigLoader  # noqa: E402

for fname in (".env", ".env.example"):
    p = REPO_ROOT / fname
    if p.is_file():
        ConfigLoader.load_env_file(str(p), override=False)

from agents import AGENT_REGISTRY  # noqa: E402
from inference.clients import LLMClient  # noqa: E402
from src.assistant.workspace.global_memory import GlobalMemory  # noqa: E402
from src.assistant.workspace.file_manager import FileManager  # noqa: E402
from src.assistant.workspace.input_resolver import InputResolver  # noqa: E402


SOURCE_WORKSPACE = (
    REPO_ROOT
    / "Runtime"
    / "assistant_pipeline"
    / "20260430_203350_smoke3b"
    / "workspaces"
    / "intake_img_01"
    / "workspace_global_20260430_203351"
)

# We keep entries from agents UPSTREAM of KeyFrameAgent in the
# intake_img_01 chain. Any entry produced by KeyFrameAgent or later is
# dropped — that's the post-KF pollution we need to filter out.
KEEP_AGENT_IDS = {"user", "IntakeImageAgent", "BriefEnricherAgent", "StoryAgent", "ScreenplayAgent"}


def _read_global_memory(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    # Single ```json … ``` fence holds the entries array.
    import re
    m = re.search(r"```json\s*\n([\s\S]*?)\n```", text, re.MULTILINE)
    if not m:
        raise RuntimeError(f"No JSON fence found in {path}")
    return json.loads(m.group(1))


def _write_global_memory(path: Path, entries: list[dict]) -> None:
    body = (
        "# Global memory — diagnostic replay\n\n"
        "Truncated snapshot of intake_img_01 workspace at the point right "
        "before KeyFrameAgent ran. Used to reproduce InputResolver's label "
        "routing decision for KF without contamination from KF's own outputs.\n\n"
        "## Entries\n\n"
        "```json\n"
        + json.dumps(entries, ensure_ascii=False, indent=2)
        + "\n```\n"
    )
    path.write_text(body, encoding="utf-8")


def main() -> int:
    src_mem = SOURCE_WORKSPACE / "global_memory.md"
    if not src_mem.is_file():
        print(f"ERROR: source global_memory.md not found at {src_mem}")
        return 2

    all_entries = _read_global_memory(src_mem)
    kept = [e for e in all_entries if e.get("agent_id") in KEEP_AGENT_IDS]

    print(f"=== source global_memory.md ===")
    print(f"  total entries: {len(all_entries)}")
    print(f"  kept (upstream of KF): {len(kept)}")
    print(f"  dropped agents: {sorted({e.get('agent_id','') for e in all_entries} - KEEP_AGENT_IDS)}")
    print()

    # Set up temp workspace
    temp_root = Path("/tmp") / f"diag_kf_routing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workspace_id = "diag_workspace"
    temp_ws_dir = temp_root / workspace_id
    temp_ws_dir.mkdir(parents=True, exist_ok=True)
    _write_global_memory(temp_ws_dir / "global_memory.md", kept)

    # Build GlobalMemory + FileManager + LLMClient + InputResolver
    gm = GlobalMemory(workspace_id=workspace_id, runtime_base_path=temp_root)
    fm = FileManager(workspace_id=workspace_id, runtime_base_path=temp_root)
    llm = LLMClient()
    resolver = InputResolver(gm, fm, llm)

    # Show what InputResolver will see (the registry it serializes)
    captions_index, id_to_path = gm.get_captions_index()
    print("=== caption registry (as InputResolver sees) ===")
    print(captions_index)
    print()

    fixture_path = None
    for i, p in enumerate(id_to_path):
        if "intake_image_input" in p and p.endswith(".png"):
            fixture_path = p
            print(f"  fixture image is registry id #{i}: {p}")
            break
    if fixture_path is None:
        print("  WARNING: fixture image (intake_image_input.png) not in registry — bail")
        return 2
    print()

    # Pull KF's input_needs from its descriptor
    descriptor = AGENT_REGISTRY["KeyFrameAgent"]
    input_needs = descriptor.input_needs_description
    print("=== KeyFrameAgent input_needs_description ===")
    print(input_needs)
    print()

    # Replay resolution
    print("=== running InputResolver.resolve(KeyFrameAgent) … ===")
    result = resolver.resolve(
        agent_id="KeyFrameAgent",
        step_id="diag_replay_s05",
        input_needs_description=input_needs,
    )

    print("=== InputResolver result ===")
    print(f"rationale: {result.get('rationale')}")
    print()
    print("selected_artifact_paths:")
    for p in result.get("selected_artifact_paths", []):
        print(f"  - {p}")
    print()
    print("resolved_artifacts (per label):")
    resolved = result.get("resolved_artifacts", {})
    for label, val in resolved.items():
        if isinstance(val, list):
            print(f"  [{label}] (collection, n={len(val)}):")
            for entry in val:
                ed = entry.model_dump() if hasattr(entry, "model_dump") else entry
                print(f"    - path={ed.get('path','')[-90:]}")
                print(f"      caption={(ed.get('caption') or '')[:200]}")
        else:
            ed = val.model_dump() if hasattr(val, "model_dump") else val
            print(f"  [{label}] (single):")
            print(f"    path={(ed.get('path') or '')[-90:]}")
            print(f"    caption={(ed.get('caption') or '')[:200]}")
    print()

    # Final verdict on the fixture image
    print("=== verdict on fixture image ===")
    routed_to = []
    for label, val in resolved.items():
        if isinstance(val, list):
            for entry in val:
                ed = entry.model_dump() if hasattr(entry, "model_dump") else entry
                if ed.get("path") == fixture_path:
                    routed_to.append(label)
        else:
            ed = val.model_dump() if hasattr(val, "model_dump") else val
            if ed.get("path") == fixture_path:
                routed_to.append(label)
    if routed_to:
        print(f"fixture routed to label(s): {routed_to}")
    else:
        print(f"fixture NOT routed to ANY label — resolver dropped it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
