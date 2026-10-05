# SKILLS_INDEX — lean-algo-template

Master index of all skills and reference docs.

- **Tier 1 / Tier 2 skills** are invocable via trigger phrases listed in
  [.github/copilot-instructions.md](../copilot-instructions.md). Load by trigger
  phrase — do not pre-load.
- **Reference docs** are read on demand by skills (or by you) and are not direct
  invocation targets.
- **Performance audit agents** live in [`.github/agents/`](../agents/) and are paired
  with the `performant_software/` skill files below.

**Development pipeline:**
```
implement-handler → write-unit-tests → run-backtest-analysis → create-pr
```
Debugging: `debugging → implement-handler → write-unit-tests → create-pr`

---

## Tier 1 — Lifecycle Workflow Skills

| Skill | Trigger Phrases | Status | File |
|---|---|---|---|
| `implement-handler` | "implement handler", "scaffold handler", "build handler" | ✅ Populated | [SKILL.md](lifecycle-workflows/implement-handler/SKILL.md) |
| `write-unit-tests` | "write tests", "unit tests for", "test coverage" | ✅ Populated | [SKILL.md](lifecycle-workflows/write-unit-tests/SKILL.md) |
| `run-backtest-analysis` | "analyze backtest", "interpret results", "Sharpe ratio" | ✅ Populated | [SKILL.md](lifecycle-workflows/run-backtest-analysis/SKILL.md) |
| `create-pr` | "create PR", "open pull request", "ready to merge" | ✅ Populated | [SKILL.md](lifecycle-workflows/create-pr/SKILL.md) |

---

## Tier 2 — Domain Skills

### debugging/

| Skill | Trigger Phrases | Status | File |
|---|---|---|---|
| `debugging` | "why isn't it trading", "diagnose", "silent failure", "no orders", "symbol identity", "spec drift" | ✅ Populated | [SKILL.md](debugging/SKILL.md) |
| — | *(loaded by `debugging` skill)* | 📚 Reference | [why_didnt_my_algo_trade.md](debugging/why_didnt_my_algo_trade.md) |
| — | *(loaded by `debugging` skill)* | 📚 Reference | [silent_failure_modes.md](debugging/silent_failure_modes.md) |

### quantconnect/

| Skill | Trigger Phrases | Status | File |
|---|---|---|---|
| `qc-timezone-scheduling` | "schedule time", "timezone", "DST", "wall-clock", "fires before open" | ✅ Populated | [SKILL.md](quantconnect/timezone-and-scheduling/SKILL.md) |

### trading/  *(strategy-specific — populate as you build)*

| Skill | Trigger Phrases | Status | File |
|---|---|---|---|
| *(empty)* | "entry rules", "exit rules", "sizing", "regime filter", "risk" | 📋 Stub | Create files per rule family |

### performant_software/

Each skill below has a paired read-only agent in [`.github/agents/`](../agents/).
Use the agent for an interactive audit; use the skill file as the underlying
reference.

| Skill | Paired Agent | Trigger Phrases | Status | File |
|---|---|---|---|---|
| `five-multipliers` | [`performance-audit`](../agents/performance-audit.agent.md) | "optimize", "performance framework", "Five Multipliers" | ✅ Populated | [five_multipliers.md](performant_software/five_multipliers.md) |
| `waste-and-instructions` | [`waste-eliminator`](../agents/waste-eliminator.agent.md) | "reduce instructions", "eliminate waste", "Python overhead" | ✅ Populated | [waste_and_instructions.md](performant_software/waste_and_instructions.md) |
| `ipc-dependency-chains` | [`ipc-optimizer`](../agents/ipc-optimizer.agent.md) | "IPC", "dependency chains", "instruction-level parallelism" | ✅ Populated | [ipc_dependency_chains.md](performant_software/ipc_dependency_chains.md) |
| `simd-vectorization` | [`simd-vectorizer`](../agents/simd-vectorizer.agent.md) | "SIMD", "vectorize", "NumPy optimization" | ✅ Populated | [simd_vectorization.md](performant_software/simd_vectorization.md) |
| `memory-caching` | [`cache-analyst`](../agents/cache-analyst.agent.md) | "cache efficiency", "memory hierarchy", "L1/L2 cache" | ✅ Populated | [memory_hierarchy_and_caching.md](performant_software/memory_hierarchy_and_caching.md) |
| `multithreading` | [`multithread-planner`](../agents/multithread-planner.agent.md) | "multithreading", "ProcessPoolExecutor", "GIL" | ✅ Populated | [multithreading.md](performant_software/multithreading.md) |
| `measuring-performance` | [`measure-performance`](../agents/measure-performance.agent.md) | "measure performance", "profiling", "bandwidth ceiling" | ✅ Populated | [measuring_performance.md](performant_software/measuring_performance.md) |

