"""Signature/pattern rules for known prompt-injection attack classes.

Each rule is a compiled regex tied to a category and a weight in [0, 1].
Weights are hand-tuned: high-confidence phrasing gets a high weight so a
single hit can push a message into "block" on its own, while weaker/looser
patterns get lower weights so they only contribute when combined with other
signals (keeps the false-positive rate down on benign text that happens to
mention "instructions" or "system").
"""

import re
from dataclasses import dataclass

INSTRUCTION_OVERRIDE = "instruction_override"
PERSONA_ESCAPE = "persona_escape"
PROMPT_EXFILTRATION = "prompt_exfiltration"
DELIMITER_INJECTION = "delimiter_injection"
ENCODING_EVASION = "encoding_evasion"


@dataclass(frozen=True)
class Rule:
    name: str
    category: str
    pattern: re.Pattern
    weight: float
    reason: str


@dataclass(frozen=True)
class RuleMatch:
    rule_name: str
    category: str
    weight: float
    reason: str
    matched_text: str


def _rule(name: str, category: str, pattern: str, weight: float, reason: str) -> Rule:
    return Rule(name, category, re.compile(pattern, re.IGNORECASE), weight, reason)


RULES: list[Rule] = [
    # --- Instruction override ---
    _rule(
        "ignore_previous",
        INSTRUCTION_OVERRIDE,
        r"\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all)\b[^.\n]{0,40}\b(instructions?|rules?|prompt|directives?)\b",
        0.85,
        "Attempts to override prior instructions",
    ),
    _rule(
        "new_instructions",
        INSTRUCTION_OVERRIDE,
        r"\b(new|updated|real)\s+(instructions?|rules?|directives?)\s*(:|are|from now on)",
        0.6,
        "Introduces alternate instructions",
    ),
    _rule(
        "forget_previous_task",
        INSTRUCTION_OVERRIDE,
        r"\b(forget|ignore|disregard|leave behind|remove|drop)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all)\b[^.\n]{0,40}\b(tasks?|assignments?|information)\b",
        0.75,
        "Attempts to discard prior task context in favor of a new one",
    ),
    _rule(
        "new_task_follows",
        INSTRUCTION_OVERRIDE,
        r"\bnew\s+(tasks?|instructions?)\s+(now\s+)?follow\b",
        0.5,
        "Announces a new task/instruction sequence, a common override pivot",
    ),
    _rule(
        "from_now_on",
        INSTRUCTION_OVERRIDE,
        r"\bfrom now on\b.{0,60}\b(you (will|must|shall)|act as|respond)\b",
        0.45,
        "Attempts to redefine ongoing behavior",
    ),
    # --- Persona / role escape ---
    _rule(
        "dan_jailbreak",
        PERSONA_ESCAPE,
        r"\byou are now\b.{0,30}\b(dan|jailbroken|unrestricted|uncensored|evil|free)\b",
        0.9,
        "Classic DAN-style persona jailbreak",
    ),
    _rule(
        "no_rules_persona",
        PERSONA_ESCAPE,
        r"\b(pretend|imagine|act as if)\b.{0,40}\byou (have no|don't have any|lack)\b.{0,20}\b(rules?|restrictions?|guidelines?|filters?)\b",
        0.85,
        "Requests a persona without safety rules",
    ),
    _rule(
        "developer_mode",
        PERSONA_ESCAPE,
        r"\b(developer mode|god mode|sudo mode|unlocked mode|admin mode)\b",
        0.6,
        "Invokes a fictitious privileged mode",
    ),
    _rule(
        "roleplay_no_restrictions",
        PERSONA_ESCAPE,
        r"\bact as\b.{0,40}\bwithout\b.{0,20}\b(restrictions?|limitations?|filters?|censorship)\b",
        0.7,
        "Roleplay request explicitly waiving restrictions",
    ),
    # --- System-prompt exfiltration ---
    _rule(
        "repeat_system_prompt",
        PROMPT_EXFILTRATION,
        r"\b(repeat|print|reveal|show|output|display)\b.{0,25}\b(your\s+)?(system prompt|initial instructions|system message|hidden prompt)\b",
        0.85,
        "Requests disclosure of the system prompt",
    ),
    _rule(
        "what_are_your_instructions",
        PROMPT_EXFILTRATION,
        r"\bwhat (are|were)\s+your\s+(instructions|rules|guidelines|system prompt)\b(?!\s+for\b)",
        0.55,
        "Probes for hidden instructions",
    ),
    _rule(
        "verbatim_above",
        PROMPT_EXFILTRATION,
        r"\brepeat\b.{0,20}\b(everything|text|words)\b.{0,20}\babove\b",
        0.5,
        "Requests verbatim repetition of prior context",
    ),
    # --- Delimiter / injection markers ---
    _rule(
        "fake_system_tag",
        DELIMITER_INJECTION,
        r"</?(system|assistant|user)\s*>",
        0.7,
        "Fake role/delimiter tag resembling chat markup",
    ),
    _rule(
        "inst_tokens",
        DELIMITER_INJECTION,
        r"\[/?(inst|system|sys)\]",
        0.7,
        "Fake instruction-format token",
    ),
    _rule(
        "special_role_marker",
        DELIMITER_INJECTION,
        r"<\|(system|user|assistant|im_start|im_end)\|>",
        0.75,
        "Fake special role/control token",
    ),
    # --- Encoding evasion ---
    _rule(
        "base64_blob",
        ENCODING_EVASION,
        r"(?:[A-Za-z0-9+/]{4}){20,}={0,2}",
        0.4,
        "Long base64-like blob, possible payload smuggling",
    ),
    _rule(
        "decode_and_follow",
        ENCODING_EVASION,
        r"\b(decode|base64[- ]decode)\b.{0,30}\b(and (then )?(run|execute|follow|do))\b",
        0.75,
        "Instructs decoding then acting on hidden payload",
    ),
]


def run_rules(text: str) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    for rule in RULES:
        m = rule.pattern.search(text)
        if m:
            matches.append(
                RuleMatch(
                    rule_name=rule.name,
                    category=rule.category,
                    weight=rule.weight,
                    reason=rule.reason,
                    matched_text=m.group(0)[:120],
                )
            )
    return matches
