# lean-algo-template — AI Coding Assistant Guide

**Strategy:** <!-- TODO: one-sentence thesis — instrument, holding period, edge -->.
See [docs/STRATEGY_OVERVIEW.md](../docs/STRATEGY_OVERVIEW.md) for the full spec.

**Architecture rule:** `main.py` is the *only* file that imports the LEAN SDK. All
handlers are pure Python with `__init__(self, algorithm)` constructors and no LEAN
imports. See [skills/_shared/references/architecture-rules.md](skills/_shared/references/architecture-rules.md).

**Documentation**: Detailed references live in [docs/](../docs/) and
[.github/skills/](skills/). Use **just-in-time context loading** — request specific
skills by trigger phrase only when needed. See
[COPILOT_CONTEXT_LOADING.md](COPILOT_CONTEXT_LOADING.md).

---

## Quick Reference: PR and Branch Naming

### Branch Names
- Patterns: `feat/<short-kebab-summary>` | `fix/<short-kebab-summary>` | `refactor/<short-kebab-summary>`
- Example: `feat/regime-filter-counter-state`

### PR Titles
- Action-oriented + scoped: `feat(<area>): concise summary`
- Example: `feat(handlers): add RegimeFilter counter state machine`

### PR Body Template
```markdown
## Summary
- add or update handler(s) under handlers/
- add or update unit tests under tests/unit/
- update config.py constants (with matching docs/STRATEGY_OVERVIEW.md change)
- update .github/skills/_shared/references/* if thresholds or responsibilities changed

## Validation
- poetry run black --check .
- poetry run pylint handlers/
- poetry run pytest tests/unit/ -v --cov=handlers --cov-fail-under=80
- spec / config / skills sync grep (see create-pr SKILL)
```

**Required behaviors:**
- ✅ Confirm before creating PRs (no auto-creation)
- ✅ Create PRs as drafts by default
- ✅ Never bypass with `--no-verify`; never push from `main`
- ✅ Include quality-gate results in the Validation section

---

## Available Agent Skills

Skills provide guided workflows. For full `SKILL.md` documentation, request the
skill by name or trigger phrase.

| # | Skill Name | Primary Triggers | File |
|---|---|---|---|
| 1 | `implement-handler` | "implement handler", "scaffold handler" | [SKILL.md](skills/lifecycle-workflows/implement-handler/SKILL.md) |
| 2 | `write-unit-tests` | "write tests", "test coverage" | [SKILL.md](skills/lifecycle-workflows/write-unit-tests/SKILL.md) |
| 3 | `run-backtest-analysis` | "analyze backtest", "Sharpe ratio", "PSR" | [SKILL.md](skills/lifecycle-workflows/run-backtest-analysis/SKILL.md) |
| 4 | `create-pr` | "create PR", "ready to merge", "spec/config/skills sync" | [SKILL.md](skills/lifecycle-workflows/create-pr/SKILL.md) |
| 5 | `debugging` | "why isn't it trading", "silent failure", "untracked fill" | [SKILL.md](skills/debugging/SKILL.md) |
| 6 | `qc-timezone-scheduling` | "timezone", "DST", "fires before open" | [SKILL.md](skills/quantconnect/timezone-and-scheduling/SKILL.md) |

> Strategy-specific skills (entry, exit, sizing, regime rules) live under
> [`skills/trading/`](skills/trading/) — empty in the template. Add a `SKILL.md`
> per rule family as you implement your strategy, then register it here and in
> [SKILLS_INDEX.md](skills/SKILLS_INDEX.md).
>
> The full trigger-phrase list for each skill is in its `SKILL.md` frontmatter and
> in [SKILLS_INDEX.md](skills/SKILLS_INDEX.md).

---

## Custom Agents

Purpose-built read-only agents in [`.github/agents/`](agents/) with scoped tool
access for safety and context isolation. **None** of these agents edit files or run
terminals.

| Agent | Tools | Best For |
|---|---|---|
| `performance-audit` *(router)* | `read, search, runSubagent` | Triage a slow hot path and dispatch the Five-Multipliers specialists in canonical order |
| `measure-performance` | `read, search` | Establish the throughput / bandwidth ceiling before any optimization |
| `waste-eliminator` | `read, search` | Multiplier 1 — find pure-Python overhead and loop-invariant work |
| `ipc-optimizer` | `read, search` | Multiplier 2 — split serial dependency chains into independent accumulators |
| `simd-vectorizer` | `read, search` | Multiplier 3 — NumPy dtype layout and bulk-op vectorization |
| `cache-analyst` | `read, search` | Multiplier 4 — working-set sizing, struct-of-arrays, chunking |
| `multithread-planner` | `read, search` | Multiplier 5 — separability, GIL, `ProcessPoolExecutor` partitioning |

**Invoke by name** (e.g., `@performance-audit handlers/data_handler.py:get_indicators`)
or by trigger phrase (e.g., `"performance audit"`, `"vectorize"`, `"cache efficiency"`).
The router enforces measure-first; specialists are leaf nodes.

---

## Subagents for Complex Tasks

Use subagents for multi-step exploration that would otherwise clutter the main
conversation.

| Agent | Best For |
|---|---|
| `Explore` | Fast read-only codebase exploration (quick / medium / thorough modes) — handler discovery, config audits, pattern identification |

---

## How to Request Context On-Demand

**Just-In-Time Context Loading** means requesting specific content when needed
instead of loading everything upfront.

