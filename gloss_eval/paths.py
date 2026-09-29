"""Where the prompt and case files live.

They are read from the repository checkout rather than installed as package data, so an edit to
a prompt file is exactly what the next run sends, with no reinstall in between.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = REPO_ROOT / "prompt"
CASES_DIR = REPO_ROOT / "cases"
ENV_FILE = REPO_ROOT / ".env"

SYSTEM_PROMPT = PROMPT_DIR / "system.txt"
TOOL_SCHEMA = PROMPT_DIR / "tool_schema.json"
CLITIC_TURN = PROMPT_DIR / "clitic_turn.txt"
HABER_TURN = PROMPT_DIR / "haber_turn.txt"
EARLIER_TURN = PROMPT_DIR / "earlier_turn.txt"


def display(path: Path) -> str:
    """`path` relative to the repository when it lies inside it, else its bare file name.

    Recorded results are meant to be shared, so they never carry a local absolute path.
    """
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return resolved.relative_to(REPO_ROOT).as_posix()
    return resolved.name
