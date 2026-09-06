from pathlib import Path

from .rules import ALL_RULES

SOURCE_EXTENSIONS = {".swift", ".kt"}


def scan_file(path: Path):
    lines = path.read_text().splitlines()
    findings = []
    for rule in ALL_RULES:
        if path.suffix not in rule.APPLIES_TO:
            continue
        findings.extend(rule.scan(str(path), lines))
    return findings


def scan_tree(root: Path):
    findings = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in SOURCE_EXTENSIONS:
            findings.extend(scan_file(path))
    return findings
