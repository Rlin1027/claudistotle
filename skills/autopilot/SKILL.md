---
name: autopilot
description: "Pipeline orchestrator that chains research workflow stages automatically, reducing manual intervention. Use when the user wants to run the full pipeline (or a segment) hands-free."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Autopilot — Pipeline Orchestrator

Run the Claudistotle research pipeline with minimal human intervention. The orchestrator reads project state, dispatches each stage via Task agents, evaluates results, and auto-advances when conditions are met.

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English.

## Entry Point Routing

- **`/claudistotle:autopilot`** (no args) -> Resume from wherever PROGRESS.md says. Run until pipeline completes or a pause condition triggers.
- **`/claudistotle:autopilot from [stage]`** -> Start from a specific stage (e.g., `/claudistotle:autopilot from literature-review`).
- **`/claudistotle:autopilot [stage-A] to [stage-B]`** -> Run a segment only (e.g., `/claudistotle:autopilot validate-A to draft`).

---

## Step 0 — Load State & Configuration

1. **Read** `reviews/[project-name]/PROGRESS.md`
   - Extract: Current Stage, Completed Milestones, next step
   - Determine the current pipeline position

2. **Read** `reviews/[project-name]/autopilot-config.md` (if exists)
   - Load autonomy level and gate overrides
   - If file doesn't exist, use **moderate** defaults (see Configuration section)

3. **Read** `reviews/[project-name]/INDEX.md` (if exists)
   - Get overview of project state

4. **Determine start stage**: Use PROGRESS.md to find the next pending stage, or the user's explicit `from [stage]` argument.

5. **Announce the plan** to the user:

```
═══════════════════════════════════════════════════
🤖 Autopilot Starting

📍 Start Point: [current stage]
🎯 End Point: [target or ✅ Ready to submit]
⚙️ Automation Level: [full/moderate/cautious]

Planned Execution:
  1. [stage name] — [auto/pause]
  2. [stage name] — [auto/pause]
  ...

⏸️ Pause Conditions:
  • [list conditions that will cause a pause]

Starting execution...
═══════════════════════════════════════════════════
```

---

## Step 1 — Pipeline Execution Loop

For each stage in the pipeline, repeat:

### 1.1 Pre-flight Check

