# Enhanced Strategy ETL Features

## Overview

This document describes the enhanced features implemented for the Strategy ETL system, specifically focusing on **user prompt input capture and storage**.

## 🚀 New Features

### 1. Interactive Prompt Capture

The system now provides an enhanced interactive prompt capture interface that allows users to:

- **Multi-line input**: Enter prompts across multiple lines for better readability
- **Real-time validation**: Get immediate feedback on prompt quality and suggestions
- **Interactive editing**: Edit, clear, or modify prompts during capture
- **Smart suggestions**: Receive tips for improving prompt quality

#### Usage Examples:

```bash
# Interactive prompt capture
python -m src.enhanced_cli --capture

# Direct prompt processing
python -m src.enhanced_cli "yield farming with NEAR for 20% APY"
```

#### Interactive Commands:
- `help` - Show prompt examples and tips
- `clear` - Clear all captured lines
- `back` - Remove the last line
- `show` - Display current prompt
- `done` - Finish capturing
- `cancel` - Abort capture

### 2. Persistent Storage System

#### Storage Backends

The system now supports multiple storage backends:

1. **SQLite Database** (Default)
   - Structured storage with proper relationships
   - ACID compliance
   - Efficient querying and indexing
   - File-based, no server required

2. **JSON File Storage**
   - Human-readable format
   - Easy backup and version control
   - Indexed for quick access
   - Suitable for smaller datasets

#### Storage Features

- **Automatic persistence**: All prompts, transformations, and results are automatically stored
- **User management**: Track prompts by user ID
- **Metadata support**: Store additional context with each prompt
- **Full audit trail**: Complete history of all ETL operations

### 3. Enhanced CLI Interface

#### New CLI Modes

```bash
# Interactive mode with full feature access
python -m src.enhanced_cli --interactive

# Prompt capture mode
python -m src.enhanced_cli --capture

# History viewing
python -m src.enhanced_cli --history

# Search functionality
python -m src.enhanced_cli --search "NEAR"

# Storage statistics
python -m src.enhanced_cli --stats
```

#### Interactive Commands

- `user` / `setuser` - Set user ID for session
- `history` / `h` - Show prompt history
- `search` / `s` - Search prompts by content
- `stats` / `statistics` - Show storage statistics
- `capture` / `c` / `prompt` - Capture new prompt
- `clear` / `cls` - Clear screen

### 4. Configuration Management

#### Environment Variables

```bash
# Storage configuration
export ETL_STORAGE_TYPE=json          # sqlite or json
export ETL_STORAGE_PATH=/path/to/data
export ETL_SQLITE_DB=data/prompts.db
export ETL_JSON_DIR=data/prompts

# User configuration
export ETL_DEFAULT_USER_ID=user123
export ETL_ANONYMOUS_USERS=true

# Validation settings
export ETL_MIN_CONFIDENCE=0.3
export ETL_TARGET_CONFIDENCE=0.7
export ETL_MAX_PROCESSING_TIME=30000

# Logging
export ETL_LOG_LEVEL=INFO
export ETL_LOG_FILE=logs/etl.log
```

#### Configuration File

Create `etl_config.json` for persistent settings:

```json
{
  "storage": {
    "type": "sqlite",
    "path": "data",
    "sqlite": {
      "database": "data/prompts.db"
    }
  },
  "user": {
    "default_user_id": "user123",
    "anonymous_allowed": true
  },
  "validation": {
    "min_confidence": 0.3,
    "target_confidence": 0.7
  }
}
```

### 5. Prompt History and Search

#### History Features

- **Chronological listing**: View prompts by timestamp
- **User filtering**: Filter by specific user ID
- **Statistics**: Character count, word count, metadata
- **Pagination**: Limit results for better performance

#### Search Capabilities

- **Content search**: Find prompts containing specific terms
- **User filtering**: Search within user's own prompts
- **Real-time results**: Instant search results
- **Case-insensitive**: Flexible matching

### 6. Data Models and Validation

#### Enhanced Models

The system now includes comprehensive data models:

- **UserPrompt**: Raw user input with metadata
- **TransformedPrompt**: Processed and validated prompts
- **ETLResult**: Complete processing results

#### Validation Features

- **Quality assessment**: Score prompts based on completeness
- **Shade AI compatibility**: Ensure NEAR protocol compatibility
- **Confidence scoring**: Measure transformation accuracy
- **Recommendations**: Suggest improvements for better results

## 📁 File Structure

