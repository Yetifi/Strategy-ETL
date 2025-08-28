"""
Tests for the TerminologyMapper class.
"""
import pytest
from src.terminology_mapper import TerminologyMapper
from src.models import StrategyType, AssetType, RiskLevel


class TestTerminologyMapper:
    """Test cases for TerminologyMapper."""
    
    @pytest.fixture
    def mapper(self):
        """Create a TerminologyMapper instance for testing."""
        return TerminologyMapper()
    
    def test_normalize_text(self, mapper):
        """Test text normalization."""
        text = "  Yield   Farming   Strategy  "
        normalized = mapper.normalize_text(text)
        assert normalized == "yield farming strategy"
    
    def test_detect_strategy_type_yield_farming(self, mapper):
        """Test detection of yield farming strategy."""
        text = "I want to farm yield with high APY"
        strategy_type, confidence = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.YIELD_FARMING
        assert confidence > 0.0
    
    def test_detect_strategy_type_liquidity_providing(self, mapper):
        """Test detection of liquidity providing strategy."""
        text = "Provide liquidity to the NEAR-USDC pool"
        strategy_type, confidence = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.LIQUIDITY_PROVIDING
        assert confidence > 0.0
    
    def test_detect_strategy_type_staking(self, mapper):
        """Test detection of staking strategy."""
        text = "Stake my NEAR tokens for rewards"
        strategy_type, confidence = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.STAKING
        assert confidence > 0.0
    
    def test_detect_strategy_type_arbitrage(self, mapper):
        """Test detection of arbitrage strategy."""
        text = "Find arbitrage opportunities between exchanges"
        strategy_type, confidence = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.ARBITRAGE
        assert confidence > 0.0
    
    def test_detect_strategy_type_default(self, mapper):
        """Test default strategy type when no clear match."""
        text = "Some random text without strategy keywords"
        strategy_type, confidence = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.YIELD_FARMING
        assert confidence == 0.3
    
    def test_detect_assets_near(self, mapper):
        """Test detection of NEAR asset."""
        text = "I want to use NEAR protocol for yield farming"
        assets, confidence = mapper.detect_assets(text)
        assert AssetType.NEAR in assets
        assert confidence > 0.0
    
    def test_detect_assets_stablecoins(self, mapper):
        """Test detection of stablecoin assets."""
        text = "Use USDC and USDT for liquidity providing"
        assets, confidence = mapper.detect_assets(text)
        assert AssetType.USDC in assets
        assert AssetType.USDT in assets
        assert confidence > 0.0
    
    def test_detect_assets_multiple(self, mapper):
        """Test detection of multiple assets."""
        text = "Trade between NEAR, USDC, and WBTC"
        assets, confidence = mapper.detect_assets(text)
        assert AssetType.NEAR in assets
        assert AssetType.USDC in assets
        assert AssetType.WBTC in assets
        assert confidence > 0.0
    
    def test_detect_assets_default(self, mapper):
        """Test default asset when none detected."""
        text = "Some text without asset mentions"
        assets, confidence = mapper.detect_assets(text)
        assert assets == [AssetType.NEAR]
        assert confidence == 0.2
    
    def test_detect_risk_level_low(self, mapper):
        """Test detection of low risk level."""
        text = "I want a safe and conservative strategy"
        risk_level, confidence = mapper.detect_risk_level(text)
        assert risk_level == RiskLevel.LOW
        assert confidence > 0.0
    
    def test_detect_risk_level_high(self, mapper):
        """Test detection of high risk level."""
        text = "I'm looking for aggressive and volatile strategies"
        risk_level, confidence = mapper.detect_risk_level(text)
        assert risk_level == RiskLevel.HIGH
        assert confidence > 0.0
    
    def test_detect_risk_level_default(self, mapper):
        """Test default risk level when none detected."""
        text = "Some text without risk keywords"
        risk_level, confidence = mapper.detect_risk_level(text)
        assert risk_level == RiskLevel.MEDIUM
        assert confidence == 0.0
    
    def test_extract_numerical_values_apy(self, mapper):
        """Test extraction of APY values."""
        text = "I want 15% APY from yield farming"
        values = mapper.extract_numerical_values(text)
        assert values['target_apy'] == 15.0
    
    def test_extract_numerical_values_duration(self, mapper):
        """Test extraction of duration values."""
        text = "Strategy should run for 30 days"
        values = mapper.extract_numerical_values(text)
        assert values['duration_days'] == 30
    
    def test_extract_numerical_values_multiple(self, mapper):
        """Test extraction of multiple numerical values."""
        text = "Target 25% APY over 90 days"
        values = mapper.extract_numerical_values(text)
        assert values['target_apy'] == 25.0
        assert values['duration_days'] == 90
    
    def test_extract_numerical_values_units(self, mapper):
        """Test extraction with different time units."""
        text = "Strategy for 2 weeks with 10% APY"
        values = mapper.extract_numerical_values(text)
        assert values['target_apy'] == 10.0
        assert values['duration_days'] == 14  # 2 weeks
    
    def test_map_to_near_terms(self, mapper):
        """Test mapping to NEAR-specific terms."""
        text = "I want to do yield farming and use liquidity pools"
        mapped = mapper.map_to_near_terms(text)
        assert "NEAR yield farming" in mapped
        assert "NEAR liquidity pool" in mapped
    
    def test_generate_transformation_notes(self, mapper):
        """Test generation of transformation notes."""
        detected_items = {
            'strategy_type': StrategyType.YIELD_FARMING,
            'assets': [AssetType.NEAR, AssetType.USDC],
            'risk_level': RiskLevel.MEDIUM,
            'target_apy': 20.0,
            'duration_days': 60
        }
        notes = mapper.generate_transformation_notes("test text", detected_items)
        assert len(notes) == 5
        assert "Detected strategy type: yield_farming" in notes
        assert "Detected assets: NEAR, USDC" in notes
        assert "Detected risk level: medium" in notes
        assert "Extracted target APY: 20.0%" in notes
        assert "Extracted duration: 60 days" in notes


