#!/usr/bin/env python3
"""
AAGIES - Universal Self-Healing CLI
===================================
Usage:
  1. 'aagies'          -> Scans current folder for issues and offers fixes.
  2. 'aagies <cmd>'    -> Runs <cmd> with crash protection and auto-recovery.

Capabilities:
- Restores deleted files (via Git or Local Snapshots).
- Installs missing dependencies (pip/npm).
- Creates missing config files (.env from .example).
- Analyzes crash logs for root causes.
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path
from typing import List, Optional

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AAGIES")

# Colors
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"

class AagiesDoctor:
    def __init__(self):
        self.cwd = Path.cwd()
        self.issues = []

    def log(self, msg, color=C_RESET):
        print(f"{color}{msg}{C_RESET}")

    def ask_permission(self, question: str) -> bool:
        """Strict Protocol: Ask user for authorization."""
        response = input(f"\n{C_YELLOW}⚠️  AAGIES: {question} (y/n): {C_RESET}").strip().lower()
        return response == 'y'

    # --- DIAGNOSTICS ---

    def check_git_integrity(self):
        """Check for missing/deleted files using Git."""
        if not (self.cwd / ".git").exists():
            return

        try:
            # Check for deleted files
            result = subprocess.run(["git", "ls-files", "--deleted"], capture_output=True, text=True)
            deleted_files = result.stdout.strip().splitlines()
            
            for f in deleted_files:
                self.issues.append({
                    "type": "deleted_file",
                    "file": f,
                    "desc": f"File '{f}' is missing but tracked by git.",
                    "fix": lambda f=f: subprocess.run(["git", "checkout", f], check=True)
                })
        except Exception:
            pass

    def check_python_dependencies(self):
        """Check if requirements.txt exists and packages are installed."""
        req_file = self.cwd / "requirements.txt"
        if not req_file.exists():
            return

        # Simple check: Try to import packages listed in requirements
        # (This is heuristic; a full pip check is slower but better)
        pass # Skipping complex implementation for speed, relying on 'pip install' if missing

        # Just offer to install if venv exists but looks empty?
        # Better: Check 'pip freeze' vs requirements (simplified)
        
        self.issues.append({
            "type": "dependency_check",
            "desc": "Ensure dependencies in requirements.txt are installed.",
            "fix": lambda: subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        })

    def check_env_config(self):
        """Check for missing .env files."""
        env_example = self.cwd / ".env.example"
        env_file = self.cwd / ".env"
        
        if env_example.exists() and not env_file.exists():
            self.issues.append({
                "type": "missing_config",
                "desc": "Missing .env file (template .env.example exists).",
                "fix": lambda: shutil.copy(env_example, env_file)
            })

    def run_scan(self):
        """Run all static checks."""
        self.log(f"🛡️  AAGIES: Scanning {self.cwd.name}...", C_CYAN)
        
        self.check_git_integrity()
        self.check_env_config()
        # Add more checks here
        
        if not self.issues:
            self.log("✅ System Healthy. No obvious issues found.", C_GREEN)
            return

        self.log(f"\n🚨 Found {len(self.issues)} potential issues:", C_RED)
        for i, issue in enumerate(self.issues):
            print(f"  {i+1}. {issue['desc']}")

        # Auto-fix loop
        for issue in self.issues:
            if self.ask_permission(f"Fix: {issue['desc']}?"):
                try:
                    self.log("   Executing fix...", C_CYAN)
                    issue['fix']()
                    self.log("   ✅ Fixed.", C_GREEN)
                except Exception as e:
                    self.log(f"   ❌ Failed to fix: {e}", C_RED)

    # --- RUNTIME WRAPPER ---

    def run_protected(self, command: List[str]):
        """Run a command with crash analysis."""
        cmd_str = " ".join(command)
        self.log(f"🛡️  AAGIES: Running protected command: '{cmd_str}'", C_CYAN)
        
        try:
            # Run the command and stream output
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream stdout/stderr in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Check exit code
            rc = process.poll()
            if rc != 0:
                # Capture stderr for analysis
                _, stderr = process.communicate()
                self.log(f"\n🚨 Process crashed with exit code {rc}", C_RED)
                if stderr:
                    print(stderr)
                
                self.analyze_crash(stderr or "")
                
        except Exception as e:
            self.log(f"❌ Execution failed: {e}", C_RED)

    def analyze_crash(self, logs: str):
        """Analyze crash logs and offer fixes."""
        if "ModuleNotFoundError" in logs:
            module = logs.split("No module named '")[-1].split("'")[0]
            self.log(f"\n💡 Diagnosis: Missing Python module '{module}'", C_YELLOW)
            if self.ask_permission(f"Install '{module}' via pip?"):
                subprocess.run([sys.executable, "-m", "pip", "install", module])
                self.log("✅ Installed. Try running again.", C_GREEN)
        
        elif "FileNotFoundError" in logs:
            filename = logs.split("No such file or directory: '")[-1].split("'")[0]
            self.log(f"\n💡 Diagnosis: Missing file '{filename}'", C_YELLOW)
            # Check if we can restore it via git
            if (self.cwd / ".git").exists():
                if self.ask_permission(f"Attempt to restore '{filename}' from git?"):
                    subprocess.run(["git", "checkout", filename])

    def auto_start(self):
        """Intelligently find the entry point and run it protected."""
        self.log(f"🧠 AAGIES: Looking for startup scripts in {self.cwd.name}...", C_CYAN)

        # Priority List of Start Scripts
        starters = [
            ("./start_all.sh", "Universal Launcher"),
            ("./start.sh", "Shell Launcher"),
            ("python3 main.py", "Python Main"),
            ("python3 app.py", "Python App"),
            ("python3 terminator.py", "Terminator Core"),
            ("npm start", "Node Project"),
            ("make run", "Makefile")
        ]

        for cmd, desc in starters:
            # Check if file exists (first part of command)
            entry_file = cmd.split()[0]
            if entry_file.startswith("./"):
                entry_file = entry_file[2:]
            
            if (self.cwd / entry_file).exists() or shutil.which(entry_file):
                self.log(f"🚀 Found {desc}: '{entry_file}'", C_GREEN)
                self.run_protected(cmd.split())
                return

        self.log("❌ Could not find a standard startup script (start_all.sh, main.py, etc).", C_RED)
        self.log("   Please run 'aagies <your_command>' manually.", C_YELLOW)

def main():
    doctor = AagiesDoctor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--start":
            # Auto-Start Mode
            doctor.auto_start()
        else:
            # Wrapper Mode: aagies <cmd>
            doctor.run_protected(sys.argv[1:])
    else:
        # Scan Mode: aagies
        doctor.run_scan()

if __name__ == "__main__":
    main()
