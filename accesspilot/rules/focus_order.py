import re

from ..findings import Finding

RULE_ID = "focus-order"
CRITERION = "WCAG 2.2 SC 2.4.3 Focus Order / EN 301 549 11.4.3"
APPLIES_TO = {".swift", ".kt"}

_CLICK = re.compile(r'setOnClickListener')
_HIDE = re.compile(r'importantForAccessibility\s*=\s*View\.IMPORTANT_FOR_ACCESSIBILITY_NO')

_WINDOW = 4


def scan(file_path, lines):
    """Flag interactive views that are excluded from the accessibility tree
    while still handling clicks -- they become unreachable in TalkBack's
    focus traversal order even though they're still interactive on-screen."""
    findings = []
    for i, line in enumerate(lines):
        if not _CLICK.search(line):
            continue
        window = lines[max(0, i - _WINDOW):i + _WINDOW]
        if not any(_HIDE.search(w) for w in window):
            continue
        findings.append(Finding(
            file=file_path,
            line=i + 1,
            rule_id=RULE_ID,
            criterion=CRITERION,
            message="Interactive view is excluded from the accessibility tree "
                    "(IMPORTANT_FOR_ACCESSIBILITY_NO) while still handling clicks, "
                    "making it unreachable in TalkBack's focus traversal order.",
            snippet=line.strip(),
        ))
    return findings