class TestTerminologyMapperIntegration:
    """Integration tests for TerminologyMapper."""
    
    @pytest.fixture
    def mapper(self):
        """Create a TerminologyMapper instance for testing."""
        return TerminologyMapper()
    
    def test_complete_strategy_analysis(self, mapper):
        """Test complete analysis of a complex strategy prompt."""
        text = """
        I want to do yield farming on NEAR protocol with USDC and USDT.
        Target 18% APY over 6 months. Looking for medium risk strategies.
        """
        
        # Test strategy type detection
        strategy_type, strategy_conf = mapper.detect_strategy_type(text)
        assert strategy_type == StrategyType.YIELD_FARMING
        assert strategy_conf > 0.0
        
        # Test asset detection
        assets, assets_conf = mapper.detect_assets(text)
        assert AssetType.NEAR in assets
        assert AssetType.USDC in assets
        assert AssetType.USDT in assets
        assert assets_conf > 0.0
        
        # Test risk level detection
        risk_level, risk_conf = mapper.detect_risk_level(text)
        assert risk_level == RiskLevel.MEDIUM
        assert risk_conf > 0.0
        
        # Test numerical value extraction
        values = mapper.extract_numerical_values(text)
        assert values['target_apy'] == 18.0
        assert values['duration_days'] == 180  # 6 months
        
        # Test NEAR term mapping
        mapped = mapper.map_to_near_terms(text)
        assert "NEAR protocol" in mapped
        assert "NEAR yield farming" in mapped
    
    def test_edge_cases(self, mapper):
        """Test edge cases and unusual inputs."""
        # Empty text
        strategy_type, conf = mapper.detect_strategy_type("")
        assert strategy_type == StrategyType.YIELD_FARMING
        assert conf == 0.3
        
        # Very long text
        long_text = "yield farming " * 100
        strategy_type, conf = mapper.detect_strategy_type(long_text)
        assert strategy_type == StrategyType.YIELD_FARMING
        assert conf > 0.0
        
        # Mixed case text
        mixed_text = "YIELD FARMING with NEAR and USDC"
        strategy_type, conf = mapper.detect_strategy_type(mixed_text)
        assert strategy_type == StrategyType.YIELD_FARMING
        assert conf > 0.0
        
        # Text with numbers and symbols
        symbol_text = "Strategy: 25% APY, 90 days, NEAR/USDC"
        values = mapper.extract_numerical_values(symbol_text)
        assert values['target_apy'] == 25.0
        assert values['duration_days'] == 90
