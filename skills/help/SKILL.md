# Claudistotle Help & User Guide

Interactive usage guide. Presents what Claudistotle can do and teaches the user how to use it effectively.

**Triggers**: `help`, `explanation`, `teaching`, `tutorial`, `how to use`, `how to use`, `guide`, `usage instructions`, `feature overview`

---

## Behavior

When this skill is invoked, present the guide below **in the user's language**. Do NOT dump the entire guide at once — present it as an interactive conversation:

1. First, show the **Welcome** section and the **Quick Overview** of what Claudistotle can do.
2. Then ask the user what they'd like to learn more about (present the topics as choices).
3. Based on their choice, show the relevant section in detail.
4. After each section, offer to explain another topic or start working.

This keeps the experience conversational rather than overwhelming.

---

## Welcome

```
╔══════════════════════════════════════════════════════════════╗
║        Claudistotle — Philosophy Research Assistant          ║
╚══════════════════════════════════════════════════════════════╝
```

Claudistotle is a full-pipeline philosophy research tool that helps you go from a rough topic idea to a polished academic paper. It handles literature search across 8+ academic databases, writes with verified citations only (never fabricates references), and simulates three-round peer review.

---

## Quick Overview — What Can It Do?

Present this as a concise summary:

**Research pipeline (in order):**

| Phase | Command | What it does |
|-------|---------|-------------|
| 0 | `/claudistotle:research-design` | Define your research question, scope, and methodology |
| 1-6 | `/claudistotle:literature-review` | Automated literature review — searches 8 academic databases, collects verified citations, writes a synthesis |
| QA | `/claudistotle:validate` | Quality gate — checks coverage, citation integrity, or change records |
| — | `/claudistotle:refine` | Re-evaluate your research question based on what the literature actually says |
| 7 | `/claudistotle:draft` | Write your paper — builds an argument skeleton first, then expands to prose |
| 8 | `/claudistotle:peer-review` | Three-round simulated peer review (argument → evidence → writing quality) |
| — | `/claudistotle:feedback` | Record advisor feedback and route it to the right stage |
| — | `/claudistotle:text-commentary` | Close reading and annotation of primary source texts |
| — | `/claudistotle:autopilot` | Run the entire pipeline automatically with minimal intervention |

**Utility commands:**

| Command | What it does |
|---------|-------------|
| `/claudistotle:setup` | First-time configuration (API keys, environment) |
| `/claudistotle:help` | This guide |
| `/claudistotle:philosophy-research` | Direct access to academic database search scripts |

After showing this, ask: "Which topic would you like to learn more about?"

Offer these choices:

1. **Getting started** — First research project walkthrough
2. **The research workflow** — How the phases connect
3. **Literature review details** — How the automated search works
4. **Writing and peer review** — How drafting and revision work
5. **Autopilot mode** — Hands-free pipeline execution
6. **Text commentary** — Close reading of primary sources
7. **Tips and best practices** — Get the most out of Claudistotle
8. **I'm ready to start** — Jump right in

---

## Topic 1: Getting Started

### If they haven't run /claudistotle:setup yet:

Tell them to run `/claudistotle:setup` first. It will guide them through:
- Environment verification (Python, uv, jq)
- API key configuration (Brave Search, CrossRef, Semantic Scholar, OpenAlex)
- Creating their first project workspace

### If they're already set up:

Walk them through starting their first research:

```
Step 1: Tell me your research topic
────────────────────────────────────
Just describe what you want to research. Be as specific or vague as you want.

Examples:
  "I want to write about the extended mind thesis and its implications for cognitive offloading"
  "I want to research the relationship between Camus's philosophy of the absurd and existentialism"
  "Explore the relationship between Wittgenstein's language games and AI alignment"

Step 2: I'll invoke /claudistotle:research-design
──────────────────────────────────────────────────
This will help you:
  → Narrow down your research question
  → Define your methodology (analytic, continental, comparative...)
  → Plan your thesis structure
  → Output: research-proposal.md

Step 3: Literature review
─────────────────────────
Once your research question is defined, say:
  "Generate a literature review for this research"
  or simply: "Start literature review"

This kicks off the automated 6-phase literature review.
```

---

## Topic 2: The Research Workflow

