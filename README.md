# AccessPilot (local MVP)

AccessPilot scans a Swift/Kotlin codebase for common WCAG 2.2 / EN 301 549
accessibility violations, generates real code-level patches to fix them
(not a runtime overlay), and produces a VPAT-style conformance report --
all locally, with no build, no simulator, no GitHub account, and no
network calls.

This is a scoped local proof of concept for the AccessPilot product idea
described in `plan.md`: prove that an AI agent can find real accessibility
bugs in native mobile source and produce mergeable code fixes, end to end.

## What it detects

| Rule | What it flags | Criterion |
| --- | --- | --- |
| `missing-label` | `Image`/`ImageView`/`ImageButton` with no `accessibilityLabel` / `contentDescription` nearby | WCAG 2.2 SC 4.1.2 / EN 301 549 5.1.2, 5.1.3 |
| `touch-target-size` | Hardcoded `frame`/`LayoutParams` sizes under 44x44pt (iOS) or 48x48dp (Android) | WCAG 2.2 SC 2.5.8 / EN 301 549 11.8.2 |
| `contrast-ratio` | Hardcoded text/background hex color pairs with a contrast ratio below 4.5:1 | WCAG 2.2 SC 1.4.3 / EN 301 549 5.1.4 |
| `focus-order` | Interactive views hidden from the accessibility tree (`IMPORTANT_FOR_ACCESSIBILITY_NO`) while still handling clicks | WCAG 2.2 SC 2.4.3 / EN 301 549 11.4.3 |

Detection is regex/line-based on source text -- there's no real Swift/Kotlin
compiler or AST involved, and contrast is computed from hardcoded hex
literals found in source, not from a rendered screenshot. That's
intentional: it's enough to prove the concept without the investment of a
real parser.

`missing-label` and `touch-target-size` also ship an automated **fixer**
that rewrites the violating line(s) and emits the change as a `.patch`
unified diff. `contrast-ratio` and `focus-order` are detect-only -- picking
a real fixed color or reordering a real focus flow needs human judgment.

## Requirements

Python 3.9+, standard library only. `pytest` if you want to run the tests.
The `git` binary must be on your `PATH` (used to simulate the "opens a PR"
step locally).

## Running it

From the repo root:

```
python3 -m accesspilot scan samples/ --output output/
```

This will:

1. Scan every `.swift`/`.kt` file under `samples/` and collect findings.
2. Generate a `.patch` file per fixable finding under `output/patches/`.
3. Write `output/report.md` -- every finding with file:line and criterion.
4. Write `output/vpat.md` -- a VPAT-style conformance table (draft, clearly
   labeled as not a legal document).
5. Create `output/scratch-repo/` -- a git repo copied from `samples/`, with
   one branch per fix (e.g. `accesspilot/fix-missing-label-profileview`)
   already committed. This simulates "AccessPilot opened a PR" without
   touching GitHub/GitLab or needing any credentials.

Inspect the result:

```
cat output/report.md
cat output/vpat.md
ls output/patches/
git -C output/scratch-repo log --all --oneline --graph
git -C output/scratch-repo checkout accesspilot/fix-missing-label-profileview
cat output/scratch-repo/ios/ProfileView.swift   # see the applied fix
```

You can also apply a patch to a fresh copy of `samples/` yourself to see
that it's a real, mergeable diff:

```
cp -r samples /tmp/samples-check && cd /tmp/samples-check
git init -q
git apply --check /path/to/output/patches/missing-label-profileview-L6.patch
```

To regenerate just the report and VPAT without patches or git (e.g. for a
quick re-check), use:

```
python3 -m accesspilot report samples/ --output output/
```

`output/` is generated at runtime and is not checked into git.

## Running the tests

```
python3 -m pytest tests/
```

Covers:
- Each rule against a known-bad and known-good snippet.
- Each fixer: the patch it produces applies cleanly with `git apply --check`,
  and re-scanning the fixed snippet yields zero findings for that rule.
- Report/VPAT rendering.

## Seeded sample violations

`samples/` contains four small files, each seeded with a specific,
intentional violation so the tool has something real to find:

- `samples/ios/ProfileView.swift` -- missing accessibility label on an
  `Image`, and an undersized (30x30pt) touch target.
- `samples/ios/LoginButton.swift` -- low-contrast text/background color pair.
- `samples/android/MainActivity.kt` -- `ImageView` missing `contentDescription`.
- `samples/android/SettingsFragment.kt` -- a clickable view hidden from the
  accessibility tree, breaking TalkBack focus order.

## Explicitly out of scope for this local MVP

- No GitHub/GitLab API calls or real PR creation -- replaced by a local git
  branch + commit in a scratch copy of the sample repo.
- No CI hook / webhook integration -- invoked manually from the CLI.
- No real Swift/Kotlin compiler or AST -- regex/line-based heuristics only.
- No rendered-screenshot contrast measurement -- computed from hardcoded
  hex/RGB literals in source.
- No accounts, billing, hosting, or multi-user anything.
- No App Store submission or legally binding VPAT -- the generated report
  is a structural draft, clearly labeled as a demo artifact.

See `plan.md` for the full scoping rationale.
