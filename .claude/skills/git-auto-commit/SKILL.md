---
name: git-auto-commit
description: Automated git commit workflow that stages all changes, generates intelligent commit messages, and pushes to remote repository. Trigger this skill when user asks to commit code with phrases like "提交代码", "commit my code", "提交", "commit", "帮我提交", "自动提交", "auto commit", "保存代码", "save my work", "push代码", or any request to commit, save, or push changes. Use for quick iterative development workflows or when user wants to skip manual git operations and have Claude handle the full commit cycle automatically.
---

# Git Auto-Commit

## Overview

Automates the complete git commit cycle: stage all changes (respecting .gitignore), generate intelligent commit messages based on file changes, create commits, and push to remote repository.

## When to Use

Use this skill when the user asks to:
- "Auto commit my code changes"
- "Commit and push my work"
- "Save my changes to git"
- "Create a commit and push it"
- Any request implying automated git workflow without manual intervention

## Workflow

### 1. Check Git Repository Status

Verify the current directory is a git repository and check for uncommitted changes.

### 2. Stage All Changes

Stage all modified, added, and deleted files using `git add -A`. This automatically respects .gitignore rules.

### 3. Generate Commit Message

Analyze staged changes to generate a descriptive commit message:
- **Added files**: "add <filename>" or "add N files"
- **Modified files**: "update <filename>" or "update N files"
- **Deleted files**: "remove <filename>" or "remove N files"
- **Multiple changes**: Combine with commas, truncate if too long

Example messages:
- `add auth.py, update main.py`
- `update config.json`
- `add 3 files, remove 1 file`

### 4. Create Commit

Create commit with the generated message using `git commit -m "<message>"`.

### 5. Push to Remote

Push the commit to the remote repository using `git push`.

## Usage

Execute the auto-commit script directly:

```bash
python3 scripts/auto_commit.py
```

The script will:
- Display which files are being staged
- Show the generated commit message
- Report success or any errors during push

## Error Handling

- **Not a git repository**: Script exits with error message
- **No changes to commit**: Script exits gracefully with message
- **Push fails**: Commit is created locally, but push error is reported

## Script Details

The `scripts/auto_commit.py` script handles the complete workflow:

**Key features:**
- Automatic git repository detection
- Change detection using `git status --porcelain`
- Intelligent commit message generation based on file operations (add/modify/delete/rename)
- Current branch detection for targeted push
- Comprehensive error handling with informative messages

**Requirements:**
- Python 3
- Git installed and configured
- Git remote repository configured (for push operation)
