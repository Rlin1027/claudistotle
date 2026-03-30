# Claudistotle Setup Wizard

First-time configuration skill. Guides users through environment verification, API key setup, and workspace initialization.

**Triggers**: `setup`, `configure`, `initialize`, first time, API key, install

---

## Step 1: Environment Check

Run the following diagnostics and present results as a checklist:

```bash
# Check Python
python3 --version 2>/dev/null || python --version 2>/dev/null

# Check uv
uv --version 2>/dev/null

# Check jq
jq --version 2>/dev/null

# Check if plugin venv exists
ls -la "$CLAUDE_PLUGIN_DATA/.venv/bin/python" 2>/dev/null || ls -la "$CLAUDE_PLUGIN_DATA/.venv/Scripts/python" 2>/dev/null
```

Present results:

```
Environment Check
─────────────────
[✓/✗] Python 3.9+: [version]
[✓/✗] uv: [version]
[✓/✗] jq: [version]
[✓/✗] Virtual environment: [path]
[✓/✗] Critical packages: beautifulsoup4, lxml, arxiv, requests, pybtex, pymarkdownlnt, pyyaml, python-dotenv
```

**If anything fails**, provide platform-specific fix instructions:

| Tool | macOS | Linux (apt) | Windows |
|------|-------|-------------|---------|
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Same | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| jq | `brew install jq` | `sudo apt install jq` | `winget install jqlang.jq` or `choco install jq` |
| Python | `brew install python@3.12` | `sudo apt install python3` | Download from python.org |

**If environment is healthy**, proceed to Step 2.

---

## Step 2: API Key Configuration

Check for existing `.env` file at the secure, persistent location (`$CLAUDE_PLUGIN_DATA/.env`):

```bash
ENV_FILE="${CLAUDE_PLUGIN_DATA}/.env"
cat "$ENV_FILE" 2>/dev/null || echo "No .env file found at $ENV_FILE"
```

> **Security note**: API keys are stored ONLY in `$CLAUDE_PLUGIN_DATA/.env`, never in the plugin directory. This prevents accidental exposure via version control and survives plugin updates.

### Guide user through each key:

Present this overview first:

```
API Key Configuration
─────────────────────

Claudistotle uses these academic database APIs for literature search.

┌─────────────────┬──────────┬────────────────────────────────────────────┐
│ Variable        │ Required │ How to get                                 │
├─────────────────┼──────────┼────────────────────────────────────────────┤
│ BRAVE_API_KEY   │ ✦ Yes    │ https://brave.com/search/api/              │
│                 │          │ Sign up → free tier (2,000 queries/month)  │
│                 │          │ Copy API key from dashboard                │
├─────────────────┼──────────┼────────────────────────────────────────────┤
│ CROSSREF_MAILTO │ ✦ Yes    │ Just your email address — no signup needed │
│                 │          │ Used for CrossRef "polite pool" (faster)   │
├─────────────────┼──────────┼────────────────────────────────────────────┤
│ S2_API_KEY      │ ○ Rec.   │ https://www.semanticscholar.org/product/api│
│                 │          │ Request free key → 10x rate limit boost    │
├─────────────────┼──────────┼────────────────────────────────────────────┤
│ OPENALEX_EMAIL  │ ○ Rec.   │ Just your email address — no signup needed │
│                 │          │ Enables polite pool access for OpenAlex    │
├─────────────────┼──────────┼────────────────────────────────────────────┤
│ CORE_API_KEY    │ △ Opt.   │ https://core.ac.uk/services/api            │
│                 │          │ Register for free key (improves limits)    │
└─────────────────┴──────────┴────────────────────────────────────────────┘

✦ = Required  ○ = Recommended  △ = Optional
```

Then guide interactively:

1. **Ask the user for each key one by one.** Start with required keys.
2. For email-only fields (CROSSREF_MAILTO, OPENALEX_EMAIL), explain that no signup is needed — just provide an email address.
3. For API keys (BRAVE, S2, CORE), provide the signup URL and brief instructions.
4. **If a key already exists in `$CLAUDE_PLUGIN_DATA/.env`**, show a masked preview (first 4...last 4 chars) and ask if user wants to keep or replace it.

### Write the .env file

