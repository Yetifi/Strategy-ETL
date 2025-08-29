"""
Configuration settings for the Strategy ETL system.
"""
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the Strategy ETL system."""
    
    # Default storage settings
    DEFAULT_STORAGE_TYPE = "sqlite"
    DEFAULT_STORAGE_PATH = "data"
    
    # Database settings
    DEFAULT_DB_NAME = "prompts.db"
    DEFAULT_DB_PATH = "data/prompts.db"
    
    # JSON storage settings
    DEFAULT_JSON_PATH = "data/prompts"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/etl.log"
    
    # ETL settings
    MAX_PROMPT_LENGTH = 10000
    MIN_PROMPT_LENGTH = 10
    MAX_PROCESSING_TIME_MS = 30000  # 30 seconds
    
    # Validation settings
    MIN_CONFIDENCE_SCORE = 0.3
    TARGET_CONFIDENCE_SCORE = 0.7
    
    # User settings
    DEFAULT_USER_ID = None
    ANONYMOUS_USERS_ALLOWED = True
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """Get storage configuration."""
        storage_type = os.getenv("ETL_STORAGE_TYPE", cls.DEFAULT_STORAGE_TYPE)
        storage_path = os.getenv("ETL_STORAGE_PATH", cls.DEFAULT_STORAGE_PATH)
        
        return {
            "type": storage_type,
            "path": storage_path,
            "sqlite": {
                "database": os.getenv("ETL_SQLITE_DB", cls.DEFAULT_DB_PATH),
                "timeout": 30,
                "check_same_thread": False
            },
            "json": {
                "directory": os.getenv("ETL_JSON_DIR", cls.DEFAULT_JSON_PATH),
                "indent": 2,
                "ensure_ascii": False
            }
        }
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the database file path."""
        config = cls.get_storage_config()
        if config["type"] == "sqlite":
            return config["sqlite"]["database"]
        return config["path"]
    
    @classmethod
    def get_json_storage_path(cls) -> str:
        """Get the JSON storage directory path."""
        config = cls.get_storage_config()
        if config["type"] == "json":
            return config["json"]["directory"]
        return config["path"]
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
        # Ensure data directory exists
        data_dir = Path(cls.DEFAULT_STORAGE_PATH)
        data_dir.mkdir(exist_ok=True)
        
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Ensure JSON storage directory exists if using JSON
        config = cls.get_storage_config()
        if config["type"] == "json":
            json_dir = Path(config["json"]["directory"])
            json_dir.mkdir(exist_ok=True, parents=True)
    
    @classmethod
    def get_user_config(cls) -> Dict[str, Any]:
        """Get user-related configuration."""
        return {
            "default_user_id": os.getenv("ETL_DEFAULT_USER_ID", cls.DEFAULT_USER_ID),
            "anonymous_allowed": os.getenv("ETL_ANONYMOUS_USERS", "true").lower() == "true",
            "max_prompt_length": int(os.getenv("ETL_MAX_PROMPT_LENGTH", cls.MAX_PROMPT_LENGTH)),
            "min_prompt_length": int(os.getenv("ETL_MIN_PROMPT_LENGTH", cls.MIN_PROMPT_LENGTH))
        }
    
    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Get validation configuration."""
        return {
            "min_confidence": float(os.getenv("ETL_MIN_CONFIDENCE", cls.MIN_CONFIDENCE_SCORE)),
            "target_confidence": float(os.getenv("ETL_TARGET_CONFIDENCE", cls.TARGET_CONFIDENCE_SCORE)),
            "max_processing_time": int(os.getenv("ETL_MAX_PROCESSING_TIME", cls.MAX_PROCESSING_TIME_MS))
        }
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            "level": os.getenv("ETL_LOG_LEVEL", cls.LOG_LEVEL),
            "format": os.getenv("ETL_LOG_FORMAT", cls.LOG_FORMAT),
            "file": os.getenv("ETL_LOG_FILE", cls.LOG_FILE),
            "console": os.getenv("ETL_LOG_CONSOLE", "true").lower() == "true"
        }
    
    @classmethod
    def load_from_file(cls, config_file: str = "etl_config.json") -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            import json
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
        
        return {}
    
    @classmethod
    def save_to_file(cls, config: Dict[str, Any], config_file: str = "etl_config.json"):
        """Save configuration to a JSON file."""
        try:
            import json
            config_path = Path(config_file)
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Configuration saved to {config_file}")
        except Exception as e:
            print(f"Error saving config file {config_file}: {e}")
    
    @classmethod
    def create_default_config(cls, config_file: str = "etl_config.json"):
        """Create a default configuration file."""
        default_config = {
            "storage": cls.get_storage_config(),
            "user": cls.get_user_config(),
            "validation": cls.get_validation_config(),
            "logging": cls.get_logging_config(),
            "description": "Strategy ETL Configuration File"
        }
        
        cls.save_to_file(default_config, config_file)
        return default_config


# Environment variable mappings
ENV_VARS = {
    "ETL_STORAGE_TYPE": "Storage backend type (sqlite/json)",
    "ETL_STORAGE_PATH": "Base storage path",
    "ETL_SQLITE_DB": "SQLite database file path",
    "ETL_JSON_DIR": "JSON storage directory",
    "ETL_DEFAULT_USER_ID": "Default user ID for prompts",
    "ETL_ANONYMOUS_USERS": "Allow anonymous users (true/false)",
    "ETL_MAX_PROMPT_LENGTH": "Maximum prompt length in characters",
    "ETL_MIN_PROMPT_LENGTH": "Minimum prompt length in characters",
    "ETL_MIN_CONFIDENCE": "Minimum confidence score (0.0-1.0)",
    "ETL_TARGET_CONFIDENCE": "Target confidence score (0.0-1.0)",
    "ETL_MAX_PROCESSING_TIME": "Maximum processing time in milliseconds",
    "ETL_LOG_LEVEL": "Logging level (DEBUG/INFO/WARNING/ERROR)",
    "ETL_LOG_FILE": "Log file path",
    "ETL_LOG_CONSOLE": "Enable console logging (true/false)"
}


def print_env_help():
    """Print help for environment variables."""
    print("Environment Variables for Strategy ETL:")
    print("=" * 50)
    for var, description in ENV_VARS.items():
        print(f"{var}: {description}")
    print("\nExample usage:")
    print("export ETL_STORAGE_TYPE=json")
    print("export ETL_STORAGE_PATH=/path/to/storage")
    print("export ETL_DEFAULT_USER_ID=user123")


if __name__ == "__main__":
    # Create default configuration
    config = Config.create_default_config()
    print("Default configuration created:")
    print(json.dumps(config, indent=2))
    
    print("\n" + "=" * 50)
    print_env_help()
