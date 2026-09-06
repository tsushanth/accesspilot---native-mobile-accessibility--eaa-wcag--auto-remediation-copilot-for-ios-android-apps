from pathlib import Path

from accesspilot.findings import Finding
from accesspilot.report import render_report, render_vpat

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "accesspilot" / "vpat_template.md"


def test_render_report_includes_file_line_and_criterion():
    findings = [Finding(
        file="ios/ProfileView.swift",
        line=6,
        rule_id="missing-label",
        criterion="WCAG 2.2 SC 4.1.2 Name, Role, Value / EN 301 549 5.1.2, 5.1.3",
        message="Image is missing a label",
        snippet="Image(...)",
    )]

    text = render_report(findings, Path("samples"))

    assert "ios/ProfileView.swift" in text
    assert "Line 6" in text
    assert "4.1.2" in text


def test_render_vpat_marks_violated_criterion_does_not_support():
    findings = [Finding(
        file="ios/ProfileView.swift",
        line=6,
        rule_id="missing-label",
        criterion="WCAG 2.2 SC 4.1.2 Name, Role, Value / EN 301 549 5.1.2, 5.1.3",
        message="m",
        snippet="s",
    )]

    text = render_vpat(findings, TEMPLATE_PATH)

    assert "Does Not Support" in text
    assert "Supports" in text


def test_render_vpat_all_supports_when_no_findings():
    text = render_vpat([], TEMPLATE_PATH)
    table_lines = [line for line in text.splitlines() if line.startswith("| WCAG")]

    assert table_lines
    assert all("| Supports |" in line for line in table_lines)
