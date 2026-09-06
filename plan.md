# AccessPilot — Local MVP Scaffold Plan

## Core value being demoed

Given a folder of Swift/Kotlin source files, the tool:
1. **Detects** WCAG 2.2 / EN 301 549 violations (missing labels, undersized touch targets, contrast failures, focus-order issues) using static text/regex analysis — no build, no simulator, no running app.
2. **Auto-fixes** each violation by generating a real code-level patch (a `.patch` unified diff, applicable with `git apply`) — not a runtime overlay.
3. **Simulates the PR step** locally: creates a git branch per fix and commits the patch into a scratch copy of the sample repo, so the "opens a PR" workflow is provable end-to-end without any GitHub account, token, or network call.
4. **Generates a VPAT-style conformance report** (Markdown) mapping each finding to its EN 301 549 / WCAG 2.2 success criterion.

This is the smallest slice that proves "AI finds real accessibility bugs and produces mergeable code fixes, not a widget" — the whole thesis of the product.

## Stack

**Python 3, standard library only** (`re`, `pathlib`, `argparse`, `difflib`, `subprocess`, `dataclasses`). No pip install, no framework, no compiled AST parser.

Why Python over Node/TS or Go:
- Zero build step, zero `package.json`/`go.mod` ceremony — run with `python3 -m accesspilot ...` directly.
- `difflib` gives unified-diff patch generation for free.
- Regex-based heuristic scanning is sufficient to prove the detection concept on sample files; a real Swift/Kotlin AST parser is a post-MVP investment, not needed to demo the idea.
- `subprocess` + the system `git` binary is enough to fake the "branch + commit = PR" step with zero API/auth.

## Explicitly out of scope for this local MVP

- No GitHub/GitLab API calls, no PR creation, no auth tokens — replaced by local git branch + commit in a scratch copy of the sample repo.
- No CI hook / webhook integration — the tool is invoked manually from the CLI.
- No real Swift/Kotlin compiler or AST (SwiftSyntax, PSI, etc.) — regex/line-based heuristics on sample source files only.
- No real screen-rendering contrast measurement — contrast check computes WCAG relative-luminance ratio from hardcoded hex/RGB literals found in source, not from a rendered screenshot.
- No accounts, no billing, no multi-user anything.
- No hosting/deploy — runs entirely on local filesystem.
- No App Store submission or real VPAT legal sign-off — the generated report is a structural draft, clearly labeled as a demo artifact.

## File / directory layout

```
accesspilot/
  __main__.py            # CLI entry point (argparse: scan, report subcommands)
  scanner.py              # walks a source tree, runs each rule, collects Finding objects
  findings.py             # Finding dataclass (file, line, rule_id, WCAG/EN criterion, snippet)
  rules/
    __init__.py           # rule registry
    missing_labels.py     # missing accessibilityLabel (Swift) / contentDescription (Kotlin)
    touch_targets.py       # hardcoded frame/size literals under 44x44pt / 48x48dp
    contrast.py             # hardcoded hex/RGB color pairs -> luminance ratio check
    focus_order.py          # heuristic: accessibilityElements / traversal order mismatches
  fixers/
    __init__.py            # fixer registry, keyed by rule_id
    missing_labels_fixer.py # inserts .accessibilityLabel("...") / contentDescription = "..."
    touch_targets_fixer.py  # rewrites undersized frame/size literals to 44/48
  patcher.py               # renders a Finding+fix into a unified diff (difflib) + writes .patch file
  gitflow.py                # copies sample repo to scratch dir, creates a branch per fix, commits patch
  report.py                 # renders VPAT-style Markdown report from all findings
  vpat_template.md           # section skeleton mapped to EN 301 549 criteria

samples/
  ios/ProfileView.swift      # contains a missing-label violation + undersized touch target
  ios/LoginButton.swift      # contains a contrast failure
  android/MainActivity.kt    # contains a missing contentDescription
  android/SettingsFragment.kt # contains a focus-order violation

tests/
  test_rules.py              # each rule against a minimal known-bad/known-good snippet
  test_fixers.py              # each fixer produces a patch that applies cleanly and fixes the snippet
  test_report.py              # report generation produces expected section headers/criteria

README.md                    # one-page: what this is, how to run it, sample output
```

`output/` (report.md, vpat.md, *.patch, scratch git repo) is created at runtime and is not checked in.

## Verification

1. **Unit tests** (`pytest tests/`): for each rule, feed a hand-written snippet with a known violation and one without, assert the scanner flags exactly the bad one with the correct WCAG/EN criterion. For each fixer, assert the generated patch applies via `git apply --check` and that re-scanning the patched file yields zero findings for that rule.
2. **Manual end-to-end run-through:**
   ```
   python3 -m accesspilot scan samples/ --output output/
   ```
   Expected result, inspected by hand:
   - `output/report.md` lists every seeded violation in `samples/` with file:line and WCAG/EN 301 549 criterion.
   - `output/patches/*.patch` — one patch per fix; `git apply --check` each against a copy of `samples/` succeeds.
   - `output/vpat.md` — a VPAT-style table with each criterion marked Supports/Does Not Support based on findings.
   - `output/scratch-repo/` — a git repo (copied from `samples/`) with one branch per fix (e.g. `accesspilot/fix-missing-label-loginbutton`) already committed, provable with `git -C output/scratch-repo log --all --oneline`.
3. **Regression check:** re-running the scan against the post-fix branches in `scratch-repo/` should report zero findings for the fixed rule on the fixed file, proving the patch actually resolves the violation.
