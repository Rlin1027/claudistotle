#!/bin/bash
# Claudistotle Plugin — Environment Setup (SessionStart hook)
# Installs Python dependencies into a persistent venv at ${CLAUDE_PLUGIN_DATA}/.venv/
# and loads user's .env ONLY from ${CLAUDE_PLUGIN_DATA}/.env (never from pwd or plugin root).
#
# Key difference from non-plugin version:
#   - pyproject.toml lives at ${CLAUDE_PLUGIN_ROOT}/pyproject.toml
#   - venv lives at ${CLAUDE_PLUGIN_DATA}/.venv/ (persists across sessions and plugin updates)
#   - .env lives at ${CLAUDE_PLUGIN_DATA}/.env (isolated from plugin code and version control)

set -e

# Add homebrew to PATH (for uv installed via homebrew)
if [ -d "/opt/homebrew/bin" ]; then
  export PATH="/opt/homebrew/bin:$PATH"
elif [ -d "/usr/local/bin" ]; then
  export PATH="/usr/local/bin:$PATH"
fi

# ─── Validate plugin environment variables ───────────────────────────────────
if [ -z "$CLAUDE_PLUGIN_ROOT" ]; then
  echo "Environment setup failed: CLAUDE_PLUGIN_ROOT not set. Is this running as a Claude Code plugin?" >&2
  exit 2
fi

if [ -z "$CLAUDE_PLUGIN_DATA" ]; then
  echo "Environment setup failed: CLAUDE_PLUGIN_DATA not set. Is this running as a Claude Code plugin?" >&2
  exit 2
fi

if [ -z "$CLAUDE_ENV_FILE" ]; then
  echo "Environment setup failed: CLAUDE_ENV_FILE not available. This hook should only run during SessionStart events." >&2
  exit 2
fi

# ─── .env loader ─────────────────────────────────────────────────────────────
load_dotenv() {
  local env_file="$1"
  [ -f "$env_file" ] || return 0

  while IFS= read -r line || [ -n "$line" ]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local value="${BASH_REMATCH[2]}"
      if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
        value="${BASH_REMATCH[1]}"
      fi
      export "$key=$value"
    fi
  done < "$env_file"
}

# ─── Verify uv is installed ─────────────────────────────────────────────────
if ! command -v uv &> /dev/null; then
  echo "Environment setup failed: uv is not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 2
fi

# ─── Persistent venv at CLAUDE_PLUGIN_DATA ───────────────────────────────────
VENV_DIR="${CLAUDE_PLUGIN_DATA}/.venv"
PLUGIN_PYPROJECT="${CLAUDE_PLUGIN_ROOT}/pyproject.toml"

# Ensure plugin data directory exists
mkdir -p "$CLAUDE_PLUGIN_DATA"

# Capture environment state before activation
ENV_BEFORE=$(export -p | sort)

# ─── Load .env ONLY from CLAUDE_PLUGIN_DATA (secure, isolated location) ──────
ENV_FILE="${CLAUDE_PLUGIN_DATA}/.env"

# Safety check: warn if .env exists in plugin root (should never be committed)
if [ -f "${CLAUDE_PLUGIN_ROOT}/.env" ]; then
  echo "[Claudistotle] WARNING: Found .env in plugin directory (${CLAUDE_PLUGIN_ROOT}/.env)." >&2
  echo "  This is unsafe — API keys may be exposed via version control." >&2
  echo "  Move it to the secure location:  mv \"${CLAUDE_PLUGIN_ROOT}/.env\" \"${CLAUDE_PLUGIN_DATA}/.env\"" >&2
  echo "  Then delete the original." >&2
  # If secure location doesn't exist yet, auto-migrate (one-time)
  if [ ! -f "$ENV_FILE" ]; then
    cp "${CLAUDE_PLUGIN_ROOT}/.env" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo "  [Auto-migrated] Copied to ${ENV_FILE}. Please delete ${CLAUDE_PLUGIN_ROOT}/.env manually." >&2
  fi
fi

if [ -f "$ENV_FILE" ]; then
  # Restrict permissions: owner read/write only
  chmod 600 "$ENV_FILE" 2>/dev/null || true
  load_dotenv "$ENV_FILE"
else
  echo "[Claudistotle] No .env file found at ${ENV_FILE}" >&2
  echo "  Run /claudistotle:setup to configure API keys, or create it manually:" >&2
  echo "    mkdir -p \"${CLAUDE_PLUGIN_DATA}\" && cat > \"${ENV_FILE}\" << 'ENVEOF'" >&2
  echo "BRAVE_API_KEY=your-key-here" >&2
  echo "CROSSREF_MAILTO=your-email@example.com" >&2
  echo "S2_API_KEY=your-key-here" >&2
  echo "OPENALEX_EMAIL=your-email@example.com" >&2
  echo "CORE_API_KEY=your-key-here" >&2
  echo "ENVEOF" >&2
fi

# Export the canonical .env path so Python scripts can load from the same location
export CLAUDISTOTLE_ENV_FILE="$ENV_FILE"