Present the workflow visually:

```
  ┌─────────────────┐
  │ research-design  │  Phase 0: Define your question
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │ literature-review│  Phases 1-6: Automated search & synthesis
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │   validate (A)   │  Quality gate: Is literature coverage sufficient?
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │     refine       │  Re-evaluate: proceed / narrow / pivot / expand?
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │      draft       │  Phase 7: Argument skeleton → full prose
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │   validate (B)   │  Quality gate: Citation integrity check
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │   peer-review    │  Phase 8: Three rounds of simulated review
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │   validate (C)   │  Quality gate: Change record completeness
  └────────┬────────┘
           ▼
         ✅ Done

  Side tracks (can enter at any point):
  • /claudistotle:feedback — Incorporate advisor feedback
  • /claudistotle:text-commentary — Close reading (independent)
```

Explain the key concepts:

- **Quality gates (`/claudistotle:validate`)**: These are checkpoints between phases. They catch problems early — missing literature coverage, orphan citations, incomplete revision records. You don't have to invoke them manually; the workflow suggests when to run them.
- **`/claudistotle:refine`**: After reviewing the literature, you might discover your question is too broad, too narrow, or needs a different angle. This skill helps you decide.
- **Everything saves to `reviews/[project-name]/`**: All your work lives in one directory. Every skill reads from and writes to the same project folder.
- **PROGRESS.md**: Tracks where you are. If you close Claude and come back later, it reads this file to resume.

---

## Topic 3: Literature Review Details

Explain the 6-phase automated process:

```
Phase 1: Environment check
  └─ Verifies API keys, Python packages, and project structure

Phase 2: Domain decomposition
  └─ AI planner breaks your topic into 3-5 searchable domains
  └─ Example: "extended mind thesis" →
       Domain 1: Extended mind (Clark & Chalmers)
       Domain 2: Cognitive offloading
       Domain 3: Distributed cognition
       Domain 4: Epistemic tools and technology

Phase 3: Parallel research (the big one)
  └─ For EACH domain, a specialized agent:
       • Searches Semantic Scholar, OpenAlex, CORE, arXiv
       • Searches Stanford Encyclopedia of Philosophy, Internet Encyclopedia
       • Searches PhilPapers, Notre Dame Philosophical Reviews
       • Verifies every citation via CrossRef (no fabricated references!)
       • Downloads open-access PDFs when available
  └─ Output: per-domain BibTeX files with rich annotations

Phase 4: Synthesis planning
  └─ AI designs a coherent outline from all collected literature

Phase 5: Section writing
  └─ Parallel writers produce each section of the review

Phase 6: Assembly
  └─ Merges sections, deduplicates bibliography, lints, optionally converts to DOCX
```

Key points to emphasize:
- **Every citation is verified** — the system checks each paper against CrossRef/Semantic Scholar. If it can't verify a paper exists, it flags it.
- **BibTeX files are richly annotated** — beyond standard fields, they contain summaries, relevance ratings, and source provenance in `note` and `keywords` fields.
- **Open-access PDF download** — Phase 6 tries to fetch full-text PDFs via Unpaywall for papers that are open access.

---

## Topic 4: Writing & Peer Review

### Drafting (`/claudistotle:draft`)

```
Step 1: Argument Skeleton
─────────────────────────
Before writing prose, the system builds a structured outline:
  • Each section has: CLAIM / EVIDENCE / COUNTERARGUMENT / REBUTTAL / FUNCTION
  • A logic pre-review checks for gaps (missing evidence, weak rebuttals)
  • You review and approve the skeleton before prose writing begins

Step 2: Prose Writing
─────────────────────
  • Expands the skeleton into full academic prose
  • Automatically integrates your text commentaries (if you did close readings)
  • Chicago author-date citations
  • Output: paper-draft.md
```

### Peer Review (`/claudistotle:peer-review`)

```
Three rounds, each with two AI personas:

  Round 1 — Argument Validity (Athena reviews, Calliope revises)
    Focus: logical structure, claim support, counterarguments

  Round 2 — Evidence Quality (Athena reviews, Calliope revises)
    Focus: citation accuracy, source quality, evidence gaps
    Bonus: auto-runs citation integrity check before review

  Round 3 — Writing Quality (Athena reviews, Calliope revises)
    Focus: prose clarity, academic style, transitions

After each round, you decide:
  → Accept → move to next round
  → Minor revision → Calliope fixes, move on
  → Major revision → more extensive rewrite
  → Restructure → go back to /claudistotle:draft
```

