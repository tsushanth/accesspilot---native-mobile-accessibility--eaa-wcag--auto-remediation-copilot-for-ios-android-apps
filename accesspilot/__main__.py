import argparse
from pathlib import Path

from .fixers import FIXERS
from .gitflow import apply_fix_branch, init_scratch_repo
from .patcher import make_patch, write_patch
from .report import render_report, render_vpat
from .scanner import scan_tree

VPAT_TEMPLATE_PATH = Path(__file__).parent / "vpat_template.md"


def _slug(text: str) -> str:
    return text.lower().replace(" ", "-").replace("_", "-")


def cmd_scan(args):
    samples_root = Path(args.path).resolve()
    output_root = Path(args.output).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    findings = scan_tree(samples_root)
    findings.sort(key=lambda f: (f.file, f.line))
    print(f"Scanned {samples_root} -- {len(findings)} finding(s).")

    patches_dir = output_root / "patches"
    fix_jobs = []
    for finding in findings:
        fixer = FIXERS.get(finding.rule_id)
        if fixer is None:
            continue

        file_path = Path(finding.file)
        original_lines = file_path.read_text().splitlines()
        fixed_lines = fixer(original_lines, finding)
        if fixed_lines is None:
            continue

        rel_path = file_path.relative_to(samples_root).as_posix()
        stem = Path(rel_path).stem
        name = f"{finding.rule_id}-{_slug(stem)}-L{finding.line}"
        patch_text = make_patch(rel_path, original_lines, fixed_lines)
        patch_path = write_patch(patches_dir, name, patch_text)
        branch_name = f"accesspilot/fix-{finding.rule_id}-{_slug(stem)}"
        fix_jobs.append((finding, rel_path, patch_path, branch_name))
        print(f"  patch written: {patch_path.relative_to(output_root)}")

    report_text = render_report(findings, samples_root)
    (output_root / "report.md").write_text(report_text)

    vpat_text = render_vpat(findings, VPAT_TEMPLATE_PATH)
    (output_root / "vpat.md").write_text(vpat_text)

    scratch_dir = output_root / "scratch-repo"
    init_scratch_repo(samples_root, scratch_dir)
    for finding, rel_path, patch_path, branch_name in fix_jobs:
        commit_message = (
            f"Fix {finding.rule_id}: {finding.message}\n\n"
            f"{finding.criterion}\nFile: {rel_path}:{finding.line}"
        )
        apply_fix_branch(scratch_dir, branch_name, patch_path, commit_message)
        print(f"  branch committed: {branch_name}")

    print(
        f"\nDone. See {output_root}/report.md, {output_root}/vpat.md, "
        f"{output_root}/patches/, {output_root}/scratch-repo/"
    )


def cmd_report(args):
    samples_root = Path(args.path).resolve()
    output_root = Path(args.output).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    findings = scan_tree(samples_root)
    findings.sort(key=lambda f: (f.file, f.line))

    (output_root / "report.md").write_text(render_report(findings, samples_root))
    (output_root / "vpat.md").write_text(render_vpat(findings, VPAT_TEMPLATE_PATH))
    print(f"Report and VPAT written to {output_root}")


def build_parser():
    parser = argparse.ArgumentParser(prog="accesspilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser(
        "scan", help="Scan a source tree, generate fix patches, a report, a VPAT, and scratch-repo branches"
    )
    scan_parser.add_argument("path", help="Path to the source tree to scan (e.g. samples/)")
    scan_parser.add_argument("--output", default="output", help="Output directory (default: output/)")
    scan_parser.set_defaults(func=cmd_scan)

    report_parser = subparsers.add_parser(
        "report", help="Scan a source tree and write only report.md + vpat.md (no patches or git)"
    )
    report_parser.add_argument("path", help="Path to the source tree to scan (e.g. samples/)")
    report_parser.add_argument("--output", default="output", help="Output directory (default: output/)")
    report_parser.set_defaults(func=cmd_report)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
