---
name: literature-review
description: Coordinate comprehensive literature reviews on any research topic in philosophy. Manages 6-phase workflow including domain decomposition, literature search, and synthesis. Use proactively when user requests a literature review.
allowed-tools: Bash, Read, Write, Grep, Glob, Edit
---

# Literature Review Workflow

## Overview

This skill coordinates the production of a focused, insight-driven, rigorous, and accurate literature review for philosophy research proposals. The skill coordinates specialized subagents using the Task tool to execute a structured 6-phase workflow.

## Critical: Task List Management

**ALWAYS maintain a todo list and update `PROGRESS.md` to enable resume across conversations.**

Use the existing `reviews/[project-name]/PROGRESS.md` (created by `/claudistotle:research-design`) as the single source of truth for progress tracking. If it doesn't exist, create it with the template below.

**Update `PROGRESS.md` after EVERY completed phase** using this format:

```markdown
# Research Progress: [project-name]

## Current Stage
[Phase N]: [description] | Next: [next step]

## Next Step
[Specific instruction for what to do next]

## Milestones
- [date] [milestone description]

## Recently Modified Files
- [filename] ([date])

## Progress History
| Date | Previous Stage | New Stage | Action |
|------|---------------|-----------|--------|
```

`PROGRESS.md` is the only progress file in this workflow.

## Workflow Architecture

Strictly follow this workflow consisting of six distinct phases:

1. Verify environment and determine execution mode
2. Structure literature review domains (Task tool: `literature-review-planner` agent)
3. Research domains in parallel (Task tool: `domain-literature-researcher` agents)
4. Outline synthesis review across domains (Task tool: `synthesis-planner` agent)
5. Write review for each section in parallel (Task tool: `synthesis-writer` agent)
6. Assemble final review files and move intermediate files

Advance only to a subsequent phase after completing the current phase.

**Shared conventions**: See `conventions.md` for BibTeX format, UTF-8 encoding, and citation style.

## Task Tool Usage

Invoke subagents using the Task tool with these parameters:
- `subagent_type`: The agent name (e.g., "literature-review-planner")
- `prompt`: The instructions for the agent (include working directory and output filename)
- `description`: Short description (3-5 words)

**Do NOT use `run_in_background`**. Foreground execution streams status updates to the user. Parallel execution is achieved by including multiple Task calls in a single message.

Do NOT read agent definition files before invoking them. Agent definitions are for the system, not for you to read.

---

## Phase 1: Verify Environment and Determine Execution Mode

This phase validates conditions for subsequent phases to function.

1. Check if file `CLAUDE.local.md` (in the project root) contains instructions about environment setup. Follow these instructions for environment verification and all phases in the literature review workflow.

