**This is the plugin version of Claudistotle.** Install with: `/plugin marketplace add Rlin1027/claudistotle` then `/plugin install claudistotle@claudistotle`

**Claudistotle** is a philosophy research assistant that covers the full research pipeline: topic refinement, automated literature review with verified citations, primary text analysis, academic writing, and peer review simulation.

# Mode

**Production mode** (default): Route user requests to the appropriate skill based on what they need (see Skill Routing below). On startup, read `reviews/[project-name]/PROGRESS.md` (if exists) to understand current research stage.

**Development mode**: Only if user explicitly asks to develop, improve, or test agents/skills. Work on definitions in `agents/` and `skills/`.

# Skill Routing

| User wants to... | Invoke |
|---|---|
| First-time setup, configure API keys, verify environment | `/claudistotle:setup` |
| Usage guide, tutorial, how to use this tool | `/claudistotle:help` |
| Choose a topic, narrow a research question, plan a thesis | `/claudistotle:research-design` |
| Generate a literature review with verified citations | `/claudistotle:literature-review` |
| Do close reading / annotate logical connectors / write text commentary | `/claudistotle:text-commentary` |
| Write or draft a paper, thesis chapter, or article | `/claudistotle:draft` |
| Get feedback on a draft, simulate peer review, revise | `/claudistotle:peer-review` |
| Refine the research question after literature review | `/claudistotle:refine` |
| Validate outputs between phases (coverage, citations, changes) | `/claudistotle:validate` |
| Record and process advisor/external feedback | `/claudistotle:feedback` |
| Run the pipeline automatically with minimal intervention | `/claudistotle:autopilot` |
| Search academic databases directly (advanced) | `/claudistotle:philosophy-research` |

## Typical Research Workflow

```
/claudistotle:research-design  ->  /claudistotle:literature-review  ->  /claudistotle:validate(A)  ->  /claudistotle:refine  ->  /claudistotle:draft  ->  /claudistotle:validate(B)  ->  /claudistotle:peer-review  ->  /claudistotle:validate(C)  ->  ✅
        (Phase 0)                   (Phases 1-6)                    Coverage check              Question                 (Phase 7)                  Citation check               (Phase 8)                       Record check
                                                                                              refinement
                                                    ↑                                                                                                                                        |
                                                    └──── /claudistotle:feedback (advisor feedback can re-enter at any point) ←──────────────┘

                              /claudistotle:text-commentary (independent: primary text analysis, links to sources/primary/)

Automated mode: /claudistotle:autopilot chains stages automatically, pausing only at critical decision points.
```

**Quality gates between phases:**
- `/claudistotle:validate` Mode A (after literature-review): Checks literature coverage against research question
- `/claudistotle:refine` (after validate A): Compares research question against literature landscape — proceed, narrow, pivot, or expand
- `/claudistotle:validate` Mode B (after draft): Checks citation integrity (orphans, idle refs, format)
- `/claudistotle:validate` Mode C (after peer-review): Checks change record completeness

All outputs are saved to `reviews/[project-name]/`. Each skill reads outputs from previous skills in the same directory.

## Workspace Directory Structure

Each project directory under `reviews/` uses this structure:

```
reviews/[project-name]/
├── INDEX.md                    ← Project index (auto-generated, for efficient context usage)
├── research-proposal.md        ← Active working files (skills read/write directly)
├── literature-review-final.md
├── literature-all.bib
├── argument-skeleton.md
├── paper-draft.md
├── change-record.md
├── commentary-*.md
├── advisor-feedback.md         ← External feedback records (from /feedback)
├── autopilot-config.md         ← Autopilot autonomy settings (optional, from template)
├── PROGRESS.md                 ← Research progress tracker (auto-updated by all skills)
├── sources/
│   ├── primary/                ← Primary source texts (user-provided, linked to commentary-*.md)
│   └── secondary/              ← Secondary literature full-text (auto-downloaded + PDF→MD)
├── archive/                    ← Version history (auto-archived at decision points)
│   ├── research-proposal-v1-YYYY-MM-DD.md
│   ├── argument-skeleton-v1-YYYY-MM-DD.md
│   └── paper-draft-pre-round1-YYYY-MM-DD.md
├── intermediate_files/          ← Sub-agent temp files (literature-review internals)
│   ├── literature-domain-*.bib
│   ├── synthesis-outline.md
│   └── synthesis-section-*.md
└── reports/                    ← Timestamped quality reports (intellectual audit trail)
    ├── validate-coverage-YYYY-MM-DD.md
    ├── refine-analysis-YYYY-MM-DD.md
    ├── validate-citation-YYYY-MM-DD.md
    ├── review-round1-YYYY-MM-DD.md
    ├── review-round2-YYYY-MM-DD.md
    ├── review-round3-YYYY-MM-DD.md
    ├── validate-record-YYYY-MM-DD.md
    └── feedback-session-YYYY-MM-DD.md
```

**Rule**: Active working files stay flat at the root (skills reference these paths directly). Subdirectories are for archiving, logging, and source storage only.

## Key Workflow Details