After collecting all values, write (or update) the `.env` file at `$CLAUDE_PLUGIN_DATA/.env`:

```bash
ENV_FILE="${CLAUDE_PLUGIN_DATA}/.env"
mkdir -p "${CLAUDE_PLUGIN_DATA}"
cat > "$ENV_FILE" << 'EOF'
# Claudistotle API Configuration
# Required
BRAVE_API_KEY=<collected-value>
CROSSREF_MAILTO=<collected-value>

# Recommended
S2_API_KEY=<collected-value>
OPENALEX_EMAIL=<collected-value>

# Optional
# CORE_API_KEY=<collected-value>
EOF
chmod 600 "$ENV_FILE"
```

**Rules**:
- ALWAYS write to `$CLAUDE_PLUGIN_DATA/.env`, never to the plugin directory or project root.
- If `.env` already exists, only update the keys the user provided. Preserve all other existing content.
- Never overwrite a key without asking.
- Comment out optional keys that the user skipped (with `#` prefix).
- Ensure the file ends with a newline.
- Set `chmod 600` (owner read/write only) after writing.

---

## Step 3: Verification

Run the comprehensive check script:

```bash
$PYTHON "$CLAUDE_PLUGIN_ROOT/skills/philosophy-research/scripts/check_setup.py" --verbose
```

Present the results. If any **required** checks fail, help the user fix them before proceeding.

If the `--verbose` check shows API connectivity issues:
- **Brave returns 401/403**: API key is invalid — guide user to re-check the key from their dashboard
- **Semantic Scholar returns 429**: Rate limited — the key may take a few minutes to activate
- **CrossRef is unreachable**: Network issue — check internet connection
- **Any API timeout**: Might be a firewall or proxy issue

---

## Step 4: Workspace Initialization

Ask the user:

```
Would you like to create your first research project?
```

If yes:
1. Ask for a project name (suggest kebab-case, e.g., `extended-mind-thesis`)
2. Create the directory structure:

```bash
PROJECT_NAME="<user-provided-name>"
mkdir -p "reviews/$PROJECT_NAME"

# Create initial PROGRESS.md
cat > "reviews/$PROJECT_NAME/PROGRESS.md" << EOF
# Research Progress: $PROJECT_NAME

## Current Stage
Setup complete. Ready to begin research design.

## Next Step
Run \`/claudistotle:research-design\` to define your research question and methodology.

## Milestones
- [$(date +%Y-%m-%d)] Project initialized via /claudistotle:setup
EOF
```

3. Ask if user wants to use autopilot mode. If yes, copy the config template:

```bash
cp "$CLAUDE_PLUGIN_ROOT/skills/autopilot/autopilot-config-template.md" "reviews/$PROJECT_NAME/autopilot-config.md"
```

---

## Step 5: Completion Summary

Present the final summary:

```
✅ Claudistotle Setup Complete
──────────────────────────────

Environment:
  Python: [version] ✓
  Virtual env: [path] ✓
  Packages: all installed ✓

API Keys:
  BRAVE_API_KEY: [masked] ✓
  CROSSREF_MAILTO: [value] ✓
  S2_API_KEY: [masked or "not set"]
  OPENALEX_EMAIL: [value or "not set"]

Workspace:
  Project: reviews/[name]/ ✓

Next Steps:
  1. /claudistotle:research-design — Define research question
  2. /claudistotle:literature-review — Automated literature review
  3. See GETTING_STARTED.md for the full workflow guide
```

---

## Language Rule

Match the user's language throughout the entire setup process. If the user writes in Chinese, present all prompts, instructions, and summaries in Chinese. If in English, use English. The tables and code blocks above show bilingual formats — use only the appropriate language based on the user's input.

---

## PROGRESS.md Update

After completion, update `reviews/[project-name]/PROGRESS.md` (if a project was created) to record setup completion.

---

## Machine-Readable Exit Signal

Append as the last line of output:

- All checks pass and workspace created: `<!-- STAGE_EXIT: PASS -->`
- All checks pass but no workspace created: `<!-- STAGE_EXIT: PASS:NO_WORKSPACE -->`
- Required checks failed: `<!-- STAGE_EXIT: FAIL:setup_incomplete -->`
