# GATEKEEPER (Autonomous Error Guard & Intelligent Self-healing)
=========================================================

AAGIES is a universal self-healing and protection system designed to ensure your projects remain functional even if files are missing or systems crash.

## 🚀 Quick Start

To use AAGIES, simply use the single-word command in any project directory:

```bash
aagies-start
```
*This will automatically find your project's entry point (start_all.sh, main.py, etc.) and launch it with full protection.*

## 🛠 Features

- **Self-Healing**: Automatically detects missing files or modules.
- **Auto-Restoration**: Restores deleted files from local snapshots or Git.
- **Dependency Management**: Automatically offers to install missing Python libraries.
- **Protected Execution**: Wraps your commands to catch crashes and diagnose root causes.
- **Manual Scan**: Run `aagies` without arguments to scan your project for health issues.

## 📦 Installation

If the alias is not active, run:
```bash
bash ~/Desktop/AAGIES-Core/install_aagies.sh
source ~/.zshrc
```

## 📋 Dependencies

- Python 3.8+
- (Optional) Google Cloud SDK (for AEGIS ADK features)