---

## Topic 5: Autopilot Mode

```
/claudistotle:autopilot — Run the pipeline with minimal intervention
```

Explain the three autonomy levels:

```
┌────────────┬────────────────────────────────────────────────────┐
│ Level      │ What happens                                       │
├────────────┼────────────────────────────────────────────────────┤
│ cautious   │ Pauses at every decision point for your approval   │
│ moderate   │ Auto-advances routine steps, pauses at key choices │
│ full       │ Runs nearly autonomously (0-1 pauses total)        │
└────────────┴────────────────────────────────────────────────────┘
```

How to set it up:
1. Create `reviews/[project-name]/autopilot-config.md` (the setup wizard can do this)
2. Set your preferred autonomy level
3. Run `/claudistotle:autopilot`

Self-healing: If a quality gate fails (e.g., literature coverage gap), autopilot automatically retries — runs a supplementary search, then re-validates. Up to 2 retries before pausing for human help.

---

## Topic 6: Text Commentary

```
/claudistotle:text-commentary — Close reading of primary source texts
```

This is an independent skill (not part of the main pipeline) for analyzing original philosophical texts:

1. Place your primary source in `reviews/[project-name]/sources/primary/`
2. Tell Claude which text to analyze
3. The skill produces a structured commentary:
   - Logical connector annotation (marks therefore, however, because, etc.)
   - Section-by-section analysis (introduction / development / conclusion)
   - Key argument extraction

The commentary files (`commentary-*.md`) are automatically picked up by `/claudistotle:draft` and integrated into your paper with footnote attribution.

---

## Topic 7: Tips & Best Practices

Present these as practical advice:

### Getting better results

- **Be specific about your topic.** "Kant's ethics" is too broad. "Kant's categorical imperative and its application to AI decision-making" gives much better results.
- **Mention your methodology** if you have one: analytic, continental, comparative, historical... This shapes how the literature review is structured.
- **Specify domains to include/exclude.** "Focus on anglophone analytic tradition" or "Include both Western and Chinese philosophy" helps the search agent target the right sources.

### Workflow tips

- **You don't have to follow the full pipeline.** Need just a literature review? Run `/claudistotle:literature-review` directly. Want to jump to drafting? Go ahead.
- **Use `/claudistotle:validate` anytime you're unsure.** It auto-detects which check to run based on your most recent work.
- **Resume interrupted work** by simply saying "continue". Claude reads PROGRESS.md to pick up where you left off.
- **Save on API costs**: Use Sonnet for most work (type `/model` in Claude Code to switch). Opus is only needed for the most complex synthesis tasks.

### Working with outputs

- **BibTeX files** can be imported directly into Zotero, Mendeley, or BibDesk.
- **Open .bib files in a text editor** — they contain much more than reference managers show (summaries, relevance scores, source notes).
- **DOCX export** works if you have pandoc installed. The literature review skill auto-generates it in Phase 6.

### Common issues

- **"API key not set"** → Run `/claudistotle:setup` to configure your `.env` file.
- **Literature review seems to miss papers** → The search covers 8 databases but cannot access paywalled content. Download important PDFs manually to `sources/secondary/`.
- **Draft doesn't use my commentary** → Make sure commentary files are named `commentary-*.md` and placed in the project root directory (not in a subfolder).

---

## Topic 8: Ready to Start

If the user wants to jump right in:

1. Check if they have a project already (look for `reviews/*/PROGRESS.md`)
2. If yes: read PROGRESS.md and tell them where they left off, suggest the next step
3. If no: ask what they want to research, then invoke `/claudistotle:research-design`

---

## Language Rule

Match the user's language throughout. All section headers, explanations, tips, and interactive prompts should be in the user's language. The ASCII art and command names stay in English (they're code), but all descriptive text adapts.

---

## Machine-Readable Exit Signal

This is an interactive help skill — no pipeline output to validate.

`<!-- STAGE_EXIT: PASS -->`
