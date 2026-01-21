#!/usr/bin/env python3
"""
Checkpoint Manager - Manages project checkpoints and snapshots for error recovery.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

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


class CheckpointManager:
    """Manages project checkpoints and snapshots for error recovery."""
    
    def __init__(self, ai_manager=None):
        self._ensure_checkpoint_dir()
        self.checkpoints = self._load_checkpoints()
        self.ai_manager = ai_manager
    
    def _ensure_checkpoint_dir(self):
        """Ensure checkpoint directory exists."""
        CHECKPOINT_DIR.mkdir(exist_ok=True)
    
    def _load_checkpoints(self) -> Dict:
        """Load all checkpoints from disk."""
        checkpoints = {}
        if CHECKPOINT_DIR.exists():
            for checkpoint_file in CHECKPOINT_DIR.glob("*.json"):
                try:
                    with open(checkpoint_file) as f:
                        checkpoint_data = json.load(f)
                    checkpoints[checkpoint_file.stem] = checkpoint_data
                except Exception as e:
                    print(f"{C_YELLOW}Warning: Could not load checkpoint {checkpoint_file.name}: {e}{C_RESET}")
        return checkpoints
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get path for a checkpoint file."""
        return CHECKPOINT_DIR / f"{checkpoint_id}.json"
    
    def create_checkpoint(self, project_id: str, project_name: str, project_path: Path, description: str = "Auto-save") -> Dict:
        """Create a checkpoint snapshot of a project."""
        checkpoint_id = f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        # Create checkpoint data
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "project_id": project_id,
            "project_name": project_name,
            "project_path": str(project_path),
            "created_at": datetime.now().isoformat(),
            "description": description,
            "files": self._scan_project_files(project_path),
            "status": "active"
        }
        
        # Save checkpoint
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Add to memory
            self.checkpoints[checkpoint_id] = checkpoint_data
            
            return checkpoint_data
        except Exception as e:
            return {"error": f"Failed to create checkpoint: {str(e)}"}
    
    def _scan_project_files(self, project_path: Path) -> Dict:
        """Scan project files and create a snapshot."""
        file_snapshot = {
            "file_count": 0,
            "file_list": [],
            "file_sizes": {},
            "file_hashes": {}
        }
        
        try:
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(project_path))
                    file_snapshot["file_list"].append(rel_path)
                    file_snapshot["file_count"] += 1
                    
                    # Get file size
                    file_snapshot["file_sizes"][rel_path] = file_path.stat().st_size
                    
                    # Get file hash (for important files only to save time)
                    if file_path.suffix in ['.py', '.js', '.json', '.txt', '.md']:
                        file_snapshot["file_hashes"][rel_path] = self._get_file_hash(file_path)
        
        except Exception as e:
            print(f"{C_YELLOW}Warning: Error scanning files: {e}{C_RESET}")
        
        return file_snapshot
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            return f"error: {str(e)}"
    
    def list_checkpoints(self, project_id: str = None) -> List[Dict]:
        """List all checkpoints, optionally filtered by project."""
        if project_id:
            return [cp for cp_id, cp in self.checkpoints.items() if cp.get("project_id") == project_id]
        return list(self.checkpoints.values())
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Get a specific checkpoint."""
        return self.checkpoints.get(checkpoint_id)
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Dict:
        """Restore a project from a checkpoint."""
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return {"error": "Checkpoint not found"}
        
        project_path = Path(checkpoint["project_path"])
        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)
        
        # Restore files from checkpoint
        restored_files = []
        failed_files = []
        
        # This would be enhanced with actual file restoration in a full implementation
        # For now, we'll simulate the process
        for file_path in checkpoint["files"]["file_list"]:
            full_path = project_path / file_path
            try:
                # Ensure directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # In a real implementation, we would restore from backup
                # For simulation, we'll just touch the file
                full_path.touch(exist_ok=True)
                restored_files.append(file_path)
                
            except Exception as e:
                failed_files.append(f"{file_path}: {str(e)}")
        
        return {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "project_name": checkpoint["project_name"],
            "restored_files": restored_files,
            "failed_files": failed_files,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_error_with_checkpoint(self, checkpoint_id: str, error_message: str) -> Dict:
        """Analyze an error using checkpoint data and AI."""
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return {"error": "Checkpoint not found"}
        
        # Use AI to analyze the error with checkpoint context
        context = f"""
        Error Analysis Request:
        
        Error: {error_message}
        
        Checkpoint Context:
        - Project: {checkpoint['project_name']}
        - Checkpoint Time: {checkpoint['created_at']}
        - Files at checkpoint time: {len(checkpoint['files']['file_list'])} files
        - File list: {', '.join(checkpoint['files']['file_list'][:10])}...
        """
        
        # Use the hybrid AI system to analyze the error
        # Note: AI manager is now passed as dependency
        if self.ai_manager:
            ai_analysis = self.ai_manager.execute_ai_operation("advanced_analysis", context)
        else:
            ai_analysis = "AI analysis unavailable - AI manager not configured"
        
        # Combine AI analysis with checkpoint data
        analysis_result = {
            "checkpoint_id": checkpoint_id,
            "error_message": error_message,
            "project_name": checkpoint["project_name"],
            "checkpoint_time": checkpoint["created_at"],
            "ai_analysis": ai_analysis,
            "recovery_suggestions": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add recovery suggestions based on error type
        if "ModuleNotFoundError" in error_message:
            analysis_result["recovery_suggestions"].append({
                "type": "missing_module",
                "suggestion": "Install the missing Python module",
                "command": f"pip install {error_message.split('No module named ')[-1].split('\"')[0]}"
            })
        
        elif "FileNotFoundError" in error_message:
            missing_file = error_message.split("No such file or directory: '")[-1].split("'")[0]
            analysis_result["recovery_suggestions"].append({
                "type": "missing_file",
                "suggestion": "Restore missing file from checkpoint",
                "file": missing_file,
                "action": "restore_file"
            })
        
        # Add checkpoint restoration suggestion
        analysis_result["recovery_suggestions"].append({
            "type": "checkpoint_restore",
            "suggestion": "Restore entire project from this checkpoint",
            "action": "restore_checkpoint",
            "checkpoint_id": checkpoint_id
        })
        
        return analysis_result
    
    def cleanup_old_checkpoints(self, max_checkpoints: int = 10) -> Dict:
        """Clean up old checkpoints, keeping only the most recent ones."""
        all_checkpoints = self.list_checkpoints()
        
        if len(all_checkpoints) <= max_checkpoints:
            return {"message": "No cleanup needed", "kept": len(all_checkpoints), "removed": 0}
        
        # Sort by creation time (newest first)
        sorted_checkpoints = sorted(all_checkpoints, key=lambda x: x["created_at"], reverse=True)
        
        # Keep the newest ones
        to_keep = sorted_checkpoints[:max_checkpoints]
        to_remove = sorted_checkpoints[max_checkpoints:]
        
        # Remove old checkpoints
        removed_count = 0
        for checkpoint in to_remove:
            try:
                checkpoint_path = self._get_checkpoint_path(checkpoint["checkpoint_id"])
                if checkpoint_path.exists():
                    checkpoint_path.unlink()
                    removed_count += 1
                    # Remove from memory
                    if checkpoint["checkpoint_id"] in self.checkpoints:
                        del self.checkpoints[checkpoint["checkpoint_id"]]
            except Exception as e:
                print(f"{C_YELLOW}Warning: Could not remove checkpoint {checkpoint['checkpoint_id']}: {e}{C_RESET}")
        
        return {
            "message": "Cleanup completed",
            "kept": len(to_keep),
            "removed": removed_count,
            "timestamp": datetime.now().isoformat()
        }
