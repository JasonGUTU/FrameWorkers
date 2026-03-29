/* ── helpers ── */
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function syntaxHighlight(data) {
  const str = JSON.stringify(data, null, 2);
  return str.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?|[{}\[\],:])/g,
    (m) => {
      if (/^"/.test(m)) return /:$/.test(m)
        ? `<span class="json-key">${escapeHtml(m)}</span>`
        : `<span class="json-str">${escapeHtml(m)}</span>`;
      if (/true|false/.test(m)) return `<span class="json-bool">${m}</span>`;
      if (/null/.test(m))        return `<span class="json-null">${m}</span>`;
      if (/[{}\[\]]/.test(m))    return `<span class="json-punct">${m}</span>`;
      if (/[,:]/.test(m))        return `<span class="json-punct">${m}</span>`;
      return `<span class="json-num">${m}</span>`;
    }
  );
}

function primaryTextFromValue(text) {
  if (text == null || text === "") return "";
  return typeof text === "string" ? text.trim() : "";
}

function hydrateIndexedAssets(assets) {
  const out = {};
  for (const [k, v] of Object.entries(assets || {})) {
    const idx = v && v.value && v.value._asset_index;
    if (idx && typeof idx === "object" && idx.json_uri) {
      out[k] = { _hydrated_from_uri: idx.json_uri, _asset_index: idx };
    } else {
      out[k] = v;
    }
  }
  return out;
}

/* ── demo data ── */
const DESCRIPTOR_MAP = {
  StoryAgent: "story_blueprint",
  ScreenplayAgent: "screenplay",
  StoryboardAgent: "storyboard",
  KeyFrameAgent: "keyframes",
  VideoAgent: "video_package",
  AudioAgent: "audio_package",
};

const EXECUTE_EXAMPLE = {
  agent_id: "StoryAgent",
  task_id: "task_demo_001",
  execute_fields: {
    text: "Create a cinematic short: a watchmaker fixes a broken watch before midnight.",
  },
};

/* ── builders ── */
function ioBlock(title, badgeLabel, badgeClass, subtitle, data) {
  const sub = subtitle ? `<p class="io-sub">${escapeHtml(subtitle)}</p>` : "";
  return `
    <div class="io-block">
      <div class="io-block-header">
        <span class="io-badge ${badgeClass}">${badgeLabel}</span>
        <h4>${title}</h4>
      </div>
      ${sub}
      <pre>${syntaxHighlight(data)}</pre>
    </div>`;
}

function sectionCard(colorClass, icon, titleHtml, descText, bodyHtml) {
  const desc = descText ? `<span class="section-desc">${descText}</span>` : "";
  return `
    <div class="section-card ${colorClass}">
      <div class="section-header">
        <div class="section-icon">${icon}</div>
        <h2>${titleHtml}</h2>
        ${desc}
      </div>
      <div class="section-body">${bodyHtml}</div>
    </div>`;
}

function phaseArrow() {
  return `
    <div class="phases-arrow">
      <svg class="phases-arrow-svg" width="28" height="16" viewBox="0 0 28 16" fill="none">
        <line x1="0" y1="8" x2="22" y2="8" stroke="url(#pa)" stroke-width="1.5"/>
        <polyline points="16,3 22,8 16,13" stroke="url(#pa)" stroke-width="1.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
        <defs>
          <linearGradient id="pa" x1="0" y1="0" x2="28" y2="0" gradientUnits="userSpaceOnUse">
            <stop stop-color="#4f8ef7"/>
            <stop offset="1" stop-color="#a78bfa"/>
          </linearGradient>
        </defs>
      </svg>
    </div>`;
}