2. Run the environment verification check:
   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/philosophy-research/scripts/check_setup.py --json
   ```

3. Parse the JSON output and check the `status` field:
   - If `status` is `"ok"`: Proceed to step 5
   - If `status` is `"error"`: **ABORT IMMEDIATELY** with clear instructions

4. **If environment check fails**, inform the user:
   ```
   Environment verification failed. Cannot proceed with literature review.

   See GETTING_STARTED.md on how to set up the environment.
   ```

**Why this matters**: If the environment isn't configured, the `philosophy-research` skill scripts used by the domain researchers will fail, causing agents to fall back to unstructured web searches, undermining review quality.

5. Check for an active review pointer and determine resume point:

   **Check `reviews/.active-review`** to find the review directory:
   - If `reviews/.active-review` exists → read the path from it (e.g., `reviews/epistemic-autonomy-ai`), use that as the working directory, and check file state below
   - If `reviews/.active-review` does NOT exist → this is a fresh review, proceed to step 6
     (If you suspect an orphaned review from a previous interruption, scan `reviews/*/PROGRESS.md` to locate it.)

   **Resume logic** (check files in the review directory, in order):

   ```
   1. If literature-review-final.md exists -> Workflow complete, inform user

   2. If synthesis-section-*.md files exist:
      - Count existing section files
      - Check synthesis-outline.md for total sections expected
      - If all sections exist -> Resume at Phase 6 (assembly)
      - If some sections missing -> Resume Phase 5 for missing sections only

   3. If synthesis-outline.md exists -> Resume at Phase 5

   4. If literature-domain-*.bib files exist:
      - Count existing domain files
      - Check lit-review-plan.md for total domains expected
      - If all domains exist -> Resume at Phase 4
      - If some domains missing -> Resume Phase 3 for missing domains only

   5. If lit-review-plan.md exists -> Resume at Phase 3

   6. If PROGRESS.md exists but no other files -> Resume at Phase 2

   7. Otherwise -> Treat as fresh review (proceed to step 6)
   ```

   Output: "Resuming from Phase [N]: [phase name]..."

   **CRITICAL**: When resuming Phase 3 or Phase 5 with partial completion, only invoke agents for MISSING files. Do not re-run completed work.

6. Offer user choice of execution mode:
   - **Full Autopilot**: Execute all phases automatically without pausing for feedback between phases. Bash permissions are pre-configured in `settings.json` so no approval prompts should appear.
   - **Human-in-the-Loop**: Phase-by-phase with feedback

7. Create working directory and write the active-review pointer:
   ```bash
   mkdir -p reviews/[project-short-name]
   echo "reviews/[project-short-name]" > reviews/.active-review
   ```
   Use a short, descriptive name (e.g., `epistemic-autonomy-ai`, `mechanistic-interp`).

   **Guard — name collision**: If `reviews/[project-short-name]/literature-review-final.md` already exists, warn the user that a completed review occupies that path. Ask whether to overwrite or choose a different name (e.g., append `-2`).

   **Guard — concurrent review**: If `reviews/.active-review` already exists and points to a *different* directory, warn the user that another review appears to be in progress. Ask whether to abandon the previous review or resume it instead.

   **CRITICAL**: All subsequent file operations happen in `reviews/[project-short-name]/`. Pass this path to ALL subagents.

---

## Phase 1.5: Knowledge Base Query (Optional)

This phase checks the knowledge base for prior research relevant to the current topic. If no knowledge base exists, this phase is silently skipped.

1. Check if `knowledge-base/index.md` exists
   - If NO: skip this phase entirely (backward compatible, no warning needed)
   - If YES: proceed

2. Read `knowledge-base/index.md` to identify philosophers, concepts, and debates related to the research topic

3. Use Grep to search `knowledge-base/wiki/**/*.md` for terms from the research idea

4. Read matching wiki pages (max 5 most relevant)

5. Compile a **Prior Knowledge Brief**:
   ```markdown
   ## Prior Knowledge Brief: [research topic]
   ### Known Philosophers
   - [Name] — [core claim, 1 sentence]

   ### Known Concepts
   - [Concept] — [definition, 1 sentence]

   ### Known Papers
   - [BibTeX key] — [one-line summary]

   ### Research Gaps
   - [Areas mentioned in wiki but not deeply explored]
   ```

6. Pass the Prior Knowledge Brief as **additional context** to the `literature-review-planner` agent in Phase 2:
   - Append to the agent prompt: "Prior knowledge from previous projects: [brief]. Use this to inform domain decomposition — prioritize domains that extend or challenge existing knowledge. Known papers should be referenced but not re-searched."

7. Collect BibTeX keys from the brief as a "known papers" list. Pass to `domain-literature-researcher` agents in Phase 3 as: "Already known papers (do not re-search): [keys]"

**CRITICAL**: This phase must NOT block the workflow. If any step fails (file read error, no matches), log the error and proceed to Phase 2 as normal.

---

## Phase 2: Structure Literature Review Domains

1. Receive and review research idea from user. If you require further information, clarification or direction, ask the user. 
2. Use Task tool to invoke `literature-review-planner` agent with research idea:
   - subagent_type: "literature-review-planner"
   - prompt: Include full research idea, requirements, AND working directory path
   - Example prompt: "Research idea: [idea]. Working directory: reviews/[project-name]/. Write output to reviews/[project-name]/lit-review-plan.md"
3. Wait for `literature-review-planner` agent to structure the literature review into domains
4. Read `reviews/[project-name]/lit-review-plan.md` (generated by agent)
5. Get user feedback on plan, iterate if needed using Task tool to invoke `literature-review-planner` agent again
6. **Update PROGRESS.md**

Never advance to a next step in this phase before completing the current step.

---

## Phase 3: Research Literature in Domains

1. Identify and enumerate N domains (typically 3-8) listed in `reviews/[project-name]/lit-review-plan.md`
2. **Launch all N domain researchers in parallel** using a single message with multiple Task tool calls:
   - subagent_type: "domain-literature-researcher"
   - prompt: Include domain focus, key questions, research idea, working directory, AND output filename
   - Example prompt for domain 1: "Domain: [name]. Focus: [focus]. Key questions: [questions]. Research idea: [idea]. Working directory: reviews/[project-name]/. Write output to: reviews/[project-name]/literature-domain-1.bib"
   - description: "Domain [N]: [domain name]"
   - **CRITICAL**: Include ALL Task tool calls in a single message to enable parallel execution
3. Wait for all N agents to finish using TaskOutput (block until complete). Expected outputs: `reviews/[project-name]/literature-domain-1.bib` through `literature-domain-N.bib`. **Update PROGRESS.md after all domains complete**
4. **Collect source issues**: Note any "Source issues:" reported by domain researchers for the final summary

Never advance to Phase 4 before all domain researchers have completed.

---

## Phase 4: Outline Synthesis Review Across Domains

1. Use Task tool to invoke `synthesis-planner` agent:
   - subagent_type: "synthesis-planner"
   - prompt: Include research idea, working directory, list of BibTeX files, and original plan path
   - Example prompt: "Research idea: [idea]. Working directory: reviews/[project-name]/. BibTeX files: literature-domain-1.bib through literature-domain-N.bib. Plan: lit-review-plan.md. Write output to: reviews/[project-name]/synthesis-outline.md"
   - description: "Plan synthesis structure"
2. Planner reads BibTeX files and creates tight outline
3. Wait for agent to finish using TaskOutput. Expected output: `reviews/[project-name]/synthesis-outline.md` (800-1500 words outline for a 3000-4000 word review)
4. **Update PROGRESS.md**

Never advance to a next step in this phase before completing the current step.

---

## Phase 5: Write Review Sections in Parallel

1. Read synthesis outline `reviews/[project-name]/synthesis-outline.md` to identify sections
2. For each section: identify relevant BibTeX .bib files from the outline
3. **Launch all N synthesis writers in parallel** using a single message with multiple Task tool calls:
   - subagent_type: "synthesis-writer"
   - prompt: Include working directory, section heading (exactly as it appears in the outline),
     outline path, and relevant BibTeX files
   - **CRITICAL**: Use the outline's own section headings verbatim (e.g., "## Introduction",
     "## Section 1: The Charge"). Do NOT renumber sections linearly (1, 2, 3...) if the outline
     uses different numbering. Writers follow the outline's numbering, so mismatches cause them
     to write the wrong section or produce inconsistent headings. Output filenames should be
     numbered sequentially (synthesis-section-1.md through synthesis-section-N.md) for correct
     assembly order.
   - Example prompt: "Working directory: reviews/[project-name]/. Write the section headed
     '## Introduction' from the outline. Outline: synthesis-outline.md. Relevant BibTeX files:
     literature-domain-1.bib, literature-domain-3.bib. Output filename:
     synthesis-section-1.md"
   - description: "Write section [N]: [section name]"
   - **CRITICAL**: Include ALL Task tool calls in a single message to enable parallel execution
4. Wait for all N agents to finish. Each agent returns the **complete section content as text** (they do NOT write files themselves).
5. **Orchestrator writes each section to disk**: For each completed agent, extract the markdown content from its output and write it to the corresponding file:
   ```
   reviews/[project-name]/intermediate_files/synthesis-section-1.md
   reviews/[project-name]/intermediate_files/synthesis-section-2.md
   ...
   reviews/[project-name]/intermediate_files/synthesis-section-N.md
   ```
   Use the Write tool for each file. The agent output starts with the `##` heading — write everything from that heading onward (exclude the completion statistics block at the end if present).
