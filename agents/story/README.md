# StoryAgent

Expands a draft (or structures a user outline) into a **full** `story_blueprint` JSON persisted by the Assistant / workspace.

## Screenplay creative prompt vs full artifact

**ScreenplayAgent** (in `screenplay/agent.py`) embeds a **field-selected** copy of story `content` in its blueprint creative-fill user message via `_story_content_embed_for_creative_llm`: it **omits whole keys** (e.g. cast `profile` / `motivation` / `flaw`, location `description`, arc `conflict` / `turning_point`, scene `goal` / `conflict` / `turn`) so the screenplay LLM is not fed duplicate long narrative that it must rewrite anyway. **`build_skeleton` still uses the full** `story_blueprint` from `resolved_inputs`. No list/string slicing — only absent keys.

See `agents/SCHEMA_SLIMDOWN_EVAL.md` §1.3.
