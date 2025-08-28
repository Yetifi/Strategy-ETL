"""
Tests for the ETLProcessor class.
"""
import pytest
from unittest.mock import Mock, patch
from src.etl_processor import ETLProcessor, ETLProcessorFactory
from src.models import UserPrompt, TransformedPrompt, ETLResult, StrategyType, AssetType, RiskLevel


class TestETLProcessor:
    """Test cases for ETLProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create an ETLProcessor instance for testing."""
        return ETLProcessor()
    
    def test_extract_phase(self, processor):
        """Test the extract phase of the ETL pipeline."""
        raw_text = "I want to do yield farming with NEAR"
        user_id = "user123"
        metadata = {"source": "web"}
        
        result = processor.extract(raw_text, user_id, metadata)
        
        assert isinstance(result, UserPrompt)
        assert result.raw_text == raw_text
        assert result.user_id == user_id
        assert result.metadata == metadata
        assert result.id is not None
        assert result.timestamp is not None
    
    def test_transform_phase(self, processor):
        """Test the transform phase of the ETL pipeline."""
        user_prompt = UserPrompt(
            id="test_id",
            raw_text="Yield farming with NEAR for 20% APY over 90 days"
        )
        
        result = processor.transform(user_prompt)
        
        assert isinstance(result, TransformedPrompt)
        assert result.original_prompt_id == user_prompt.id
        assert result.strategy_type == StrategyType.YIELD_FARMING
        assert result.primary_asset == AssetType.NEAR
        assert result.risk_level == RiskLevel.MEDIUM
        assert result.target_apy == 20.0
        assert result.duration_days == 90
        assert result.confidence_score > 0.0
        assert len(result.transformation_notes) > 0
    
    def test_load_phase_success(self, processor):
        """Test successful load phase."""
        transformed_prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.8
        )
        
        result = processor.load(transformed_prompt)
        assert result is True
    
    def test_load_phase_with_storage_backend(self, processor):
        """Test load phase with storage backend."""
        transformed_prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.8
        )
        
        mock_storage = Mock()
        result = processor.load(transformed_prompt, mock_storage)
        assert result is True
    
    def test_complete_pipeline_success(self, processor):
        """Test the complete ETL pipeline with successful execution."""
        raw_text = "Provide liquidity to NEAR-USDC pool for medium risk"
        
        result = processor.process(raw_text)
        
        assert isinstance(result, ETLResult)
        assert result.success is True
        assert result.original_prompt.raw_text == raw_text
        assert result.transformed_prompt is not None
        assert result.transformed_prompt.strategy_type == StrategyType.LIQUIDITY_PROVIDING
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert result.transformed_prompt.secondary_assets == [AssetType.USDC]
        assert result.transformed_prompt.risk_level == RiskLevel.MEDIUM
        assert result.errors == []
        assert result.processing_time_ms >= 0
    
    def test_complete_pipeline_with_user_id(self, processor):
        """Test the complete ETL pipeline with user ID."""
        raw_text = "Stake NEAR tokens for rewards"
        user_id = "user456"
        
        result = processor.process(raw_text, user_id)
        
        assert result.success is True
        assert result.original_prompt.user_id == user_id
        assert result.transformed_prompt.strategy_type == StrategyType.STAKING
    
    def test_complete_pipeline_with_metadata(self, processor):
        """Test the complete ETL pipeline with metadata."""
        raw_text = "Arbitrage between NEAR and USDC"
        metadata = {"source": "mobile_app", "version": "1.0"}
        
        result = processor.process(raw_text, metadata=metadata)
        
        assert result.success is True
        assert result.original_prompt.metadata == metadata
        assert result.transformed_prompt.strategy_type == StrategyType.ARBITRAGE
    
    def test_pipeline_error_handling(self, processor):
        """Test error handling in the ETL pipeline."""
        # Mock the transform method to raise an exception
        with patch.object(processor, 'transform', side_effect=Exception("Transform error")):
            result = processor.process("test text")
            
            assert result.success is False
            assert result.transformed_prompt is None
            assert len(result.errors) > 0
            assert "ETL processing failed" in result.errors[0]
    
    def test_determine_execution_priority(self, processor):
        """Test execution priority determination."""
        # High risk should result in high priority
        priority = processor._determine_execution_priority(StrategyType.YIELD_FARMING, RiskLevel.HIGH)
        assert priority == "high"
        
        # Arbitrage should result in high priority
        priority = processor._determine_execution_priority(StrategyType.ARBITRAGE, RiskLevel.MEDIUM)
        assert priority == "high"
        
        # Normal case
        priority = processor._determine_execution_priority(StrategyType.STAKING, RiskLevel.LOW)
        assert priority == "normal"
    
    def test_should_auto_compound(self, processor):
        """Test auto-compound determination."""
        # Yield farming should auto-compound
        assert processor._should_auto_compound(StrategyType.YIELD_FARMING) is True
        
        # Staking should auto-compound
        assert processor._should_auto_compound(StrategyType.STAKING) is True
        
        # Arbitrage should not auto-compound
        assert processor._should_auto_compound(StrategyType.ARBITRAGE) is False


