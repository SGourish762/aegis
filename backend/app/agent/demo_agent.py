"""A small sample agent to protect.

This is intentionally NOT backed by a real LLM — it's a scripted/stubbed
planner that pattern-matches a task description into a sequence of tool
calls from a fixed toolset. That keeps the demo free and deterministic while
still exercising the thing Aegis actually protects: a stream of proposed
agent actions that need to be checked against policy before they run.

Fixed toolset: read_file, write_file, delete_file, http_get, run_shell,
send_email.
"""

import re

from app.schemas import ProposedAction

_URL_RE = re.compile(r"https?://[^\s,]+")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_FILE_RE = re.compile(r"\bfile\s+(?:called\s+|named\s+)?([\w./\\-]+\.\w+)", re.IGNORECASE)
_COMMAND_RE = re.compile(r"\brun(?:\s+(?:the\s+)?(?:shell\s+)?command)?\s+[\"']?([^\"'.\n]+)[\"']?", re.IGNORECASE)


def _extract_path(task: str, default: str = "notes.txt") -> str:
    m = _FILE_RE.search(task)
    return m.group(1) if m else default


def propose_actions(task: str) -> list[ProposedAction]:
    """Turn a natural-language task into a list of proposed tool calls.

    Keyword-triggered rather than exhaustive NLU by design — this is a demo
    surface for the policy engine, not a production planner.
    """
    lower = task.lower()
    actions: list[ProposedAction] = []

    if "delete" in lower and "file" in lower:
        actions.append(ProposedAction(tool="delete_file", params={"path": _extract_path(task)}))

    if "read" in lower and "file" in lower:
        actions.append(ProposedAction(tool="read_file", params={"path": _extract_path(task)}))

    if "write" in lower and "file" in lower:
        actions.append(
            ProposedAction(
                tool="write_file",
                params={"path": _extract_path(task), "content": task},
            )
        )

    url_match = _URL_RE.search(task)
    if url_match or "fetch" in lower or "download" in lower or "http" in lower:
        actions.append(
            ProposedAction(
                tool="http_get",
                params={"url": url_match.group(0) if url_match else "http://example.com"},
            )
        )

    if "shell" in lower or "execute" in lower or "run command" in lower or lower.startswith("run "):
        cmd_match = _COMMAND_RE.search(task)
        actions.append(
            ProposedAction(
                tool="run_shell",
                params={"command": cmd_match.group(1).strip() if cmd_match else task},
            )
        )

    if "email" in lower or "send" in lower and _EMAIL_RE.search(task):
        email_match = _EMAIL_RE.search(task)
        actions.append(
            ProposedAction(
                tool="send_email",
                params={
                    "to": email_match.group(0) if email_match else "unknown@example.com",
                    "subject": f"Re: {task[:60]}",
                    "body": task,
                },
            )
        )

    if not actions:
        # Harmless default plan for tasks that don't match any trigger.
        actions.append(ProposedAction(tool="read_file", params={"path": "README.md"}))

    return actions
