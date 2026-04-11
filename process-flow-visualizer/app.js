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
const EXECUTE_EXAMPLE = {
  agent_id: "StoryAgent",
  task_id: "task_demo_001",
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
  const _noop = { set innerHTML(_v) {}, set outerHTML(_v) {} };
  const $g = (id) => document.getElementById(id) || _noop;
  const flowEl     = $g("flowViz");
  const directorEl = $g("directorViz");
  const httpEl     = $g("httpViz");
  const phasesEl   = $g("phasesViz");
  const subagentEl = $g("subagentViz");
  const workspaceEl= $g("workspaceViz");
  const testAgentsEl          = $g("testAgentsViz");
  const testAssistantServiceEl = $g("testAssistantServiceViz");
  const testWorkspaceEl       = $g("testWorkspaceViz");
  const testSerializersEl     = $g("testSerializersViz");
  const testAssistantHttpEl   = $g("testAssistantHttpViz");
  const taskStackEl           = $g("taskStackViz");
  const testDirectorNostackEl = $g("testDirectorNostackViz");
  const testDtsEl             = $g("testDtsViz");

  const { agent_id: agentId, task_id: taskId } = EXECUTE_EXAMPLE;

  const packagedAssets = {};
  const mapped = {
    task_id: taskId,
    assets: packagedAssets,
  };
  const hydratedAssets = hydrateIndexedAssets(mapped.assets);

  /* ── Flow diagram — Chat loop + T-shape pipeline ── */
  flowEl.innerHTML = `
    <div class="flow-diagram">
      <svg class="flow-svg" viewBox="0 0 820 190" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrBlue"   markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0.5 L0,7.5 L7,4 Z" fill="#7eb3ff"/></marker>
          <marker id="arrTeal"   markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0.5 L0,7.5 L7,4 Z" fill="#2dd4bf"/></marker>
          <marker id="arrYellow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0.5 L0,7.5 L7,4 Z" fill="#fbbf24"/></marker>
          <marker id="arrYellowFaint" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0.5 L0,7.5 L7,4 Z" fill="#a37f1a"/></marker>
          <marker id="arrOrange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0.5 L0,7.5 L7,4 Z" fill="#f97316"/></marker>
        </defs>

        <!-- ══ CURRENT path: Chat bypasses Task Stack → polls Director directly ══ -->
        <!-- arc over Task Stack node -->
        <path d="M 94 38 C 148 8 222 8 264 38" fill="none"
              stroke="#a37f1a" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="5,3"
              marker-end="url(#arrYellowFaint)"/>
        <text x="179" y="6" text-anchor="middle" font-size="8.5" fill="#64748b">current · poll</text>

        <!-- Director → Chat reply (arc below current path) -->
        <path d="M 264 66 Q 160 118 94 55" fill="none"
              stroke="#a37f1a" stroke-width="1.2" stroke-opacity="0.4" stroke-dasharray="4,3"
              marker-end="url(#arrYellowFaint)"/>
        <text x="155" y="116" text-anchor="middle" font-size="8.5" fill="#64748b">reply</text>

        <!-- ══ FUTURE path: Chat → Task Stack → Director ══ -->
        <line x1="94" y1="46" x2="118" y2="46"
              stroke="#f97316" stroke-width="1.5" stroke-opacity="0.55" stroke-dasharray="4,3"
              marker-end="url(#arrOrange)"/>
        <line x1="238" y1="46" x2="260" y2="46"
              stroke="#f97316" stroke-width="1.5" stroke-opacity="0.55" stroke-dasharray="4,3"
              marker-end="url(#arrOrange)"/>
        <text x="179" y="58" text-anchor="middle" font-size="8" fill="#7c4a1e">future</text>

        <!-- Director → Assistant -->
        <line x1="384" y1="42" x2="422" y2="42"
              stroke="#7eb3ff" stroke-width="2.5" stroke-opacity="0.9" marker-end="url(#arrBlue)"/>
        <text x="403" y="35" text-anchor="middle" font-size="9.5" fill="#94a3b8">HTTP</text>

        <!-- Assistant → Sub-agent -->
        <line x1="554" y1="42" x2="596" y2="42"
              stroke="#a78bfa" stroke-width="2.5" stroke-opacity="0.9" marker-end="url(#arrBlue)"/>
        <text x="575" y="35" text-anchor="middle" font-size="9.5" fill="#94a3b8">in-process</text>

        <!-- Assistant → Workspace -->
        <line x1="488" y1="70" x2="488" y2="110"
              stroke="#2dd4bf" stroke-width="2.5" stroke-opacity="0.9"
              stroke-dasharray="5,3" marker-end="url(#arrTeal)"/>
        <text x="504" y="93" text-anchor="start" font-size="9" fill="#94a3b8">read / write</text>

        <!-- ── Nodes ── -->
        <!-- Chat -->
        <rect x="10" y="26" width="84" height="40" rx="9"
              fill="rgba(100,116,139,0.1)" stroke="rgba(100,116,139,0.35)" stroke-width="1.2"/>
        <text x="52" y="43" text-anchor="middle" font-size="13">💬</text>
        <text x="52" y="57" text-anchor="middle" font-size="11.5" font-weight="700" fill="#94a3b8">Chat</text>

        <!-- Task Stack (TODO — dashed border, between Chat and Director) -->
        <rect x="118" y="22" width="120" height="48" rx="10"
              fill="rgba(249,115,22,0.07)" stroke="rgba(249,115,22,0.4)" stroke-width="1.5"
              stroke-dasharray="5,3"/>
        <text x="178" y="42" text-anchor="middle" font-size="13">📋</text>
        <text x="178" y="58" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fb923c">Task Stack</text>

        <!-- Director -->
        <rect x="264" y="18" width="120" height="48" rx="10"
              fill="rgba(251,191,36,0.09)" stroke="rgba(251,191,36,0.4)" stroke-width="1.5"/>
        <text x="324" y="38" text-anchor="middle" font-size="14">🎬</text>
        <text x="324" y="55" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fbbf24">Director</text>

        <!-- Assistant -->
        <rect x="422" y="20" width="132" height="48" rx="10"
              fill="rgba(79,142,247,0.12)" stroke="rgba(79,142,247,0.45)" stroke-width="1.5"/>
        <text x="488" y="40" text-anchor="middle" font-size="14">⚙️</text>
        <text x="488" y="57" text-anchor="middle" font-size="12" font-weight="700" fill="#7eb3ff">Assistant</text>

        <!-- Sub-agent -->
        <rect x="596" y="20" width="120" height="44" rx="10"
              fill="rgba(167,139,250,0.1)" stroke="rgba(167,139,250,0.4)" stroke-width="1.2"/>
        <text x="656" y="39" text-anchor="middle" font-size="14">🤖</text>
        <text x="656" y="55" text-anchor="middle" font-size="12" font-weight="700" fill="#c4b5fd">Sub-agent</text>

        <!-- Workspace -->
        <rect x="422" y="114" width="132" height="38" rx="10"
              fill="rgba(45,212,191,0.1)" stroke="rgba(45,212,191,0.45)" stroke-width="1.5"/>
        <text x="488" y="130" text-anchor="middle" font-size="12">💾</text>
        <text x="488" y="144" text-anchor="middle" font-size="11.5" font-weight="700" fill="#2dd4bf">Workspace</text>

        <!-- Sub-labels -->
        <text x="52"  y="77" text-anchor="middle" font-size="8.5" fill="#475569">User / Frontend</text>
        <text x="178" y="80" text-anchor="middle" font-size="8" fill="#7c4a1e">Frontend ↔ Director 中间层</text>
        <text x="178" y="90" text-anchor="middle" font-size="8" fill="#7c4a1e">TODO · Roadmap 01</text>
        <text x="324" y="76" text-anchor="middle" font-size="8.5" fill="#475569">Orchestrator · LLM Router</text>
        <text x="488" y="78" text-anchor="middle" font-size="8.5" fill="#475569">Pipeline Runner</text>
        <text x="656" y="74" text-anchor="middle" font-size="8.5" fill="#475569">Pipeline Agent</text>
        <text x="488" y="163" text-anchor="middle" font-size="8.5" fill="#475569">Runtime Storage</text>
      </svg>
    </div>`;

  /* ── Director section ── */
  // Phase 1: _cycle() — poll, mark read, fetch agents
  const dirPhase1Html =
    stepCard("GET /api/messages/unread  (每 2 秒轮询)", [
      ["sender_type", '"user"', "param"],
      ["check_director_read", "true", "param"],
      ["check_user_read", "false", "param"],
      ["→ 取第一条", "unread[0]  →  msg_id + content", "returns"],
    ]) +
    stepCard("PUT /api/messages/{id}/read-status", [
      ["director_read_status", '"READ"', "param"],
    ], "标记后同一条消息不会再次被消费") +
    stepCard("GET /api/assistant/sub-agents", [
      ["→ returns", "[{ id, description, asset_key, capabilities }]", "returns"],
    ], "catalog 传入 run_nostack_pipeline，路由时使用");

  // Phase 2: run_nostack_pipeline() 开头 — 拉取上下文，合并 goal
  const dirPhase2Html =
    stepCard("GET /api/assistant/workspace/memory/brief", [
      ["task_id", '"standalone_chat"  (固定)', "param"],
      ["→ gm0", "{ global_memory: [{ task_id, agent_id, created_at, execution_result }] }", "returns"],
    ]) +
    stepCard("_latest_execution_summary(task_id)", [
      ["GET /api/assistant/executions/task/{task_id}", "取 executions[-1]", "param"],
      ["→ summary0", "{ execution_id, status, agent_id, results, error } | null", "returns"],
    ]) +
    stepCard("_prior_user_chat_lines(client, current_msg_id)", [
      ["GET /api/messages/list", "全量消息列表", "param"],
      ["过滤", "sender_type==user，排除 current_msg_id，按 timestamp 排序", "note"],
      ["→ prior_lines", "List[str]  最近 24 条用户文本  (MERGE_PRIOR_USER_LINES_MAX=24)", "returns"],
    ]) +
    stepCard("planner.merge_session_goal()", [
      ["latest_user_message", "当前消息文本", "param"],
      ["global_memory", "gm0[:40]", "param"],
      ["execution_summary", "summary0 (或 null)", "param"],
      ["prior_user_chat_lines", "prior_lines (或 None)", "param"],
    ], "needs_llm = bool(global_memory) or bool(execution_id) or bool(prior_lines) — 否则直接返回原文") +
    stepCard("LLM call  →  merged_goal", [
      ["model", "DIRECTOR_ROUTING_MODEL  (gemini-2.5-flash)", "param"],
      ["→ JSON", '{ "merged_goal": "<全量指令>" }', "returns"],
    ], "goal_text 固定用于本次 run 全部 step 的 routing LLM original_user_goal 输入（不传给 sub-agent）");

  // Phase 3: while True 路由→执行循环
  const dirPhase3Html =
    stepCard("while True:  (每步先刷新上下文)", [
      ["GET /api/assistant/workspace/memory/brief", "→ gm (fresh)", "param"],
      ["_latest_execution_summary(task_id)", "→ summary (fresh)", "param"],
    ], "每次路由前重新拉取，确保 LLM 看到最新记忆和执行结果") +
    stepCard("planner.choose_pipeline_step()", [
      ["original_user_goal", "goal_text  (全程不变)", "param"],
      ["after_frontend_user_message", "step==0 时为 true", "param"],
      ["last_agent_id", "上一步 agent id (或 None)", "param"],
      ["available_agents / global_memory / execution_summary", "fresh 上下文", "param"],
      ["LLM routing call", "prompt(allowed+catalog+goal+memory+execution+step) → JSON", "note"],
      ['→ JSON: action=="done"', "break → POST /api/messages/create (Pipeline complete)", "returns"],
      ['→ JSON: action=="run"', "选择 agent_id，进入 execute_agent", "returns"],
      ['→ !should_run', "break → POST /api/messages/create (routing 错误)", "returns"],
    ]) +
    stepCard("client.execute_agent(agent_id, task_id)", [
      ["POST /api/assistant/execute", "→ 见下方 HTTP 卡", "param"],
      ["body", '{ "agent_id": "...", "task_id": "..." }', "param"],
      ["→ result", "{ status, error, error_reasoning, global_memory_brief, … }", "returns"],
    ], "status==FAILED 或含 error → break，发送错误消息") +
    stepCard("POST /api/messages/create  (每步回复)", [
      ["content", '"[DirectorNoStack] Step N: **agent_id** → COMPLETED\\n[status + error preview]"', "param"],
      ["sender_type", '"director"', "param"],
    ]);

  directorEl.outerHTML = sectionCard(
    "card-orange", "🎬",
    "DirectorNoStack 编排循环",
    "director_nostack/director.py + router.py",
    `<div class="phases-grid">
      <div class="phase-block phase-1">
        <div class="phase-header">
          <div class="phase-num">1</div>
          <h3>Poll &amp; Consume</h3>
        </div>
        <div class="phase-body">${dirPhase1Html}</div>
      </div>
      ${phaseArrow()}
      <div class="phase-block phase-2">
        <div class="phase-header">
          <div class="phase-num">2</div>
          <h3>Merge Goal</h3>
        </div>
        <div class="phase-body">${dirPhase2Html}</div>
      </div>
      ${phaseArrow()}
      <div class="phase-block phase-3">
        <div class="phase-header">
          <div class="phase-num">3</div>
          <h3>Pipeline Loop</h3>
        </div>
        <div class="phase-body">${dirPhase3Html}</div>
      </div>
    </div>`
  );

  /* ── HTTP section ── */
  const httpRequest = { agent_id: agentId, task_id: taskId };
  const httpResponse = {
    task_id: taskId,
    execution_id: "exec_demo_placeholder",
    status: "COMPLETED",
    error: null,
    error_reasoning: null,
    workspace_id: "workspace_global",
    global_memory_brief: {
      global_memory: [
        {
          execution_id: "exec_demo_placeholder",
          agent_id: agentId,
          task_id: taskId,
          status: "COMPLETED",
          created_at: "2026-04-07T12:00:00Z",
        },
      ],
    },
  };
  /* ── Task Stack (TODO) ── */
  taskStackEl.outerHTML = sectionCard(
    "card-orange", "📋",
    "Dynamic Task Stack — Director 集成",
    "dynamic-task-stack/  ·  Roadmap 01",
    `<div style="display:inline-block;background:rgba(255,160,40,0.15);border:1px solid rgba(255,160,40,0.4);color:#f0a040;font-size:0.78em;font-weight:600;letter-spacing:.08em;padding:3px 10px;border-radius:4px;margin-bottom:18px">TODO</div>
    <div style="display:flex;flex-direction:column;gap:12px;font-size:0.88em;color:#ccc;line-height:1.7">
      <div>
        <div style="font-weight:600;color:#e0e0e0;margin-bottom:4px">现状</div>
        <div>DirectorNoStack 使用固定 <code>standalone_chat</code> task_id，轮询 <code>/api/messages/unread</code> 驱动 pipeline，任务状态完全依赖内存与 chat 消息，无法中断恢复或并发调度。</div>
      </div>
      <div>
        <div style="font-weight:600;color:#e0e0e0;margin-bottom:4px">目标：将 Director 迁移至 Task Stack</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          <div>① <strong>任务生命周期管理</strong> — 每个 pipeline 运行对应一个 Task Stack 任务，支持 PENDING / RUNNING / COMPLETED / FAILED 状态追踪</div>
          <div>② <strong>中断恢复</strong> — pipeline 中断后可从上一个已完成 step 续跑，无需重头执行</div>
          <div>③ <strong>并发调度</strong> — 多个 user session 可并行运行独立 pipeline，不再共享同一 task_id</div>
          <div>④ <strong>上下文统一</strong> — Director 与 Assistant 共用 Task Stack 的 workspace / memory 接口，消除重复状态维护</div>
        </div>
      </div>
      <div style="padding:10px 14px;background:rgba(255,255,255,0.03);border-left:3px solid rgba(255,160,40,0.4);border-radius:4px;color:#aaa">
        依赖 Dynamic Task Stack 的 <code>create_app</code> 路由与 <code>AssistantStateStore</code> 已就绪，主要工作为 Director 调度层的重构。
      </div>
    </div>`
  );

  httpEl.outerHTML = sectionCard(
    "card-blue", "🌐",
    `HTTP &nbsp;<code>POST /api/assistant/execute</code>`,
    "Director ↔ Assistant",
    `<div style="margin-bottom:14px;padding:10px 14px;background:rgba(126,179,255,0.06);border-left:3px solid rgba(126,179,255,0.4);border-radius:4px;font-size:0.84em;color:#bbb;line-height:1.6">
      <strong style="color:#7eb3ff">HTTP body 收敛：</strong>
      只剩 <code>{agent_id, task_id}</code>。原始用户文本 / 媒体必须先经 <code>POST /api/workspace/upload</code> + 调对应 <code>IntakeXxxAgent</code> 落成 artifact，再由下游 agent 通过 <code>artifact_registry caption index</code> 召回。
    </div>
    <div class="http-pair">
      ${ioBlock("Director → Assistant", "REQUEST", "badge-request", "body 只携 agent_id + task_id；任何 user 输入需提前落 workspace artifact", httpRequest)}
      <div class="arrow-col"><div class="arrow-shaft"></div><div class="arrow-tip"></div></div>
      ${ioBlock("Assistant → Director", "RESPONSE", "badge-response",
        "task_id · execution_id · status · error · error_reasoning · workspace_id · global_memory_brief …", httpResponse)}
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
    stepCard("① 校验 + 启动", [
      ["build_execution_inputs(agent_id, task_id, workspace)", "校验 descriptor 在 registry，准备 inputs dict 骨架", "note"],
    ], "input-channel 统一后，sub-agent 只有一个输入源：InputResolver 选出来的 artifact") +
    stepCard("② LLM #1 选历史 artifact", [
      ["调用", "_resolve_inputs_for_agent_with_llm(descriptor, task_id, workspace)", "note"],
      ["委托", "workspace.resolve_inputs_for_agent(agent_id, task_id, input_needs_description, llm_client, model=input_package_model)", "note"],
      ["输入源", "descriptor.input_needs_description + artifact_registry caption index（无其他通道）", "note"],
      ["输出", "{ resolved_artifacts, selected_artifact_paths, rationale }", "returns"],
    ], "原始用户文本/媒体必须先经 POST /api/workspace/upload + IntakeXxxAgent 落成 artifact，才能被 caption 召回") +
    stepCard("③ 拼平面 inputs dict", [
      ["return", "{ task_id, resolved_artifacts }", "returns"],
    ], "inputs dict 一共 2 个 key，平面无嵌套；resolved_artifacts 是 sub-agent 唯一看得到的输入通道");

  const phase2Html =
    stepCard("_execute_pipeline_descriptor", [
      ["①", "inputs.task_id + inputs.resolved_artifacts → 直接传给 descriptor.build_input(task_id, resolved_artifacts: dict)", "note"],
      ["②", "descriptor.build_equipped_agent(pipeline_llm_client) → agent", "note"],
      ["③", "descriptor.build_input(task_id, resolved_artifacts) → typed_input", "note"],
      ["④", "若 agent.materializer 非空：mkdtemp + 构造 MaterializeContext(task_id, typed_input, persist_binary)", "note"],
      ["⑤", "await agent.run(typed_input, materialize_ctx=...) → ExecutionResult", "note"],
    ], "Assistant 不关心 sub-agent 内部；agent.run 签名只有 typed_input + materialize_ctx，没有 bundle/ctx");

  const phase3Html =
    stepCard("process_results(execution, workspace, overwrite_existing_assets)", [
      ["①", "log_execution_result(execution) → execution event 日志（含 retry_attempts / eval_summary）", "note"],
      ["②", "_deterministic_output_persist_plan(execution, descriptor) → plan（task_id 前缀已 bake 进每个 filename，不再有 LLM 重写步骤）", "note"],
      ["③", "persist_execution_from_plan(plan, overwrite) → (paths, asset_index)；落盘后回调 _register_artifacts_callback 把 ArtifactRef 追加到 global_memory.md", "note"],
      ["④", "get_memory_brief(task_id) → memory_brief：用第 ③ 步刚回调登记进 global_memory 的 ArtifactRef 拼最终响应", "note"],
      ["⑤", "返回 { task_id, execution_id, status, error, error_reasoning, workspace_id, global_memory_brief }", "returns"],
    ], "global_memory 是唯一记录层（既是语义记录又是 artifact ledger），在第 ③ 步内部回调 _register_artifacts_callback → global_memory.register 时一次性写入；不再有独立的 _sync_global_memory_after_execution / add_memory_entry / artifact_caption 路径");

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
          <div>
            <h3>Execute Agent</h3>
            <p style="margin:4px 0 0;font-size:0.78em;color:#94a3b8;font-weight:400;line-height:1.35">resolved_artifacts dict → build_input → run</p>
          </div>
        </div>
        <div class="phase-body">${phase2Html}</div>
      </div>
      ${phaseArrow()}
      <div class="phase-block phase-3">
        <div class="phase-header">
          <div class="phase-num">3</div>
          <div>
            <h3>Persist Results</h3>
            <p style="margin:4px 0 0;font-size:0.78em;color:#94a3b8;font-weight:400;line-height:1.35">LLM #2 路径 · 落盘 · agent caption → memory</p>
          </div>
        </div>
        <div class="phase-body">${phase3Html}</div>
      </div>
    </div>`
  );

  /* ── Sub-agent section ── */
  const subagentIn = {
    "resolved_artifacts (dict)": {
      shape: "dict[label_name, ResolvedArtifactEntry | list[ResolvedArtifactEntry]]  —— key 是 consumer 在 input_needs_description 的 [label] 头里声明的名字；(single) → 单个 entry，(collection) → list",
      "entry shape": "ResolvedArtifactEntry { caption, scope, path, mime, payload? }  —— pydantic class in agents/common_schema.py; payload 仅 JSON artifact 才有，已 load 好",
      note: "唯一输入通道；没有 hints / source_text / 用户原始媒体直传槽。原始输入必须先经 IntakeAgent 落成 artifact，再由 InputResolver LLM 通过 caption index 召回。descriptor 在 build_input 顶部调 ResolvedArtifactEntry.coerce(value) 把原始值统一转成 typed entry",
    },
    "descriptor.build_input": {
      signature: "(task_id, resolved_artifacts: dict) → TypedInput (Pydantic BaseModel)",
      note: "descriptor 从 resolved_artifacts 按自己声明的 label 取出条目，组成强类型输入。Sub-agent 看不到 workspace / artifact_registry / 任何包装类",
    },
  };

  const subagentOut = {
    "ExecutionResult fields (agent.run 进程内)": {
      output: "BaseModel | None  — Pydantic 主输出",
      asset_dict: "dict[str, Any] | None  — materializer 归一化",
      eval_result: "dict  — { overall_pass, ... }",
      passed: "bool",
      attempts: "int",
      media_assets: "list[MediaAsset]  — 媒体类 agent 专用",
    },
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
    "get_global_memory_brief(task_id?, agent_id?, limit?)": {
      returns: "{ global_memory: [{ task_id, agent_id, execution_id, created_at, artifacts:[{caption,scope,path,mime}] }] }",
      note: "global_memory 是唯一的语义记录层，同时也是 artifact ledger（不再分 memory / artifact_registry 两层）",
    },
    "list_workspace_artifacts()": {
      returns: "List[{ path, filename, mime, caption, scope, agent_id, task_id, execution_id, created_at }]",
      note: "扁平化 global_memory 视图；HTTP listing + 测试自省用",
    },
    "resolve_inputs_for_agent(*, agent_id, task_id, input_needs_description, llm_client, model)": {
      returns: "{ resolved_artifacts:{<label>:entry|[entry,...]}, selected_artifact_paths, rationale }",
      note: "Phase 1 LLM #1 入口；委托 InputResolver(global_memory, file_manager, llm) 走 caption index 召回",
    },
    "get_workspace_root_file_tree_text()": {
      returns: "str  — workspace 根下完整树（含 artifacts/）",
      note: "Phase 3 LLM #2 编排相对路径时作为 ground truth",
    },
    "hydrate_indexed_assets(assets)": {
      note: "把含 _asset_index.json_uri 的占位条目展开成完整 payload",
    },
    "collect_materialized_files(media_assets)": {
      note: "把 sub-agent 已物化的 MediaAsset 列表收成 _media_files dict 喂给持久化计划",
    },
    "get_logs(*, operation_type?, resource_type?, agent_id?, task_id?, limit?, level?, event?, execution_id?)": {
      returns: "List[LogEntry]",
    },
  };

  const wsWrite = {
    "store_file_at_relative_path(relative_path, file_content, filename='')": {
      returns: "StoredFile (path/filename/size)",
      note: "纯写字节，不登记 artifact、不写 artifact 事件日志；登记由上层 ArtifactWriter 完成",
    },
    "persist_raw_upload(*, file_content, mime, original_filename='')": {
      returns: "{ path, filename, mime, caption, scope='raw_pending' }",
      note: "用户原始上传入口：写到 inputs/<ts>_<filename> + 直接 global_memory.register 一条 raw_pending artifact，等待对应 IntakeAgent 通过 [raw_*_upload] label 接手",
    },
    "persist_execution_from_plan(execution, assignments, *, overwrite_existing=False)": {
      returns: "(persisted_paths, asset_index)",
      note: "Phase 3 落盘主入口；内部回调 _register_artifacts_callback → global_memory.register(execution_id, agent_id, task_id, artifacts=[ArtifactRef])",
    },
    "log_execution_started(execution) / log_execution_result(execution)": {
      note: "execution event 日志；result 自动抽 retry_attempts + eval_summary",
    },
  };

  workspaceEl.outerHTML = sectionCard(
    "card-teal", "💾",
    "Workspace 边界",
    "Runtime 工作区读写",
    ioBlock(
      "Workspace → Assistant",
      "READ",
      "badge-read",
      "数据从 Workspace 回到 Assistant；调用方仍是 Assistant（get / list / hydrate）",
      wsRead
    ) +
    `<div class="io-divider"></div>` +
    ioBlock(
      "Assistant → Workspace",
      "WRITE",
      "badge-write",
      "数据写入 Workspace；由 Assistant 调用 persist / log / add_memory 等",
      wsWrite
    )
  );

  /* ── Tests — per-component cards ── */
  function testTable(rows) {
    return `<table class="suite-table">${
      rows.map(([label, desc]) => `
        <tr>
          <td class="suite-label">${escapeHtml(label)}</td>
          <td class="suite-desc">${desc}</td>
        </tr>`).join("")
    }</table>`;
  }

  /* Director */
  testDirectorNostackEl.outerHTML = sectionCard(
    "card-green", "🧪", "Director — 消息驱动 Pipeline 编排", "pytest tests/director_nostack/ -v  # live: FW_ENABLE_NOSTACK_LIVE_E2E=1",
    testTable([
      ["消息轮询与去重消费",
        "<strong>目的：</strong>验证消息消费幂等性；<strong>结果：</strong>无消息时不触发执行；消息标记已读后不重复消费"],
      ["Pipeline 循环路由与终止",
        "<strong>目的：</strong>验证 while-True 循环路由与终止；<strong>结果：</strong>单/双 agent run→done 正确退出；after_frontend_user_message 首步为 true；merged goal 通过 routing LLM 的 original_user_goal 入参影响 agent 选择"],
      ["会话目标合并",
        "<strong>目的：</strong>验证目标合并的边界条件；<strong>结果：</strong>无 global_memory + 无 prior_lines 时跳过 LLM；prior 消息按 timestamp 排序并排除当前 msg_id；dict 内容完整序列化为 JSON"],
      ["全链路 HTTP 集成",
        "<strong>目的：</strong>验证从用户 POST 到 Director 回复的完整路径；<strong>结果：</strong>用户 POST → _cycle → execute → chat 回复；嵌入式直接调用 run_nostack_pipeline 也通过"],
      ["真实 LLM 路由验证",
        "<strong>目的：</strong>用真实 LlmSubAgentPlanner 驱动路由，验证 LLM 能正确选出 agent 并在下一轮返回 done；<strong>结果：</strong>至少一条执行记录、agent_id 正确、Director 发出 Pipeline complete 消息"],
      ["完整生成",
        `<strong>目的：</strong>Director 驱动完整 pipeline 端到端生成视频，验证从用户消息到产出文件的全链路；<strong>结果：</strong>video 产出可播放。
<div style="margin-top:14px">
  <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:6px">User Prompt</div>
  <div style="font-size:1.05em;font-style:italic;color:#ddd;padding:10px 14px;background:rgba(255,255,255,0.05);border-left:3px solid #888;border-radius:4px">"Generate about a 10-second cinematic clip: rain on cobblestones, a cyclist rolls under one warm streetlight; no dialogue, slow mood."</div>
</div>
<div style="margin-top:14px">
  <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:6px">StoryAgent → Storyline</div>
  <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-left:3px solid #5a8a6a;border-radius:4px;font-size:0.88em;line-height:1.6;color:#ccc">
    <div style="color:#e8c97a;font-weight:600;margin-bottom:6px">An elderly librarian's quiet closing routine is shattered by a cryptic bookmark in a returned book, hinting at a reunion with someone she thought was lost forever.</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Drama</span>
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Slice of Life</span>
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Poignant · Quiet · Emotional · Hopeful</span>
    </div>
    <div><strong style="color:#aaa">Inciting —</strong> Elara, closing the library at blue hour, discovers an unexpected bookmark with familiar handwriting tucked into a returned book.</div>
    <div style="margin-top:4px"><strong style="color:#aaa">Turn —</strong> Her calm focus shifts to profound surprise and poignant reflection — a long-lost connection suddenly resurfaces.</div>
  </div>
</div>
<div style="margin-top:12px"><video controls style="max-width:100%;border-radius:6px" src="./demo_director.mp4"></video></div>`],
    ])
  );

  testDtsEl.outerHTML = sectionCard(
    "card-green", "🧪", "Dynamic Task Stack 测试", "pytest tests/dynamic_task_stack/ -v",
    testTable([
      ["Flask App 初始化",
        "<strong>目的：</strong>验证 create_app 正确注册核心路由；<strong>结果：</strong>支持运行时 config 覆盖，路由可达"],
    ])
  );

  /* Assistant */
  testAssistantHttpEl.outerHTML = sectionCard(
    "card-green", "🧪", "Assistant HTTP API 测试", "pytest tests/assistant/test_assistant_http_e2e.py tests/assistant/test_full_pipeline_live_e2e.py -v",
    testTable([
      ["端点全链路",
        "<strong>目的：</strong>验证 REST 端点端到端联通；<strong>结果：</strong>发现 → 创建 task → execute → 查 executions → workspace files/logs/memory/brief 全部返回正确"],
      ["跨 agent 数据流",
        "<strong>目的：</strong>验证前序 agent 产出流入后续 agent；<strong>结果：</strong>ProducerAgent 产出被 ConsumerAgent 在同一 task 读取；global_memory 出现在下游 inputs"],
      ["路由 + 兜底校验",
        "<strong>目的：</strong>验证缺失 agent_id / task_id 时返回 400；非法 agent_id 返回 404"],
      ["完整生成",
        `<strong>目的：</strong>真实 LLM + fal API 驱动完整 pipeline，生成约 1 分钟视频；<strong>结果：</strong>audio_results 包含 final_delivery_asset，产出可播放。
<div style="margin-top:14px">
  <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:6px">User Prompt</div>
  <div style="font-size:1.05em;font-style:italic;color:#ddd;padding:10px 14px;background:rgba(255,255,255,0.05);border-left:3px solid #888;border-radius:4px">"Create a simple cinematic short video around ten seconds long: a watchmaker fixes one broken watch before midnight."</div>
</div>
<div style="margin-top:14px">
  <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:6px">StoryAgent → Storyline</div>
  <div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-left:3px solid #5a8a6a;border-radius:4px;font-size:0.88em;line-height:1.6;color:#ccc">
    <div style="color:#e8c97a;font-weight:600;margin-bottom:6px">A retired watchmaker races against the final ten seconds before midnight to repair his late wife's cherished pocket watch, seeking a moment of peace and connection as the new year begins.</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Drama</span>
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Slice of Life</span>
      <span style="background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:12px;font-size:0.82em">Poignant · Hopeful · Tense · Nostalgic</span>
    </div>
    <div><strong style="color:#aaa">Setup —</strong> Elias works on his late wife's pocket watch with seconds to midnight, grief and urgency intertwined.</div>
    <div style="margin-top:4px"><strong style="color:#aaa">Crisis —</strong> A small mistake causes his hands to falter; he glances at the clock and steadies his resolve.</div>
    <div style="margin-top:4px"><strong style="color:#aaa">Climax —</strong> With renewed resolve, he performs the final delicate repair just as midnight arrives — the watch ticks.</div>
    <div style="margin-top:4px"><strong style="color:#aaa">Resolution —</strong> Elias smiles softly amidst fireworks — a quiet moment of peace and connection with her memory.</div>
  </div>
</div>
<div style="margin-top:12px"><video controls style="max-width:100%;border-radius:6px" src="./demo.mp4"></video></div>
<div style="margin-top:16px">
  <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:10px">已知问题分析</div>
  <div style="display:flex;flex-direction:column;gap:10px">
    <div style="padding:10px 14px;background:rgba(255,100,80,0.06);border-left:3px solid #c0503a;border-radius:4px;font-size:0.87em;line-height:1.7;color:#ccc">
      <div style="font-weight:600;color:#e88;margin-bottom:4px">① KeyframeAgent — Anchor 一致性不足</div>
      <div>已实现分层 anchor 机制，但人物外观、场景风格仍存在跨镜头漂移。</div>
      <div style="margin-top:6px;background:rgba(0,0,0,0.25);border-radius:4px;padding:8px 12px;font-family:monospace;font-size:0.85em;color:#9ecfaa;line-height:1.8">
        Layer 1 — Global anchors&nbsp;&nbsp;: text → generate_image()<br>
        Layer 2 — Scene anchors&nbsp;&nbsp;&nbsp;: global anchor img + prompt → edit_image()<br>
        Layer 3 — Shot keyframes&nbsp;&nbsp;: scene anchor img(s) + prompt → edit_image()
      </div>
      <div style="margin-top:8px;color:#aaa"><strong style="color:#bbb">待优化：</strong>目前每个角色/场景仅有单一 anchor 图，可扩展为多视角 anchor（正面 / 侧面 / 特写），进一步提升人物一致性。</div>
    </div>
    <div style="padding:10px 14px;background:rgba(255,180,40,0.05);border-left:3px solid #a07828;border-radius:4px;font-size:0.87em;line-height:1.7;color:#ccc">
      <div style="font-weight:600;color:#d4a84b;margin-bottom:4px">② Video Generation — 模型能力局限</div>
      <div>当前视频生成模型在运动合理性、时序连贯性、细节保真度上存在上限，属于底层模型能力问题，非 pipeline 逻辑问题。短期可通过换用更强的 video gen API 缓解，长期依赖模型本身的迭代进步。</div>
    </div>
  </div>
</div>`],
    ])
  );

  testAssistantServiceEl.outerHTML = sectionCard(
    "card-green", "🧪", "Assistant Service 测试", "pytest tests/assistant/test_assistant_service_unit.py -v",
    testTable([
      ["执行输入打包",
        "<strong>目的：</strong>验证 build_execution_inputs 正确打包上下文；<strong>结果：</strong>InputResolver 选出的 artifact 落进 inputs.resolved_artifacts；descriptor.build_input 收到的就是这个 dict（无包装类）"],
      ["文件持久化",
        "<strong>目的：</strong>验证 agent 产出写入 workspace 的完整路径；<strong>结果：</strong>overwrite 模式替换旧文件；媒体 URI 重写为 workspace 路径；materializer 临时目录执行后清理；路径遵循 artifacts/media/{agent}/ 规范"],
    ])
  );

  testSerializersEl.outerHTML = sectionCard(
    "card-green", "🧪", "Assistant Serializers 测试", "pytest tests/assistant/test_assistant_serializers_unit.py -v",
    testTable([
      ["序列化完整性",
        "<strong>目的：</strong>验证 Assistant/Execution 模型序列化为 dict 的字段完整性；<strong>结果：</strong>文件/日志 helper 字段不丢失；response 中二进制字段重写为 workspace 路径"],
    ])
  );

  /* Sub-agents */
  testAgentsEl.outerHTML = sectionCard(
    "card-green", "🧪", "Sub-agents 测试", "pytest tests/agents/ -v",
    testTable([
      ["Agent 描述符合约",
        "<strong>目的：</strong>验证 registry 注册/列举/reload 正确；<strong>结果：</strong>identity 字段完整、build_input 使用 v2 命名与字面 asset key、无旧版 input fallback"],
      ["媒体产出物化",
        "<strong>目的：</strong>验证各媒体 materializer 产出路径与格式；<strong>结果：</strong>video/keyframe/audio 产出正确、fal 多图 payload 支持与拒绝、scene 拼接时长、audio mux 保留视频时长"],
    ])
  );

  /* Workspace */
  testWorkspaceEl.outerHTML = sectionCard(
    "card-green", "🧪", "Workspace Managers 测试", "pytest tests/assistant/test_assistant_workspace_managers_unit.py -v",
    testTable([
      ["文件管理器",
        "<strong>目的：</strong>验证文件列举与二进制读取；<strong>结果：</strong>从 URI 读取内容正确、收集已物化文件完整"],
      ["记忆管理器",
        "<strong>目的：</strong>验证 global_memory 读写与过滤；<strong>结果：</strong>brief 返回精简行（无 content/artifact_locations）；按 task_id/agent_id 过滤一致；写入必须提供 task_id"],
      ["日志管理器",
        "<strong>目的：</strong>验证日志多维过滤；<strong>结果：</strong>按 operation_type / resource_type / agent_id 过滤结果正确"],
      ["资产管理器",
        "<strong>目的：</strong>验证 asset index 读写；<strong>结果：</strong>hydrate 展开正确、persist index 写入文件可读回"],
    ])
  );


}

render();