/* ── render ── */
function render() {
  const flowEl     = document.getElementById("flowViz");
  const httpEl     = document.getElementById("httpViz");
  const phasesEl   = document.getElementById("phasesViz");
  const subagentEl = document.getElementById("subagentViz");
  const workspaceEl= document.getElementById("workspaceViz");

  const { agent_id: agentId, task_id: taskId, execute_fields: ef } = EXECUTE_EXAMPLE;
  const executeFields = (ef && typeof ef === "object" && !Array.isArray(ef)) ? { ...ef } : {};

  const packagedAssets = {};
  if (executeFields.text) packagedAssets.source_text = primaryTextFromValue(executeFields.text);
  const mapped = {
    task_id: taskId,
    assets: packagedAssets,
    config: { target_total_duration_sec: 60, language: "en" },
  };
  const hydratedAssets = hydrateIndexedAssets(mapped.assets);

  const resultPayload = {
    produced_by: agentId,
    asset_key: DESCRIPTOR_MAP[agentId] || "(unknown)",
    _execution_debug: { attempts: 1, overall_pass: true },
  };

  /* ── Flow diagram — T-shape: Workspace below Assistant ── */
  flowEl.innerHTML = `
    <div class="flow-diagram">
      <svg class="flow-svg" viewBox="0 0 580 148" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrBlue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0.5 L0,7.5 L7,4 Z" fill="#7eb3ff"/>
          </marker>
          <marker id="arrTeal" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0.5 L0,7.5 L7,4 Z" fill="#2dd4bf"/>
          </marker>
        </defs>

        <!-- ── Lines ── -->
        <!-- Director → Assistant -->
        <line x1="134" y1="42" x2="180" y2="42"
              stroke="#7eb3ff" stroke-width="2.5" stroke-opacity="0.9" marker-end="url(#arrBlue)"/>
        <text x="157" y="35" text-anchor="middle" font-size="9.5" fill="#94a3b8" letter-spacing="0.5">HTTP</text>

        <!-- Assistant → Sub-agent -->
        <line x1="308" y1="42" x2="372" y2="42"
              stroke="#a78bfa" stroke-width="2.5" stroke-opacity="0.9" marker-end="url(#arrBlue)"/>
        <text x="340" y="35" text-anchor="middle" font-size="9.5" fill="#94a3b8" letter-spacing="0.5">in-process</text>

        <!-- Assistant → Workspace (vertical, dashed) -->
        <line x1="246" y1="70" x2="246" y2="98"
              stroke="#2dd4bf" stroke-width="2.5" stroke-opacity="0.9"
              stroke-dasharray="5,3" marker-end="url(#arrTeal)"/>
        <text x="261" y="87" text-anchor="start" font-size="9.5" fill="#94a3b8" letter-spacing="0.5">read / write</text>

        <!-- ── Nodes ── -->
        <!-- Director -->
        <rect x="10" y="20" width="124" height="44" rx="10"
              fill="rgba(251,191,36,0.09)" stroke="rgba(251,191,36,0.4)" stroke-width="1.2"/>
        <text x="72" y="40" text-anchor="middle" font-size="14">🎬</text>
        <text x="72" y="56" text-anchor="middle" font-size="12" font-weight="700" fill="#fbbf24">Director</text>

        <!-- Assistant -->
        <rect x="186" y="20" width="120" height="48" rx="10"
              fill="rgba(79,142,247,0.12)" stroke="rgba(79,142,247,0.45)" stroke-width="1.5"/>
        <text x="246" y="40" text-anchor="middle" font-size="14">⚙️</text>
        <text x="246" y="57" text-anchor="middle" font-size="12" font-weight="700" fill="#7eb3ff">Assistant</text>

        <!-- Sub-agent -->
        <rect x="378" y="20" width="130" height="44" rx="10"
              fill="rgba(167,139,250,0.1)" stroke="rgba(167,139,250,0.4)" stroke-width="1.2"/>
        <text x="443" y="40" text-anchor="middle" font-size="14">🤖</text>
        <text x="443" y="56" text-anchor="middle" font-size="12" font-weight="700" fill="#c4b5fd">Sub-agent</text>

        <!-- Workspace (below Assistant) -->
        <rect x="186" y="102" width="120" height="40" rx="10"
              fill="rgba(45,212,191,0.1)" stroke="rgba(45,212,191,0.45)" stroke-width="1.5"/>
        <text x="246" y="119" text-anchor="middle" font-size="12">💾</text>
        <text x="246" y="133" text-anchor="middle" font-size="11.5" font-weight="700" fill="#2dd4bf">Workspace</text>

        <!-- Sub-labels -->
        <text x="72"  y="74" text-anchor="middle" font-size="9" fill="#475569">Orchestrator</text>
        <text x="246" y="78" text-anchor="middle" font-size="9" fill="#475569">Pipeline Runner</text>
        <text x="443" y="74" text-anchor="middle" font-size="9" fill="#475569">Pipeline Agent</text>
        <text x="246" y="148" text-anchor="middle" font-size="9" fill="#475569">Runtime Storage</text>
      </svg>
    </div>`;

  /* ── HTTP section ── */
  const httpRequest = { agent_id: agentId, task_id: taskId, execute_fields: executeFields };
  const httpResponse = {
    task_id: taskId,
    execution_id: "exec_demo_placeholder",
    status: "COMPLETED",
    results: resultPayload,
    error: null,
    workspace_id: "workspace_global",
  };
  httpEl.outerHTML = sectionCard(
    "card-blue", "🌐",
    `HTTP &nbsp;<code>POST /api/assistant/execute</code>`,
    "Director ↔ Assistant",
    `<div class="http-pair">
      ${ioBlock("Director → Assistant", "REQUEST", "badge-request", null, httpRequest)}
      <div class="arrow-col"><div class="arrow-shaft"></div><div class="arrow-tip"></div></div>
      ${ioBlock("Assistant → Director", "RESPONSE", "badge-response",
        "task_id · execution_id · status · results · error · workspace_id", httpResponse)}
    </div>`
  );

  /* ── Execution phases — step cards ── */
  function stepCard(fnName, rows, note) {
    const rowsHtml = rows.map(([label, val, type]) => `
      <div class="step-row">
        <span class="step-label">${escapeHtml(label)}</span>
        <span class="step-val step-${type || 'neutral'}">${escapeHtml(val)}</span>
      </div>`).join("");
    const noteHtml = note ? `<div class="step-note">${escapeHtml(note)}</div>` : "";
    return `
      <div class="step-card">
        <div class="step-fn">${escapeHtml(fnName)}</div>
        <div class="step-rows">${rowsHtml}</div>
        ${noteHtml}
      </div>`;
  }

  const phase1Html =
    stepCard("workspace.get_memory_brief(task_id)", [
      ["task_id", taskId, "param"],
      ["returns", "{ global_memory: [MemoryEntry, ...] }", "returns"],
    ]) +
    stepCard("_resolve_inputs_for_agent_with_llm(agent_id, task_id, workspace, packaged_data)", [
      ["① 读取上下文", "descriptor.catalog_entry[:1200]  +  global_memory artifact_locations  +  workspace.get_task_file_tree_text(task_id)", "note"],
      ["② system prompt", '"You select which semantic artifacts this sub-agent needs. Use only role values from available_roles. Return strict JSON only."', "param"],
      ["③ user prompt", '{ target_agent_id, descriptor_hint, available_roles, global_memory, file_tree }', "param"],
      ["④ LLM call", "pipeline_llm_client.chat_json(max_tokens=700, reasoning_effort='low')", "param"],
      ["⑤ 校验", "required_roles 非空 且 selected_roles 覆盖全部 required_roles，否则抛 BadExecuteFieldsError", "note"],
      ["→ returns", "{ required_roles, selected_roles, append_to_source_text, rationale }", "returns"],
    ]) +
    stepCard("package_data(text_seed)", [
      ["text_seed", executeFields.text, "param"],
      ["produces", "assets: { source_text: '...' }", "returns"],
    ]);

  const phase2Html =
    stepCard("descriptor.build_input(task_id, bundle, config)", [
      ["task_id",   taskId,        "param"],
      ["bundle",    "FrozenInputBundleV2",  "param"],
      ["config",    "{ target_total_duration_sec: 60, language: 'en' }", "param"],
      ["→ returns", "TypedInput (Pydantic model)", "returns"],
    ]) +
    stepCard("await agent.run(typed_input, **kwargs)", [
      ["input_bundle_v2",  "FrozenInputBundleV2",   "param"],
      ["materialize_ctx",  "MaterializeContext",     "param"],
      ["rework_notes",     '""',                    "param"],
      ["max_retries",      "3",                     "param"],
      ["→ returns",        "ExecutionResult",        "returns"],
    ], "async — 内部含 evaluator retry 循环");

  const phase3Html =
    stepCard("_deterministic_output_persist_plan(execution, asset_key)", [
      ["purpose", "先生成确定性 base_plan，作为 LLM 的起点", "note"],
      ["→ returns", "base_plan: List[{ kind, source_key, relative_path, role }]", "returns"],
    ]) +
    stepCard("_refine_output_persist_plan_with_llm(workspace, execution, descriptor, base_plan)", [
      ["① 读取上下文", "descriptor.catalog_entry[:900]  +  workspace_file_tree (含 artifacts/)  +  task_runtime_file_tree  +  execution.results._naming_specs  +  naming_policy", "note"],
      ["② system prompt", '"Adjust relative_path to avoid collisions and align with artifacts/media/<Agent>/<kind>/ layout. Keep same number of entries, kind/source_key unchanged. Every path must start with artifacts/."', "param"],
      ["③ user prompt", '{ target_agent_id, task_id, descriptor_hint, proposed_assignments: base_plan, naming_specs, naming_policy, workspace_file_tree, task_runtime_file_tree }', "param"],
      ["④ LLM call", "pipeline_llm_client.chat_json(max_tokens=4000, reasoning_effort='low')", "param"],
      ["⑤ merge", "_merge_persist_assignments(base_plan, llm_assignments) — LLM 结果与 base_plan 合并", "note"],
      ["→ returns", 'assignments: [{ kind: "binary|media|json_snapshot|keyframes_manifest", source_key, relative_path: "artifacts/...", role }]', "returns"],
    ]) +
    stepCard("workspace.persist_execution_from_plan(execution, assignments, overwrite=True)", [
      ["execution",         "AgentExecution",          "param"],
      ["assignments",       "List[PersistAssignment]", "param"],
      ["overwrite_existing","True",                    "param"],
    ]) +
    stepCard("workspace.log_execution_result(execution)", [
      ["execution", "AgentExecution (status=COMPLETED|FAILED)", "param"],
    ]) +
    stepCard("workspace.add_memory_entry(content, task_id, agent_id, ...)", [
      ["content",            "summary string",  "param"],
      ["task_id",            taskId,            "param"],
      ["agent_id",           agentId,           "param"],
      ["artifact_locations", "List[str]",       "param"],
    ]);

  phasesEl.outerHTML = sectionCard(
    "card-orange", "⚡",
    "Assistant 执行三阶段",
    "execute_agent_for_task()",
    `<div class="phases-grid">
      <div class="phase-block phase-1">
        <div class="phase-header">
          <div class="phase-num">1</div>
          <h3>Build Inputs</h3>
        </div>
        <div class="phase-body">${phase1Html}</div>
      </div>
      ${phaseArrow()}
      <div class="phase-block phase-2">
        <div class="phase-header">
          <div class="phase-num">2</div>
          <h3>Execute Agent</h3>
        </div>
        <div class="phase-body">${phase2Html}</div>
      </div>
      ${phaseArrow()}
      <div class="phase-block phase-3">
        <div class="phase-header">
          <div class="phase-num">3</div>
          <h3>Persist Results</h3>
        </div>
        <div class="phase-body">${phase3Html}</div>
      </div>
    </div>`
  );

  /* ── Sub-agent section ── */
  const subagentIn = {
    "descriptor.build_input": {
      signature: "(task_id, readonly_input_bundle_v2: FrozenInputBundleV2, config) → TypedInput (Pydantic)",
      typed_input_preview: { task_id: mapped.task_id, config: mapped.config, assets: hydratedAssets },
    },
    "input_bundle_v2": "FrozenInputBundleV2 — context.resolved_inputs 含 LLM selected_roles",
  };

  const subagentOut = {
    "ExecutionResult fields": {
      output: "BaseModel | None  — Pydantic 主输出",
      asset_dict: "dict[str, Any] | None  — materializer 归一化",
      eval_result: "dict  — { overall_pass, ... }",
      passed: "bool",
      attempts: "int",
      media_assets: "list[MediaAsset]  — 媒体类 agent 专用",
    },
    "example_results": resultPayload,
  };

  subagentEl.outerHTML = sectionCard(
    "card-purple", "🤖",
    "Sub-agent 边界",
    "进程内调用，非 HTTP",
    ioBlock("Assistant → Sub-agent", "INPUT", "badge-input", null, subagentIn) +
    `<div class="io-divider"></div>` +
    ioBlock("Sub-agent → Assistant", "OUTPUT", "badge-output", null, subagentOut)
  );

  /* ── Workspace section ── */
  const wsRead = {
    "get_memory_brief(task_id)": {
      returns: "{ global_memory: [MemoryEntry] }",
      note: "每次 execute 必调用，注入上下文记忆",
    },
    "hydrate_indexed_assets(assets)": {
      params: "assets: Dict[str, Any]",
      note: "将含 _asset_index.json_uri 的项展开为 sub-agent 可消费形态",
    },
    "list_files()": {
      params: "无参数",
      returns: "List[FileMetadata]  — 返回工作区所有文件",
    },
    "list_memory_entries(task_id, agent_id, limit)": {
      returns: "List[MemoryEntry]",
    },
    "get_task_file_tree_text(task_id)": {
      returns: "str  — 文件树文本，供 LLM 感知产出结构",
    },
    "get_logs(operation_type, resource_type, agent_id, task_id, limit)": {
      returns: "List[LogEntry]",
    },
  };

  const wsWrite = {
    "log_execution_started(execution)": "写入执行开始日志",
    "log_execution_result(execution)": "写入完成日志 + metrics",
    "persist_execution_from_plan(execution, assignments, overwrite_existing)": {
      note: "LLM 生成 assignments 后调用，按计划落盘产出文件",
    },
    "add_memory_entry(content, task_id, agent_id, execution_result, artifact_locations)": {
      note: "执行成功后写入长期记忆",
    },
  };

  workspaceEl.outerHTML = sectionCard(
    "card-teal", "💾",
    "Workspace 边界",
    "Runtime 工作区读写",
    ioBlock("Assistant → Workspace", "READ", "badge-read", null, wsRead) +
    `<div class="io-divider"></div>` +
    ioBlock("Workspace ← Assistant", "WRITE", "badge-write", null, wsWrite)
  );
}

render();
