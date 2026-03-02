# Agentic AI LinkedIn Research Log (2026-02-21)

## Scope
- Goal: craft a high-performing LinkedIn post on agentic AI with evidence from real agent products (not only SDK marketing).
- Method:
- Code-level review of modern OSS agent products.
- Live LinkedIn feed extraction via `grais-tab-webdata-reader` from attached tab.

## Modern agent products sampled (star snapshot)
- `openclaw/openclaw` - 215,288
- `google-gemini/gemini-cli` - 95,142
- `browser-use/browser-use` - 78,642
- `OpenHands/OpenHands` - 68,024
- `openinterpreter/open-interpreter` - 62,304
- `openai/codex` - 61,276
- `cline/cline` - 58,210
- `Aider-AI/aider` - 40,797
- `RooVetGit/Roo-Code` - 22,318
- `SWE-agent/SWE-agent` - 18,518

## Code-level findings (current)
- Tool-first is universal in this sample (tool schemas/registries/tool call handling present across products).
- Multi-agent/delegation exists, but usually in specific scenarios:
- `openai/codex`: sub-agent thread orchestration and forwarding.
- `RooVetGit/Roo-Code`: explicit subtask delegation via `new_task`, with strict isolation rules.
- `OpenHands/OpenHands`: explicit `AgentDelegateAction`.
- `Aider-AI/aider`: architect -> editor staged handoff pattern.
- Parallelization is selective/safety-scoped:
- `google-gemini/gemini-cli`: scheduler queue with guard against concurrent scheduling while active.
- `cline/cline`: explicit parallel tool-calling config and gating.
- `RooVetGit/Roo-Code`: explicit handling for parallel tool calls + delegation edge cases.
- `openai/codex`: internal async parallel startup tasks (session init path).
- Important nuance:
- Some frameworks expose multi-agent features, but execution defaults often remain one orchestrator + tools + state machine.

## OpenClaw-specific signals
- README advertises:
- local-first gateway control plane
- multi-agent routing
- first-class tools
- routing/session internals in code:
- `src/routing/resolve-route.ts` (agent routing resolution and session key generation).
- `src/routing/session-key.ts` (agent-prefixed session keys + subagent session key handling).
- `src/agents/agent-scope.ts` (`subagents`, per-agent config, per-agent workspace/session resolution).

## LinkedIn feed format patterns observed from attached tab
- Strong hook in first 1-2 lines is common.
- Short lines with high whitespace density.
- Bullets/lists increase scanability.
- Contrast framing performs well:
- "everyone thinks X"
- "reality is Y"
- Call-to-action patterns:
- direct question
- keyword comment CTA ("Comment X")
- follow/repost prompt
- Observed effective structures:
- Problem statement -> mechanism -> bullet breakdown -> conclusion -> CTA.
- Personal narrative -> inflection point -> mission statement -> soft CTA.

## Post direction hypothesis
- Best angle:
- "The bottleneck is not building agents; it's understanding decision architecture."
- Supporting claim:
- "Most production-grade agent products are tool-first with selective delegation, not default multi-agent swarms."
- Suggested conflict frame:
- "Architecture theater vs operational cognition."

## Next updates to append
- Refine evidence table with exact file references for each product.
- Narrow to the freshest products only if needed (exclude older perception-heavy examples).
- Draft 2-3 post variants:
- technical builder tone
- founder/operator tone
- high-controversy comment-bait tone

## Update: modern products only (refined evidence)
- Removed older-perception-heavy examples from core argument.
- Current primary set:
- `openclaw/openclaw`
- `google-gemini/gemini-cli`
- `browser-use/browser-use`
- `OpenHands/OpenHands`
- `openinterpreter/open-interpreter`
- `openai/codex`
- `cline/cline`
- `Aider-AI/aider`
- `RooVetGit/Roo-Code`
- `SWE-agent/SWE-agent`

### Product evidence snapshots
- `openclaw/openclaw`
- Positioning: multi-agent routing + first-class tools in README highlights.
- `README.md` lines ~141-146.
- Code: per-agent config includes `subagents`, `tools`, `groupChat`.
- `src/agents/agent-scope.ts` lines ~27-30.
- Code: session key utilities explicitly include subagent helpers.
- `src/routing/session-key.ts` lines ~5-9.

- `openai/codex`
- Sub-agent orchestration primitive:
- `codex-rs/core/src/codex_delegate.rs` lines ~34-39.
- Parallel infra init with `tokio::join!`:
- `codex-rs/core/src/codex.rs` lines ~1070-1110.

- `cline/cline`
- Tool surface includes `new_task` and `use_subagents`.
- `src/shared/tools.ts` lines ~22, ~35.
- Parallel semantics are explicit (`READ_ONLY_TOOLS`, toggle-driven behavior).
- `src/shared/tools.ts` lines ~42-55.
- Runtime flags include `subagentsEnabled` and `enableParallelToolCalling`.
- `src/core/task/index.ts` lines ~1853, ~1863.

- `RooVetGit/Roo-Code`
- Explicit delegation to child task:
- `src/core/task/Task.ts` lines ~2376-2388.
- Strong protection for delegated execution when `new_task` appears with other tools (tool isolation/truncation).
- `src/core/task/Task.ts` lines ~3500-3531.

