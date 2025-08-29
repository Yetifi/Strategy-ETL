"""
Tests for the enhanced Strategy ETL features.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the enhanced features
from src.enhanced_cli import EnhancedCLI
from src.prompt_storage import PromptStorageManager
from src.config import Config
from src.models import UserPrompt, TransformedPrompt, ETLResult


class TestEnhancedCLI:
    """Test the enhanced CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cli = EnhancedCLI(storage_type="sqlite")
        self.cli.storage_manager.storage_path = str(Path(self.temp_dir) / "test.db")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        assert self.cli.storage_manager is not None
        assert self.cli.processor is not None
        assert self.cli.current_user_id is None
    
    def test_set_user_id(self):
        """Test setting user ID."""
        self.cli.set_user_id("test_user")
        assert self.cli.current_user_id == "test_user"
    
    def test_process_prompt(self):
        """Test prompt processing."""
        self.cli.set_user_id("test_user")
        result = self.cli.process_prompt("yield farming with NEAR")
        
        assert result is not None
        # The result should be printed, not returned
    
    @patch('builtins.input', return_value='done')
    def test_capture_prompt_empty(self, mock_input):
        """Test prompt capture with empty input."""
        result = self.cli.capture_prompt()
        assert result is None
    
    @patch('builtins.input', side_effect=['yield farming with NEAR', 'done'])
    @patch('builtins.print')  # Mock print to avoid output during tests
    def test_capture_prompt_simple(self, mock_print, mock_input):
        """Test simple prompt capture."""
        result = self.cli.capture_prompt()
        assert result == "yield farming with NEAR"
    
    def test_show_stats(self):
        """Test showing storage statistics."""
        # This should not raise an error
        self.cli.show_stats()
    
    def test_show_history_empty(self):
        """Test showing empty history."""
        # This should not raise an error
        self.cli.show_history()


class TestPromptStorage:
    """Test the prompt storage functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = PromptStorageManager(storage_type="sqlite")
        self.storage.storage_path = str(Path(self.temp_dir) / "test.db")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_storage_initialization(self):
        """Test storage manager initialization."""
        assert self.storage.storage_type == "sqlite"
        assert self.storage.storage_path is not None
    
    def test_store_and_retrieve_user_prompt(self):
        """Test storing and retrieving user prompts."""
        from datetime import datetime
        
        prompt = UserPrompt(
            id="test_id",
            raw_text="test prompt",
            timestamp=datetime.utcnow(),
            user_id="test_user",
            metadata={"source": "test"}
        )
        
        # Store the prompt
        success = self.storage.store_user_prompt(prompt)
        assert success is True
        
        # Retrieve the prompt
        prompts = self.storage.get_user_prompts()
        assert len(prompts) == 1
        assert prompts[0].id == "test_id"
        assert prompts[0].raw_text == "test prompt"
    
    def test_get_prompt_history(self):
        """Test getting prompt history."""
        history = self.storage.get_prompt_history()
        assert isinstance(history, list)
    
    def test_search_prompts(self):
        """Test searching prompts."""
        results = self.storage.search_prompts("test")
        assert isinstance(results, list)
    
    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        stats = self.storage.get_storage_stats()
        assert isinstance(stats, dict)
        assert "storage_type" in stats


class TestConfiguration:
    """Test the configuration functionality."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        storage_config = Config.get_storage_config()
        assert storage_config["type"] == "sqlite"
        
        user_config = Config.get_user_config()
        assert user_config["anonymous_allowed"] is True
        
        validation_config = Config.get_validation_config()
        assert validation_config["min_confidence"] == 0.3
    
    def test_environment_variables(self):
        """Test environment variable configuration."""
        with patch.dict(os.environ, {"ETL_STORAGE_TYPE": "json"}):
            storage_config = Config.get_storage_config()
            assert storage_config["type"] == "json"
    
    def test_create_default_config(self):
        """Test creating default configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            config = Config.create_default_config(config_file)
            assert isinstance(config, dict)
            assert "storage" in config
            assert "user" in config
            assert "validation" in config
            
            # Verify file was created
            assert Path(config_file).exists()
        finally:
            # Clean up
            Path(config_file).unlink(missing_ok=True)
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_path = Config.DEFAULT_STORAGE_PATH
            Config.DEFAULT_STORAGE_PATH = temp_dir
            
            try:
                Config.ensure_directories()
                assert Path(temp_dir).exists()
            finally:
                Config.DEFAULT_STORAGE_PATH = original_path


class TestIntegration:
    """Test integration between components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cli = EnhancedCLI(storage_type="sqlite")
        self.cli.storage_manager.storage_path = str(Path(self.temp_dir) / "test.db")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test the complete workflow from prompt to storage."""
        # Set user ID
        self.cli.set_user_id("integration_test_user")
        
        # Process a prompt
        self.cli.process_prompt("stake NEAR tokens for compound interest")
        
        # Check storage
        stats = self.cli.storage_manager.get_storage_stats()
        assert stats["total_prompts"] >= 1
        
        # Check history
        history = self.cli.storage_manager.get_prompt_history()
        assert len(history) >= 1
        
        # Search for the prompt
        results = self.cli.storage_manager.search_prompts("NEAR")
        assert len(results) >= 1
    
    def test_user_isolation(self):
        """Test that users can only see their own prompts."""
        # User 1
        self.cli.set_user_id("user1")
        self.cli.process_prompt("user1 prompt")
        
        # User 2
        self.cli.set_user_id("user2")
        self.cli.process_prompt("user2 prompt")
        
        # Check isolation
        user1_prompts = self.cli.storage_manager.get_user_prompts(user_id="user1")
        user2_prompts = self.cli.storage_manager.get_user_prompts(user_id="user2")
        
        assert len(user1_prompts) == 1
        assert len(user2_prompts) == 1
        assert user1_prompts[0].user_id == "user1"
        assert user2_prompts[0].user_id == "user2"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