- **Language rule**: All skills match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English.
- **`/validate` auto-detection**: When invoked without specifying a mode, `/validate` auto-detects which mode to run based on which files were most recently modified.
- **`/draft` is two-step**: Step 1 builds an argument skeleton (CLAIM/EVIDENCE/COUNTERARGUMENT/REBUTTAL/FUNCTION per section) with a logic pre-review, then waits for user confirmation before Step 2 writes prose. The skeleton is saved to `argument-skeleton.md`.
- **`/draft` integrates text commentaries**: On startup, `/draft` scans for `commentary-*.md` files in the workspace and builds a commentary index. During prose writing, relevant close-reading analyses are automatically integrated with footnote attribution.
- **`/peer-review` Round 2 automation**: Round 2 (evidence quality) automatically runs `/validate` Mode B citation check logic internally before Athena's review, embedding orphan/idle citation results in the review report.
- **`/feedback` routes by type**: Classifies advisor feedback into directional/literature/argumentation/evidence/writing, then routes to the appropriate skill (/refine, /literature-review, /draft, /peer-review) with the feedback as additional context.
- **`/literature-review` auto-downloads sources**: Phase 6 attempts to download open-access PDFs via Unpaywall, converts to Markdown, and reports un-downloadable papers for manual download.
- **`/text-commentary` links to sources/primary/**: Commentary filenames use the same slug as primary source files in `sources/primary/`, allowing `/draft` to trace from commentary back to original text.
- **`INDEX.md` for context efficiency**: A lightweight project index (`reviews/[project-name]/INDEX.md`) lists all bib entries, sources, commentaries, and reports in compact form. Skills read INDEX.md first, then selectively load specific entries via Grep, avoiding loading entire files (e.g., `literature-all.bib`) into context. Regenerated by `/literature-review` and `/text-commentary` via `generate_index.py`.
- **`PROGRESS.md` auto-update**: Every skill updates `PROGRESS.md` upon completion with current stage, next step, and milestone records. Claude Code reads this file on startup to resume context.
- **Stage completion prompts**: Every skill outputs a standardized completion banner showing current position in the workflow, outputs produced, and the recommended next step.
- **Machine-readable exit signals**: Every skill appends a `<!-- STAGE_EXIT: ... -->` comment as its last output line. These signals (`PASS`, `FAIL:reason`, `PAUSE:reason`) are used by `/autopilot` for programmatic auto-advance and self-heal decisions.
- **`/autopilot` orchestrator**: Chains pipeline stages automatically via Task agents. Reads `autopilot-config.md` for autonomy level (full/moderate/cautious). Auto-advances on `PASS` signals, pauses on `PAUSE` signals, and self-heals on `FAIL` signals (e.g., re-running supplementary literature review for coverage gaps). Parallel text-commentary execution supported.

# Objectives

**Priority order** (applies to all skills):

1. **Accurate** — Only cite verified papers; never fabricate references
2. **Comprehensive** — Cover all major positions and key debates
3. **Rigorous and concise** — Analytical depth, tight prose; balanced presentation of positions
4. **Reproducible** — Structured workflow, standard BibTeX output, Chicago author-date citations

**NOT priorities**:
- Speed — Quality over fast completion
- Context efficiency — Use full context as needed

# File Structure

- `reviews/` — All research projects. Each has its own subdirectory (e.g., `reviews/camus-absurd/`). Gitignored (local only).
- `skills/research-design/` — Topic refinement and research question formulation (Phase 0).
- `skills/literature-review/` — Orchestration skill for automated 6-phase literature review. `scripts/` contains assembly, deduplication, bibliography generation, and linting tools.
- `skills/philosophy-research/` — API search scripts for 8 academic sources (Semantic Scholar, OpenAlex, CORE, arXiv, SEP, IEP, PhilPapers, NDPR), citation verification (CrossRef), and web search fallback (Brave).
- `skills/text-commentary/` — Primary text close reading: logical connector annotation and structured commentary (introduction/development/conclusion). `references/` contains the assignment guide and examples.
- `skills/draft/` — Two-step academic writing: Step 1 builds argument skeleton with logic pre-review + user gate; Step 2 expands into prose integrating `commentary-*.md`. Supports analytic, continental, and comparative philosophy templates.
- `skills/refine/` — Research question refinement after literature review. Compares proposal against literature landscape and recommends proceed/narrow/pivot/expand.
- `skills/validate/` — Quality gate between workflow phases. Checks literature coverage (Mode A), citation integrity (Mode B), and change record completeness (Mode C).
- `skills/peer-review/` — Three-round peer review: Round 1 (argument validity), Round 2 (evidence quality + citation check), Round 3 (writing quality). Each round: Athena reviews → Calliope revises → user decision gate.
- `skills/feedback/` — External feedback integration: records advisor/committee feedback, classifies by type, routes to appropriate workflow stage with context.
- `skills/autopilot/` — Pipeline orchestrator: chains stages via Task agents, auto-advances on PASS, self-heals on FAIL, pauses at critical decision points. Configurable autonomy levels (full/moderate/cautious).
- `skills/setup/` — First-time configuration wizard: environment check, API key setup, workspace initialization.
- `skills/help/` — Interactive usage guide and tutorial. Teaches users how to use all Claudistotle skills effectively.
- `agents/` — Specialized subagent definitions invoked by the literature-review skill.
- `hooks/scripts/` — Quality gates: BibTeX validation, metadata provenance checking, background bash blocking, environment setup.
- `docs/` — Shared specifications (ARCHITECTURE.md, conventions.md, permissions-guide.md).
- `docs/references/` — Shared knowledge base: philosophical-methods.md, writing-standards.md, citation-guide.md, research-pipeline.md. Referenced by multiple skills.
- `.claude-plugin/plugin.json` — Plugin configuration and metadata.
- `settings.json` — Hook definitions and permissions (checked in).
- `GETTING_STARTED.md` — Setup guide and API key configuration.

# Literature Review Workflow Architecture

**`/literature-review` skill** — Coordinates the 6-phase automated workflow:
- Phase 1: Verify environment and determine execution mode
- Phase 2: Task tool invokes `literature-review-planner` — Decomposes topic into domains
- Phase 3: Task tool invokes `domain-literature-researcher` x N (parallel) — API searches; outputs BibTeX
- Phase 4: Task tool invokes `synthesis-planner` — Designs outline from collected literature
- Phase 5: Task tool invokes `synthesis-writer` x N (parallel) — Writes sections
- Phase 6: Assemble final review, deduplicate BibTeX, generate bibliography, lint, optional DOCX

**Specialized subagents** (invoked via Task tool, cannot spawn other subagents):
- `literature-review-planner` — Decomposes topic into domains and search strategies (methodology-aware)
- `domain-literature-researcher` — Searches academic sources, produces BibTeX with rich annotations
- `synthesis-planner` — Designs tight outline from collected literature
- `synthesis-writer` — Writes individual sections (style adapts to philosophical tradition; reads `research-proposal.md` for strategic positioning)

# Development

For agent architecture and design patterns, see `docs/ARCHITECTURE.md`.

## Windows Compatibility

This repository works natively on Windows without WSL. Claude Code on Windows requires Git for Windows and uses Git Bash to execute hooks and commands. The SessionStart hook detects the platform and activates the correct venv path.

## Setup

```bash
uv sync          # Create venv and install all dependencies (including dev)
```

Regular users get only production dependencies — the SessionStart hook runs `uv sync --no-group dev`.

API keys are required for literature searches. See `GETTING_STARTED.md` for setup instructions, or run:
```bash
$PYTHON $CLAUDE_PLUGIN_ROOT/skills/philosophy-research/scripts/check_setup.py
```

## Principles

- **Keep the repository lean** — Remove deprecated files rather than marking them.
- **Single source of truth** — Dependencies in `pyproject.toml`, agent definitions in `agents/`, skill definitions in `skills/`, shared references in `docs/references/`.
- **Simple and concise** — Prefer simple solutions. Keep instructions brief and effective.
- **Verify assumptions empirically** — Test before codifying.
- **Cross-platform** — Must work on Linux, macOS, and Windows. Use forward slashes in paths.
- **Python file I/O** — Always pass `encoding='utf-8'` to `open()`, `read_text()`, and `write_text()`.

## Permissions

- **Evaluation order**: deny -> ask -> allow. First matching rule wins.
- **Bash is allowed globally** in `settings.json` and plugin configuration. Safety comes from deny rules (`sudo`, `dd`, `mkfs`), ask rules (`rm`, `rmdir`), and scoped `Write`/`Edit` (only `reviews/`).
- **Do not revert to enumerated Bash patterns.** This was attempted 4 times (Jan-Feb 2026) and failed each time.

## Hooks and Python

Claude Code runs each hook command in its own shell process — the SessionStart venv activation does NOT carry over. **All hooks that invoke Python must use the project venv explicitly**, never bare `python`.

- **`.env` loading**: API keys are stored ONLY at `${CLAUDE_PLUGIN_DATA}/.env` (never in the plugin directory). Loaded at two layers: (1) `hooks/scripts/setup-environment.sh` reads `${CLAUDE_PLUGIN_DATA}/.env` and exports `CLAUDISTOTLE_ENV_FILE`, (2) each script calls `load_env()` from `_env_loader.py` which reads the same file. The `.env` file is `chmod 600` (owner-only) for security.
- **Shell hooks**: Resolve `$PYTHON` with cross-platform fallback.
- **Bash tool calls**: Use `$PYTHON` (absolute path set by `hooks/scripts/setup-environment.sh`).
- **PreToolUse hooks**: Fire for subagent tool calls. Frontmatter hooks do NOT fire for Task-spawned subagents.

## Adding Python Dependencies

1. `pyproject.toml` — Add to `dependencies`
2. `uv.lock` — Regenerate with `uv lock`
3. `hooks/scripts/setup-environment.sh` — Add `check_package` call if required
4. `skills/philosophy-research/scripts/check_setup.py` — Add if for philosophy-research skill
