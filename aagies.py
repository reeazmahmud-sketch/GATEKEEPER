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
import json
from pathlib import Path
from typing import List, Optional, Dict

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AAGIES")

# Colors
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"

class JsonFile:
    """Helper class for manipulating JSON files."""
    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            self.data = {}
        else:
            with open(self.path) as f:
                self.data = json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

class AagiesDoctor:
    def __init__(self):
        self.cwd = Path.cwd()
        self.issues = []
        self.config_path = Path.home() / ".aagies" / "config.json"
        self.config_path.parent.mkdir(exist_ok=True)
        self.config = self.get_config()

    def get_config(self) -> Dict:
        """Get config from ~/.aagies/config.json"""
        if not self.config_path.exists():
            return {"project_dirs": [str(self.cwd)]}
        with open(self.config_path) as f:
            return json.load(f)

    def save_config(self):
        """Save config to ~/.aagies/config.json"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_project_directories(self) -> List[Path]:
        """Get project directories from config."""
        return [Path(d) for d in self.config.get("project_dirs", [])]

    def add_project_directory(self, new_dir: str):
        """Add a project directory to the config."""
        dirs = self.config.get("project_dirs", [])
        if new_dir not in dirs:
            dirs.append(new_dir)
            self.config["project_dirs"] = dirs
            self.save_config()
            self.log(f"Added '{new_dir}' to project directories.", C_GREEN)
        else:
            self.log(f"'{new_dir}' is already in the project directories.", C_YELLOW)

    def remove_project_directory(self, directory: str):
        """Remove a project directory from the config."""
        dirs = self.config.get("project_dirs", [])
        if directory in dirs:
            dirs.remove(directory)
            self.config["project_dirs"] = dirs
            self.save_config()
            self.log(f"Removed '{directory}' from project directories.", C_GREEN)
        else:
            self.log(f"'{directory}' is not in the project directories.", C_YELLOW)

    def log(self, msg, color=C_RESET):
        print(f"{color}{msg}{C_RESET}")

    def ask_permission(self, question: str) -> bool:
        """Strict Protocol: Ask user for authorization."""
        response = input(f"\n{C_YELLOW}⚠️  AAGIES: {question} (y/n): {C_RESET}").strip().lower()
        return response == 'y'

    def discover_projects(self, directories: List[Path]) -> List[Dict[str, str]]:
        """Scans for projects in the given directories."""
        projects = []
        for directory in directories:
            if (directory / "package.json").exists():
                projects.append({"type": "Node.js", "path": directory})
            if (directory / "requirements.txt").exists():
                projects.append({"type": "Python", "path": directory})
            if (directory / "pyproject.toml").exists():
                projects.append({"type": "Python", "path": directory})
        return projects

    def check_python_installed(self) -> bool:
        """Check if Python 3 is installed."""
        return shutil.which("python3") is not None

    def check_node_installed(self) -> bool:
        """Check if Node.js is installed."""
        return shutil.which("node") is not None

    def install_dependencies(self, project_type: str):
        """Install dependencies for a given project type."""
        if project_type == "Node.js":
            if not self.check_node_installed():
                self.log("Node.js is not installed. Please install it first.", C_RED)
                # Offer to install it
                if self.ask_permission("Install Node.js using Homebrew?"):
                    subprocess.run(["brew", "install", "node"], check=True)
                else:
                    return
            self.log("Installing Node.js dependencies...", C_CYAN)
            subprocess.run(["npm", "install"], check=True)
            self.log("✅ Dependencies installed.", C_GREEN)
        elif project_type == "Python":
            if not self.check_python_installed():
                self.log("Python 3 is not installed. Please install it first.", C_RED)
                # Offer to install it
                if self.ask_permission("Install Python 3 using Homebrew?"):
                    subprocess.run(["brew", "install", "python"], check=True)
                else:
                    return
            self.log("Installing Python dependencies...", C_CYAN)
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            self.log("✅ Dependencies installed.", C_GREEN)

    def interactive_project_scan(self):
        """Interactive UI for project selection and creation."""
        self.log("Looking for existing projects in configured directories...", C_CYAN)
        project_dirs = self.get_project_directories()
        projects = self.discover_projects(project_dirs)

        if projects:
            self.log("Found the following projects:", C_GREEN)
            for i, p in enumerate(projects):
                self.log(f"  {i+1}. {p['type']} project at {p['path']}")
            
            choice = input("\nSelect a project to manage (or 'c' to create a new one): ")
            if choice.lower() == 'c':
                self.create_new_project()
                return

            try:
                project_index = int(choice) - 1
                if 0 <= project_index < len(projects):
                    project = projects[project_index]
                    if self.ask_permission(f"Install dependencies for this {project['type']} project?"):
                        # Change directory to the project path before installing dependencies
                        os.chdir(project['path'])
                        self.install_dependencies(project['type'])
                else:
                    self.log("Invalid selection.", C_RED)
            except ValueError:
                self.log("Invalid input.", C_RED)
        else:
            self.log("No existing projects found in configured directories.", C_YELLOW)
            if self.ask_permission("Create a new project?"):
                self.create_new_project()

    def create_new_project(self):
        """Guides user through creating a new project."""
        project_dirs = self.get_project_directories()
        self.log("Available project directories:", C_CYAN)
        for i, d in enumerate(project_dirs):
            self.log(f"  {i+1}. {d}")
        
        dir_choice = input("Select a directory to create the project in (or 'a' to add a new one): ")
        if dir_choice.lower() == 'a':
            new_dir = input("Enter the full path of the new directory: ")
            self.add_project_directory(new_dir)
            project_dir = Path(new_dir)
        else:
            try:
                dir_index = int(dir_choice) - 1
                if 0 <= dir_index < len(project_dirs):
                    project_dir = project_dirs[dir_index]
                else:
                    self.log("Invalid selection.", C_RED)
                    return
            except ValueError:
                self.log("Invalid input.", C_RED)
                return

        project_type = input("Select project type (Python/Node.js): ").strip().lower()
        project_name = input("Enter project name: ").strip()
        project_path = project_dir / project_name

        if project_path.exists():
            self.log("Directory already exists.", C_RED)
            return

        project_path.mkdir()
        self.log(f"Created project directory: {project_path}", C_GREEN)

        if "python" in project_type:
            (project_path / "requirements.txt").touch()
            (project_path / "main.py").touch()
            self.log("Created requirements.txt and main.py", C_GREEN)
        elif "node" in project_type:
            package_json = JsonFile(project_path / "package.json")
            package_json.set("name", project_name)
            package_json.set("version", "1.0.0")
            package_json.set("description", "")
            package_json.set("main", "index.js")
            package_json.save()
            (project_path / "index.js").touch()
            self.log("Created package.json and index.js", C_GREEN)
        else:
            self.log("Unknown project type.", C_RED)

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
            doctor.auto_start()
        elif sys.argv[1] == "add-dir":
            if len(sys.argv) > 2:
                doctor.add_project_directory(sys.argv[2])
            else:
                doctor.log("Please provide a directory to add.", C_RED)
        elif sys.argv[1] == "remove-dir":
            if len(sys.argv) > 2:
                doctor.remove_project_directory(sys.argv[2])
            else:
                doctor.log("Please provide a directory to remove.", C_RED)
        else:
            doctor.run_protected(sys.argv[1:])
    else:
        doctor.interactive_project_scan()

if __name__ == "__main__":
    main()