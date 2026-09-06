import subprocess
import tempfile
from pathlib import Path

from accesspilot.findings import Finding
from accesspilot.fixers import missing_labels_fixer, touch_targets_fixer
from accesspilot.patcher import make_patch
from accesspilot.rules import missing_labels, touch_targets


def _apply_check(rel_path, original_lines, fixed_lines):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(original_lines) + "\n")

        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

        patch_file = tmp_path / "fix.patch"
        patch_file.write_text(make_patch(rel_path, original_lines, fixed_lines))

        subprocess.run(["git", "apply", "--check", str(patch_file)], cwd=tmp_path, check=True)


def test_missing_label_fixer_swift_produces_clean_patch_and_resolves_finding():
    original = ['Image(systemName: "person.crop.circle")', ".resizable()"]
    finding = Finding(file="Foo.swift", line=1, rule_id="missing-label", criterion="x", message="m", snippet=original[0])

    fixed = missing_labels_fixer.fix(original, finding)

    assert fixed is not None
    _apply_check("Foo.swift", original, fixed)
    assert missing_labels.scan("Foo.swift", fixed) == []


def test_missing_label_fixer_kotlin_produces_clean_patch_and_resolves_finding():
    original = ["val avatar = ImageView(this)", "avatar.setImageResource(R.drawable.ic_avatar)"]
    finding = Finding(file="Foo.kt", line=1, rule_id="missing-label", criterion="x", message="m", snippet=original[0])

    fixed = missing_labels_fixer.fix(original, finding)

    assert fixed is not None
    _apply_check("Foo.kt", original, fixed)
    assert missing_labels.scan("Foo.kt", fixed) == []


def test_touch_target_fixer_swift_produces_clean_patch_and_resolves_finding():
    original = [".frame(width: 30, height: 30)"]
    finding = Finding(file="Foo.swift", line=1, rule_id="touch-target-size", criterion="x", message="m", snippet=original[0])

    fixed = touch_targets_fixer.fix(original, finding)

    assert fixed is not None
    _apply_check("Foo.swift", original, fixed)
    assert touch_targets.scan("Foo.swift", fixed) == []


def test_touch_target_fixer_kotlin_produces_clean_patch_and_resolves_finding():
    original = ["view.layoutParams = ViewGroup.LayoutParams(30, 30)"]
    finding = Finding(file="Foo.kt", line=1, rule_id="touch-target-size", criterion="x", message="m", snippet=original[0])

    fixed = touch_targets_fixer.fix(original, finding)

    assert fixed is not None
    _apply_check("Foo.kt", original, fixed)
    assert touch_targets.scan("Foo.kt", fixed) == []
