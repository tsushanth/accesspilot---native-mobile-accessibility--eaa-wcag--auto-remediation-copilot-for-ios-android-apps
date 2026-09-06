import re

from ..findings import Finding

RULE_ID = "contrast-ratio"
CRITERION = "WCAG 2.2 SC 1.4.3 Contrast (Minimum) / EN 301 549 5.1.4"
APPLIES_TO = {".swift", ".kt"}

_HEX = re.compile(r'"#([0-9A-Fa-f]{6})"')
_TEXT_HINT = re.compile(r'(?i)\b(?:text|title|label|font)\w*\s*=')
_BG_HINT = re.compile(r'(?i)\b(?:background|bg)\w*\s*=')

MIN_RATIO = 4.5


def _luminance(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def channel(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = channel(r), channel(g), channel(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(hex_a, hex_b):
    la, lb = _luminance(hex_a), _luminance(hex_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def scan(file_path, lines):
    """Pair the nearest hardcoded text-color and background-color hex
    literals in the file and flag them if their WCAG contrast ratio is
    below the 4.5:1 minimum for normal text."""
    text_color = None
    bg_color = None
    for i, line in enumerate(lines):
        hex_match = _HEX.search(line)
        if not hex_match:
            continue
        if _TEXT_HINT.search(line):
            text_color = (i, hex_match.group(1))
        elif _BG_HINT.search(line):
            bg_color = (i, hex_match.group(1))

    if not (text_color and bg_color):
        return []

    ratio = _ratio(text_color[1], bg_color[1])
    if ratio >= MIN_RATIO:
        return []

    line_no = max(text_color[0], bg_color[0])
    return [Finding(
        file=file_path,
        line=line_no + 1,
        rule_id=RULE_ID,
        criterion=CRITERION,
        message=f"Text #{text_color[1]} on background #{bg_color[1]} has a contrast "
                f"ratio of {ratio:.2f}:1, below the {MIN_RATIO}:1 minimum.",
        snippet=lines[line_no].strip(),
    )]
