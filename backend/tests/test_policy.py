from app.policy.engine import evaluate
from app.schemas import ProposedAction


def test_allowed_action_read_file():
    result = evaluate(ProposedAction(tool="read_file", params={"path": "notes.txt"}))
    assert result.decision == "allow"


def test_explicit_deny_delete_file():
    result = evaluate(ProposedAction(tool="delete_file", params={"path": "notes.txt"}))
    assert result.decision == "deny"
    assert "always denied" in result.reason


def test_explicit_deny_run_shell():
    result = evaluate(ProposedAction(tool="run_shell", params={"command": "rm -rf /"}))
    assert result.decision == "deny"


def test_conditional_deny_http_get_non_allowlisted_domain():
    result = evaluate(ProposedAction(tool="http_get", params={"url": "http://evil.example.net/steal"}))
    assert result.decision == "deny"
    assert "allowlist" in result.reason


def test_conditional_allow_http_get_allowlisted_domain():
    result = evaluate(ProposedAction(tool="http_get", params={"url": "https://api.github.com/repos"}))
    assert result.decision == "allow"


def test_conditional_deny_send_email_non_allowlisted_domain():
    result = evaluate(ProposedAction(tool="send_email", params={"to": "target@evil.net", "subject": "x", "body": "y"}))
    assert result.decision == "deny"


def test_conditional_allow_send_email_allowlisted_domain():
    result = evaluate(ProposedAction(tool="send_email", params={"to": "user@example.com", "subject": "x", "body": "y"}))
    assert result.decision == "allow"


def test_default_deny_unknown_action():
    result = evaluate(ProposedAction(tool="launch_missiles", params={}))
    assert result.decision == "deny"
    assert "Unknown tool" in result.reason
