"""
Tests for the validators.
"""
import pytest
from src.validators import ShadeAIValidator, PromptQualityValidator
from src.models import TransformedPrompt, StrategyType, AssetType, RiskLevel


class TestShadeAIValidator:
    """Test cases for ShadeAIValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a ShadeAIValidator instance for testing."""
        return ShadeAIValidator()
    
    @pytest.fixture
    def valid_prompt(self):
        """Create a valid transformed prompt for testing."""
        return TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            secondary_assets=[AssetType.USDC],
            risk_level=RiskLevel.MEDIUM,
            target_apy=20.0,
            duration_days=90,
            confidence_score=0.8,
            transformation_notes=["Test note"]
        )
    
    def test_validate_prompt_success(self, validator, valid_prompt):
        """Test successful validation of a valid prompt."""
        is_valid, errors = validator.validate_prompt(valid_prompt)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_prompt_missing_required_fields(self, validator):
        """Test validation failure due to missing required fields."""
        # Missing confidence_score - create with minimal required fields then modify
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.5
        )
        # Manually set to None to test validation
        prompt.confidence_score = None
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Missing required field: confidence_score" in errors
    
    def test_validate_prompt_invalid_strategy_type(self, validator):
        """Test validation failure due to invalid strategy type."""
        # Create a prompt with an invalid strategy type - create with valid type then modify
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.8
        )
        # Manually set to invalid type to test validation
        prompt.strategy_type = "invalid_strategy"
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Invalid strategy type" in errors[0]
    
    def test_validate_prompt_low_confidence(self, validator):
        """Test validation failure due to low confidence score."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.ARBITRAGE,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.5  # Below minimum 0.7 for arbitrage
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Confidence score 0.50 below minimum 0.7" in errors[0]
    
    def test_validate_prompt_incompatible_assets(self, validator):
        """Test validation failure due to incompatible assets."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.STAKING,
            primary_asset=AssetType.WBTC,  # Not compatible with staking
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Primary asset WBTC not compatible with strategy type staking" in errors
    
    def test_validate_prompt_missing_required_assets(self, validator):
        """Test validation failure due to missing required assets."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.LIQUIDITY_PROVIDING,
            primary_asset=AssetType.SHADE,  # Not in required assets for LP
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Strategy liquidity_providing requires one of: ['NEAR', 'USDC']" in errors
    
    def test_validate_prompt_invalid_apy(self, validator):
        """Test validation failure due to invalid APY values."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            target_apy=1500.0,  # Above maximum 1000%
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Target APY must be between 0% and 1000%" in errors
    
    def test_validate_prompt_invalid_duration(self, validator):
        """Test validation failure due to invalid duration values."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            duration_days=5000,  # Above maximum 3650 days
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Duration must be between 1 and 3650 days" in errors
    
    def test_validate_prompt_wrong_protocol(self, validator):
        """Test validation failure due to wrong protocol."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            near_protocol="ETHEREUM",  # Wrong protocol
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Protocol must be NEAR for Shade AI compatibility" in errors
    
    def test_validate_prompt_not_shade_compatible(self, validator):
        """Test validation failure due to Shade AI incompatibility."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            shade_ai_compatible=False,  # Not compatible
            confidence_score=0.8
        )
        
        is_valid, errors = validator.validate_prompt(prompt)
        assert is_valid is False
        assert "Prompt must be marked as Shade AI compatible" in errors
    
    def test_get_validation_schema(self, validator):
        """Test retrieval of validation schema."""
        schema = validator.get_validation_schema()
        
        assert "required_fields" in schema
        assert "strategy_combinations" in schema
        assert "constraints" in schema
        
        # Check that all strategy types are included
        assert len(schema["strategy_combinations"]) == 8  # All 8 strategy types
        
        # Check constraints
        assert schema["constraints"]["target_apy_range"] == [0, 1000]
        assert schema["constraints"]["duration_days_range"] == [1, 3650]
        assert schema["constraints"]["confidence_score_range"] == [0.0, 1.0]


class TestPromptQualityValidator:
    """Test cases for PromptQualityValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a PromptQualityValidator instance for testing."""
        return PromptQualityValidator()
    
    @pytest.fixture
    def high_quality_prompt(self):
        """Create a high-quality transformed prompt for testing."""
        return TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            secondary_assets=[AssetType.USDC, AssetType.USDT],
            risk_level=RiskLevel.MEDIUM,
            target_apy=25.0,
            duration_days=90,
            confidence_score=0.9,
            transformation_notes=["Note 1", "Note 2", "Note 3"]
        )
    
    @pytest.fixture
    def low_quality_prompt(self):
        """Create a low-quality transformed prompt for testing."""
        return TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.3,
            transformation_notes=[]
        )
    
    def test_assess_quality_excellent(self, validator, high_quality_prompt):
        """Test quality assessment for excellent prompt."""
        result = validator.assess_quality(high_quality_prompt)
        
        assert result["quality_score"] >= 80
        assert result["quality_level"] == "Excellent"
        assert result["confidence_score"] == 0.9
        assert result["asset_completeness"] is True
        assert result["parameter_completeness"] is True
        assert result["transformation_notes_count"] == 3
    
    def test_assess_quality_poor(self, validator, low_quality_prompt):
        """Test quality assessment for poor prompt."""
        result = validator.assess_quality(low_quality_prompt)
        
        assert result["quality_score"] < 40
        assert result["quality_level"] == "Poor"
        assert result["confidence_score"] == 0.3
        assert result["asset_completeness"] is True
        assert result["parameter_completeness"] is False
        assert result["transformation_notes_count"] == 0
    
    def test_assess_quality_good(self, validator):
        """Test quality assessment for good prompt."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            secondary_assets=[AssetType.USDC],
            risk_level=RiskLevel.MEDIUM,
            target_apy=20.0,
            confidence_score=0.7,
            transformation_notes=["Test note"]
        )
        
        result = validator.assess_quality(prompt)
        
        # With 0.7 confidence (20), primary asset (15), secondary asset (2), APY (15), notes (4) = 56 points
        assert 40 <= result["quality_score"] < 60
        assert result["quality_level"] == "Fair"
    
    def test_assess_quality_fair(self, validator):
        """Test quality assessment for fair prompt."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.5,
            transformation_notes=[]
        )
        
        result = validator.assess_quality(prompt)
        
        # With 0.5 confidence (10), primary asset (15) = 25 points
        assert 20 <= result["quality_score"] < 40
        assert result["quality_level"] == "Poor"
    
    def test_quality_scoring_breakdown(self, validator):
        """Test detailed quality scoring breakdown."""
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            secondary_assets=[AssetType.USDC, AssetType.USDT],
            risk_level=RiskLevel.MEDIUM,
            target_apy=20.0,
            duration_days=90,
            confidence_score=0.8,
            transformation_notes=["Note 1", "Note 2"]
        )
        
        result = validator.assess_quality(prompt)
        
        # Confidence score: 0.8 = 20 points
        # Assets: primary (15) + secondary (4) = 19 points
        # Parameters: APY (15) + duration (10) = 25 points
        # Notes: 2 notes = 8 points
        # Total: 20 + 19 + 25 + 8 = 82 points (Excellent)
        
        assert result["quality_score"] == 82
        assert result["quality_level"] == "Excellent"
    
    def test_recommendations_generation(self, validator, low_quality_prompt):
        """Test generation of quality improvement recommendations."""
        result = validator.assess_quality(low_quality_prompt)
        
        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        
        # Should recommend improving prompt clarity due to low confidence
        assert any("improving prompt clarity" in rec.lower() for rec in recommendations)
        
        # Should recommend adding secondary assets
        assert any("secondary assets" in rec.lower() for rec in recommendations)
        
        # Should recommend specifying target APY
        assert any("target apy" in rec.lower() for rec in recommendations)
        
        # Should recommend adding transformation notes
        assert any("transformation notes" in rec.lower() for rec in recommendations)
    
    def test_quality_thresholds(self, validator):
        """Test quality threshold configurations."""
        thresholds = validator.quality_thresholds
        
        assert thresholds["min_confidence"] == 0.5
        assert thresholds["min_assets"] == 1
        assert thresholds["max_secondary_assets"] == 5
        assert thresholds["min_transformation_notes"] == 1


class TestValidatorIntegration:
    """Integration tests for validators."""
    
    @pytest.fixture
    def shade_validator(self):
        """Create a ShadeAIValidator instance for testing."""
        return ShadeAIValidator()
    
    @pytest.fixture
    def quality_validator(self):
        """Create a PromptQualityValidator instance for testing."""
        return PromptQualityValidator()
    
    def test_complete_validation_workflow(self, shade_validator, quality_validator):
        """Test complete validation workflow for a prompt."""
        # Create a prompt that should pass both validations
        prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            secondary_assets=[AssetType.USDC],
            risk_level=RiskLevel.MEDIUM,
            target_apy=20.0,
            duration_days=90,
            confidence_score=0.8,
            transformation_notes=["Detected strategy type: yield_farming", "Detected assets: NEAR, USDC"]
        )
        
        # Validate Shade AI compatibility
        is_shade_compatible, shade_errors = shade_validator.validate_prompt(prompt)
        assert is_shade_compatible is True
        assert len(shade_errors) == 0
        
        # Assess quality
        quality_result = quality_validator.assess_quality(prompt)
        assert quality_result["quality_level"] in ["Good", "Excellent"]
        assert quality_result["quality_score"] >= 60
    
    def test_validation_edge_cases(self, shade_validator, quality_validator):
        """Test validation edge cases."""
        # Test with minimum viable prompt
        minimal_prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.YIELD_FARMING,
            primary_asset=AssetType.NEAR,
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.4  # Minimum for yield farming
        )
        
        # Should pass Shade validation
        is_valid, errors = shade_validator.validate_prompt(minimal_prompt)
        assert is_valid is True
        
        # But quality should be lower
        quality_result = quality_validator.assess_quality(minimal_prompt)
        assert quality_result["quality_level"] in ["Fair", "Poor"]
    
    def test_validation_failure_scenarios(self, shade_validator):
        """Test various validation failure scenarios."""
        # Test with completely invalid prompt
        invalid_prompt = TransformedPrompt(
            id="test_id",
            original_prompt_id="orig_id",
            strategy_type=StrategyType.ARBITRAGE,
            primary_asset=AssetType.SHADE,  # Not compatible with arbitrage
            risk_level=RiskLevel.MEDIUM,
            confidence_score=0.5,  # Below minimum for arbitrage
            near_protocol="ETHEREUM",  # Wrong protocol
            shade_ai_compatible=False  # Not compatible
        )
        
        is_valid, errors = shade_validator.validate_prompt(invalid_prompt)
        assert is_valid is False
        assert len(errors) >= 3  # Multiple validation failures
        
        # Check specific error types
        error_messages = [error.lower() for error in errors]
        assert any("confidence score" in msg for msg in error_messages)
        assert any("not compatible" in msg for msg in error_messages)
        assert any("protocol must be near" in msg for msg in error_messages)
        assert any("shade ai compatible" in msg for msg in error_messages)
