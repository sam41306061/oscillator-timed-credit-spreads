# Copilot Context Loading Guide

Load only what you need, when you need it. The dispatch table in
`.github/copilot-instructions.md` loads automatically (~700 tokens). Everything else —
skill files, reference docs, strategy spec — is loaded on demand only.

---

## Token Budgets (approximate)

| Context Type | Tokens | When Loaded |
|---|---|---|
| `copilot-instructions.md` dispatch table | ~700 | Every conversation (automatic) |
| One Tier 1 lifecycle `SKILL.md` | ~2–3k | When a lifecycle workflow is invoked |
| One Tier 2 domain `SKILL.md` | ~1–2k | When a domain skill is invoked |
| One `_shared/references/` file | ~400–700 | When any skill references it |
| `docs/STRATEGY_OVERVIEW.md` | ~6k | Only when full strategy spec is needed |
| `docs/RAG_CONTEXT.md` (generated) | ~4–8k | After running `inject_context.py` |
| **Typical working session** | **~8–15k** | **~50k+ tokens available for actual work** |

---

## Common Workflow Sequences

### Implementing a new handler
1. Say: `"implement handler — <name>"`
2. Loads: `lifecycle-workflows/implement-handler/SKILL.md`
3. Skill pulls: `_shared/references/architecture-rules.md`, `handler-responsibilities.md`,
   `config-thresholds.md`
4. Handoff: `"write tests"` → `lifecycle-workflows/write-unit-tests/SKILL.md`
5. Handoff: `"create PR"` → `lifecycle-workflows/create-pr/SKILL.md`

### Debugging no-trade behavior
1. Say: `"why isn't my algo trading"`
2. Loads: `debugging/SKILL.md`
3. Follow the 5-phase diagnostic checklist
4. If scheduling issue: `"timezone"` → `quantconnect/timezone-and-scheduling/SKILL.md`

### Interpreting a backtest
1. Say: `"analyze backtest"` + paste QC statistics output
2. Loads: `lifecycle-workflows/run-backtest-analysis/SKILL.md`

### Optimising a hot path
1. Say: `"performance audit"` (or `"optimize"`)
2. Loads: `agents/performance-audit.agent.md` (router)
3. Router dispatches to specialist agents in canonical order:
   `measure-performance` → `waste-eliminator` → `ipc-optimizer` → `simd-vectorizer`
   → `cache-analyst` → `multithread-planner`

---

## Loading Shared References Directly

| Say... | Loads... |
|---|---|
| `"read config thresholds"` | `.github/skills/_shared/references/config-thresholds.md` |
| `"read architecture rules"` | `.github/skills/_shared/references/architecture-rules.md` |
| `"read handler responsibilities"` | `.github/skills/_shared/references/handler-responsibilities.md` |

---

## QC API Reference (RAG)

Before asking about specific QuantConnect APIs (indicators, scheduling, history,
consolidators), regenerate the RAG context for that topic:

```bash
poetry run python rag/inject_context.py --query "<your topic>" --top-k 5
```

Then say: `"read docs/RAG_CONTEXT.md and answer: <your question>"`.

---

## Anti-Patterns

| Anti-Pattern | Why It Hurts | Better Approach |
|---|---|---|
| "Read all the skill files" | Fills context window before any work begins | Use a trigger phrase to load one skill at a time |
| Loading `STRATEGY_OVERVIEW.md` proactively | Tokens for content that may not be needed | Load only when the spec is actually consulted |
| Running `inject_context.py` for every question | Slow and ~4–8k tokens per run | Run only before QC-API-specific questions |
| Pasting entire LEAN log files | Fills context; AI loses track of the question | Paste the 20–30 relevant lines + describe the symptom |
| Skipping the dispatch table | Skills not invoked; AI reasons from general knowledge | Use trigger phrases to load the authoritative skill |
