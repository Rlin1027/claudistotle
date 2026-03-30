"""Centralized .env loader for Claudistotle scripts.

Loads environment variables from the canonical location:
  $CLAUDISTOTLE_ENV_FILE  (set by SessionStart hook → points to $CLAUDE_PLUGIN_DATA/.env)

Falls back to find_dotenv() ONLY if the env var is not set (e.g. running scripts manually
during development). Never searches pwd blindly.
"""

import os
from pathlib import Path


def load_env() -> None:
    """Load .env from the secure, plugin-data location."""
    from dotenv import load_dotenv

    env_file = os.environ.get("CLAUDISTOTLE_ENV_FILE", "")

    if env_file and Path(env_file).is_file():
        load_dotenv(env_file, override=True)
        return

    # Fallback for manual/dev usage: try CLAUDE_PLUGIN_DATA/.env
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    if plugin_data:
        fallback = Path(plugin_data) / ".env"
        if fallback.is_file():
            load_dotenv(str(fallback), override=True)
            return

    # Last resort: default load_dotenv behavior (find nearest .env walking up)
    # This keeps scripts functional during standalone development
    load_dotenv(override=True)