### Common Requests
- **"Show me the full SKILL.md for `<skill-name>`"** — complete workflow doc.
- **"Read architecture rules"** — load [_shared/references/architecture-rules.md](skills/_shared/references/architecture-rules.md).
- **"Read config thresholds"** — load [_shared/references/config-thresholds.md](skills/_shared/references/config-thresholds.md).
- **"Read handler responsibilities"** — load [_shared/references/handler-responsibilities.md](skills/_shared/references/handler-responsibilities.md).
- **"Read strategy overview"** — load [docs/STRATEGY_OVERVIEW.md](../docs/STRATEGY_OVERVIEW.md).
- **"Show skills index"** — load [skills/SKILLS_INDEX.md](skills/SKILLS_INDEX.md).
- **"Run RAG inject for `<topic>`"** — execute `poetry run python rag/inject_context.py --query "<topic>" --top-k 5`, then read `docs/RAG_CONTEXT.md`.

See [COPILOT_CONTEXT_LOADING.md](COPILOT_CONTEXT_LOADING.md) for token budgets and
the full JIT-loading pattern.

---

## Framework Essentials

### Project Structure
```
main.py                → ONLY file that imports the LEAN SDK
config.py              → Final-typed strategy constants (single source of truth)
type_stubs.py          → LEAN type doubles for unit tests
handlers/              → Pure-Python business logic (no LEAN imports)
adapters/              → Platform adapters (non-LEAN backends)
universe/              → Static symbol candidates (CSV)
rag/                   → QC API RAG pipeline (crawler + retriever)
tests/                 → pytest unit + integration tests
docs/                  → Strategy spec, file map, dev guide
.github/skills/        → Invocable SKILL.md workflows + reference docs
.github/agents/        → Read-only specialist agents
```

### Critical Commands
```bash
# Format / lint / test (run before every PR)
poetry run black --check .
poetry run pylint handlers/
poetry run pytest tests/unit/ -v --cov=handlers --cov-fail-under=80

# RAG context for QC API questions
poetry run python rag/inject_context.py --query "<topic>" --top-k 5
```

### Development Pipeline
```
implement-handler → write-unit-tests → run-backtest-analysis → create-pr
```
Debugging: `debugging → implement-handler → write-unit-tests → create-pr`.
All handoffs require user confirmation — no auto-chaining.

### Strategy Notes
<!-- TODO: pin known constraints here as you discover them.
     Examples (delete and replace once your strategy is live):
       - Universe is rebuilt every N trading days
       - Indicator warm-up requires ≥ M bars
       - Daily eval fires at HH:MM in <timezone>
       - Known data-vendor quirk: …
-->

---

## Key Documentation Files

| File | Purpose |
|---|---|
| [docs/STRATEGY_OVERVIEW.md](../docs/STRATEGY_OVERVIEW.md) | Human-authored spec + Gherkin contract (source of truth for intent) |
| [docs/FILE_MAP.md](../docs/FILE_MAP.md) | Per-file responsibility map |
| [docs/DEVELOPMENT_GUIDE.md](../docs/DEVELOPMENT_GUIDE.md) | Setup, workflow, conventions |
| [docs/PLATFORM_ADAPTERS.md](../docs/PLATFORM_ADAPTERS.md) | Running handlers on non-LEAN backends |
| [docs/AI_RAG_STRUCTURE.md](../docs/AI_RAG_STRUCTURE.md) | RAG pipeline architecture |
| [docs/IMPLEMENTATION_PLAN.md](../docs/IMPLEMENTATION_PLAN.md) | Phased build plan |
| [docs/CHECKLIST_TEMPLATE.md](../docs/CHECKLIST_TEMPLATE.md) | Per-handler checklist |
| [README.md](../README.md) | Project overview + quickstart |

---

## Anti-Patterns ❌

**Avoid:**
- `from QuantConnect import ...` or `from AlgorithmImports import ...` **inside any handler file** — only `main.py` may import the LEAN SDK
- Hardcoded thresholds in handlers or tests — every numeric value lives in `config.py` as a `Final` constant
- Keying dicts on raw `Symbol` — use the canonical ticker string (see *Symbol Identity* in `architecture-rules.md`)
- Reading the *settled* position count to gate *pending* decisions in an async-fill loop (see *Decisions vs. Settled State*)
- Bypassing the quality gate with `--no-verify`; pushing directly to `main`
- Pre-loading every `SKILL.md` at the start of a conversation — use trigger phrases
- Editing a threshold in `config.py` without updating `docs/STRATEGY_OVERVIEW.md` and `_shared/references/config-thresholds.md` in the same commit

---

## Getting Started

1. **New to this project?** → Read [docs/STRATEGY_OVERVIEW.md](../docs/STRATEGY_OVERVIEW.md) and [docs/FILE_MAP.md](../docs/FILE_MAP.md).
2. **Need the skill catalog?** → Say `"show skills index"` to load [SKILLS_INDEX.md](skills/SKILLS_INDEX.md).
3. **Ready to build?** → Say `"implement handler — <name>"` to invoke the lifecycle workflow.
4. **Stuck?** → Say `"why isn't it trading"` (debugging) or `"performance audit"` (optimization).

---

**Last Updated:** June 4, 2026
**Context Strategy:** Just-In-Time Loading (minimize auto-loaded tokens; pull skills by trigger phrase)
