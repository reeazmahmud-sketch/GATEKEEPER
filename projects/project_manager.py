#!/usr/bin/env python3
"""
Project Manager - Manages project configurations and operations.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Import local modules
from security.security_manager import SecurityManager
from ai.ai_model_manager import AIModelManager
from checkpoints.checkpoint_manager import CheckpointManager

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


class ProjectManager:
    
    def __init__(self):
        self._ensure_config_dirs()
        self.projects = self._load_projects()
        self.security_manager = SecurityManager()
        self.ai_manager = AIModelManager()
        self.checkpoint_manager = CheckpointManager(self.ai_manager)  # Pass AI manager as dependency
    
    def _ensure_config_dirs(self):
        """Ensure all required directories exist."""
        AAGIES_CONFIG_DIR.mkdir(exist_ok=True)
    
    def _load_projects(self) -> Dict:
        """Load projects configuration."""
        if not PROJECTS_CONFIG.exists():
            return {"projects": {}, "last_active": None}
        
        with open(PROJECTS_CONFIG) as f:
            return json.load(f)
    
    def save_projects(self):
        """Save projects configuration."""
        with open(PROJECTS_CONFIG, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def create_project(self, project_name: str, location: Path, ai_model: str, folder_access: List[str]):
        """Create a new project with specified configuration."""
        # Validate AI model
        if ai_model not in self.ai_manager.get_available_models():
            return {"error": "Invalid AI model selected"}
        
        # Validate folder access
        valid_access = []
        for folder in folder_access:
            if self.security_manager.is_desktop_access_allowed(folder):
                valid_access.append(folder)
        
        # Create project directory
        project_path = location / project_name
        try:
            project_path.mkdir(exist_ok=True)
            
            # Create project configuration
            project_id = str(hash(project_name + str(time.time())))
            self.projects["projects"][project_id] = {
                "name": project_name,
                "path": str(project_path),
                "ai_model": ai_model,
                "folder_access": valid_access,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Set as last active project
            self.projects["last_active"] = project_id
            self.save_projects()
            
            return {"success": True, "project_id": project_id, "path": str(project_path)}
            
        except Exception as e:
            return {"error": f"Failed to create project: {str(e)}"}
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project information."""
        return self.projects["projects"].get(project_id)
    
    def list_projects(self) -> List[Dict]:
        """List all projects."""
        return list(self.projects["projects"].values())
    
    def update_project_ai_model(self, project_id: str, ai_model: str) -> bool:
        """Update AI model for a project."""
        if project_id in self.projects["projects"] and ai_model in self.ai_manager.get_available_models():
            self.projects["projects"][project_id]["ai_model"] = ai_model
            self.projects["projects"][project_id]["last_used"] = datetime.now().isoformat()
            self.save_projects()
            return True
        return False
    
    def update_project_folder_access(self, project_id: str, folder_access: List[str]) -> bool:
        """Update folder access for a project."""
        if project_id in self.projects["projects"]:
            # Validate folder access
            valid_access = []
            for folder in folder_access:
                if self.security_manager.is_desktop_access_allowed(folder):
                    valid_access.append(folder)
            
            self.projects["projects"][project_id]["folder_access"] = valid_access
            self.projects["projects"][project_id]["last_used"] = datetime.now().isoformat()
            self.save_projects()
            return True
        return False
    
    # Helper methods to find project by name (for compatibility)
    def get_project_by_name(self, project_name: str) -> Optional[Dict]:
        """Get project information by name."""
        for project_id, project in self.projects["projects"].items():
            if project["name"] == project_name:
                return project
        return None
    
    def get_project_id_by_name(self, project_name: str) -> Optional[str]:
        """Get project ID by name."""
        for project_id, project in self.projects["projects"].items():
            if project["name"] == project_name:
                return project_id
        return None
    
    def get_last_active_project(self) -> Optional[Dict]:
        """Get the last active project."""
        last_active_id = self.projects["last_active"]
        if last_active_id:
            return self.get_project(last_active_id)
        return None
    
    def set_last_active_project(self, project_id: str) -> bool:
        """Set the last active project."""
        if project_id in self.projects["projects"]:
            self.projects["last_active"] = project_id
            self.projects["projects"][project_id]["last_used"] = datetime.now().isoformat()
            self.save_projects()
            return True
        return False
    
    # --- CHECKPOINT METHODS ---
    
    def create_project_checkpoint(self, project_id: str, description: str = "Auto-save") -> Dict:
        """Create a checkpoint for a project."""
        project = self.get_project(project_id)
        if not project:
            return {"error": "Project not found"}
        
        project_path = Path(project["path"])
        if not project_path.exists():
            return {"error": "Project path does not exist"}
        
        return self.checkpoint_manager.create_checkpoint(
            project_id=project_id,
            project_name=project["name"],
            project_path=project_path,
            description=description
        )
    
    def list_project_checkpoints(self, project_id: str) -> List[Dict]:
        """List checkpoints for a project."""
        return self.checkpoint_manager.list_checkpoints(project_id)
    
    def restore_project_from_checkpoint(self, checkpoint_id: str) -> Dict:
        """Restore a project from a checkpoint."""
        return self.checkpoint_manager.restore_from_checkpoint(checkpoint_id)
    
    def analyze_project_error(self, checkpoint_id: str, error_message: str) -> Dict:
        """Analyze a project error using checkpoint data."""
        return self.checkpoint_manager.analyze_error_with_checkpoint(checkpoint_id, error_message)
    
    def cleanup_project_checkpoints(self, project_id: str, max_checkpoints: int = 5) -> Dict:
        """Clean up old checkpoints for a project."""
        checkpoints = self.list_project_checkpoints(project_id)
        if len(checkpoints) <= max_checkpoints:
            return {"message": "No cleanup needed", "project_id": project_id, "kept": len(checkpoints), "removed": 0}
        
        # Sort by creation time (newest first)
        sorted_checkpoints = sorted(checkpoints, key=lambda x: x["created_at"], reverse=True)
        to_remove = sorted_checkpoints[max_checkpoints:]
        
        removed_count = 0
        for checkpoint in to_remove:
            try:
                checkpoint_path = self.checkpoint_manager._get_checkpoint_path(checkpoint["checkpoint_id"])
                if checkpoint_path.exists():
                    checkpoint_path.unlink()
                    removed_count += 1
            except Exception as e:
                print(f"{C_YELLOW}Warning: Could not remove checkpoint {checkpoint['checkpoint_id']}: {e}{C_RESET}")
        
        return {
            "message": "Cleanup completed",
            "project_id": project_id,
            "kept": max_checkpoints,
            "removed": removed_count
        }
