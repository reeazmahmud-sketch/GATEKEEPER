#!/usr/bin/env python3
"""
AI Model Manager - Manages AI models and project-specific AI configurations.
"""

import json
from pathlib import Path
from typing import Dict, Optional

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


class AIModelManager:
    """Manages AI models and project-specific AI configurations."""
    
    def __init__(self):
        self._ensure_config_dirs()
        self.ai_config = self._load_ai_config()
    
    def _ensure_config_dirs(self):
        """Ensure all required directories exist."""
        AAGIES_CONFIG_DIR.mkdir(exist_ok=True)
    
    def _load_ai_config(self) -> Dict:
        """Load AI configuration."""
        if not AI_CONFIG.exists():
            default_config = {
                "available_models": {
                    "local_llm": {
                        "name": "Local LLM (Free Tier)",
                        "type": "local",
                        "description": "Local AI model for basic operations (no internet required)",
                        "capabilities": ["basic_analysis", "file_recovery", "dependency_check", "simple_questions"],
                        "requires_internet": False,
                        "cost": "Free",
                        "priority": 1
                    },
                    "cloud_basic": {
                        "name": "Cloud AI (Basic Tier)",
                        "type": "cloud",
                        "description": "Cloud-based AI with basic capabilities",
                        "capabilities": ["advanced_analysis", "complex_questions", "limited_search"],
                        "requires_internet": True,
                        "cost": "Basic",
                        "priority": 2,
                        "api_endpoint": "https://api.basic-ai.com/v1"
                    },
                    "cloud_pro": {
                        "name": "Cloud AI (Pro Tier)",
                        "type": "cloud",
                        "description": "Premium cloud AI with full capabilities",
                        "capabilities": ["advanced_analysis", "complex_questions", "internet_search", "code_generation", "full_features"],
                        "requires_internet": True,
                        "cost": "Paid",
                        "priority": 3,
                        "api_endpoint": "https://api.pro-ai.com/v1"
                    }
                },
                "routing_rules": {
                    "basic_analysis": "local_llm",
                    "file_recovery": "local_llm",
                    "dependency_check": "local_llm",
                    "simple_questions": "local_llm",
                    "advanced_analysis": "cloud_basic",
                    "complex_questions": "cloud_basic",
                    "internet_search": "cloud_pro",
                    "code_generation": "cloud_pro"
                },
                "fallback_strategy": {
                    "local_to_cloud": True,
                    "cloud_to_local": True,
                    "timeout_seconds": 30
                }
            }
            with open(AI_CONFIG, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        with open(AI_CONFIG) as f:
            return json.load(f)
    
    def save_ai_config(self):
        """Save AI configuration."""
        with open(AI_CONFIG, 'w') as f:
            json.dump(self.ai_config, f, indent=2)
    
    def get_available_models(self) -> Dict:
        """Get all available AI models."""
        return self.ai_config["available_models"]
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get information about a specific AI model."""
        return self.ai_config["available_models"].get(model_id)
    
    def set_routing_rule(self, operation: str, model_id: str):
        """Set routing rule for a specific operation."""
        if model_id in self.ai_config["available_models"]:
            self.ai_config["routing_rules"][operation] = model_id
            self.save_ai_config()
            return True
        return False
    
    def get_routing_rule(self, operation: str) -> str:
        """Get the AI model routed for a specific operation."""
        return self.ai_config["routing_rules"].get(operation, "local_llm")
