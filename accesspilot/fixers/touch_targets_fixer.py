import re

from ..rules.touch_targets import MIN_SWIFT, MIN_KOTLIN

RULE_ID = "touch-target-size"

_SWIFT_FRAME = re.compile(
    r'(\.frame\(\s*width:\s*)(\d+(?:\.\d+)?)(\s*,\s*height:\s*)(\d+(?:\.\d+)?)(\s*\))'
)
_KOTLIN_LAYOUT = re.compile(r'(LayoutParams\(\s*)(\d+)(\s*,\s*)(\d+)(\s*\))')


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def fix(lines, finding):
    """Rewrite the undersized width/height literals in place so both
    dimensions meet the platform's minimum touch target size."""
    idx = finding.line - 1
    original = lines[idx]
    is_swift = finding.file.endswith(".swift")
    pattern = _SWIFT_FRAME if is_swift else _KOTLIN_LAYOUT
    minimum = MIN_SWIFT if is_swift else MIN_KOTLIN

    def replace(m):
        width = max(float(m.group(2)), minimum)
        height = max(float(m.group(4)), minimum)
        return f"{m.group(1)}{_fmt(width)}{m.group(3)}{_fmt(height)}{m.group(5)}"

    new_line = pattern.sub(replace, original)
    if new_line == original:
        return None

    new_lines = list(lines)
    new_lines[idx] = new_line
    return new_lines
