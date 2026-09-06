import re

RULE_ID = "missing-label"

_SWIFT_IMAGE_NAME = re.compile(r'Image\(\s*systemName:\s*"([^"]+)"\s*\)')
_KOTLIN_VAR = re.compile(r'\b(?:val|var)\s+(\w+)\s*=\s*(?:ImageView|ImageButton)\s*\(')


def _describe(line, is_swift):
    if is_swift:
        m = _SWIFT_IMAGE_NAME.search(line)
        if m:
            return m.group(1).replace(".", " ").replace("-", " ").strip().capitalize()
        return "TODO: describe this image"
    m = _KOTLIN_VAR.search(line)
    if m:
        return m.group(1).replace("_", " ").strip().capitalize()
    return "TODO: describe this view"


def _indent_for_chain(lines, idx):
    if idx + 1 < len(lines) and lines[idx + 1].lstrip().startswith("."):
        next_line = lines[idx + 1]
        return next_line[:len(next_line) - len(next_line.lstrip())]
    original = lines[idx]
    base = original[:len(original) - len(original.lstrip())]
    return base + "    "


def fix(lines, finding):
    """Insert an accessibilityLabel (Swift) / contentDescription (Kotlin)
    assignment on the line right after the flagged element."""
    idx = finding.line - 1
    original = lines[idx]
    is_swift = finding.file.endswith(".swift")
    description = _describe(original, is_swift)
    new_lines = list(lines)

    if is_swift:
        indent = _indent_for_chain(lines, idx)
        new_lines.insert(idx + 1, f'{indent}.accessibilityLabel("{description}")')
    else:
        m = _KOTLIN_VAR.search(original)
        var_name = m.group(1) if m else "view"
        indent = original[:len(original) - len(original.lstrip())]
        new_lines.insert(idx + 1, f'{indent}{var_name}.contentDescription = "{description}"')

    return new_lines
