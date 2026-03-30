# Autopilot Configuration

# Copy this file to reviews/[project-name]/autopilot-config.md and adjust as needed.

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
# true  = Auto-advance to next round when all Critical/Important issues resolved
# false = Wait for user decision after each round
auto_advance_review: true

## Self-heal Retry Limit (max_heal_retries)
# Maximum retries for the same failure type, pause for user help if exceeded
max_heal_retries: 2

## Parallel text-commentary (parallel_commentaries)
# List primary source document paths to auto-analyze in parallel with the pipeline (relative to reviews/[project-name]/)
# Leave empty = no parallel processing
# Examples:
#   - sources/primary/camus-mythe-de-sisyphe-ch1.pdf
#   - sources/primary/sartre-existentialism-is-humanism.pdf
parallel_commentaries:
