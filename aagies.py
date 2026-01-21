#!/usr/bin/env python3
"""
AAGIES - Autonomous Error Guard & Intelligent Self-healing
=========================================================
Advanced AI Project Management & Security Gateway System

Main module that exposes all core components of the AAGIES system.
"""

import logging
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AAGIES")

# Import all core modules (after logging config to capture import-time logs)
from security import SecurityManager  # noqa: E402
from ai import AIModelManager  # noqa: E402
from checkpoints import CheckpointManager  # noqa: E402
from projects import ProjectManager  # noqa: E402
from ui import AAGIESGateway  # noqa: E402

# Colors (re-export for convenience)
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"

# Constants (re-export for convenience)
DESKTOP_PATH = Path.home() / "Desktop"
AAGIES_CONFIG_DIR = Path.home() / ".aagies"
PROJECTS_CONFIG = AAGIES_CONFIG_DIR / "projects.json"
SECURITY_CONFIG = AAGIES_CONFIG_DIR / "security.json"
AI_CONFIG = AAGIES_CONFIG_DIR / "ai_config.json"
CHECKPOINT_DIR = AAGIES_CONFIG_DIR / "checkpoints"

# Expose all classes
__all__ = [
    "SecurityManager",
    "AIModelManager",
    "CheckpointManager",
    "ProjectManager",
    "AAGIESGateway"
]


def main():
    """Main entry point with CLI support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AAGIES - Autonomous Error Guard & Intelligent Self-healing"
    )
    parser.add_argument("--start", action="store_true", help="Auto-start last active project")
    parser.add_argument("--list", action="store_true", help="List all managed projects")
    parser.add_argument("--new", action="store_true", help="Create new project with AI setup")
    parser.add_argument("--open", type=str, metavar="project", help="Open existing project")
    parser.add_argument("--ai-status", action="store_true", help="Check AI system status")
    parser.add_argument("--ai-config", action="store_true", help="Configure AI models")
    parser.add_argument("--security-check", action="store_true", help="Run security audit")
    
    args = parser.parse_args()
    
    try:
        if args.start:
            gateway = AAGIESGateway()
            last_project = gateway.project_manager.get_last_active_project()
            if last_project:
                print(f"{C_GREEN}🚀 Opening last active project: {last_project['name']}{C_RESET}")
                gateway._open_project(last_project['name'])
            else:
                print(f"{C_YELLOW}No last active project found.{C_RESET}")
        elif args.list:
            gateway = AAGIESGateway()
            gateway._list_projects()
        elif args.new:
            gateway = AAGIESGateway()
            gateway._create_new_project_flow()
        elif args.open:
            gateway = AAGIESGateway()
            gateway._open_project(args.open)
        elif args.ai_status:
            gateway = AAGIESGateway()
            gateway._check_ai_status()
        elif args.ai_config:
            gateway = AAGIESGateway()
            gateway._configure_ai_models()
        elif args.security_check:
            gateway = AAGIESGateway()
            gateway._run_security_audit()
        else:
            # Launch interactive mode
            gateway = AAGIESGateway()
            gateway.run()
            
    except KeyboardInterrupt:
        print(f"\n{C_GREEN}👋 AAGIES shutdown gracefully.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}❌ AAGIES encountered an error: {e}{C_RESET}")
        import traceback
        print(f"{C_YELLOW}Debug info: {traceback.format_exc()}{C_RESET}")


if __name__ == "__main__":
    main()