class TestETLProcessorFactory:
    """Test cases for ETLProcessorFactory."""
    
    def test_create_standard_processor(self):
        """Test creation of standard ETL processor."""
        processor = ETLProcessorFactory.create_standard_processor()
        assert isinstance(processor, ETLProcessor)
    
    def test_create_processor_with_custom_mapper(self):
        """Test creation of ETL processor with custom mapper."""
        from src.terminology_mapper import TerminologyMapper
        custom_mapper = TerminologyMapper()
        
        processor = ETLProcessorFactory.create_processor_with_custom_mapper(custom_mapper)
        assert isinstance(processor, ETLProcessor)
        assert processor.terminology_mapper is custom_mapper


class TestETLProcessorIntegration:
    """Integration tests for ETLProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create an ETLProcessor instance for testing."""
        return ETLProcessor()
    
    def test_yield_farming_strategy(self, processor):
        """Test complete processing of yield farming strategy."""
        raw_text = """
        I want to do yield farming on NEAR protocol.
        Use USDC and USDT for diversification.
        Target 25% APY over 6 months.
        Looking for medium risk strategies.
        """
        
        result = processor.process(raw_text)
        
        assert result.success is True
        assert result.transformed_prompt.strategy_type == StrategyType.YIELD_FARMING
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert AssetType.USDC in result.transformed_prompt.secondary_assets
        assert AssetType.USDT in result.transformed_prompt.secondary_assets
        assert result.transformed_prompt.target_apy == 25.0
        assert result.transformed_prompt.duration_days == 180
        assert result.transformed_prompt.risk_level == RiskLevel.MEDIUM
        assert result.transformed_prompt.auto_compound is True
    
    def test_liquidity_providing_strategy(self, processor):
        """Test complete processing of liquidity providing strategy."""
        raw_text = """
        Provide liquidity to NEAR-USDC pool.
        Low risk, stable returns.
        Duration: 1 year.
        """
        
        result = processor.process(raw_text)
        
        assert result.success is True
        assert result.transformed_prompt.strategy_type == StrategyType.LIQUIDITY_PROVIDING
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert AssetType.USDC in result.transformed_prompt.secondary_assets
        assert result.transformed_prompt.risk_level == RiskLevel.LOW
        assert result.transformed_prompt.duration_days == 365
        assert result.transformed_prompt.execution_priority == "normal"
    
    def test_staking_strategy(self, processor):
        """Test complete processing of staking strategy."""
        raw_text = "Stake my NEAR tokens for staking rewards"
        
        result = processor.process(raw_text)
        
        assert result.success is True
        assert result.transformed_prompt.strategy_type == StrategyType.STAKING
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert result.transformed_prompt.auto_compound is True
    
    def test_arbitrage_strategy(self, processor):
        """Test complete processing of arbitrage strategy."""
        raw_text = """
        Find arbitrage opportunities between NEAR and USDC.
        High risk, high reward.
        Execute quickly.
        """
        
        result = processor.process(raw_text)
        
        assert result.success is True
        assert result.transformed_prompt.strategy_type == StrategyType.ARBITRAGE
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert AssetType.USDC in result.transformed_prompt.secondary_assets
        assert result.transformed_prompt.risk_level == RiskLevel.HIGH
        assert result.transformed_prompt.execution_priority == "high"
    
    def test_swapping_strategy(self, processor):
        """Test complete processing of swapping strategy."""
        raw_text = "Swap NEAR for USDC and then back to NEAR"
        
        result = processor.process(raw_text)
        
        assert result.success is True
        assert result.transformed_prompt.strategy_type == StrategyType.SWAPPING
        assert result.transformed_prompt.primary_asset == AssetType.NEAR
        assert AssetType.USDC in result.transformed_prompt.secondary_assets
        assert result.transformed_prompt.execution_priority == "high"
    
    def test_edge_cases_and_variations(self, processor):
        """Test various edge cases and input variations."""
        test_cases = [
            # Minimal input
            ("yield farming", StrategyType.YIELD_FARMING),
            
            # Mixed case
            ("YIELD FARMING with NEAR", StrategyType.YIELD_FARMING),
            
            # With extra whitespace
            ("  liquidity   providing  ", StrategyType.LIQUIDITY_PROVIDING),
            
            # With punctuation
            ("Stake NEAR tokens!", StrategyType.STAKING),
            
            # With numbers and symbols
            ("25% APY yield farming", StrategyType.YIELD_FARMING),
            
            # Complex sentence
            ("I would like to engage in yield farming activities on the NEAR blockchain using USDC and USDT tokens with a target return of 20% annually over a period of 6 months while maintaining a moderate risk profile", StrategyType.YIELD_FARMING)
        ]
        
        for raw_text, expected_strategy in test_cases:
            result = processor.process(raw_text)
            assert result.success is True
            assert result.transformed_prompt.strategy_type == expected_strategy
            assert result.transformed_prompt.confidence_score > 0.0
