---
name: create-pr
description: |
  Run the quality gate and create a pull request.
  Trigger phrases: "create PR", "open pull request", "ready to merge", "submit PR",
  "create pull request", "push PR", "spec/config/skills sync"
argument-hint: "Branch name and a one-line description of the change (e.g., 'feat/data-handler — adds ATR caching')"
---

# Create PR

## Philosophy

No code reaches `main` without passing every quality check. The gate is not optional
even for small changes — a config drift or an accidental LEAN import can silently
break the backtest.

**Hard boundaries:**
- Never bypass with `--no-verify` or by skipping individual checks.
- Do not open a PR from `main` — always work from a feature branch.
- Branch naming: `feat/<description>`, `fix/<description>`, or `refactor/<description>`.
- Coverage must be ≥ 80% on the handler(s) changed — not just the repo average.

---

## Phase 1 — Confirm Branch

```bash
git branch --show-current
```

If on `main`, stop: `git checkout -b feat/<description>` first.

---

## Phase 0 — Spec / Config / Skills Sync

**Run this first.** A bare-number drift between the spec, `config.py`, and the skill
docs is a silent failure the test suite cannot catch.

```bash
# Numbers in skill docs must match config.py for every threshold the strategy uses.
# Replace the loop variable list with your strategy's actual constants.
for name in MIN_DAYS_TO_EVENT MAX_DAYS_TO_EVENT SMA_LONG_PERIOD EMA_MID_PERIOD \
            MAX_ATR_EXTENSION ENTRY_ZONE_TOLERANCE_PCT MAX_UNIVERSE_SIZE; do
  echo "=== $name ==="
  grep -rn "$name" config.py docs/ .github/skills/ 2>/dev/null
done
```

Stop and fix if:
- A value appears in `docs/STRATEGY_OVERVIEW.md` but a different value in `config.py`.
- A value in `_shared/references/config-thresholds.md` is stale vs. `config.py`.
- A per-skill `SKILL.md` cites a literal number that no longer matches `config.py`.

---

## Phase 2 — Quality Gate (all must pass)

Fix each failure before moving to the next check.

```bash
# 1. Format
poetry run black --check .

# 2. Lint
poetry run pylint handlers/

# 3. Tests + coverage
poetry run pytest tests/unit/ -v --cov=handlers --cov-report=term-missing --cov-fail-under=80

# 4. Hardcode check — no magic numbers in handler files
grep -rnE "[^A-Za-z_][0-9]+(\.[0-9]+)?" handlers/ | grep -v "config\." | grep -v "#"
```

- **Black fails:** `poetry run black .`, re-check.
- **Coverage fails:** load `write-unit-tests` skill to add missing cases.
- **Hardcode check flags a line:** move the value to `config.py` as a `Final` constant.

---

## Phase 3 — Build PR Description

```markdown
## Summary
<One-sentence description of what changed and why>

## Handlers Changed
- `<handler_name>.py` — <what changed>

## Quality Gate
- [x] Black — passed
- [x] Pylint — passed (score: X.X/10)
- [x] Tests — passed (coverage: XX%)
- [x] No hardcoded thresholds
- [x] Spec / config / skills in sync

## Config Constants Added or Changed
- `CONSTANT_A` = <value>

## Testing
<Unit tests added, backtest run, manual QC log review>
```

---

## Phase 4 — Create the PR

```bash
git add -p          # review each hunk before staging
git commit -m "feat: <description>"
git push origin <branch-name>
gh pr create --title "feat: <description>" --body-file pr_body.md --draft
```

Review the draft PR before marking ready for review.

---

## Handoff Menu

| Next Step | Trigger | Skill |
|---|---|---|
| Fix failing tests before PR | "test failing", "coverage low" | `lifecycle-workflows/write-unit-tests` |
| Validate backtest before merging | "analyze backtest" | `lifecycle-workflows/run-backtest-analysis` |

---

## Reference Files

- [Architecture rules](../../_shared/references/architecture-rules.md)
- `pyproject.toml` — Black line length and Pylint configuration