- `google-gemini/gemini-cli`
- Tool kinds separated into mutating vs read-only parallel-safe classes.
- `packages/core/src/tools/tools.ts` lines ~823-836.
- Scheduler prevents concurrent scheduling while active (serialization guard).
- `packages/core/src/core/coreToolScheduler.ts` lines ~502-505.

- `OpenHands/OpenHands`
- Explicit delegate action model:
- `openhands/events/action/agent.py` lines ~77-85 (`AgentDelegateAction`).

- `Aider-AI/aider`
- Two-stage handoff pattern in architecture mode: architect output passed to editor coder.
- `aider/coders/architect_coder.py` lines ~22-45.

- `SWE-agent/SWE-agent`
- Retry architecture tracks sub-agent stats separately from reviewer path.
- `sweagent/agent/agents.py` lines ~257-269.

- `browser-use/browser-use`
- Action-centric single agent output shape (`List of actions to execute`).
- `browser_use/agent/views.py` lines ~431-434.
- Core types indicate one agent state/history/action loop.
- `browser_use/agent/service.py` imports around `AgentState`, `ActionResult`.

- `openinterpreter/open-interpreter`
- Direct loop framing in core docs: model response -> send code to computer -> parse response -> feed back to model.
- `interpreter/core/core.py` lines ~30-34.

## Update: LinkedIn feed format signals (live tab extraction)
- Source tab: `https://www.linkedin.com/feed/` via Grais tab reader.
- High-performing structural signals observed:
- Hook appears in first 1-3 short lines.
- Short line density is high (many lines under ~40 chars).
- List-driven body (`•` bullets) increases scanability for agent/system explanations.
- Strong contrast statements perform well:
- from "AI as tool" -> "AI as team/system"
- from hype -> usage reality
- CTA is usually explicit:
- direct question
- keyword comment trigger
- follow/repost instruction

### Engagement examples from sampled visible feed
- Example A (ad/promoted, high raw engagement but not benchmarkable for organic): ~216 reactions, 3 comments.
- Example B (organic long agent-themed list post): ~8 reactions, 7 comments, 1 repost.
- Example C (short claim + data framing): ~6 reactions.

### Practical takeaway for our post
- We should combine:
- contrarian one-line hook
- evidence paragraph (modern products, code-level)
- tight list (3-5 bullets)
- one discussion question CTA
- Avoid overlong promotional CTA or heavy hashtag stacks.

## Update: framework messaging vs product runtime

### Framework/SDK messaging signals (docs)
- Anthropic engineering guidance explicitly warns against complexity-first:
- "most successful implementations use simple, composable patterns rather than complex frameworks."
- recommends simplest solution first; many tasks work with optimized single-call/simpler setups.
- Source: Anthropic engineering article, 2024-12-19.
- LangChain multi-agent docs explicitly frame multi-agent patterns and include:
- manager (agents as tools)
- handoffs
- explicit note that a single agent with good tools/prompt can often be enough.
- Source: LangChain multi-agent docs page.
- OpenAI Agents docs/navigation emphasize:
- manager (agents as tools)
- handoffs
- tool use behavior and tool context.
- Source: OpenAI Agents docs.
- CrewAI README positioning emphasizes:
- "Open source Multi-AI Agent orchestration framework."
- Source: CrewAI README.

### Synthesis
- Framework surface area highlights multi-agent/handoff patterns (useful and real).
- Product runtime implementations in current OSS leaders still heavily optimize:
- tool design/registries
- state/session routing
- selective delegation boundaries
- constrained parallelism
- This supports the post thesis:
- teams over-index on architecture patterns before mastering decision boundaries and runtime reliability.

## Visualization artifact (generated)
- SVG chart:
- `/Users/mathiasasberg/Projects/satcom/agentic-framework-review-2026-02-21.svg`
- PNG chart (LinkedIn-ready upload format):
- `/Users/mathiasasberg/Projects/satcom/agentic-framework-review-2026-02-21.png`
- Simplified LinkedIn version (no stars):
- `/Users/mathiasasberg/Projects/satcom/agentic-framework-reality-simple-2026-02-21.svg`
- `/Users/mathiasasberg/Projects/satcom/agentic-framework-reality-simple-2026-02-21.png`

### Matrix encoded in chart
- `Tool-centric runtime`
- OpenClaw=Yes, Gemini CLI=Yes, browser-use=Yes, OpenHands=Yes, Open Interpreter=Yes, Codex=Yes, Cline=Yes, Aider=Yes, Roo Code=Yes, SWE-agent=Yes
- `Delegation/Subagent`
- OpenClaw=Yes, Gemini CLI=No, browser-use=No, OpenHands=Yes, Open Interpreter=No, Codex=Yes, Cline=Yes, Aider=Yes, Roo Code=Yes, SWE-agent=Yes
- `Parallel control`
- OpenClaw=No (not observed in sampled files), Gemini CLI=Yes, browser-use=No, OpenHands=No, Open Interpreter=No, Codex=Yes, Cline=Yes, Aider=No, Roo Code=Yes, SWE-agent=No
- `Agent-as-tool`
- OpenClaw=No (not observed in sampled files), Gemini CLI=No, browser-use=No, OpenHands=No, Open Interpreter=No, Codex=No, Cline=Yes, Aider=No, Roo Code=Yes, SWE-agent=No