6. **Update PROGRESS.md** after all sections are written to disk.

Never advance to Phase 6 before all synthesis writers have completed and all files are written.

---

## Phase 6: Assemble Final Review Files and Move Intermediate Files

**Working directory**: `reviews/[project-name]/`

> **CRITICAL: Verify `$PYTHON` before running any script.** Run `echo $PYTHON` first. If empty, set it:
> ```bash
> PYTHON="${CLAUDE_PLUGIN_DATA}/.venv/bin/python3"
> [ -f "$PYTHON" ] || PYTHON="${CLAUDE_PLUGIN_ROOT}/.venv/bin/python3"
> ```
> All scripts below MUST use `$PYTHON`, never `python3` or a hardcoded path.

**Expected outputs of this phase** (final):
- `literature-review-final.md` — complete review with YAML frontmatter
- `literature-review-final.docx` — DOCX version (if pandoc is installed)
- `literature-all.bib` — aggregated bibliography

1. Assemble final review with YAML frontmatter:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/assemble_review.py \
     "reviews/[project-name]/literature-review-final.md" \
     --title "[Research Topic]" \
     reviews/[project-name]/intermediate_files/synthesis-section-*.md
   ```

   Then use **Read** to verify section ordering and transitions.

2. **Normalize section headings**:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/normalize_headings.py \
     "reviews/[project-name]/literature-review-final.md"
   ```

   The script enforces consistent numbering: `## Section N: Title` for body sections,
   `### N.M Title` for subsections. Introduction and Conclusion remain unnumbered.
   If the script reports errors, investigate before proceeding.
   Then use **Read** to verify the heading structure looks correct.

