# Global memory — `workspace_global_20260508_131836`

Per-execution record of every artifact persisted in this workspace. Each entry below is one agent execution; its `artifacts` array carries the natural-language `caption`, `scope`, absolute `path` and `mime` for every file that execution wrote.

`InputResolver` reads this index to match artifacts against each consumer agent's `[label]` slots. Execution history (including failures) lives in the assistant executions table, not here.

## Entries

```json
[
  {
    "execution_id": "brief_20260508_131846_759498",
    "agent_id": "user",
    "step_id": "",
    "created_at": "2026-05-08T13:18:46.763268+00:00",
    "artifacts": [
      {
        "caption": "Structured metadata document (JSON) for a user-submitted text brief. Payload carries the raw text verbatim. Pipeline entry point — consumed by story / screenplay / narration agents.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_phaseB_v2_20260508_131825/_workspace/workspace_global_20260508_131836/inputs/brief_20260508_131846_759498.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_1_f8462668",
    "agent_id": "StoryAgent",
    "step_id": "step_1_f9a01e2e",
    "created_at": "2026-05-08T13:20:31.629971+00:00",
    "artifacts": [
      {
        "caption": "Story blueprint: 3 scene(s), 2 character(s). Structured input for screenplay generation.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_phaseB_v2_20260508_131825/_workspace/workspace_global_20260508_131836/artifacts/StoryAgent/step_1_f9a01e2e_storyagent_exec_1.json",
        "mime": "application/json"
      }
    ]
  },
  {
    "execution_id": "exec_2_8e27aa40",
    "agent_id": "ScreenplayAgent",
    "step_id": "step_2_6dcc548d",
    "created_at": "2026-05-08T13:24:00.176759+00:00",
    "artifacts": [
      {
        "caption": "Screenplay: 3 scene(s), 11 shot(s). Input for keyframe planning and audio scoring.",
        "scope": "global",
        "path": "/home/zhendong_li/FrameWorkers/evals/sub-agents/framework_cr_001_phaseB_v2_20260508_131825/_workspace/workspace_global_20260508_131836/artifacts/ScreenplayAgent/step_2_6dcc548d_screenplayagent_exec_2.json",
        "mime": "application/json"
      }
    ]
  }
]
```