# Sync environment: create/update venv at the persistent location
# We use uv sync with --project pointing to the plugin's pyproject.toml
# The venv is created at CLAUDE_PLUGIN_DATA for persistence across sessions
export UV_PROJECT_ENVIRONMENT="$VENV_DIR"
if ! uv sync --quiet --no-group dev --project "$CLAUDE_PLUGIN_ROOT" 2>/dev/null; then
  # Fallback: create venv manually and pip install
  if [ ! -d "$VENV_DIR" ]; then
    uv venv "$VENV_DIR" 2>/dev/null || {
      echo "Environment setup failed: Could not create virtual environment." >&2
      exit 2
    }
  fi
  # Parse dependencies from pyproject.toml and install
  VIRTUAL_ENV="$VENV_DIR" uv pip install --quiet \
    beautifulsoup4 lxml arxiv requests pybtex pymarkdownlnt pyyaml python-dotenv 2>/dev/null || {
    echo "Environment setup failed: Could not install dependencies." >&2
    exit 2
  }
fi

# Activate the virtual environment (cross-platform)
if [ -f "$VENV_DIR/Scripts/activate" ]; then
  source "$VENV_DIR/Scripts/activate"
elif [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
else
  echo "Environment setup failed: venv activation script not found at $VENV_DIR" >&2
  exit 2
fi

# Set cross-platform $PYTHON as ABSOLUTE path
if [ -f "$VENV_DIR/Scripts/python" ]; then
  export PYTHON="$VENV_DIR/Scripts/python"
else
  export PYTHON="$VENV_DIR/bin/python"
fi

# Capture environment state after activation
ENV_AFTER=$(export -p | sort)

# Persist only new/changed environment variables
comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"

# ─── Check critical packages ────────────────────────────────────────────────
MISSING_PACKAGES=""
check_package() {
  local pkg_name="$1"
  local import_name="$2"
  if ! "$PYTHON" -c "import $import_name" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES $pkg_name"
  fi
}

check_package "beautifulsoup4" "bs4"
check_package "lxml" "lxml"
check_package "arxiv" "arxiv"
check_package "requests" "requests"
check_package "pybtex" "pybtex"
check_package "pymarkdownlnt" "pymarkdown"
check_package "pyyaml" "yaml"
check_package "python-dotenv" "dotenv"

if [ -n "$MISSING_PACKAGES" ]; then
  echo "Environment setup warning: Missing packages:$MISSING_PACKAGES. Attempting install..." >&2
  VIRTUAL_ENV="$VENV_DIR" uv pip install $MISSING_PACKAGES --quiet 2>/dev/null || {
    echo "Environment setup failed: Could not install missing packages:$MISSING_PACKAGES" >&2
    exit 2
  }
fi

# Check system tools required by hooks
if ! command -v jq &> /dev/null; then
  echo "Warning: jq not installed. SubagentStop hook requires jq for BibTeX validation." >&2
  echo "Install with: brew install jq (macOS), apt install jq (Linux), or choco install jq (Windows)" >&2
fi

# ─── Context output (equivalent to CLAUDE.md) ───────────────────────────────
cat <<'CONTEXT'
[Claudistotle] Philosophy research assistant loaded.

Skill routing:
| User wants to... | Invoke |
|---|---|
| First-time setup, configure API keys | /claudistotle:setup |
| Usage guide, tutorial, how to use | /claudistotle:help |
| Choose a topic, narrow a research question | /claudistotle:research-design |
| Generate a literature review with verified citations | /claudistotle:literature-review |
| Close reading / text commentary | /claudistotle:text-commentary |
| Write or draft a paper | /claudistotle:draft |
| Simulate peer review, revise | /claudistotle:peer-review |
| Refine the research question after literature review | /claudistotle:refine |
| Validate outputs between phases | /claudistotle:validate |
| Record and process advisor/external feedback | /claudistotle:feedback |
| Run the pipeline automatically | /claudistotle:autopilot |
| Search academic databases directly | /claudistotle:philosophy-research |

Workflow: research-design → literature-review → validate(A) → refine → draft → validate(B) → peer-review → validate(C)
All outputs saved to reviews/[project-name]/. Read PROGRESS.md on startup to resume.
Language rule: Match user's language.
Priority: Accurate > Comprehensive > Rigorous > Reproducible.

Key details:
- /claudistotle:validate auto-detects mode based on recently modified files.
- /claudistotle:draft is two-step: argument skeleton → user gate → prose.
- /claudistotle:peer-review Round 2 runs citation checks internally.
- /claudistotle:feedback routes by type to appropriate skill.
- /claudistotle:literature-review auto-downloads open-access PDFs via Unpaywall.
- INDEX.md for context efficiency. PROGRESS.md auto-updated by all skills.
- Machine-readable exit signals: <!-- STAGE_EXIT: PASS|FAIL|PAUSE -->
- /claudistotle:autopilot chains stages via Task agents with configurable autonomy.
CONTEXT

echo ""
echo "Python environment ready: $("$PYTHON" --version 2>&1), venv at $VENV_DIR"
exit 0