3. **Aggregate and cross-domain deduplicate** all domain BibTeX files:

   Domain researchers work in isolation and may find the same papers. This step merges and deduplicates across all domains.

   Use **Glob** to find all `literature-domain-*.bib` files. Run the deduplication script to create `literature-all.bib`:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/dedupe_bib.py \
     "reviews/[project-name]/literature-all.bib" \
     reviews/[project-name]/literature-domain-*.bib
   ```

   The script will:
   - Keep the first occurrence of each citation key
   - Prefer entries with abstracts over entries without (abstract-aware merging)
   - Upgrade importance level if a later domain assigned higher importance
   - Remove INCOMPLETE flags when merged entry has an abstract
   - Deduplicate by DOI (catches same paper with different keys)
   - Log which duplicates were removed to console

4. Generate bibliography and append to final review:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/generate_bibliography.py \
     "reviews/[project-name]/literature-review-final.md" \
     "reviews/[project-name]/literature-all.bib"
   ```

   The script will:
   - Match cited works by surname+year proximity in the review text
   - Format references in Chicago Author-Date style from BibTeX metadata only
   - Deduplicate entries with the same DOI
   - Append (or replace) a `## References` section at the end of the review

5. Lint the final markdown file:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/lint_md.py \
     "reviews/[project-name]/literature-review-final.md"
   ```

   Fix any reported issues before proceeding. The References section is now in scope for linting — verify no false positives from italicized journal names, DOI URLs, or other bibliography formatting.

6. Clean up intermediate files (use absolute paths to avoid cwd issues):

   Move JSON API response files to `intermediate_files/json/` for archival (allows debugging while keeping review directory clean):
   ```bash
   mkdir -p "reviews/[project-name]/intermediate_files/json"
   mv "reviews/[project-name]"/*.json "reviews/[project-name]/intermediate_files/json/" 2>/dev/null || true
   ```

   Move stray API-result files from project root (agents sometimes omit the `$REVIEW_DIR/` prefix).
   Use targeted prefixes — never bare `*.json`, which could swallow unrelated files:
   ```bash
   find . -maxdepth 1 \( -name "philpapers_*.json" -o -name "pp_*.json" -o -name "s2_*.json" -o -name "openalex_*.json" -o -name "stage3_*.json" -o -name "arxiv_*.json" \) -exec mv {} "reviews/[project-name]/intermediate_files/json/" \;
   find . -maxdepth 1 -name "*.bib" -exec mv {} "reviews/[project-name]/intermediate_files/" \;
   ```

   Move remaining intermediate files and remove the active-review pointer:
   ```bash
   mv "reviews/[project-name]/lit-review-plan.md" "reviews/[project-name]/synthesis-outline.md" "reviews/[project-name]/intermediate_files/"
   mv "reviews/[project-name]/literature-domain-"*.bib "reviews/[project-name]/intermediate_files/" 2>/dev/null || true
   rm -f reviews/.active-review
   ```

   Safety net — move any remaining non-final files to `intermediate_files/`.
   **IMPORTANT**: Preserve all workspace files that other skills depend on:
   ```bash
   for f in "reviews/[project-name]"/*; do
     case "$(basename "$f")" in
       literature-review-final.md|literature-review-final.docx|literature-all.bib) ;;
       intermediate_files|sources|reports|archive) ;;
       research-proposal.md|README.md|PROGRESS.md|INDEX.md|advisor-feedback.md|autopilot-config.md) ;;
       commentary-*) ;;
       *) mv "$f" "reviews/[project-name]/intermediate_files/" 2>/dev/null || true ;;
     esac
   done
   ```

   Stray directories — agents sometimes create directories at the project root by mistake. Remove any empty directories that match the review topic:
   ```bash
   find . -maxdepth 1 -type d -empty -not -name '.*' -not -name 'reviews' -not -name 'docs' -exec rmdir {} \;
   ```

   **Note:** Do NOT use `cd` to change directories. Always use paths relative to the repo root or absolute paths to prevent working directory mismatches in subsequent commands.

**After cleanup** (final state — literature-review outputs + preserved workspace files):
```
reviews/[project-name]/
├── literature-review-final.md    # Final review (markdown)
├── literature-review-final.docx  # Final review (if pandoc available)
├── literature-all.bib            # Aggregated bibliography
├── INDEX.md                      # Project index for efficient context usage
├── research-proposal.md          # (preserved) Research proposal from /research-design
├── README.md                     # (preserved) Project documentation
├── PROGRESS.md                   # (preserved) Progress tracker
├── advisor-feedback.md           # (preserved, if exists) Feedback records
├── commentary-*.md               # (preserved, if exist) Text commentaries
├── sources/
│   ├── primary/                  # (preserved) User-provided primary texts
│   └── secondary/                # Auto-downloaded full-text PDFs + MD conversions
│       ├── [slug].pdf
│       └── [slug].md
├── reports/                      # (preserved) Quality reports from other skills
├── archive/                      # (preserved) Version history
└── intermediate_files/           # Workflow artifacts
    ├── json/                     # JSON files archived here
    │   ├── s2_results.json
    │   ├── openalex_results.json
    │   └── stage3_*.json
    ├── lit-review-plan.md
    ├── synthesis-outline.md
    ├── synthesis-section-1.md
    ├── synthesis-section-N.md
    ├── literature-domain-1.bib
    ├── literature-domain-N.bib
    └── [other intermediate files, if they exist]
```

7. **Collect full-text PDFs for secondary sources:**

   Attempt to download freely available full-text PDFs for papers in `literature-all.bib`:

   ```bash
   $PYTHON -c "
   import re, os, urllib.request, json

   bib_path = 'reviews/[project-name]/literature-all.bib'
   sources_dir = 'reviews/[project-name]/sources/secondary'
   os.makedirs(sources_dir, exist_ok=True)

   # Parse bib entries for DOIs and URLs
   with open(bib_path, encoding='utf-8') as f:
       content = f.read()

   entries = re.findall(r'@\w+\{(\w+),.*?\n\}', content, re.DOTALL)
   dois = re.findall(r'doi\s*=\s*\{(.+?)\}', content)
   urls = re.findall(r'url\s*=\s*\{(.+?)\}', content)

   downloaded = []
   failed = []

   # Try Unpaywall for open-access PDFs via DOI
   for doi in dois:
       try:
           api_url = f'https://api.unpaywall.org/v2/{doi}?email=claudistotle@example.com'
           req = urllib.request.Request(api_url, headers={'User-Agent': 'Claudistotle/1.0'})
           resp = urllib.request.urlopen(req, timeout=10)
           data = json.loads(resp.read())
           if data.get('best_oa_location', {}).get('url_for_pdf'):
               pdf_url = data['best_oa_location']['url_for_pdf']
               # Derive filename from DOI
               slug = doi.split('/')[-1].replace('.', '-')[:50]
               out_path = os.path.join(sources_dir, f'{slug}.pdf')
               if not os.path.exists(out_path):
                   urllib.request.urlretrieve(pdf_url, out_path)
                   downloaded.append(slug)
       except Exception:
           failed.append(doi)
           continue

   print(f'Downloaded: {len(downloaded)} PDFs')
   print(f'Failed/unavailable: {len(failed)} DOIs')
   if failed:
       print('FAILED_DOIS:' + '|'.join(failed))
   "
   ```

   **Convert downloaded PDFs to Markdown** (for full-text search during `/draft`):

   ```bash
   $PYTHON -c "
   import os, glob
   try:
       import pymupdf4llm
   except ImportError:
       print('pymupdf4llm not installed, skipping PDF-to-MD conversion')
       exit(0)

   sources_dir = 'reviews/[project-name]/sources/secondary'
   for pdf in glob.glob(os.path.join(sources_dir, '*.pdf')):
       md_path = pdf.rsplit('.', 1)[0] + '.md'
       if not os.path.exists(md_path):
           try:
               md = pymupdf4llm.to_markdown(pdf)
               with open(md_path, 'w', encoding='utf-8') as f:
                   f.write(md)
               print(f'Converted: {os.path.basename(pdf)} -> .md')
           except Exception as e:
               print(f'Failed to convert {os.path.basename(pdf)}: {e}')
   "
   ```

   **Report un-downloadable papers to user:**

   If any papers could not be downloaded automatically, output a clear list:

   ```
   📥 Auto-downloaded [N] full texts to sources/secondary/

   ⚠️ The following [M] papers could not be auto-downloaded (paywall or no open-access version). Please download manually:
   1. [Author (Year)] "[Title]" — DOI: [doi]
   2. ...

   After manual download, place the PDF in reviews/[project-name]/sources/secondary/.
   The system will auto-convert to Markdown on the next run.
   ```

8. **Generate project index** for efficient context usage in downstream skills:

   ```bash
   $PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/generate_index.py \
     "reviews/[project-name]/"
   ```

   This creates `reviews/[project-name]/INDEX.md` — a lightweight lookup table that lets downstream skills (`/claudistotle:validate`, `/claudistotle:refine`, `/claudistotle:draft`, etc.) understand what literature is available without loading the full `literature-all.bib` into context.

9. **Report source issues**: If any domain researchers reported source issues (API errors, partial results), output a summary:
   ```
   ⚠️ Source issues during literature search:
   - Domain [name]: [source]: [issue]
   ```
   If no issues: omit this message.

10. **Optional: Convert to DOCX** (if pandoc is installed):
   ```bash
   if command -v pandoc &> /dev/null; then
     pandoc "reviews/[project-name]/literature-review-final.md" \
       --from markdown \
       --to docx \
       --output "reviews/[project-name]/literature-review-final.docx" \
       --citeproc \
       --bibliography="reviews/[project-name]/literature-all.bib" \
       && echo "Converted to DOCX: literature-review-final.docx"
   else
     echo "Pandoc not installed, skipping DOCX conversion"
   fi
   ```

   **Important:** Use paths relative to repo root (not bare filenames). Do NOT use `&&/||` chaining for this check, as Pandoc errors would trigger the wrong fallback message.

11. **Knowledge Base Ingest** (optional):

   If `knowledge-base/CLAUDE.md` exists (knowledge base has been initialized):

   a. Check `knowledge-base/log.md` for prior ingest of this project name. If already ingested, skip.
   b. Copy raw data to knowledge base:
      ```bash
      mkdir -p knowledge-base/raw/[project-name]
      cp reviews/[project-name]/literature-all.bib knowledge-base/raw/[project-name]/
      cp reviews/[project-name]/literature-review-final.md knowledge-base/raw/[project-name]/
      ```
   c. Run entity extraction (Pass 1) against the raw copy:
      ```bash
      $PYTHON $CLAUDE_PLUGIN_ROOT/skills/knowledge/scripts/extract_entities.py \
        "knowledge-base/raw/[project-name]/literature-all.bib"
      ```
   d. Invoke `knowledge-ingest` agent via Task tool (Pass 2) with:
      - Entity stubs JSON from step c
      - Project name
      - BibTeX path: `knowledge-base/raw/[project-name]/literature-all.bib`
      - Literature review path: `knowledge-base/raw/[project-name]/literature-review-final.md`
      - Knowledge base path: `knowledge-base/`
   d. Add ingest results to the completion banner:
      ```
      📚 Knowledge base: [N] philosophers, [M] concepts stored in knowledge-base/
      ```

   If `knowledge-base/CLAUDE.md` does NOT exist, add a tip to the completion banner:
   ```
   💡 Tip: Use /claudistotle:knowledge ingest [project-name] to store research results in the knowledge base,
      enabling future projects to reuse existing knowledge. Initialize the knowledge base on first use.
   ```

   **CRITICAL**: This step is non-blocking. If ingest fails, the literature review is still complete.
   Report any ingest errors but do NOT fail the overall workflow.

---

## Error Handling

**Too few papers** (<5 per domain): Re-invoke `domain-literature-researcher` agents with broader terms

**Synthesis thin**: Request expansion from `synthesis-planner` agent, or loop back to planning `literature-review-planner` agent

**API failures**: Domain researchers report "Source issues:" in their completion message. Collect these for the final summary. Re-run domains with critical failures if needed.

---

## Quality Standards

- Academic rigor: proper citations, balanced coverage
- Relevance: clear connection to research proposal
- Comprehensiveness: no major positions missed
- **Citation integrity**: ONLY real papers found via skill scripts (structured API searches)
- **Citation format**: (Author Year) in-text, Chicago-style bibliography

---

## Status Updates

Output status updates directly as text (visible to user in real-time):

| Event | Status Format |
|-------|---------------|
| **Workflow start** | `Starting literature review: [topic]` |
| **Environment check** | `Phase 1/6: Verifying environment and determining execution mode...` |
| **Environment OK** | `Environment OK. Proceeding...` |
| **Environment FAIL** | `Environment verification failed. [details]` |
| **Phase transition** | `Phase 2/6: Structuring literature review into domains` |
| **Phase transition** | `Phase 3/6: Researching literature in [N] domains (parallel)` |
| **Phase transition** | `Phase 4/6: Outlining synthesis review across domains` |
| **Phase transition** | `Phase 5/6: Writing [N] review sections (parallel)` |
| **Agent launch (parallel)** | `Launching [N] domain researchers in parallel...` |
| **Agent completion** | `Domain [N] complete: literature-domain-[N].bib ([number of sources included] sources)` |
| **Phase completion** | `Phase [N] complete: [summary]` |
| **Assembly** | `Assembling final review with YAML frontmatter...` |
| **BibTeX aggregation** | `Aggregating BibTeX files -> literature-all.bib` |
| **Cleanup** | `Moving intermediate files -> intermediate_files/` |
| **DOCX conversion** | `Converted to DOCX: literature-review-final.docx` |
| **Workflow complete** | `Literature review complete: literature-review-final.md ([wordcount])` |
| **Source issues (if any)** | `⚠️ Source issues: [aggregated list from domain researchers]` |

---

## Stage Completion Protocol

When `/literature-review` completes successfully (Phase 6 assembly done), output the following to the user and update `PROGRESS.md`:

### User-Facing Prompt

```
═══════════════════════════════════════════════════
✅ Stage Complete: Literature Review (Phases 1-6)

📄 Outputs:
   • literature-review-final.md ([wordcount] words)
   • literature-all.bib ([N] sources)
   • INDEX.md (Research data index)
   • sources/secondary/ ([M] full-text downloads)

📍 Current Position: Phases 1-6 — /literature-review ✅

➡️ Next Step: /claudistotle:validate (Mode A — Literature Coverage Check)
   Verify literature comprehensively covers all dimensions of research question.

📥 [If any sources not downloaded] [K] sources need manual download; see list above.

💡 Tip: For close reading analysis of primary texts, use /claudistotle:text-commentary
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- **Current Status** → Stage: `/literature-review` Complete | Next: Run `/validate` Mode A
- **Completed Milestones** → Append: `- [x] Literature Review — [date] — [N] sources, [wordcount]-word synthesis`
- **Recently Modified Files** → Update file records
- **Progress History** → Append status change

---

## Machine-Readable Exit Signal

As the **last line** of output, append:

```
<!-- STAGE_EXIT: PASS -->
```

If source issues were encountered but the review still completed:

```
<!-- STAGE_EXIT: PASS:WITH_WARNINGS -->
```

This signal is used by `/autopilot` to detect stage completion and auto-advance to `/validate` Mode A.

---

## Success Metrics

- Focused, rigorous, insight-driven review (3000-8000 words)
- Resumable (PROGRESS.md enables continuity)
- Valid BibTeX files