---

## Reference Docs (loaded on demand by skills)

### _shared/references/ — cross-cutting

| File | Say... |
|---|---|
| [architecture-rules.md](_shared/references/architecture-rules.md) | "read architecture rules" |
| [config-thresholds.md](_shared/references/config-thresholds.md) | "read config thresholds" |
| [handler-responsibilities.md](_shared/references/handler-responsibilities.md) | "read handler responsibilities" |

### lifecycle/ — algo lifecycle rules

| File | Status | Description |
|---|---|---|
| [warmup_and_readiness.md](lifecycle/warmup_and_readiness.md) | ✅ Populated | Handler init order, daily schedule phases, fill reconciliation |
| [algo_lifecycle_rules.md](lifecycle/algo_lifecycle_rules.md) | ✅ Populated | `initialize()`, `on_data()`, `on_order_event()`, scheduled events, warm-up guard |

### indicators/

| File | Status | Description |
|---|---|---|
| [indicator_caching_rules.md](indicators/indicator_caching_rules.md) | ✅ Populated | Cache key structure, EMA seeding, ATR computation invariants |
| [multi_timeframe_indicators.md](indicators/multi_timeframe_indicators.md) | ✅ Populated | Native vs manual computation, consolidators, multi-symbol management |
| [indicator_readiness_gates.md](indicators/indicator_readiness_gates.md) | ✅ Populated | `IsReady` behaviour, `set_warm_up`, history injection, min bar requirements |

### data/

| File | Status | Description |
|---|---|---|
| [data_alignment_invariants.md](data/data_alignment_invariants.md) | ✅ Populated | Dual-format support, column naming, chronological ordering |
| [consolidation_rules.md](data/consolidation_rules.md) | ✅ Populated | `TradeBar`/`QuoteBar` consolidators, `DataNormalizationMode`, history alignment |

### options/  *(drop if equities-only)*

| File | Status | Description |
|---|---|---|
| [option_chain_filtering.md](options/option_chain_filtering.md) | ✅ Populated | Contract selection flow, OI gate, IV analytics, delta extraction |

### backtesting/

| File | Status | Description |
|---|---|---|
| [results_interpretation.md](backtesting/results_interpretation.md) | ✅ Populated | Runtime statistics, key metrics (Sharpe/PSR/drawdown), charts |
| [overfitting_prevention.md](backtesting/overfitting_prevention.md) | ✅ Populated | Hypothesis-driven research, parameter detection, backtest count limits |
| [deployment_constraints.md](backtesting/deployment_constraints.md) | ✅ Populated | Node specs, RAM/log/order/chart quotas, runtime limits |
| [debugging_backtests.md](backtesting/debugging_backtests.md) | ✅ Populated | QC debugger workflow, breakpoints, variable inspection |

---

## Legend

- ✅ **Populated** — content is authoritative and current
- 📚 **Reference** — supporting document; loaded by a skill, not invoked directly
- 📋 **Stub** — slot registered but file not yet created

---

## Adding a New Skill

1. Create `.github/skills/<tier>/<skill-name>/SKILL.md` with:
   - YAML frontmatter (`name`, `description` with trigger phrases, `argument-hint`)
   - Philosophy + hard boundaries
   - 4–6 phased workflow steps
   - Handoff Menu table
   - Reference Files section
2. Register it in this index with tier, trigger phrases, and status.
3. Add a dispatch row to [.github/copilot-instructions.md](../copilot-instructions.md).

All three steps are required — an unregistered skill is invisible to the AI.

## Adding a New Agent

1. Create `.github/agents/<agent-name>.agent.md` with YAML frontmatter declaring
   `description` (with trigger phrases), `tools`, `user-invocable`, and
   `argument-hint`.
2. Register it in the Tier 3 dispatch table in
   [.github/copilot-instructions.md](../copilot-instructions.md).
3. If the agent has a paired reference skill, register both in the
   `performant_software/` (or relevant) table above.
