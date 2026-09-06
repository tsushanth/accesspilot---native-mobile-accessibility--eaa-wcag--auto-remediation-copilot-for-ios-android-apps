import re

from ..findings import Finding

RULE_ID = "touch-target-size"
CRITERION = (
    "WCAG 2.2 SC 2.5.8 Target Size (Minimum) / EN 301 549 11.8.2 "
    "(platform HIG: 44x44pt iOS, 48x48dp Android)"
)
APPLIES_TO = {".swift", ".kt"}

_SWIFT_FRAME = re.compile(r'\.frame\(\s*width:\s*(\d+(?:\.\d+)?)\s*,\s*height:\s*(\d+(?:\.\d+)?)\s*\)')
_KOTLIN_LAYOUT = re.compile(r'LayoutParams\(\s*(\d+)\s*,\s*(\d+)\s*\)')

MIN_SWIFT = 44.0
MIN_KOTLIN = 48.0


def scan(file_path, lines):
    """Flag hardcoded frame/layout-params literals smaller than the platform's
    minimum touch target size."""
    is_swift = file_path.endswith(".swift")
    pattern = _SWIFT_FRAME if is_swift else _KOTLIN_LAYOUT
    minimum = MIN_SWIFT if is_swift else MIN_KOTLIN
    unit = "pt" if is_swift else "dp"

    findings = []
    for i, line in enumerate(lines):
        m = pattern.search(line)
        if not m:
            continue
        width, height = float(m.group(1)), float(m.group(2))
        if width >= minimum and height >= minimum:
            continue
        findings.append(Finding(
            file=file_path,
            line=i + 1,
            rule_id=RULE_ID,
            criterion=CRITERION,
            message=f"Touch target is {m.group(1)}x{m.group(2)}{unit}, below the "
                    f"{int(minimum)}x{int(minimum)}{unit} minimum.",
            snippet=line.strip(),
        ))
    return findings
