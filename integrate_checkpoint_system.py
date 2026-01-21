#!/usr/bin/env python3
"""
Integration script to add checkpoint system to AAGIES
"""

import sys
from pathlib import Path

def integrate_checkpoint_system():
    """Integrate checkpoint system into main AAGIES application."""
    
    # Read the main AAGIES file
    aagies_file = Path("aagies.py")
    checkpoint_file = Path("checkpoint_system.py")
    
    if not aagies_file.exists():
        print(f"❌ Main AAGIES file not found: {aagies_file}")
        return False
    
    if not checkpoint_file.exists():
        print(f"❌ Checkpoint system file not found: {checkpoint_file}")
        return False
    
    print(f"📁 Found AAGIES file: {aagies_file}")
    print(f"📁 Found Checkpoint system: {checkpoint_file}")
    
    # Read aagies file to check for existing integration
    with open(aagies_file, 'r') as f:
        aagies_content = f.read()

    # Check if checkpoint system is already integrated
    if 'CheckpointManager' in aagies_content:
        print("ℹ️  Checkpoint system appears to be already integrated")
        return True
    
    # Find the import section to add checkpoint imports
    import_section_end = aagies_content.find('from datetime import datetime, timedelta')
    if import_section_end == -1:
        print("❌ Could not find import section")
        return False
    
    # Add checkpoint import after the existing imports
    checkpoint_import = '\nfrom checkpoint_system import CheckpointManager'
    
    # Insert the import
    modified_content = (
        aagies_content[:import_section_end + len('from datetime import datetime, timedelta')] +
        checkpoint_import +
        aagies_content[import_section_end + len('from datetime import datetime, timedelta'):]
    )
    
    # Find the constants section to add checkpoint directory
    constants_end = modified_content.find('AI_CONFIG = AAGIES_CONFIG_DIR / "ai_config.json"')
    if constants_end == -1:
        print("❌ Could not find constants section")
        return False
    
    # Add checkpoint directory constant
    checkpoint_constant = '\nCHECKPOINT_DIR = AAGIES_CONFIG_DIR / "checkpoints"'
    
    # Insert the constant
    modified_content = (
        modified_content[:constants_end + len('AI_CONFIG = AAGIES_CONFIG_DIR / "ai_config.json"')] +
        checkpoint_constant +
        modified_content[constants_end + len('AI_CONFIG = AAGIES_CONFIG_DIR / "ai_config.json"'):]
    )
    
    # Find the ProjectManager __init__ to add checkpoint manager
    project_manager_init = modified_content.find('self.ai_manager = AIModelManager()')
    if project_manager_init == -1:
        print("❌ Could not find ProjectManager __init__")
        return False
    
    # Add checkpoint manager initialization
    checkpoint_init = '\n        self.checkpoint_manager = CheckpointManager(CHECKPOINT_DIR)'
    
    # Insert the initialization
    modified_content = (
        modified_content[:project_manager_init + len('self.ai_manager = AIModelManager()')] +
        checkpoint_init +
        modified_content[project_manager_init + len('self.ai_manager = AIModelManager()'):]
    )
    
    # Find the AAGIESGateway __init__ to add checkpoint manager
    gateway_init = modified_content.find('self.project_manager = ProjectManager()')
    if gateway_init == -1:
        print("❌ Could not find AAGIESGateway __init__")
        return False
    
    # Add checkpoint manager to gateway
    gateway_checkpoint = '\n        self.checkpoint_manager = self.project_manager.checkpoint_manager'
    
    # Insert the checkpoint manager
    modified_content = (
        modified_content[:gateway_init + len('self.project_manager = ProjectManager()')] +
        gateway_checkpoint +
        modified_content[gateway_init + len('self.project_manager = ProjectManager()'):]
    )
    
    # Add checkpoint methods to ProjectManager
    project_manager_end = modified_content.find('def set_last_active_project(self, project_id: str) -> bool:')
    if project_manager_end == -1:
        print("❌ Could not find end of ProjectManager class")
        return False
    
    # Find the end of the set_last_active_project method
    method_end = modified_content.find('\n\n    def get_project(self, project_id: str) -> Optional[Dict]:', project_manager_end)
    if method_end == -1:
        print("❌ Could not find end of set_last_active_project method")
        return False
    
    # Add checkpoint methods
    checkpoint_methods = '''
    
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
                print(f"Warning: Could not remove checkpoint {checkpoint['checkpoint_id']}: {e}")
        
        return {
            "message": "Cleanup completed",
            "project_id": project_id,
            "kept": max_checkpoints,
            "removed": removed_count
        }'''
    
    # Insert the checkpoint methods
    modified_content = (
        modified_content[:method_end] +
        checkpoint_methods +
        modified_content[method_end:]
    )
    
    # Add checkpoint menu items to AAGIESGateway
    menu_end = modified_content.find('print(f"  0. {C_RED}Exit{C_RESET}")')
    if menu_end == -1:
        print("❌ Could not find menu end")
        return False
    
    # Add checkpoint menu section
    checkpoint_menu = '''
        print()
        print(f"{C_CYAN}💾 CHECKPOINT MANAGEMENT:{C_RESET}")
        print(f"  9. {C_BLUE}Create Checkpoint{C_RESET}")
        print(f" 10. {C_BLUE}List Checkpoints{C_RESET}")
        print(f" 11. {C_BLUE}Restore from Checkpoint{C_RESET}")
        print(f" 12. {C_BLUE}Analyze Error with Checkpoint{C_RESET}")'''
    
    # Insert the checkpoint menu
    modified_content = (
        modified_content[:menu_end] +
        checkpoint_menu +
        modified_content[menu_end:]
    )
    
    # Update the menu prompt
    menu_prompt = modified_content.find('choice = input(f"{C_CYAN}Enter your choice (0-8): {C_RESET}").strip()')
    if menu_prompt == -1:
        print("❌ Could not find menu prompt")
        return False
    
    # Update to include checkpoint options
    new_prompt = 'choice = input(f"{C_CYAN}Enter your choice (0-12): {C_RESET}").strip()'
    
    # Replace the prompt
    modified_content = (
        modified_content[:menu_prompt] +
        new_prompt +
        modified_content[menu_prompt + len('choice = input(f"{C_CYAN}Enter your choice (0-8): {C_RESET}").strip()'):]
    )
    
    # Add checkpoint methods to AAGIESGateway class
    gateway_methods_end = modified_content.find('def _run_security_audit(self):')
    if gateway_methods_end == -1:
        print("❌ Could not find end of gateway methods")
        return False
    
    # Find the end of the security audit method
    security_audit_end = modified_content.find('\n\n    def run(self):', gateway_methods_end)
    if security_audit_end == -1:
        print("❌ Could not find end of security audit method")
        return False
    
    # Add checkpoint methods to gateway
    gateway_checkpoint_methods = '''
    
    # --- CHECKPOINT METHODS ---
    
    def _create_checkpoint_flow(self):
        """Handle creating a checkpoint for a project."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found. Create a project first.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== CREATE CHECKPOINT ==={C_RESET}")
        print(f"Select project to create checkpoint for:")
        
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']}")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        description = input(f"{C_CYAN}Enter checkpoint description (or press Enter for auto-save): {C_RESET}").strip()
        if not description:
            description = "Auto-save"
        
        # Create checkpoint
        result = self.project_manager.create_project_checkpoint(project['name'], description)
        
        if "error" in result:
            print(f"{C_RED}Failed to create checkpoint: {result['error']}{C_RESET}")
        else:
            print(f"{C_GREEN}✅ Checkpoint created successfully!{C_RESET}")
            print(f"   Checkpoint ID: {result['checkpoint_id']}")
            print(f"   Project: {result['project_name']}")
            print(f"   Files snapshotted: {result['files']['file_count']}")
            print(f"   Description: {result['description']}")
    
    def _list_checkpoints_flow(self):
        """Handle listing checkpoints for a project."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== LIST CHECKPOINTS ==={C_RESET}")
        print(f"Select project to list checkpoints for:")
        
        for i, project in enumerate(projects, 1):
            checkpoints = self.project_manager.list_project_checkpoints(project['name'])
            print(f"  {i}. {project['name']} ({len(checkpoints)} checkpoints)")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        # List checkpoints
        checkpoints = self.project_manager.list_project_checkpoints(project['name'])
        
        if not checkpoints:
            print(f"{C_YELLOW}No checkpoints found for this project.{C_RESET}")
            return
        
        print(f"\nCheckpoints for '{project['name']}':")
        for i, checkpoint in enumerate(checkpoints, 1):
            print(f"  {i}. {checkpoint['checkpoint_id']}")
            print(f"     Created: {checkpoint['created_at']}")
            print(f"     Description: {checkpoint['description']}")
            print(f"     Files: {checkpoint['files']['file_count']}")
            print()
    
    def _restore_checkpoint_flow(self):
        """Handle restoring a project from a checkpoint."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== RESTORE FROM CHECKPOINT ==={C_RESET}")
        print(f"Select project to restore:")
        
        for i, project in enumerate(projects, 1):
            checkpoints = self.project_manager.list_project_checkpoints(project['name'])
            print(f"  {i}. {project['name']} ({len(checkpoints)} checkpoints)")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        # List checkpoints
        checkpoints = self.project_manager.list_project_checkpoints(project['name'])
        
        if not checkpoints:
            print(f"{C_YELLOW}No checkpoints found for this project.{C_RESET}")
            return
        
        print(f"\nSelect checkpoint to restore:")
        for i, checkpoint in enumerate(checkpoints, 1):
            print(f"  {i}. {checkpoint['checkpoint_id']} - {checkpoint['description']} ({checkpoint['created_at']})")
        
        checkpoint_choice = self._get_user_choice("Select checkpoint:", [str(i) for i in range(1, len(checkpoints) + 1)])
        checkpoint = checkpoints[int(checkpoint_choice) - 1]
        
        # Confirm restoration
        if not self._ask_permission(f"Are you sure you want to restore '{project['name']}' from checkpoint {checkpoint['checkpoint_id']}? This may overwrite current files."):
            print(f"{C_YELLOW}Restoration cancelled.{C_RESET}")
            return
        
        # Restore from checkpoint
        result = self.project_manager.restore_project_from_checkpoint(checkpoint['checkpoint_id'])
        
        if "error" in result:
            print(f"{C_RED}Failed to restore: {result['error']}{C_RESET}")
        else:
            print(f"{C_GREEN}✅ Project restored successfully!{C_RESET}")
            print(f"   Restored files: {len(result['restored_files'])}")
            if result['failed_files']:
                print(f"   {C_YELLOW}Failed to restore {len(result['failed_files'])} files{C_RESET}")
    
    def _analyze_error_flow(self):
        """Handle analyzing an error using checkpoints."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== ANALYZE ERROR WITH CHECKPOINT ==={C_RESET}")
        print(f"Select project with the error:")
        
        for i, project in enumerate(projects, 1):
            checkpoints = self.project_manager.list_project_checkpoints(project['name'])
            print(f"  {i}. {project['name']} ({len(checkpoints)} checkpoints)")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        # List checkpoints
        checkpoints = self.project_manager.list_project_checkpoints(project['name'])
        
        if not checkpoints:
            print(f"{C_YELLOW}No checkpoints found for this project.{C_RESET}")
            return
        
        print(f"\nSelect checkpoint to use for error analysis:")
        for i, checkpoint in enumerate(checkpoints, 1):
            print(f"  {i}. {checkpoint['checkpoint_id']} - {checkpoint['description']} ({checkpoint['created_at']})")
        
        checkpoint_choice = self._get_user_choice("Select checkpoint:", [str(i) for i in range(1, len(checkpoints) + 1)])
        checkpoint = checkpoints[int(checkpoint_choice) - 1]
        
        # Get error message
        error_message = input(f"{C_CYAN}Enter the error message you're seeing: {C_RESET}").strip()
        
        if not error_message:
            print(f"{C_YELLOW}No error message provided.{C_RESET}")
            return
        
        # Analyze error
        result = self.project_manager.analyze_project_error(checkpoint['checkpoint_id'], error_message)
        
        print(f"\n{C_GREEN}=== ERROR ANALYSIS RESULTS ==={C_RESET}")
        print(f"Error: {result['error_message']}")
        print(f"Project: {result['project_name']}")
        print(f"Checkpoint Time: {result['checkpoint_time']}")
        print(f"Analysis Time: {result['timestamp']}")
        
        print(f"\n{C_BLUE}AI Analysis:{C_RESET}")
        print(f"  {result['ai_analysis']}")
        
        print(f"\n{C_MAGENTA}Recovery Suggestions:{C_RESET}")
        for i, suggestion in enumerate(result['recovery_suggestions'], 1):
            print(f"  {i}. {suggestion['suggestion']}")
            if 'command' in suggestion:
                print(f"     Command: {suggestion['command']}")
            if 'file' in suggestion:
                print(f"     File: {suggestion['file']}")
            if 'action' in suggestion:
                print(f"     Action: {suggestion['action']}")'''
    
    # Insert the checkpoint methods
    modified_content = (
        modified_content[:security_audit_end] +
        gateway_checkpoint_methods +
        modified_content[security_audit_end:]
    )
    
    # Add checkpoint cases to the main run method
    run_method_start = modified_content.find('elif choice == "8":')
    if run_method_start == -1:
        print("❌ Could not find run method")
        return False
    
    # Find the end of the security audit case
    run_method_middle = modified_content.find('elif choice == "0":', run_method_start)
    if run_method_middle == -1:
        print("❌ Could not find end of run method cases")
        return False
    
    # Add checkpoint cases
    checkpoint_cases = '''
            elif choice == "9":
                self._create_checkpoint_flow()
            elif choice == "10":
                self._list_checkpoints_flow()
            elif choice == "11":
                self._restore_checkpoint_flow()
            elif choice == "12":
                self._analyze_error_flow()'''
    
    # Insert the checkpoint cases
    modified_content = (
        modified_content[:run_method_middle] +
        checkpoint_cases +
        modified_content[run_method_middle:]
    )
    
    # Update the docstring to mention checkpoint features
    docstring_end = modified_content.find('"""')
    if docstring_end == -1:
        print("❌ Could not find end of docstring")
        return False
    
    # Find a good place to add checkpoint info to docstring
    usage_section = modified_content.find('aagies --security-check   -> Run security audit')
    if usage_section == -1:
        print("❌ Could not find usage section in docstring")
        return False
    
    # Add checkpoint features to docstring
    checkpoint_docs = '''

Checkpoint Features:
- Automatic snapshots of project state
- File-level tracking with hashes
- Error recovery based on historical checkpoints
- AI-powered error analysis with context
- Multiple checkpoint versions per project'''
    
    # Insert the checkpoint documentation
    modified_content = (
        modified_content[:usage_section + len('aagies --security-check   -> Run security audit')] +
        checkpoint_docs +
        modified_content[usage_section + len('aagies --security-check   -> Run security audit'):]
    )
    
    # Write the modified content back to the file
    with open(aagies_file, 'w') as f:
        f.write(modified_content)
    
    print(f"✅ Checkpoint system successfully integrated into {aagies_file}")
    print(f"📁 Modified file size: {len(modified_content)} bytes")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting checkpoint system integration...")
    success = integrate_checkpoint_system()
    
    if success:
        print("\n🎉 Integration completed successfully!")
        print("\n📋 Summary of changes:")
        print("  ✅ Added CheckpointManager import")
        print("  ✅ Added CHECKPOINT_DIR constant")
        print("  ✅ Added checkpoint manager initialization")
        print("  ✅ Added checkpoint methods to ProjectManager")
        print("  ✅ Added checkpoint menu items")
        print("  ✅ Added checkpoint methods to AAGIESGateway")
        print("  ✅ Added checkpoint cases to main run method")
        print("  ✅ Updated documentation")
        print("\n🚀 Ready to test the integrated system!")
    else:
        print("\n❌ Integration failed. Please check the error messages.")
        sys.exit(1)
