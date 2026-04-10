---
name: knowledge
description: Manage the philosophy research knowledge base. Ingest project results into the wiki or query existing knowledge. Use when user wants to build up or search their cross-project research knowledge.
allowed-tools: Bash, Read, Write, Grep, Glob, Edit
---

# Knowledge Base Management

## Overview

This skill manages a Karpathy-style three-layer knowledge base (`raw/` → `wiki/` → `schema`) that accumulates research knowledge across Claudistotle projects. It supports two operations:

- **Ingest**: Extract philosophers, concepts, and relationships from a completed literature review and store them as structured wiki pages
- **Query**: Search the knowledge base for existing knowledge on a topic

## Sub-Commands

### `/claudistotle:knowledge ingest [project-name]`

Ingests the results of a completed literature review into the knowledge base using a two-pass pipeline:
- **Pass 1** (deterministic): Python script extracts entities from BibTeX
- **Pass 2** (LLM): Agent enriches with relationships and philosophical analysis

#### Steps

1. **Validate project exists**:
   - Check that `reviews/[project-name]/literature-all.bib` exists
   - Check that `reviews/[project-name]/literature-review-final.md` exists
   - If either is missing, inform user: "Project '[project-name]' does not have a completed literature review. Run `/claudistotle:literature-review` first."

2. **Idempotency check**:
   - Read `knowledge-base/log.md`
   - If `[project-name]` appears in the Project column, warn user:
     ```
     ⚠️ Project "[project-name]" was already ingested on [date].
     Re-ingesting may create duplicate entries in wiki pages.
     ```
   - Use AskUserQuestion: "Continue with re-ingest?" [Yes / No]
   - If No → abort with message "Ingest cancelled."

3. **Initialize knowledge base** (if needed):
   - Check if `knowledge-base/CLAUDE.md` exists
   - If not → create the full directory structure and schema files:
     ```bash
     mkdir -p knowledge-base/raw knowledge-base/wiki/philosophers knowledge-base/wiki/concepts knowledge-base/wiki/debates knowledge-base/notes/reading-notes knowledge-base/notes/ideas
     ```
     Then create `CLAUDE.md`, `index.md`, and `log.md` with their templates.

4. **Copy raw data**:
   ```bash
   mkdir -p knowledge-base/raw/[project-name]
   cp reviews/[project-name]/literature-all.bib knowledge-base/raw/[project-name]/
   cp reviews/[project-name]/literature-review-final.md knowledge-base/raw/[project-name]/
   ```

5. **Pass 1 — Entity extraction** (deterministic):
   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/knowledge/scripts/extract_entities.py \
     knowledge-base/raw/[project-name]/literature-all.bib
   ```
   Capture the JSON output. If the script reports 0 entities, inform user and skip Pass 2.

6. **Pass 2 — LLM enrichment**: Invoke `knowledge-ingest` agent via Task tool:
   - subagent_type: "knowledge-ingest"
   - prompt: Include:
     - The entity stubs JSON from Pass 1
     - Project name
     - BibTeX path: `knowledge-base/raw/[project-name]/literature-all.bib`
     - Literature review path: `knowledge-base/raw/[project-name]/literature-review-final.md`
     - Knowledge base path: `knowledge-base/`
   - description: "Ingest: [project-name]"

7. **Report results**:
   ```
   ✅ Knowledge base updated from project "[project-name]"
   📄 Philosophers: [N] created, [M] updated
   📄 Concepts: [N] created, [M] updated
   📄 Debates: [N] created
   📚 Total wiki pages: [total]

   💡 Use /claudistotle:knowledge query [topic] to explore the knowledge base.
   ```

---

### `/claudistotle:knowledge query [topic]`

Searches the knowledge base for existing knowledge related to a topic. Returns a summary of relevant philosophers, concepts, papers, and cross-project connections.

#### Steps

1. **Check knowledge base exists**:
   - If `knowledge-base/index.md` does not exist:
     ```
     ⚠️ Knowledge base not initialized. Run /claudistotle:knowledge ingest [project-name]
     to start building your knowledge base from completed literature reviews.
     ```
     Abort.

2. **Search index**:
   - Read `knowledge-base/index.md`
   - Identify rows in Philosophers, Concepts, and Debates tables that match the query topic (case-insensitive partial match)

3. **Search wiki pages**:
   - Use Grep to search `knowledge-base/wiki/**/*.md` for the topic
   - Collect up to 5 matching file paths (most relevant first)

4. **Read and synthesize**:
   - Read each matching wiki page
   - Extract relevant sections (Core Claims, Definition, Key Perspectives, Related Papers)

5. **Present findings**:
   ```
   📖 Knowledge Base Query: "[topic]"

   ## Related Philosophers
   - [[slug|Name]] — [core claim relevant to query]
   ...

   ## Related Concepts
   - [[slug|Concept]] — [definition excerpt]
   ...

   ## Relevant Papers (from prior projects)
   - Author (Year). "Title." — CORE ARGUMENT: [summary]
   ...

   ## Cross-Project Connections
   - In project [X], this topic appeared in the context of [Y]
   ...

   📊 Sources: [N] wiki pages across [M] projects
   ```

6. **Generate Prior Knowledge Brief** (for programmatic use):
   ```markdown
   ## Prior Knowledge Brief: [topic]
   ### Known Philosophers
   - [Name] — [core claim, 1 sentence]

   ### Known Concepts
   - [Concept] — [definition, 1 sentence]

   ### Known Papers
   - [BibTeX key] — [one-line summary]

   ### Research Gaps
   - [Areas mentioned in wiki but not deeply explored]
   ```

   This brief can be passed to `/literature-review` Phase 1.5 to avoid redundant searches.

---

## Error Handling

- **Missing BibTeX/review files**: Inform user which files are missing, suggest running `/literature-review` first
- **Empty extraction**: If Pass 1 returns 0 entities, inform user that no significant entities were found (threshold: 2+ papers)
- **Agent failure**: If Pass 2 agent fails, report the error but preserve Pass 1 results. User can retry with `/claudistotle:knowledge ingest [project-name]`
- **Corrupted wiki page**: If Edit fails mid-operation, the agent logs the failure in `log.md`. User can inspect and manually fix the page.

## Machine-Readable Exit Signal

As the **last line** of output for ingest, append:
```
<!-- STAGE_EXIT: PASS -->
```

If issues occurred but ingest partially completed:
```
<!-- STAGE_EXIT: PASS:WITH_WARNINGS -->
```
