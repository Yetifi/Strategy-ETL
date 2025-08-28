# Strategy ETL

A dedicated ETL (Extract, Transform, Load) process for handling user-submitted prompts for DeFi strategies. This system takes any prompt provided by a user and adapts it into a format that is understandable and actionable by the Shade AI agent on the NEAR protocol.

## 🎯 Overview

The Strategy ETL system allows users to type free-form strategy descriptions while ensuring our system outputs a standardized, Shade-compatible prompt. It handles the complete pipeline from raw user input to validated, NEAR-specific strategy execution parameters.

## 🏗️ Architecture

The system is built with a modular, extensible architecture:

```
src/
├── models.py              # Data models and enums
├── terminology_mapper.py  # DeFi terminology mapping
├── etl_processor.py      # Main ETL pipeline
└── validators.py         # Shade AI compatibility validation

tests/                    # Comprehensive test suite
examples/                 # Usage examples and demos
```

## 🚀 Features

### Extract Phase
- Capture user's raw DeFi strategy prompt input
- Store original prompt for reference/debugging
- Support for user metadata and context

### Transform Phase
- **Terminology Normalization**: Maps generic DeFi terms to NEAR-specific terms
- **Strategy Detection**: Automatically identifies strategy types (yield farming, liquidity providing, staking, etc.)
- **Asset Recognition**: Detects and validates NEAR protocol assets
- **Risk Assessment**: Determines risk levels from user input
- **Parameter Extraction**: Extracts APY targets, durations, and other numerical values
- **NEAR Mapping**: Converts generic terms to NEAR-specific terminology

### Load Phase
- Save transformed prompt into database or pass directly to Shade AI execution module
- Ensure compatibility with NEAR's data structures and Shade's API schema
- Support for custom storage backends

### Validation
- **Shade AI Compatibility**: Ensures prompts meet Shade AI agent requirements
- **Quality Assessment**: Scores prompt quality and provides improvement recommendations
- **Asset Compatibility**: Validates asset combinations for each strategy type
- **Risk Validation**: Ensures risk levels are appropriate for strategy types

## 📊 Supported Strategy Types

| Strategy Type | Description | Required Assets | Min Confidence |
|---------------|-------------|-----------------|----------------|
| **Yield Farming** | Generate returns through farming activities | NEAR, USDC, USDT | 0.4 |
| **Liquidity Providing** | Provide liquidity to trading pools | NEAR, USDC | 0.5 |
| **Staking** | Stake tokens for network security | NEAR | 0.6 |
| **Lending** | Lend assets for interest | NEAR, USDC, USDT | 0.5 |
| **Borrowing** | Borrow against collateral | NEAR, USDC | 0.6 |
| **Swapping** | Trade between different assets | NEAR | 0.4 |
| **Arbitrage** | Exploit price differences | NEAR, USDC | 0.7 |
| **Compounding** | Reinvest returns for growth | NEAR, USDC | 0.5 |

## 🎯 Supported Assets

- **NEAR**: Native NEAR protocol token
- **USDC**: USD Coin stablecoin
- **USDT**: Tether stablecoin
- **DAI**: Decentralized stablecoin
- **WBTC**: Wrapped Bitcoin
- **ETH**: Ethereum
- **SHADE**: Shade protocol token
- **stNEAR**: Staked NEAR
- **LINEAR**: Linear protocol token
- **META**: Metaverse token

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Strategy-ETL
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the demonstration:
```bash
python examples/demo.py
```

### Basic Usage

```python
from src.etl_processor import ETLProcessor
from src.validators import ShadeAIValidator, PromptQualityValidator

# Initialize the ETL processor
processor = ETLProcessor()

# Process a user prompt
raw_text = "I want to do yield farming with NEAR for 20% APY over 90 days"
result = processor.process(raw_text)

# Check if successful
if result.success:
    transformed_prompt = result.transformed_prompt
    
    # Validate Shade AI compatibility
    validator = ShadeAIValidator()
    is_valid, errors = validator.validate_prompt(transformed_prompt)
    
    # Assess quality
    quality_validator = PromptQualityValidator()
    quality_result = quality_validator.assess_quality(transformed_prompt)
    
    print(f"Strategy: {transformed_prompt.strategy_type.value}")
    print(f"Primary Asset: {transformed_prompt.primary_asset.value}")
    print(f"Target APY: {transformed_prompt.target_apy}%")
    print(f"Quality Score: {quality_result['quality_score']:.0f}/100")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests
```

## 📋 Example Transformations

### Example 1: Yield Farming
**Input:**
```
I want to do yield farming on NEAR protocol.
Use USDC and USDT for diversification.
Target 25% APY over 6 months.
Looking for medium risk strategies.
```

**Output:**
- Strategy Type: `yield_farming`
- Primary Asset: `NEAR`
- Secondary Assets: `[USDC, USDT]`
- Risk Level: `medium`
- Target APY: `25.0%`
- Duration: `180 days`
- Confidence Score: `0.85`
- Auto-Compound: `True`

### Example 2: Liquidity Providing
**Input:**
```
Provide liquidity to NEAR-USDC pool.
Low risk, stable returns.
Duration: 1 year.
```

**Output:**
- Strategy Type: `liquidity_providing`
- Primary Asset: `NEAR`
- Secondary Assets: `[USDC]`
- Risk Level: `low`
- Duration: `365 days`
- Confidence Score: `0.78`
- Auto-Compound: `False`

## 🔧 Configuration

### Custom Terminology Mapping

```python
from src.terminology_mapper import TerminologyMapper
from src.etl_processor import ETLProcessorFactory

# Create custom mapper
custom_mapper = TerminologyMapper()
custom_mapper.add_strategy_pattern("custom_strategy", [r"\bcustom\b", r"\bstrategy\b"])

# Create processor with custom mapper
processor = ETLProcessorFactory.create_processor_with_custom_mapper(custom_mapper)
```

### Validation Thresholds

```python
from src.validators import ShadeAIValidator

validator = ShadeAIValidator()
schema = validator.get_validation_schema()

# Access validation rules
print(schema["strategy_combinations"])
print(schema["constraints"])
```

## 📈 Performance

- **Processing Time**: Typically < 10ms per prompt
- **Accuracy**: High confidence scores (>0.8) for well-formed prompts
- **Scalability**: Stateless design supports high-throughput processing
- **Memory**: Minimal memory footprint per operation

## 🛡️ Error Handling

The system provides comprehensive error handling:

- **Validation Errors**: Detailed feedback on Shade AI compatibility issues
- **Quality Warnings**: Recommendations for improving prompt clarity
- **Fallback Strategies**: Default values when specific parameters are missing
- **Graceful Degradation**: Continues processing even with partial information

## 🔮 Future Enhancements

- **Machine Learning**: Enhanced pattern recognition using ML models
- **Multi-Language Support**: Support for non-English prompts
- **Advanced Analytics**: Detailed performance metrics and insights
- **API Integration**: REST API for external system integration
- **Real-time Processing**: Stream processing for high-volume scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or contributions, please:

1. Check the existing issues
2. Create a new issue with detailed description
3. Provide example prompts and expected outputs
4. Include system information and error logs

---

**Built with ❤️ for the NEAR ecosystem**