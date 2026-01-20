# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Restrictions - READ FIRST

| Rule | Description |
|------|-------------|
| **NO Desktop Files** | NEVER create files or folders directly on ~/Desktop |
| **NO Desktop Downloads** | NEVER download anything to Desktop |
| **Use Project Folders** | Create files ONLY inside: `Terminator-Project/`, `AAGIES-Core/`, or other project folders |
| **Admin Override** | Use `cd-desktop-admin` ONLY with explicit user permission |

## Project Overview

AAGIES (Autonomous Error Guard & Intelligent Self-healing) is a universal self-healing CLI tool that monitors projects, detects issues (missing files, dependencies, configs), and offers automated fixes. It also provides a "Desktop Gateway" that protects the user's Desktop by auto-redirecting terminals to this folder.

## Commands

### Installation
```bash
bash ~/Desktop/AAGIES-Core/install_aagies.sh
source ~/.zshrc
```

### Usage
```bash
aagies              # Interactive project scan - finds issues and offers fixes
aagies-start        # Auto-find entry point (start_all.sh, main.py, etc.) and run with protection
aagies <command>    # Run any command with crash protection and auto-recovery
aagies add-dir /path/to/directory     # Add project directory to config
aagies remove-dir /path/to/directory  # Remove project directory from config
```

### Development
```bash
python3 aagies.py           # Run directly without alias
python3 aagies.py --start   # Auto-start mode
python3 aagies.py <command> # Protected execution
```

## Architecture

### Core: `aagies.py`
Single-file CLI with the `AagiesDoctor` class:

- **Config**: `~/.aagies/config.json` stores registered project directories
- **Project Discovery**: Scans for Python (`requirements.txt`, `pyproject.toml`) and Node.js (`package.json`) projects
- **Diagnostics**: `run_scan()` checks git integrity, `.env` config, dependencies
- **Protected Execution**: `run_protected()` wraps commands with crash detection
- **Crash Analysis**: `analyze_crash()` parses stderr for `ModuleNotFoundError`/`FileNotFoundError` and offers fixes

### Key Patterns
- All fixes require user permission via `ask_permission()` before execution
- Issues stored as dicts: `{"type": str, "desc": str, "fix": lambda}`
- Terminal colors: `C_GREEN`, `C_RED`, `C_YELLOW`, `C_CYAN` (ANSI escape codes)

### Auto-Start Priority (`auto_start()`)
Checks for entry points in this order:
1. `./start_all.sh`
2. `./start.sh`
3. `python3 main.py`
4. `python3 app.py`
5. `python3 terminator.py`
6. `npm start`
7. `make run`

### Helper Scripts (One-off, for Terminator-Integrator project)
- `refactor_integrator.py` - Updates Package.swift and refactors ScriptController
- `fix_shared_file.py` - Creates ExecuteRequest.swift in Shared module

## MANDATORY: Logging & Date Rules

### Always Use Dates
- **Date Format:** MM/DD/YYYY (USA format) - Example: `01/21/2026`
- Add dates to ALL files you create (in header comments)
- Add "Created:" and "Last Modified:" to every file

### Always Create Log Files
After completing any significant work, create a log file at:
```
/Users/reeazmahmud/Desktop/CLI-Terminal/ClaudeCode-User/
```

### Log File Naming Convention
```
[WHAT_WAS_FIXED]_[DATE].md
```
Examples:
- `TERMINAL_ZSHRC_MODULAR_FIX_01_21_2026.md`
- `TERMINATOR_STARTUP_ERROR_FIX_01_22_2026.md`
- `CPU_MEMORY_CLEANUP_01_23_2026.md`

**DO NOT** name files generically like "SESSION_LOG" or "CHANGES"

### What to Include in Log Files
1. **Quick Summary** - What was fixed (bullet points)
2. **Problems Found** - What was wrong, explain like teaching a beginner
3. **Root Cause** - Why it happened
4. **The Fix** - Exact commands/code used, with explanations
5. **Files Created/Changed** - Full list with purposes
6. **Test Results** - Did it work? Show the test and result
7. **If It Happens Again** - Step-by-step instructions to fix it
8. **Commands Reference** - All useful commands in tables

### Write for Beginners
- Explain like teaching a 10-year-old
- Show the exact command, then explain what each part means
- Include "What this means" sections
- Use tables for quick reference
- Add troubleshooting steps

### Test Everything
After making changes:
1. Test each feature
2. Document test results (PASS/FAIL)
3. If FAIL, document the error and how you fixed it
4. Add all test results to the log file
