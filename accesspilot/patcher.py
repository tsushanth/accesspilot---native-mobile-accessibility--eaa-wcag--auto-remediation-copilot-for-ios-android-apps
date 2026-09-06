import difflib
from pathlib import Path


def make_patch(rel_path: str, original_lines, fixed_lines) -> str:
    a = [line + "\n" for line in original_lines]
    b = [line + "\n" for line in fixed_lines]
    diff = difflib.unified_diff(a, b, fromfile=f"a/{rel_path}", tofile=f"b/{rel_path}")
    return "".join(diff)


def write_patch(output_dir: Path, name: str, patch_text: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}.patch"
    path.write_text(patch_text)
    return path
