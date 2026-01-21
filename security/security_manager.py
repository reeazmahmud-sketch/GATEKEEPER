#!/usr/bin/env python3
"""
Security Manager - Manages security rules and desktop protection.
"""

import json
from pathlib import Path
from typing import List, Dict

# Colors
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"

# Constants
DESKTOP_PATH = Path.home() / "Desktop"
AAGIES_CONFIG_DIR = Path.home() / ".aagies"
PROJECTS_CONFIG = AAGIES_CONFIG_DIR / "projects.json"
SECURITY_CONFIG = AAGIES_CONFIG_DIR / "security.json"
AI_CONFIG = AAGIES_CONFIG_DIR / "ai_config.json"
CHECKPOINT_DIR = AAGIES_CONFIG_DIR / "checkpoints"


class SecurityManager:
    """Manages security rules and desktop protection."""
    
    def __init__(self):
        self._ensure_config_dirs()
        self.security_config = self._load_security_config()
    
    def _ensure_config_dirs(self):
        """Ensure all required directories exist."""
        AAGIES_CONFIG_DIR.mkdir(exist_ok=True)
    
    def _load_security_config(self) -> Dict:
        """Load security configuration."""
        if not SECURITY_CONFIG.exists():
            default_config = {
                "allowed_desktop_folders": ["AAGIES-Core", "Terminator-Project"],
                "strict_mode": True,
                "auto_redirect": True,
                "project_base_dirs": [str(DESKTOP_PATH)],
                "max_projects": 20,
                "folder_access_rules": {
                    "default": ["read", "write"],
                    "restricted": ["read"]
                }
            }
            with open(SECURITY_CONFIG, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        with open(SECURITY_CONFIG) as f:
            return json.load(f)
    
    def save_security_config(self):
        """Save security configuration."""
        with open(SECURITY_CONFIG, 'w') as f:
            json.dump(self.security_config, f, indent=2)
    
    def is_desktop_access_allowed(self, folder_name: str) -> bool:
        """Check if a folder can be created/accessed on desktop."""
        allowed_folders = self.security_config["allowed_desktop_folders"]
        return folder_name in allowed_folders
    
    def add_allowed_folder(self, folder_name: str):
        """Add a folder to the allowed desktop folders list."""
        if folder_name not in self.security_config["allowed_desktop_folders"]:
            self.security_config["allowed_desktop_folders"].append(folder_name)
            self.save_security_config()
            return True
        return False
    
    def remove_allowed_folder(self, folder_name: str):
        """Remove a folder from the allowed desktop folders list."""
        if folder_name in self.security_config["allowed_desktop_folders"]:
            self.security_config["allowed_desktop_folders"].remove(folder_name)
            self.save_security_config()
            return True
        return False
    
    def get_allowed_folders(self) -> List[str]:
        """Get list of allowed desktop folders."""
        return self.security_config["allowed_desktop_folders"]
    
    def enforce_desktop_safety(self, path: Path) -> bool:
        """Enforce desktop safety rules."""
        if not self.security_config["strict_mode"]:
            return True
        
        # Check if path is on desktop
        try:
            path.relative_to(DESKTOP_PATH)
            # Path is on desktop, check if it's allowed
            folder_name = path.name
            return self.is_desktop_access_allowed(folder_name)
        except ValueError:
            # Path is not on desktop, allow access
            return True
    
    def get_folder_access_rules(self, folder_type: str = "default") -> List[str]:
        """Get access rules for a folder type."""
        return self.security_config["folder_access_rules"].get(folder_type, ["read"])
