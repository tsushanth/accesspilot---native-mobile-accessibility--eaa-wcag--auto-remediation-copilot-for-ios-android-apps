import re

from ..findings import Finding

RULE_ID = "missing-label"
CRITERION = "WCAG 2.2 SC 4.1.2 Name, Role, Value / EN 301 549 5.1.2, 5.1.3"
APPLIES_TO = {".swift", ".kt"}

_SWIFT_ELEMENT = re.compile(r'\bImage\s*\(')
_SWIFT_LABEL = re.compile(r'\.accessibilityLabel\s*\(')
_KOTLIN_ELEMENT = re.compile(r'\b(?:ImageView|ImageButton)\s*\(')
_KOTLIN_LABEL = re.compile(r'contentDescription\s*=')

_WINDOW = 3


def scan(file_path, lines):
    """Flag Image/ImageView elements with no accessibilityLabel/contentDescription
    set within the next few lines (covers SwiftUI modifier chains and Kotlin
    property assignment on the following statement)."""
    is_swift = file_path.endswith(".swift")
    element_re = _SWIFT_ELEMENT if is_swift else _KOTLIN_ELEMENT
    label_re = _SWIFT_LABEL if is_swift else _KOTLIN_LABEL
    element_name = "Image" if is_swift else "ImageView/ImageButton"
    label_name = "accessibilityLabel" if is_swift else "contentDescription"

    findings = []
    for i, line in enumerate(lines):
        if not element_re.search(line):
            continue
        window = lines[i:i + _WINDOW]
        if any(label_re.search(w) for w in window):
            continue
        findings.append(Finding(
            file=file_path,
            line=i + 1,
            rule_id=RULE_ID,
            criterion=CRITERION,
            message=f"{element_name} is missing an accessibility label ({label_name}); "
                    "screen readers cannot announce its purpose.",
            snippet=line.strip(),
        ))
    return findings
