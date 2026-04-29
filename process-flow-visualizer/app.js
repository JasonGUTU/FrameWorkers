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
  const taskStackEl           = $g("taskStackViz");

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
        <div>DirectorAgent 长驻轮询 chat（间隔 <code>POLLING_INTERVAL</code>，默认 2s），抓首条 unread user message。新消息到达后：
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li>投影当前 Plan Stack 近 <code>DIRECTOR_MEMORY_WINDOW</code>（默认 20）个 step 为 <code>stack_memory</code>，每行
            <code>{step_id, agent_id, status, intent, results_summary}</code></li>
          <li>拉 <code>MERGE_PRIOR_USER_LINES_MAX</code>（默认 10）条更早 user 文本为 <code>prior_lines</code></li>
          <li>一次 <code>merge_session_goal</code> LLM 产出 <code>merged_goal</code>；若 stack_memory 与 prior_lines 都为空，直接返回原始 latest_line（不调 LLM）</li>
        </ul></div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">② Upfront 规划 → 写入 Plan Stack</div>
        <div>一次 <code>plan_pipeline_upfront</code> LLM 产出完整计划数组 <code>[{agent_id, intent}, ...]</code>，由 <code>_persist_plan</code> 分两次
        <code>POST /api/plan-stack/modify</code> 落盘：
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li>第一批 batch ops = <code>[create_steps, create_layers]</code>：建全部 PlanStep + 一个新 layer（<code>layer_index = max(existing) + 1</code>）</li>
          <li>第二批 batch ops = <code>[add_steps_to_layers]</code>：按顺序把刚拿到的 step_id 挂进新 layer</li>
          <li><strong>execution pointer</strong>：仅当 <code>get_execution_pointer()</code> 为空（首次规划）时 <code>set_execution_pointer(new_layer, 0)</code>；否则保持当前 pointer 不动，等它走完旧 layer 自然滚进新 layer</li>
          <li>每个 PlanStep.description = <code>{agent_id, intent, plan_rationale}</code>，stack 自描述；plan-step 不做 per-step Markov 决策，整条 pipeline 一次 LLM 出</li>
          <li><code>MAX_PIPELINE_STEPS</code>（默认 20）卡住计划长度；planner 返 <code>[]</code> 时最多 3 次重试再放弃本轮</li>
        </ul></div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">③ 顺光标执行 → Assistant</div>
        <div>循环（per-cycle 全局预算 <code>MAX_EXECUTIONS_PER_CYCLE</code>，默认 30）：
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li><code>GET /api/plan-stack/next</code> → 拿 <code>{step_id, step, layer_index, step_index, layer}</code>；空则发 "Pipeline complete" 后回到轮询</li>
          <li><code>PUT /api/steps/&lt;sid&gt;/status</code> = <code>IN_PROGRESS</code></li>
          <li><code>POST /api/assistant/execute {agent_id, step_id}</code> → 拿单条 <code>AgentExecution</code>（含 status / error / inputs / results / 时间戳）</li>
          <li><code>PUT /api/steps/&lt;sid&gt;/status</code> = <code>COMPLETED</code> 或 <code>FAILED</code></li>
          <li>发一条 director chat 消息 <code>[DirectorAgent] &lt;agent_id&gt; → &lt;status&gt;</code>（带 error），给前端实时看进度</li>
          <li><code>POST /api/execution-pointer/advance</code> 推进光标</li>
        </ul></div>
      </div>

      <div>
        <div style="font-weight:600;color:#fbbf24;margin-bottom:6px">④ FAILED 走 replan（不是静态 DAG，也没有 retry 通道）</div>
        <div>step FAILED → <code>planner.replan_on_failure(...)</code> 返回 <code>ReplanDecision {new_tail, rationale}</code>，director 按 <code>new_tail</code> 是否为空分两条路径：
        <ul style="margin:6px 0 0 18px;padding:0;color:#aaa">
          <li><strong>replan</strong>（<code>new_tail</code> 非空）：先 <code>remove_steps_from_layers</code> 摘掉 stack 上所有 PENDING step，然后走 <code>_persist_plan</code> 追加新 layer 承载 <code>new_tail</code>；pointer 自然滚进新 layer。<code>replans_used += 1</code></li>
          <li><strong>skip</strong>（<code>new_tail</code> 为空 / replanner LLM 出错）：不动 stack，executor 直接 <code>advance_execution_pointer</code> 越过这个失败 step</li>
        </ul>
        <code>MAX_REPLAN_ROUNDS</code>（默认 2）限制单 cycle 内 replan 次数；耗尽后任何 FAILED 一律 skip。下一条 user message 进来 → 回到 ①，新计划再追加一层 layer。</div>
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

}

render();
