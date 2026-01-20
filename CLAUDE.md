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