```
src/
├── enhanced_cli.py          # Enhanced CLI with new features
├── prompt_storage.py        # Storage management system
├── config.py               # Configuration management
├── etl_processor.py        # Updated ETL processor
├── models.py               # Data models
├── validators.py           # Validation logic
└── terminology_mapper.py   # NEAR terminology mapping

examples/
└── enhanced_demo.py        # Demo of new features

tests/
├── test_enhanced_cli.py    # Tests for enhanced CLI
├── test_prompt_storage.py  # Tests for storage system
└── test_config.py          # Tests for configuration
```

## 🚀 Getting Started

### 1. Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run enhanced demo
python examples/enhanced_demo.py

# Interactive mode
python -m src.enhanced_cli --interactive
```

### 2. Storage Setup

```bash
# Use default SQLite storage
python -m src.enhanced_cli --stats

# Switch to JSON storage
export ETL_STORAGE_TYPE=json
python -m src.enhanced_cli --stats
```

### 3. User Management

```bash
# Set user ID for session
python -m src.enhanced_cli --interactive
> user
> Enter user ID: myuser123

# Process prompts with user tracking
python -m src.enhanced_cli --user-id myuser123 "stake NEAR tokens"
```

## 🔧 Advanced Features

### 1. Custom Storage Backends

Extend the storage system with custom backends:

```python
from src.prompt_storage import PromptStorageManager

class CustomStorageManager(PromptStorageManager):
    def store_user_prompt(self, prompt):
        # Custom storage logic
        pass

# Use custom storage
cli = EnhancedCLI(storage_manager=CustomStorageManager())
```

### 2. Batch Processing

Process multiple prompts efficiently:

```python
from src.enhanced_cli import EnhancedCLI

cli = EnhancedCLI()
prompts = [
    "yield farming with NEAR",
    "stake NEAR tokens",
    "provide liquidity to NEAR-USDC"
]

for prompt in prompts:
    result = cli.process_prompt(prompt)
    print(f"Processed: {result.success}")
```

### 3. Data Export

Export stored data for analysis:

```python
from src.prompt_storage import PromptStorageManager

storage = PromptStorageManager()
prompts = storage.get_user_prompts(limit=1000)

# Export to CSV
import pandas as pd
df = pd.DataFrame([
    {
        'id': p.id,
        'text': p.raw_text,
        'timestamp': p.timestamp,
        'user_id': p.user_id
    }
    for p in prompts
])
df.to_csv('prompts_export.csv', index=False)
```

## 📊 Performance Considerations

### 1. Storage Performance

- **SQLite**: Best for high-volume, complex queries
- **JSON**: Best for human-readable, version-controlled data
- **Memory**: Best for temporary, high-speed processing

### 2. Scaling Recommendations

- **Small scale** (< 1000 prompts): JSON storage
- **Medium scale** (1000-100000 prompts): SQLite
- **Large scale** (> 100000 prompts): Consider PostgreSQL/MySQL

### 3. Optimization Tips

- Use appropriate storage backend for your use case
- Set reasonable limits on history queries
- Implement data archival for old prompts
- Use indexes for frequently searched terms

## 🧪 Testing

### 1. Run Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_enhanced_cli.py
pytest tests/test_prompt_storage.py

# Run with coverage
pytest --cov=src
```

### 2. Test Storage Backends

```bash
# Test SQLite storage
ETL_STORAGE_TYPE=sqlite pytest tests/test_prompt_storage.py

# Test JSON storage
ETL_STORAGE_TYPE=json pytest tests/test_prompt_storage.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Storage Permission Errors**
   - Ensure write permissions to data directory
   - Check disk space availability

2. **Import Errors**
   - Verify Python path includes src directory
   - Check all dependencies are installed

3. **Database Locking**
   - Close other applications using the database
   - Check for concurrent access issues

### Debug Mode

```bash
# Enable debug logging
export ETL_LOG_LEVEL=DEBUG
python -m src.enhanced_cli --interactive
```

## 🔮 Future Enhancements

### Planned Features

1. **Web Interface**: Browser-based prompt capture
2. **API Endpoints**: RESTful API for integration
3. **Advanced Analytics**: Prompt performance metrics
4. **Machine Learning**: Smart prompt suggestions
5. **Multi-language Support**: Internationalization

### Contributing

To contribute to the enhanced features:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## 📚 Additional Resources

- [Strategy ETL Main README](README.md)
- [API Documentation](docs/api.md)
- [Configuration Guide](docs/config.md)
- [Storage Backends](docs/storage.md)

---

**Note**: This enhanced system maintains backward compatibility with the original Strategy ETL implementation while adding powerful new capabilities for prompt management and storage.
