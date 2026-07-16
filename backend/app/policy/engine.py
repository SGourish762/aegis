"""Policy engine: evaluate(action) -> decision.

Deny-by-default: unknown/unlisted tools are denied. Listed tools with a
condition (e.g. domain allowlist) are denied unless the condition passes.
"""

from app.policy.policies import TOOL_POLICIES
from app.schemas import ActionResult, ProposedAction


def evaluate(action: ProposedAction) -> ActionResult:
    policy = TOOL_POLICIES.get(action.tool)

    if policy is None:
        return ActionResult(
            action=action,
            decision="deny",
            reason=f"Unknown tool '{action.tool}' is denied by default (deny-by-default policy)",
        )

    if not policy.allow:
        return ActionResult(action=action, decision="deny", reason=policy.reason)

    if policy.condition is not None and not policy.condition(action):
        return ActionResult(action=action, decision="deny", reason=policy.condition_fail_reason)

    return ActionResult(action=action, decision="allow", reason=policy.reason)


def evaluate_all(actions: list[ProposedAction]) -> list[ActionResult]:
    return [evaluate(a) for a in actions]