- Verify required input files exist for this stage
- If missing, report and STOP (don't run a stage with missing prerequisites)

### 1.2 Dispatch Stage

Use the **Task tool** to spawn a sub-agent for the current stage. Pass the following context in the Task prompt:

```
You are running inside /claudistotle:autopilot. Execute the /claudistotle:[skill-name] skill for project "[project-name]".

AUTONOMY LEVEL: [full/moderate/cautious — from autopilot-config.md, default: moderate]

Apply the Level Presets table to determine behavior at each gate:

When level is "full":
- Skip User Confirmation Gates — proceed as if user approved
- For /claudistotle:refine: auto-advance on PROCEED or NARROW (still pause for PIVOT/EXPAND)
- For /claudistotle:draft Step 1: auto-advance if logic pre-review has zero ❌ (auto_approve_skeleton: true)
- For /claudistotle:peer-review: auto-advance between rounds when all Critical/Important issues are resolved

When level is "moderate" (DEFAULT):
- For /claudistotle:refine PROCEED: auto-advance
- For /claudistotle:refine NARROW: PAUSE — ask user
- For /claudistotle:draft Step 1: PAUSE — always ask user for skeleton approval (auto_approve_skeleton: false)
- For /claudistotle:peer-review: auto-advance between rounds

When level is "cautious":
- PAUSE at every major gate — user must confirm each stage transition
- Self-heal is OFF — report failures instead of auto-fixing

At completion, append a machine-readable exit signal as the LAST LINE of your response:
<!-- STAGE_EXIT: [signal] -->

Signals:
  PASS                              — Stage completed successfully, safe to auto-advance
  PASS:PROCEED                      — /claudistotle:refine recommends PROCEED
  PASS:NARROW                       — /claudistotle:refine recommends NARROW (auto-applied)
  PAUSE:PIVOT                       — /claudistotle:refine recommends PIVOT (needs user decision)
  PAUSE:EXPAND                      — /claudistotle:refine recommends EXPAND (needs user decision)
  PASS:SKELETON_APPROVED            — /claudistotle:draft Step 1 logic pre-review clean, skeleton saved
  PAUSE:SKELETON_NEEDS_REVIEW       — /claudistotle:draft Step 1 has ❌ items in logic pre-review
  PASS:DRAFT_COMPLETE               — /claudistotle:draft Step 2 done
  PASS:REVIEW_ROUND_N               — /claudistotle:peer-review round N completed, all critical resolved
  PAUSE:REVIEW_CRITICAL_UNRESOLVED  — /claudistotle:peer-review has unresolved critical issues
  FAIL:[reason]                     — Stage failed (e.g., FAIL:coverage_gap:3_concepts_missing)
  HEAL:[action]                     — Stage failed but self-heal is possible (e.g., HEAL:supplement_literature)

Read the full /claudistotle:[skill-name] SKILL.md and follow its protocol exactly, with the autonomous mode modifications above.
```

### 1.3 Read Stage Output

After the Task agent completes:

1. **Parse the exit signal** from the Task response (last `<!-- STAGE_EXIT: ... -->` line)
2. **Read updated PROGRESS.md** for state changes
3. **Read any new reports** in `reports/` directory

### 1.4 Evaluate & Route

Based on the exit signal and configuration:

| Exit Signal | Action |
|-------------|--------|
| `PASS` | Auto-advance to next stage |
| `PASS:PROCEED` | Auto-advance to `/draft` |
| `PASS:NARROW` | Auto-advance to `/draft` (proposal already updated) |
| `PAUSE:PIVOT` | **STOP** — present to user, await decision |
| `PAUSE:EXPAND` | Try self-heal (see §2), or STOP if max retries reached |
| `PASS:SKELETON_APPROVED` | Auto-advance to `/draft` Step 2 |
| `PAUSE:SKELETON_NEEDS_REVIEW` | **STOP** — present skeleton to user |
| `PASS:DRAFT_COMPLETE` | Auto-advance to `/validate` Mode B |
| `PASS:REVIEW_ROUND_N` | Auto-advance to next round (or `/validate` Mode C after Round 3) |
| `PAUSE:REVIEW_CRITICAL_UNRESOLVED` | **STOP** — present unresolved issues to user |
| `FAIL:*` | Try self-heal (see §2), or STOP if not healable |
| `HEAL:*` | Execute self-heal action (see §2) |

### 1.5 Progress Report (between stages)

After each successful stage, output a brief progress update:

```
───── ⏩ [stage] Complete ─────
📄 Output: [files]
⏱️ Next Step: [next stage] (auto-advancing)
───────────────────────────
```

If pausing:

```
───── ⏸️ Paused at [stage] ─────
Reason: [reason]
📄 Output: [files]

Your decision needed:
  [present options]
───────────────────────────────
```

---

## Step 2 — Self-Healing Protocol

When a stage fails or a validate gate doesn't pass, attempt automatic repair before stopping:

### 2.1 Heal Conditions

| Failure | Self-Heal Action | Max Retries |
|---------|-----------------|-------------|
| validate(A): concept coverage gaps | Run supplementary `/claudistotle:literature-review` with gap terms as search keywords | 2 |
| validate(B): orphan citations | Spawn Task to fix: search `literature-all.bib` for closest match, or remove citation | 1 |
| validate(B): missing bib fields | Spawn Task to enrich bib entries via CrossRef/Semantic Scholar | 1 |
| validate(C): incomplete change record | Spawn Task to fill in missing RATIONALE/CHANGE MADE | 1 |
| `/claudistotle:refine` → EXPAND | Run supplementary `/claudistotle:literature-review` then re-run `/claudistotle:refine` | 1 |

### 2.2 Heal Execution

```
───── 🔧 Self-Healing Initiated ─────
Issue: [failure description]
Repair Action: [what will be attempted]
Retry Count: [N]/[max]
──────────────────────────────
```

1. Dispatch the heal action as a Task agent
2. Re-run the failed stage
3. If still fails after max retries → STOP and report to user

### 2.3 Heal Guardrails

- **Never self-heal more than 2 consecutive times** for the same failure type
- **Never self-heal PIVOT** — this is a fundamental direction change that requires human judgment
- **Never self-heal skeleton issues** — argument structure requires human oversight
- Track all heal attempts in PROGRESS.md under a `### Self-Heal Log` section

---

## Step 3 — Parallel Execution (Optional)

If `autopilot-config.md` lists `parallel_commentaries`, launch them alongside the main pipeline:

### 3.1 When to Launch

- Start parallel text-commentaries at the same time as `/literature-review`
- These run independently and produce `commentary-*.md` files
- By the time `/draft` starts, commentaries are ready for integration

### 3.2 How to Launch

```
# In a single message, dispatch both:
Task 1: /claudistotle:literature-review (main pipeline)
Task 2: /claudistotle:text-commentary for [source-file-1]
Task 3: /claudistotle:text-commentary for [source-file-2]
```

### 3.3 Merge Point

- Before starting `/draft`, check if all parallel commentaries completed
- If any are still running, wait for completion
- If any failed, note in progress report but proceed (commentaries are optional)

---

## Pipeline Stage Reference

Complete ordering with stage identifiers:

| Order | Stage ID | Skill | Auto-advance? |
|-------|----------|-------|---------------|
| 0 | `research-design` | `/claudistotle:research-design` | ❌ Always interactive |
| 1 | `literature-review` | `/claudistotle:literature-review` | ✅ Always |
| 2 | `validate-A` | `/claudistotle:validate` Mode A | ✅ on PASS |
| 3 | `refine` | `/claudistotle:refine` | ✅ on PROCEED/NARROW |
| 4 | `draft-skeleton` | `/claudistotle:draft` Step 1 | ⚠️ Config-dependent |
| 5 | `draft-prose` | `/claudistotle:draft` Step 2 | ✅ Always |
| 6 | `validate-B` | `/claudistotle:validate` Mode B | ✅ on PASS |
| 7 | `review-round1` | `/claudistotle:peer-review` Round 1 | ✅ on all critical resolved |
| 8 | `review-round2` | `/claudistotle:peer-review` Round 2 | ✅ on all critical resolved |
| 9 | `review-round3` | `/claudistotle:peer-review` Round 3 | ✅ on all critical resolved |
| 10 | `validate-C` | `/claudistotle:validate` Mode C | ✅ on PASS |
| 11 | `done` | — | 🎉 Pipeline complete |

---

## Configuration Reference

`autopilot-config.md` supports these settings:

```markdown
# Autopilot Configuration

## Automation Level (level)
# full     — Fully automatic: pause only on PIVOT/EXPAND or continuous failures
# moderate — Pause at skeleton confirmation gate, otherwise automatic (default)
# cautious — Pause at every major stage (equivalent to manual mode)
level: moderate

## Auto-approve Skeleton (auto_approve_skeleton)
# true  = Auto-advance to Step 2 when logic pre-review has no ❌ items
# false = Always wait for user confirmation (default for moderate, true for full)
auto_approve_skeleton: false

## Peer-review Auto-advance (auto_advance_review)
# true  = Auto-advance to next round when all Critical issues resolved
# false = Wait for user decision after each round
auto_advance_review: true

## Self-heal Retry Limit (max_heal_retries)
max_heal_retries: 2

## Parallel text-commentary (parallel_commentaries)
# List primary source document paths to auto-analyze in parallel with the pipeline
# Leave empty = no parallel processing
parallel_commentaries:
```

### Level Presets

| Setting | `cautious` | `moderate` | `full` |
|---------|-----------|-----------|--------|
| validate → next | ✅ auto | ✅ auto | ✅ auto |
| refine PROCEED → draft | ⏸️ pause | ✅ auto | ✅ auto |
| refine NARROW → draft | ⏸️ pause | ⏸️ pause | ✅ auto |
| refine PIVOT/EXPAND | ⏸️ pause | ⏸️ pause | ⏸️ pause |
| skeleton approval | ⏸️ pause | ⏸️ pause | ✅ auto (if clean) |
| review round advance | ⏸️ pause | ✅ auto | ✅ auto |
| self-heal | ❌ off | ✅ on | ✅ on |

---

## Stage Completion Protocol

When `/autopilot` finishes (either pipeline complete or paused):

### Pipeline Complete

```
═══════════════════════════════════════════════════
🎉 Autopilot Complete — Full Research Pipeline Passed

📄 Final Output:
   • paper-draft.md (Final version)
   • literature-all.bib ([N] references)
   • change-record.md (Three-round revision history)
   • INDEX.md (Research data index)

📊 Execution Statistics:
   • Stages Executed: [N]
   • Self-heal Attempts: [N]
   • Pause Count: [N]
   • Parallel Commentaries: [N]

📍 Current Position: ✅ Ready to Submit

💡 Next Options:
   • Export as .docx (pandoc)
   • Use /claudistotle:feedback to record advisor feedback and continue iterating
   • Re-run any stage for deeper development
═══════════════════════════════════════════════════
```

### Paused

```
═══════════════════════════════════════════════════
⏸️ Autopilot Paused

📍 Pause Position: [stage]
❓ Pause Reason: [reason]

📊 Completed: [list completed stages]

Once you've made your decision, type /claudistotle:autopilot to continue.
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

- Record autopilot session start/end times
- Record all auto-advance decisions made
- Record all self-heal attempts and outcomes
- Update Current Stage to reflect final position

---

## Failure Modes to Avoid

- **Runaway loops**: Never allow more than 2 consecutive self-heal attempts for the same failure. After 2, STOP.
- **Silent skipping**: Never skip a stage. If a stage fails and can't be healed, STOP — don't proceed to the next stage.
- **Context exhaustion**: For long pipelines, the orchestrator should dispatch each stage as a fresh Task agent (not accumulate context). Read results from files, not from agent memory.
- **Overriding human judgment**: PIVOT and skeleton issues ALWAYS pause, regardless of config level. These involve fundamental research direction decisions. Note: `/claudistotle:autopilot` is the entry point for the orchestrator and routing to other skills is done via `/claudistotle:skill-name` notation.

## Quality Checklist

Before completing an autopilot session, verify:

- [ ] PROGRESS.md accurately reflects the final state
- [ ] All stage outputs are present in the project directory
- [ ] No stages were silently skipped
- [ ] Self-heal attempts (if any) are documented
- [ ] INDEX.md is up-to-date (regenerated after any literature changes)
