import shutil
import subprocess
from pathlib import Path


def _run_git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def init_scratch_repo(samples_dir: Path, scratch_dir: Path) -> Path:
    """Copy samples_dir into scratch_dir and turn it into a fresh git repo
    with one commit, simulating the "before" state of a real PR target repo."""
    if scratch_dir.exists():
        shutil.rmtree(scratch_dir)
    shutil.copytree(samples_dir, scratch_dir)
    _run_git(["init", "-q", "-b", "main"], cwd=scratch_dir)
    _run_git(["config", "user.email", "accesspilot@example.com"], cwd=scratch_dir)
    _run_git(["config", "user.name", "AccessPilot Bot"], cwd=scratch_dir)
    _run_git(["add", "-A"], cwd=scratch_dir)
    _run_git(["commit", "-q", "-m", "Initial import of sample app"], cwd=scratch_dir)
    return scratch_dir


def apply_fix_branch(scratch_dir: Path, branch_name: str, patch_path: Path, commit_message: str) -> None:
    """Branch off main, apply one fix patch, and commit it -- simulating the
    commit a real AccessPilot PR bot would push for review."""
    _run_git(["checkout", "-q", "main"], cwd=scratch_dir)
    _run_git(["checkout", "-q", "-b", branch_name], cwd=scratch_dir)
    _run_git(["apply", str(patch_path.resolve())], cwd=scratch_dir)
    _run_git(["add", "-A"], cwd=scratch_dir)
    _run_git(["commit", "-q", "-m", commit_message], cwd=scratch_dir)
