"""Default policy definitions.

Deny-by-default: any tool not explicitly listed here is denied. Tools with
conditions (e.g. domain allowlists) are denied unless the condition passes.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from app.schemas import ProposedAction

ALLOWLISTED_DOMAINS = {
    "example.com",
    "api.github.com",
    "en.wikipedia.org",
}

ALLOWLISTED_EMAIL_DOMAINS = {
    "example.com",
}


@dataclass(frozen=True)
class ToolPolicy:
    tool: str
    allow: bool
    reason: str
    condition: Optional[Callable[[ProposedAction], bool]] = None
    condition_fail_reason: str = ""


def _domain_of(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "")
    return url.split("/")[0].split(":")[0].lower()


def _http_get_allowed(action: ProposedAction) -> bool:
    url = action.params.get("url", "")
    return _domain_of(url) in ALLOWLISTED_DOMAINS


def _send_email_allowed(action: ProposedAction) -> bool:
    to = action.params.get("to", "")
    domain = to.split("@")[-1].lower() if "@" in to else ""
    return domain in ALLOWLISTED_EMAIL_DOMAINS


TOOL_POLICIES: dict[str, ToolPolicy] = {
    "read_file": ToolPolicy(
        tool="read_file",
        allow=True,
        reason="read_file is allowed by default policy",
    ),
    "write_file": ToolPolicy(
        tool="write_file",
        allow=True,
        reason="write_file is allowed by default policy",
    ),
    "delete_file": ToolPolicy(
        tool="delete_file",
        allow=False,
        reason="delete_file is always denied by default policy",
    ),
    "http_get": ToolPolicy(
        tool="http_get",
        allow=True,
        reason="http_get is allowed to allowlisted domains only",
        condition=_http_get_allowed,
        condition_fail_reason=f"http_get target domain is not in the allowlist ({sorted(ALLOWLISTED_DOMAINS)})",
    ),
    "run_shell": ToolPolicy(
        tool="run_shell",
        allow=False,
        reason="run_shell is always denied by default policy",
    ),
    "send_email": ToolPolicy(
        tool="send_email",
        allow=True,
        reason="send_email is allowed to allowlisted recipient domains only",
        condition=_send_email_allowed,
        condition_fail_reason=f"send_email recipient domain is not in the allowlist ({sorted(ALLOWLISTED_EMAIL_DOMAINS)})",
    ),
}
