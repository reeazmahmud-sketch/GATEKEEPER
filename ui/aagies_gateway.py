#!/usr/bin/env python3
"""
AAGIES Gateway - Main interface for AAGIES system.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict

# Import local modules
from security.security_manager import SecurityManager
from ai.ai_model_manager import AIModelManager
from projects.project_manager import ProjectManager

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


class AAGIESGateway:
    """Main AAGIES gateway interface."""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.ai_manager = AIModelManager()
        self.project_manager = ProjectManager()
        self.checkpoint_manager = self.project_manager.checkpoint_manager
        
        # Print welcome message
        self._print_welcome()
    
    def _print_welcome(self):
        """Print welcome message."""
        print(f"{C_CYAN}╔════════════════════════════════════════════════════════════╗")
        print(f"{C_CYAN}║  🛡️  AAGIES - Autonomous Error Guard & Intelligent Self-healing  ║")
        print(f"{C_CYAN}║        Advanced AI Project Management & Security Gateway       ║")
        print(f"{C_CYAN}╚════════════════════════════════════════════════════════════╝{C_RESET}")
        print()
    
    def _print_menu(self):
        """Print main menu."""
        print(f"{C_GREEN}📁 PROJECT MANAGEMENT:{C_RESET}")
        print(f"  1. {C_BLUE}Create New Project{C_RESET}")
        print(f"  2. {C_BLUE}Open Existing Project{C_RESET}")
        print(f"  3. {C_BLUE}List All Projects{C_RESET}")
        print(f"  4. {C_BLUE}Open Last Active Project{C_RESET}")
        print()
        print(f"{C_YELLOW}🤖 AI MANAGEMENT:{C_RESET}")
        print(f"  5. {C_BLUE}Configure AI Models{C_RESET}")
        print(f"  6. {C_BLUE}Check AI System Status{C_RESET}")
        print()
        print(f"{C_RED}🔒 SECURITY MANAGEMENT:{C_RESET}")
        print(f"  7. {C_BLUE}Manage Allowed Folders{C_RESET}")
        print(f"  8. {C_BLUE}Run Security Audit{C_RESET}")
        print()
        print(f"{C_CYAN}💾 CHECKPOINT MANAGEMENT:{C_RESET}")
        print(f"  9. {C_BLUE}Create Checkpoint{C_RESET}")
        print(f" 10. {C_BLUE}List Checkpoints{C_RESET}")
        print(f" 11. {C_BLUE}Restore from Checkpoint{C_RESET}")
        print(f" 12. {C_BLUE}Analyze Error with Checkpoint{C_RESET}")
        print()
        print(f"  0. {C_RED}Exit{C_RESET}")
        print()
    
    def _get_user_choice(self, prompt: str, options: List[str]) -> str:
        """Get user choice with validation."""
        while True:
            choice = input(f"{prompt} ").strip()
            if choice in options:
                return choice
            print(f"{C_RED}Invalid choice. Please try again.{C_RESET}")
    
    def _ask_permission(self, question: str) -> bool:
        """Ask user for permission."""
        response = input(f"{C_YELLOW}⚠️  {question} (y/n): {C_RESET}").strip().lower()
        return response == 'y'
    
    def _create_new_project_flow(self):
        """Handle new project creation flow."""
        print(f"\n{C_GREEN}=== CREATE NEW PROJECT ==={C_RESET}")
        
        # Step 1: Get project name
        project_name = input(f"{C_CYAN}Enter project name: {C_RESET}").strip()
        if not project_name:
            print(f"{C_RED}Project name cannot be empty.{C_RESET}")
            return
        
        # Step 2: Get project location
        print(f"\n{C_CYAN}Available base locations:{C_RESET}")
        for i, base_dir in enumerate(self.security_manager.security_config["project_base_dirs"], 1):
            print(f"  {i}. {base_dir}")
        
        location_choice = self._get_user_choice("Select location (1-99):", [str(i) for i in range(1, 100)])
        base_location = Path(self.security_manager.security_config["project_base_dirs"][int(location_choice) - 1])
        
        # Step 3: Select AI model
        print(f"\n{C_CYAN}Available AI Models:{C_RESET}")
        models = self.ai_manager.get_available_models()
        model_options = []
        for model_id, model_info in models.items():
            print(f"  {model_id}. {model_info['name']} ({model_info['cost']})")
            model_options.append(model_id)
        
        ai_model = self._get_user_choice("Select AI model:", model_options)
        
        # Step 4: Configure folder access
        print(f"\n{C_CYAN}Configure Folder Access:{C_RESET}")
        print("Available folders to grant access to:")
        allowed_folders = self.security_manager.get_allowed_folders()
        
        folder_access = []
        for i, folder in enumerate(allowed_folders, 1):
            access = self._ask_permission(f"Grant access to '{folder}'?")
            if access:
                folder_access.append(folder)
        
        # Create the project
        result = self.project_manager.create_project(
            project_name=project_name,
            location=base_location,
            ai_model=ai_model,
            folder_access=folder_access
        )
        
        if "error" in result:
            print(f"{C_RED}Failed to create project: {result['error']}{C_RESET}")
        else:
            print(f"{C_GREEN}✅ Project created successfully!{C_RESET}")
            print(f"   Project ID: {result['project_id']}")
            print(f"   Location: {result['path']}")
            print(f"   AI Model: {models[ai_model]['name']}")
            print(f"   Folder Access: {', '.join(folder_access) if folder_access else 'None'}")
            
            # Open the project
            if self._ask_permission("Open this project now?"):
                self._open_project(result['project_id'])
    
    def _open_existing_project_flow(self):
        """Handle opening existing project flow."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found. Create a new project first.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== OPEN EXISTING PROJECT ==={C_RESET}")
        print("Available projects:")
        
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']} (AI: {project['ai_model']})")
        
        choice = self._get_user_choice("Select project (1-99):", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        # Ask if user wants to modify AI or folder access
        if self._ask_permission("Modify AI model or folder access?"):
            self._modify_project_settings(project)
        
        # Open the project
        self._open_project(project['name'])
    
    def _modify_project_settings(self, project: Dict):
        """Modify project settings (AI model and folder access)."""
        print(f"\n{C_YELLOW}=== MODIFY PROJECT SETTINGS ==={C_RESET}")
        print(f"Current Project: {project['name']}")
        
        # Get project ID
        project_id = self.project_manager.get_project_id_by_name(project['name'])
        
        # Modify AI model
        if self._ask_permission("Change AI model?"):
            print(f"\n{C_CYAN}Available AI Models:{C_RESET}")
            models = self.ai_manager.get_available_models()
            model_options = []
            for model_id, model_info in models.items():
                current_marker = " ← CURRENT" if model_id == project['ai_model'] else ""
                print(f"  {model_id}. {model_info['name']} ({model_info['cost']}){current_marker}")
                model_options.append(model_id)
            
            new_ai_model = self._get_user_choice("Select new AI model:", model_options)
            if new_ai_model != project['ai_model']:
                self.project_manager.update_project_ai_model(project_id, new_ai_model)
                print(f"{C_GREEN}✅ AI model updated to {models[new_ai_model]['name']}{C_RESET}")
        
        # Modify folder access
        if self._ask_permission("Modify folder access?"):
            print(f"\n{C_CYAN}Current Folder Access:{C_RESET}")
            current_access = project.get('folder_access', [])
            if current_access:
                for folder in current_access:
                    print(f"  ✓ {folder}")
            else:
                print(f"  {C_YELLOW}No folder access configured{C_RESET}")
            
            print(f"\n{C_CYAN}Available folders to grant access to:{C_RESET}")
            allowed_folders = self.security_manager.get_allowed_folders()
            
            new_folder_access = []
            for folder in allowed_folders:
                has_access = folder in current_access
                access = self._ask_permission(f"Grant access to '{folder}'? (currently: {'yes' if has_access else 'no'})")
                if access:
                    new_folder_access.append(folder)
            
            self.project_manager.update_project_folder_access(project_id, new_folder_access)
            print(f"{C_GREEN}✅ Folder access updated{C_RESET}")
    
    def _open_project(self, project_name: str):
        """Open a project in a new terminal."""
        project = None
        for p in self.project_manager.list_projects():
            if p['name'] == project_name:
                project = p
                break
        
        if not project:
            print(f"{C_RED}Project '{project_name}' not found.{C_RESET}")
            return
        
        project_path = Path(project['path'])
        if not project_path.exists():
            print(f"{C_RED}Project directory '{project_path}' does not exist.{C_RESET}")
            return
        
        print(f"{C_GREEN}🚀 Opening project '{project_name}'...{C_RESET}")
        print(f"   Location: {project_path}")
        print(f"   AI Model: {project['ai_model']}")
        
        # Set as last active project
        for project_id, p in self.project_manager.projects['projects'].items():
            if p['name'] == project_name:
                self.project_manager.set_last_active_project(project_id)
                break
        
        # Open in new terminal
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', '-a', 'Terminal', str(project_path)])
            elif sys.platform == 'linux':
                subprocess.run(['gnome-terminal', '--working-directory=' + str(project_path)])
            elif sys.platform == 'win32':
                subprocess.run(['start', 'cmd', '/k', f'cd /d {project_path}'], shell=True)
            
            print(f"{C_GREEN}✅ Project opened in new terminal!{C_RESET}")
            
        except Exception as e:
            print(f"{C_YELLOW}Could not open terminal automatically: {e}{C_RESET}")
            print(f"{C_CYAN}Please manually navigate to: {project_path}{C_RESET}")
    
    def _list_projects(self):
        """List all projects."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== ALL PROJECTS ==={C_RESET}")
        for i, project in enumerate(projects, 1):
            last_active_marker = " ← LAST ACTIVE" if project['name'] == self.project_manager.get_last_active_project() else ""
            print(f"{i}. {project['name']}{last_active_marker}")
            print(f"   Location: {project['path']}")
            print(f"   AI Model: {project['ai_model']}")
            print(f"   Folder Access: {', '.join(project.get('folder_access', [])) if project.get('folder_access') else 'None'}")
            print(f"   Created: {project['created_at']}")
            print(f"   Last Used: {project['last_used']}")
            print()
    
    def _configure_ai_models(self):
        """Configure AI models and routing."""
        print(f"\n{C_GREEN}=== AI MODEL CONFIGURATION ==={C_RESET}")
        
        models = self.ai_manager.get_available_models()
        print("Available AI Models:")
        for model_id, model_info in models.items():
            print(f"  {model_id}. {model_info['name']}")
            print(f"     Type: {model_info['type']}")
            print(f"     Cost: {model_info['cost']}")
            print(f"     Internet: {'Required' if model_info['requires_internet'] else 'Not Required'}")
            print(f"     Capabilities: {', '.join(model_info['capabilities'])}")
            print()
        
        print("Current Routing Rules:")
        routing_rules = self.ai_manager.ai_config['routing_rules']
        for operation, model_id in routing_rules.items():
            model_name = models[model_id]['name']
            print(f"  {operation} → {model_name}")
        
        if self._ask_permission("Modify routing rules?"):
            print("\nSelect operation to modify:")
            for i, operation in enumerate(routing_rules.keys(), 1):
                print(f"  {i}. {operation}")
            
            operation_choice = self._get_user_choice("Select operation:", [str(i) for i in range(1, len(routing_rules) + 1)])
            selected_operation = list(routing_rules.keys())[int(operation_choice) - 1]
            
            print(f"\nSelect new AI model for '{selected_operation}':")
            model_options = list(models.keys())
            for i, model_id in enumerate(model_options, 1):
                model_name = models[model_id]['name']
                current_marker = " ← CURRENT" if model_id == routing_rules[selected_operation] else ""
                print(f"  {i}. {model_name}{current_marker}")
            
            model_choice = self._get_user_choice("Select model:", [str(i) for i in range(1, len(model_options) + 1)])
            new_model_id = model_options[int(model_choice) - 1]
            
            self.ai_manager.set_routing_rule(selected_operation, new_model_id)
            print(f"{C_GREEN}✅ Routing rule updated: {selected_operation} → {models[new_model_id]['name']}{C_RESET}")
    
    def _check_ai_status(self):
        """Check AI system status."""
        print(f"\n{C_GREEN}=== AI SYSTEM STATUS ==={C_RESET}")
        
        # Check configuration
        print("Configuration Status:")
        print(f"  AI Config Loaded: {C_GREEN}✓{C_RESET}")
        print(f"  Available Models: {len(self.ai_manager.get_available_models())}")
        
        # List models
        models = self.ai_manager.get_available_models()
        for model_id, model_info in models.items():
            status = f"{C_GREEN}Available{C_RESET}" if model_id in models else f"{C_RED}Not Available{C_RESET}"
            print(f"  {model_info['name']}: {status}")
        
        # Show routing summary
        print("\nRouting Summary:")
        routing_rules = self.ai_manager.ai_config['routing_rules']
        for operation, model_id in routing_rules.items():
            model_name = models[model_id]['name']
            print(f"  {operation} → {model_name}")
    
    def _manage_allowed_folders(self):
        """Manage allowed desktop folders."""
        print(f"\n{C_GREEN}=== MANAGE ALLOWED FOLDERS ==={C_RESET}")
        
        current_folders = self.security_manager.get_allowed_folders()
        print("Current Allowed Folders:")
        for i, folder in enumerate(current_folders, 1):
            print(f"  {i}. {folder}")
        
        if self._ask_permission("Add new allowed folder?"):
            new_folder = input(f"{C_CYAN}Enter folder name to allow: {C_RESET}").strip()
            if new_folder:
                if self.security_manager.add_allowed_folder(new_folder):
                    print(f"{C_GREEN}✅ Folder '{new_folder}' added to allowed list{C_RESET}")
                else:
                    print(f"{C_YELLOW}Folder '{new_folder}' is already allowed{C_RESET}")
        
        if self._ask_permission("Remove allowed folder?"):
            print("Select folder to remove:")
            for i, folder in enumerate(current_folders, 1):
                print(f"  {i}. {folder}")
            
            if current_folders:
                choice = self._get_user_choice("Select folder to remove:", [str(i) for i in range(1, len(current_folders) + 1)])
                folder_to_remove = current_folders[int(choice) - 1]
                
                if self._ask_permission(f"Confirm removal of '{folder_to_remove}'?"):
                    if self.security_manager.remove_allowed_folder(folder_to_remove):
                        print(f"{C_GREEN}✅ Folder '{folder_to_remove}' removed from allowed list{C_RESET}")
                    else:
                        print(f"{C_RED}Failed to remove folder{C_RESET}")
    
    def _run_security_audit(self):
        """Run security audit."""
        print(f"\n{C_GREEN}=== SECURITY AUDIT ==={C_RESET}")
        
        # Check desktop safety
        print("Desktop Safety:")
        desktop_items = list(DESKTOP_PATH.glob('*'))
        unauthorized_items = []
        
        for item in desktop_items:
            if item.name not in self.security_manager.get_allowed_folders():
                unauthorized_items.append(item.name)
        
        if unauthorized_items:
            print(f"  {C_RED}⚠️  Found unauthorized items on desktop:{C_RESET}")
            for item in unauthorized_items:
                print(f"    - {item}")
        else:
            print(f"  {C_GREEN}✓ No unauthorized items found{C_RESET}")
        
        # Check project configurations
        print("\nProject Security:")
        projects = self.project_manager.list_projects()
        for project in projects:
            project_path = Path(project['path'])
            if not project_path.exists():
                print(f"  {C_RED}⚠️  Project '{project['name']}' path does not exist{C_RESET}")
            else:
                print(f"  {C_GREEN}✓{C_RESET} {project['name']}: {project_path}")
        
        # Check AI configurations
        print("\nAI Security:")
        models = self.ai_manager.get_available_models()
        for model_id, model_info in models.items():
            if model_info['requires_internet']:
                print(f"  {C_YELLOW}ℹ️  {model_info['name']}: Requires internet access{C_RESET}")
            else:
                print(f"  {C_GREEN}✓{C_RESET} {model_info['name']}: Local operation only")
        
        print(f"\n{C_BLUE}Security audit completed.{C_RESET}")
    
    # --- CHECKPOINT METHODS ---
    
    def _create_checkpoint_flow(self):
        """Handle creating a checkpoint for a project."""
        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{C_YELLOW}No projects found. Create a project first.{C_RESET}")
            return
        
        print(f"\n{C_GREEN}=== CREATE CHECKPOINT ==={C_RESET}")
        print("Select project to create checkpoint for:")
        
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']}")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        description = input(f"{C_CYAN}Enter checkpoint description (or press Enter for auto-save): {C_RESET}").strip()
        if not description:
            description = "Auto-save"
        
        # Create checkpoint
        project_id = self.project_manager.get_project_id_by_name(project['name'])
        result = self.project_manager.create_project_checkpoint(project_id, description)
        
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
        print("Select project to list checkpoints for:")
        
        for i, project in enumerate(projects, 1):
            project_id = self.project_manager.get_project_id_by_name(project['name'])
            checkpoints = self.project_manager.list_project_checkpoints(project_id)
            print(f"  {i}. {project['name']} ({len(checkpoints)} checkpoints)")
        
        choice = self._get_user_choice("Select project:", [str(i) for i in range(1, len(projects) + 1)])
        project = projects[int(choice) - 1]
        
        # List checkpoints
        project_id = self.project_manager.get_project_id_by_name(project['name'])
        checkpoints = self.project_manager.list_project_checkpoints(project_id)
        
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
        print("Select project to restore:")
        
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
        
        print("\nSelect checkpoint to restore:")
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
        print("Select project with the error:")
        
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
        
        print("\nSelect checkpoint to use for error analysis:")
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
                print(f"     Action: {suggestion['action']}")
    
    def run(self):
        """Run the main AAGIES gateway interface."""
        while True:
            self._print_menu()
            choice = input(f"{C_CYAN}Enter your choice (0-12): {C_RESET}").strip()
            
            if choice == "1":
                self._create_new_project_flow()
            elif choice == "2":
                self._open_existing_project_flow()
            elif choice == "3":
                self._list_projects()
            elif choice == "4":
                last_project = self.project_manager.get_last_active_project()
                if last_project:
                    self._open_project(last_project['name'])
                else:
                    print(f"{C_YELLOW}No last active project found.{C_RESET}")
            elif choice == "5":
                self._configure_ai_models()
            elif choice == "6":
                self._check_ai_status()
            elif choice == "7":
                self._manage_allowed_folders()
            elif choice == "8":
                self._run_security_audit()
            elif choice == "9":
                self._create_checkpoint_flow()
            elif choice == "10":
                self._list_checkpoints_flow()
            elif choice == "11":
                self._restore_checkpoint_flow()
            elif choice == "12":
                self._analyze_error_flow()
            elif choice == "0":
                print(f"{C_GREEN}👋 Thank you for using AAGIES! Stay safe!{C_RESET}")
                break
            else:
                print(f"{C_RED}Invalid choice. Please try again.{C_RESET}")
            
            print()
