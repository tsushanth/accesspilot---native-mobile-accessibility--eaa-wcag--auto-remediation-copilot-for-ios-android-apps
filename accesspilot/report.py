from collections import defaultdict
from pathlib import Path

from .rules import ALL_RULES


def render_report(findings, samples_root: Path) -> str:
    lines = [
        "# AccessPilot Scan Report",
        "",
        f"Scanned `{samples_root}` -- {len(findings)} finding(s).",
        "",
    ]

    def display_path(raw_path):
        try:
            return Path(raw_path).relative_to(samples_root).as_posix()
        except ValueError:
            return raw_path

    by_file = defaultdict(list)
    for f in findings:
        by_file[display_path(f.file)].append(f)

    for file in sorted(by_file):
        lines.append(f"## {file}")
        lines.append("")
        for f in sorted(by_file[file], key=lambda x: x.line):
            lines.append(f"- **Line {f.line}** -- `{f.rule_id}` ({f.criterion})")
            lines.append(f"  {f.message}")
            lines.append("  ```")
            lines.append(f"  {f.snippet}")
            lines.append("  ```")
        lines.append("")

    return "\n".join(lines)


def render_vpat(findings, template_path: Path) -> str:
    template = template_path.read_text()

    findings_by_criterion = defaultdict(list)
    for f in findings:
        findings_by_criterion[f.criterion].append(f)

    table_lines = ["| Criterion | Conformance Level | Remarks |", "| --- | --- | --- |"]
    for rule in ALL_RULES:
        criterion = rule.CRITERION
        hits = findings_by_criterion.get(criterion, [])
        if hits:
            status = "Does Not Support"
            remark = f"{len(hits)} violation(s) found by rule `{rule.RULE_ID}`"
        else:
            status = "Supports"
            remark = "No violations detected by automated scan."
        table_lines.append(f"| {criterion} | {status} | {remark} |")

    return (
        template
        .replace("{{TABLE}}", "\n".join(table_lines))
        .replace("{{FINDING_COUNT}}", str(len(findings)))
    )
