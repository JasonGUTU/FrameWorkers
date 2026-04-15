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
  step_id: "task_demo_001",
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

  const { agent_id: agentId, step_id: taskId } = EXECUTE_EXAMPLE;

  const packagedAssets = {};
  const mapped = {
    step_id: taskId,
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

        <!-- ══ CURRENT path: Chat bypasses Plan Stack → polls Director directly ══ -->
        <!-- arc over Plan Stack node -->
        <path d="M 94 38 C 148 8 222 8 264 38" fill="none"
              stroke="#a37f1a" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="5,3"
              marker-end="url(#arrYellowFaint)"/>
        <text x="179" y="6" text-anchor="middle" font-size="8.5" fill="#64748b">current · poll</text>

        <!-- Director → Chat reply (arc below current path) -->
        <path d="M 264 66 Q 160 118 94 55" fill="none"
              stroke="#a37f1a" stroke-width="1.2" stroke-opacity="0.4" stroke-dasharray="4,3"
              marker-end="url(#arrYellowFaint)"/>
        <text x="155" y="116" text-anchor="middle" font-size="8.5" fill="#64748b">reply</text>

        <!-- ══ FUTURE path: Chat → Plan Stack → Director ══ -->
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

        <!-- Plan Stack (TODO — dashed border, between Chat and Director) -->
        <rect x="118" y="22" width="120" height="48" rx="10"
              fill="rgba(249,115,22,0.07)" stroke="rgba(249,115,22,0.4)" stroke-width="1.5"
              stroke-dasharray="5,3"/>
        <text x="178" y="42" text-anchor="middle" font-size="13">📋</text>
        <text x="178" y="58" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fb923c">Plan Stack</text>

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
  directorEl.outerHTML = sectionCard(
    "card-orange", "🎬",
    "DirectorAgent 编排概览",
    "director_agent/director.py + router.py",
    `<div style="display:flex;flex-direction:column;gap:20px;font-size:0.88em;color:#ccc;line-height:1.7">

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">① 接收前端需求 + 合并 session goal</div>
        <div>Director 长驻轮询 chat。新消息到达 → 投影<strong>当前 Plan Stack 的近 N 个 step</strong>（<code>{step_id, agent_id, status, intent, results_summary}</code>）作为 stack_memory → 拉 <code>MERGE_PRIOR_USER_LINES_MAX</code> 条先前用户文本 → 一次 <code>merge_session_goal</code> LLM 产出整个 session 的 <code>merged_goal</code>。</div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">② Upfront 规划 → 一次性写入 Plan Stack</div>
        <div>一次 <code>plan_pipeline_upfront</code> LLM 产出完整计划数组 <code>[{agent_id, intent}, ...]</code>，然后一次
        <code>POST /api/plan-stack/modify</code> 批量（create_steps + create_layers + add_steps_to_layers 的 batch op）把全部 PlanStep 落盘，执行光标指到新 layer 的第 0 步。
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li>不做 Markov 逐步 — 整条 pipeline 一次 LLM 决策</li>
          <li>每个 PlanStep 的 <code>description</code> 存 <code>{agent_id, intent, plan_rationale}</code>，stack 本身就是 self-describing</li>
          <li><code>MAX_PIPELINE_STEPS</code> 卡住计划长度</li>
        </ul></div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">③ 顺光标执行 → Assistant</div>
        <div>循环：<code>GET /api/plan-stack/next</code> 拿下一个 PlanStep → <code>PUT /api/steps/&lt;sid&gt;/status IN_PROGRESS</code> → <code>POST /api/assistant/execute {agent_id, step_id}</code> → 写回终态（COMPLETED/FAILED）→ <code>POST /api/execution-pointer/advance</code>。
        每个 execute 返回单条 <code>AgentExecution</code> 行，director 投影成 slim row 发一条 chat 消息通知前端。<code>MAX_EXECUTIONS_PER_CYCLE</code> 做全局兜底。</div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">④ 失败走 replan（不是静态 DAG）</div>
        <div>某 step FAILED → <code>replan_on_failure</code> LLM 输出 <code>{action: retry | skip | replan}</code>：
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li><strong>retry</strong> — 重置 step 为 PENDING + pointer 回滚，同 agent 再跑一次</li>
          <li><strong>replan</strong> — <code>remove_steps_from_layers</code> 删掉 PENDING tail + 追加新 layer 承载新 tail，pointer 自然走到新 layer</li>
          <li><strong>skip</strong> — 不动 stack，pointer 前进越过失败 step</li>
        </ul>
        <code>MAX_REPLAN_ROUNDS</code> 限制本轮 replan 次数。下一条用户消息进来 → 回到 ①，在现有 Plan Stack 上追加新 layer 继续规划。</div>
      </div>

    </div>`
  );

  /* ── HTTP section ── */
  const httpRequest = { agent_id: agentId, step_id: taskId };
  const httpResponse = {
    id: "exec_demo_placeholder",
    agent_id: agentId,
    step_id: taskId,
    status: "COMPLETED",
    error: null,
    inputs: { step_id: taskId, resolved_artifacts: {} },
    results: { summary: "…" },
    started_at: "2026-04-07T12:00:00Z",
    completed_at: "2026-04-07T12:00:05Z",
    created_at: "2026-04-07T12:00:00Z",
  };
  /* ── Plan Stack (TODO) ── */
  taskStackEl.outerHTML = sectionCard(
    "card-orange", "📋",
    "Dynamic Plan Stack — Director 集成",
    "dynamic-task-stack/  ·  Roadmap 01",
    `<div style="display:inline-block;background:rgba(255,160,40,0.15);border:1px solid rgba(255,160,40,0.4);color:#f0a040;font-size:0.78em;font-weight:600;letter-spacing:.08em;padding:3px 10px;border-radius:4px;margin-bottom:18px">TODO</div>
    <div style="display:flex;flex-direction:column;gap:12px;font-size:0.88em;color:#ccc;line-height:1.7">
      <div>
        <div style="font-weight:600;color:#e0e0e0;margin-bottom:4px">现状</div>
        <div>DirectorAgent 使用固定 <code>session-implicit (Plan Stack driven)</code> step_id，轮询 <code>/api/messages/unread</code> 驱动 pipeline，任务状态完全依赖内存与 chat 消息，无法中断恢复或并发调度。</div>
      </div>
      <div>
        <div style="font-weight:600;color:#e0e0e0;margin-bottom:4px">目标：将 Director 迁移至 Plan Stack</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          <div>① <strong>任务生命周期管理</strong> — 每个 pipeline 运行对应一个 Plan Stack 任务，支持 PENDING / RUNNING / COMPLETED / FAILED 状态追踪</div>
          <div>② <strong>中断恢复</strong> — pipeline 中断后可从上一个已完成 step 续跑，无需重头执行</div>
          <div>③ <strong>并发调度</strong> — 多个 user session 可并行运行独立 pipeline，不再共享同一 step_id</div>
          <div>④ <strong>上下文统一</strong> — Director 与 Assistant 共用 Plan Stack 的 workspace / memory 接口，消除重复状态维护</div>
        </div>
      </div>
      <div style="padding:10px 14px;background:rgba(255,255,255,0.03);border-left:3px solid rgba(255,160,40,0.4);border-radius:4px;color:#aaa">
        依赖 Dynamic Plan Stack 的 <code>create_app</code> 路由与 <code>AssistantStateStore</code> 已就绪，主要工作为 Director 调度层的重构。
      </div>
    </div>`
  );

  httpEl.outerHTML = sectionCard(
    "card-blue", "🌐",
    `HTTP &nbsp;<code>POST /api/assistant/execute</code>`,
    "Director ↔ Assistant",
    `<div style="margin-bottom:14px;padding:10px 14px;background:rgba(126,179,255,0.06);border-left:3px solid rgba(126,179,255,0.4);border-radius:4px;font-size:0.84em;color:#bbb;line-height:1.6">
      <strong style="color:#7eb3ff">HTTP body 收敛：</strong>
      只剩 <code>{agent_id, step_id}</code>。原始用户文本 / 媒体必须先经 <code>POST /api/workspace/upload</code> + 调对应 <code>IntakeXxxAgent</code> 落成 artifact，再由下游 agent 通过 <code>artifact_registry caption index</code> 召回。
    </div>
    <div class="http-pair">
      ${ioBlock("Director → Assistant", "REQUEST", "badge-request", "body 只携 agent_id + step_id；任何 user 输入需提前落 workspace artifact", httpRequest)}
      <div class="arrow-col"><div class="arrow-shaft"></div><div class="arrow-tip"></div></div>
      ${ioBlock("Assistant → Director", "RESPONSE", "badge-response",
        "单条 AgentExecution：{id, agent_id, step_id, status, error, inputs, results, started_at, completed_at, created_at} — 跨 turn 历史走 GET /executions/task/<tid>", httpResponse)}
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

  phasesEl.outerHTML = sectionCard(
    "card-orange", "⚡",
    "Assistant 执行概览",
    "execute_agent_for_step() — service.py",
    `<div style="display:flex;flex-direction:column;gap:20px;font-size:0.88em;color:#ccc;line-height:1.7">

      <div>
        <div style="font-weight:600;color:#7eb3ff;margin-bottom:6px">① Build Inputs — InputResolver LLM 选 artifact</div>
        <div>收到 Director 的 <code>{agent_id, step_id}</code> 后，Assistant 根据 descriptor 声明的 <code>input_needs_description</code>（每个 agent 自定义的输入需求描述），用 <strong>InputResolver LLM</strong> 在 <code>global_memory</code> caption index 上做语义召回，匹配出该 agent 需要的上游产物。输出扁平 dict <code>{step_id, resolved_artifacts}</code>，其中 <code>resolved_artifacts</code> 是 sub-agent 唯一看到的输入通道。</div>
        <div style="margin-top:6px;padding:8px 12px;background:rgba(255,255,255,0.03);border-left:3px solid rgba(126,179,255,0.3);border-radius:4px;color:#888;font-size:0.92em">
          原始用户输入（文本/图片/视频/音频）必须先经 <code>POST /api/workspace/upload</code> + IntakeAgent 落成 caption-rich artifact，才能被召回。
        </div>
      </div>

      <div>
        <div style="font-weight:600;color:#7eb3ff;margin-bottom:6px">② Execute Agent — descriptor 驱动 pipeline</div>
        <div>
          <code>descriptor.build_input(step_id, resolved_artifacts)</code> 生成强类型输入 → <code>descriptor.build_equipped_agent(llm_client)</code> 装配 agent → <code>agent.run(typed_input, materialize_ctx)</code> 执行。
        </div>
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li><strong>Materializer</strong> — 媒体类 agent 自带 materializer，执行期间通过 <code>persist_binary</code> 回调写临时文件，失败通过 <code>report_failure</code> 记录日志但不中断</li>
          <li><strong>Quality Gate</strong> — <code>agent.run</code> 返回 <code>passed</code> 标志（L1/L2/L3 evaluator 全部重试后仍失败 → passed=False）；Assistant 据此设置 execution status 为 COMPLETED 或 FAILED，失败时附带 eval_summary</li>
        </ul>
        <div style="margin-top:6px;color:#888;font-size:0.92em">Assistant 不关心 sub-agent 内部逻辑；<code>agent.run</code> 签名只有 <code>typed_input</code> + <code>materialize_ctx</code>。</div>
      </div>

      <div>
        <div style="font-weight:600;color:#7eb3ff;margin-bottom:6px">③ Persist Results — 确定性落盘 + caption 注册</div>
        <div>
          <ul style="margin:0 0 0 18px;padding:0;color:#aaa">
            <li><strong>日志</strong> — <code>log_execution_result</code> 写 execution event（含 retry_attempts / eval_summary）</li>
            <li><strong>路径规划</strong> — <code>_deterministic_output_persist_plan</code> 纯确定性（无 LLM），按 <code>artifacts/media/&lt;agent&gt;/&lt;type&gt;/</code> 和 <code>artifacts/&lt;agent&gt;/</code> 规则生成相对路径，step_id 前缀防冲突</li>
            <li><strong>Caption</strong> — <code>descriptor.build_captions</code> 由 producer agent 自定义产物描述；支持 <code>_update:</code> key 更新已有 caption</li>
            <li><strong>落盘</strong> — <code>persist_execution_from_plan</code> 写文件，内部回调 <code>_register_artifacts_callback</code> 把 ArtifactRef 一次性追加到 <code>global_memory.md</code></li>
          </ul>
        </div>
        <div style="margin-top:8px;color:#aaa"><strong>返回给 Director</strong>：单条 <code>AgentExecution</code>（<code>{id, agent_id, step_id, status, error, inputs, results, started_at, completed_at, created_at}</code>）。跨 turn 历史通过 <code>GET /api/assistant/executions/step/&lt;tid&gt;</code> 独立拉取。</div>
      </div>

      <div style="padding:10px 14px;background:rgba(255,255,255,0.03);border-left:3px solid rgba(126,179,255,0.3);border-radius:4px;color:#888;font-size:0.92em">
        接口细节见 <a href="./assistant.html" style="color:#7eb3ff">Assistant 子页</a>。
      </div>
    </div>`
  );

  /* ── Sub-agent section ── */
  const subagentIn = {
    "resolved_artifacts (dict)": {
      shape: "dict[label_name, ResolvedArtifactEntry | list[ResolvedArtifactEntry]]  —— key 是 consumer 在 input_needs_description 的 [label] 头里声明的名字；(single) → 单个 entry，(collection) → list",
      "entry shape": "ResolvedArtifactEntry { caption, scope, path, mime, payload? }  —— pydantic class in agents/common_schema.py; payload 仅 JSON artifact 才有，已 load 好",
      note: "唯一输入通道。原始输入必须先经 IntakeAgent 落成 artifact，再由 InputResolver LLM 通过 caption index 按 input_needs_description 的 [label] 语义召回。descriptor 在 build_input 顶部调 ResolvedArtifactEntry.coerce(value) 统一转 typed entry",
    },
    "descriptor.build_input": {
      signature: "(step_id, resolved_artifacts: dict) → TypedInput (Pydantic BaseModel)",
      note: "descriptor 从 resolved_artifacts 按自己声明的 label 取出条目，组成强类型输入。Sub-agent 看不到 workspace / global_memory / 任何包装类。上游 payload 作为 JSON 文本透传（json.dumps → str 字段），不按 key 硬读",
    },
  };

  const subagentOut = {
    "ExecutionResult (dataclass in base_agent.py)": {
      output: "BaseModel | None  — agent 的 Pydantic 主输出（即使 passed=False 也会返回，方便调试）",
      eval_result: "dict  — { overall_pass, summary, dimensions, ... }  三层评估结果",
      passed: "bool  — 所有评估层在重试预算内是否通过",
      attempts: "int  — 生成尝试次数（1-based）",
      media_assets: "list[MediaAsset]  — materializer 产出的二进制资产（非媒体 agent 为空）",
      asset_dict: "dict | None  — output 序列化为 dict，materialized URI 已就地写入",
    },
  };

  const subagentPersist = {
    "Assistant process_results 落盘": {
      "_deterministic_output_persist_plan": "纯确定性路径规划（无 LLM）：JSON → artifacts/<Agent>/, 媒体 → artifacts/media/<Agent>/<type>/",
      "build_captions": "descriptor 提供 (agent_id, output_dict) → {sys_id: {caption, scope}} → 注册到 global_memory",
      "_quality_gate_passed": "agent 的 passed 字段 → False 时 execution status = FAILED",
      "_media_files": "media_assets 收集到 output dict 的 _media_files 数组",
    },
  };

  subagentEl.outerHTML = sectionCard(
    "card-purple", "🤖",
    "Sub-agent 边界",
    "进程内调用，非 HTTP  ·  agents/descriptor.py + agents/base_agent.py",
    ioBlock("Assistant → Sub-agent", "INPUT", "badge-input",
      "descriptor.build_equipped_agent(llm) → agent; descriptor.build_input(step_id, resolved_artifacts) → typed_input; agent.run(typed_input, materialize_ctx)", subagentIn) +
    `<div class="io-divider"></div>` +
    ioBlock("Sub-agent → Assistant", "OUTPUT", "badge-output",
      "agent.run() 返回 ExecutionResult; materializer 通过 MaterializeContext(step_id, typed_input, persist_binary, report_failure) 接入", subagentOut) +
    `<div class="io-divider"></div>` +
    ioBlock("Assistant 落盘", "PERSIST", "badge-write",
      "process_results: 路径规划 → 写磁盘 → 注册 global_memory → 返回 brief", subagentPersist)
  );

  /* ── Workspace section ── */
  workspaceEl.outerHTML = sectionCard(
    "card-teal", "💾",
    "Workspace 存储",
    "_workspaces/<workspace_id>/",
    `<div style="display:flex;flex-direction:column;gap:16px;font-size:0.88em;color:#ccc;line-height:1.7">
      <div>所有 sub-agent 共享同一个 workspace 实例。<code>global_memory.md</code> 是唯一记录层（语义记录 + artifact ledger），每条 entry = 一次执行产出的 artifact 列表。</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div><strong style="color:#5eead4">写</strong> — agent 执行后确定性落盘到 <code>artifacts/</code>，回调自动注册到 global_memory；用户上传写到 <code>inputs/</code>，scope=<code>raw_pending</code> 等 IntakeAgent 接手；执行事件写 <code>logs.jsonl</code></div>
        <div><strong style="color:#5eead4">读</strong> — InputResolver LLM 从 caption index 按 label 语义召回上游产物；Director 通过 <code>GET /api/assistant/executions/step/&lt;tid&gt;</code> 获取 slim 执行摘要（含 FAILED）</div>
      </div>
    </div>`
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

  /* Director — "消息驱动 Pipeline 编排" section removed per user request */
  if (testDirectorNostackEl && testDirectorNostackEl.parentNode) testDirectorNostackEl.remove();

  testDtsEl.outerHTML = sectionCard(
    "card-green", "🧪", "Dynamic Plan Stack 测试", "pytest tests/dynamic_plan_stack/ -v",
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
        "<strong>目的：</strong>验证 REST 端点端到端联通；<strong>结果：</strong>发现 → 创建 task → execute → 查 executions → workspace files/logs 全部返回正确"],
      ["跨 agent 数据流",
        "<strong>目的：</strong>验证前序 agent 产出流入后续 agent；<strong>结果：</strong>ProducerAgent 产出被 ConsumerAgent 在同一 task 读取；global_memory 出现在下游 inputs"],
      ["路由 + 兜底校验",
        "<strong>目的：</strong>验证缺失 agent_id / step_id 时返回 400；非法 agent_id 返回 404"],
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
        "<strong>目的：</strong>验证 global_memory 读写与过滤；<strong>结果：</strong>brief 返回精简行（无 content/artifact_locations）；按 step_id/agent_id 过滤一致；写入必须提供 step_id"],
      ["日志管理器",
        "<strong>目的：</strong>验证日志多维过滤；<strong>结果：</strong>按 operation_type / resource_type / agent_id 过滤结果正确"],
      ["资产管理器",
        "<strong>目的：</strong>验证 asset index 读写；<strong>结果：</strong>hydrate 展开正确、persist index 写入文件可读回"],
    ])
  );


}

render();
