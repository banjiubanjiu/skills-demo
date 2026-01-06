#!/usr/bin/env python3
"""
Git Auto-Commit Script
Automatically stages all changes, generates a commit message, and pushes to remote.
"""

import subprocess
import sys
import os
from typing import Optional


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    try:
        result = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def has_changes() -> bool:
    """Check if there are any changes to commit."""
    result = run_command(["git", "status", "--porcelain"])
    return len(result.stdout.strip()) > 0


def get_staged_files() -> str:
    """Get list of staged files."""
    result = run_command(["git", "diff", "--cached", "--name-only"])
    return result.stdout.strip()


def get_changed_files_summary() -> str:
    """Get a summary of changed files."""
    result = run_command(["git", "diff", "--stat", "cached"])
    return result.stdout.strip()


def generate_commit_message() -> str:
    """Generate a commit message based on changes."""
    # Get the list of changed files
    result = run_command(["git", "diff", "--cached", "--name-status"])
    changes = result.stdout.strip().split('\n') if result.stdout.strip() else []

    if not changes:
        return "chore: update files"

    # Analyze changes to generate message
    added = []
    modified = []
    deleted = []
    renamed = []

    for change in changes:
        if not change:
            continue
        parts = change.split('\t')
        if len(parts) < 2:
            continue
        status, filepath = parts[0], parts[1]

        if status == 'A':
            added.append(filepath)
        elif status == 'M':
            modified.append(filepath)
        elif status == 'D':
            deleted.append(filepath)
        elif status == 'R':
            renamed.append(filepath)

    # Generate commit message based on changes
    message_parts = []

    if added:
        if len(added) == 1:
            message_parts.append(f"add {os.path.basename(added[0])}")
        else:
            message_parts.append(f"add {len(added)} files")

    if modified:
        if len(modified) == 1:
            message_parts.append(f"update {os.path.basename(modified[0])}")
        else:
            message_parts.append(f"update {len(modified)} files")

    if deleted:
        if len(deleted) == 1:
            message_parts.append(f"remove {os.path.basename(deleted[0])}")
        else:
            message_parts.append(f"remove {len(deleted)} files")

    if renamed:
        message_parts.append(f"rename {len(renamed)} file(s)")

    if not message_parts:
        return "chore: update repository"

    # Join parts and limit length
    message = ", ".join(message_parts)
    if len(message) > 72:
        message = message[:69] + "..."

    return message


def auto_commit() -> None:
    """Main function to auto-commit and push changes."""
    # Check if we're in a git repo
    if not is_git_repo():
        print("Error: Not a git repository")
        sys.exit(1)

    # Check if there are changes
    if not has_changes():
        print("No changes to commit")
        sys.exit(0)

    # Stage all changes
    print("Staging changes...")
    run_command(["git", "add", "-A"])

    # Check again if there are staged changes
    staged_files = get_staged_files()
    if not staged_files:
        print("No changes to commit after staging")
        sys.exit(0)

    print(f"Staged files:\n{staged_files}")

    # Generate commit message
    commit_msg = generate_commit_message()
    print(f"\nGenerated commit message: {commit_msg}")

    # Create commit
    print("\nCreating commit...")
    run_command(["git", "commit", "-m", commit_msg])

    # Get current branch
    branch = get_current_branch()
    if not branch:
        print("Warning: Could not determine current branch")
        sys.exit(0)

    # Push to remote
    print(f"\nPushing to remote (branch: {branch})...")
    try:
        run_command(["git", "push"])
        print("✓ Successfully pushed to remote")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Push failed with error: {e}")
        print("Commit was created locally but not pushed")
        sys.exit(1)


if __name__ == "__main__":
    auto_commit()
