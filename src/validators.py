"""
Validators for ensuring Shade AI compatibility.
"""
from typing import List, Dict, Any, Tuple
from .models import TransformedPrompt, StrategyType, AssetType, RiskLevel


class ShadeAIValidator:
    """
    Validates that transformed prompts are compatible with Shade AI agent.
    """
    
    def __init__(self):
        # Required fields for Shade AI compatibility
        self.required_fields = [
            'strategy_type', 'primary_asset', 'risk_level', 'confidence_score'
        ]
        
        # Valid strategy combinations
        self.valid_strategy_combinations = {
            StrategyType.YIELD_FARMING: {
                'required_assets': [AssetType.NEAR, AssetType.USDC, AssetType.USDT],
                'optional_assets': [AssetType.SHADE, AssetType.STNEAR, AssetType.LINEAR],
                'min_confidence': 0.4
            },
            StrategyType.LIQUIDITY_PROVIDING: {
                'required_assets': [AssetType.NEAR, AssetType.USDC],
                'optional_assets': [AssetType.USDT, AssetType.DAI, AssetType.WBTC, AssetType.ETH],
                'min_confidence': 0.5
            },
            StrategyType.STAKING: {
                'required_assets': [AssetType.NEAR],
                'optional_assets': [AssetType.STNEAR, AssetType.SHADE],
                'min_confidence': 0.6
            },
            StrategyType.LENDING: {
                'required_assets': [AssetType.NEAR, AssetType.USDC, AssetType.USDT],
                'optional_assets': [AssetType.DAI, AssetType.WBTC, AssetType.ETH],
                'min_confidence': 0.5
            },
            StrategyType.BORROWING: {
                'required_assets': [AssetType.NEAR, AssetType.USDC],
                'optional_assets': [AssetType.USDT, AssetType.DAI],
                'min_confidence': 0.6
            },
            StrategyType.SWAPPING: {
                'required_assets': [AssetType.NEAR],
                'optional_assets': [AssetType.USDC, AssetType.USDT, AssetType.DAI, AssetType.WBTC, AssetType.ETH],
                'min_confidence': 0.4
            },
            StrategyType.ARBITRAGE: {
                'required_assets': [AssetType.NEAR, AssetType.USDC],
                'optional_assets': [AssetType.USDT, AssetType.DAI, AssetType.WBTC, AssetType.ETH],
                'min_confidence': 0.7
            },
            StrategyType.COMPOUNDING: {
                'required_assets': [AssetType.NEAR, AssetType.USDC],
                'optional_assets': [AssetType.USDT, AssetType.SHADE, AssetType.STNEAR],
                'min_confidence': 0.5
            }
        }
    
    def validate_prompt(self, prompt: TransformedPrompt) -> Tuple[bool, List[str]]:
        """
        Validate a transformed prompt for Shade AI compatibility.
        
        Args:
            prompt: The transformed prompt to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if not hasattr(prompt, field) or getattr(prompt, field) is None:
                errors.append(f"Missing required field: {field}")
        
        # Check strategy type validity
        if prompt.strategy_type not in self.valid_strategy_combinations:
            errors.append(f"Invalid strategy type: {prompt.strategy_type}")
            return False, errors
        
        # Get strategy requirements
        strategy_reqs = self.valid_strategy_combinations[prompt.strategy_type]
        
        # Check confidence score
        if prompt.confidence_score is None:
            errors.append("Missing required field: confidence_score")
        elif prompt.confidence_score < strategy_reqs['min_confidence']:
            errors.append(
                f"Confidence score {prompt.confidence_score:.2f} below minimum "
                f"{strategy_reqs['min_confidence']} for {prompt.strategy_type.value}"
            )
        
        # Check primary asset compatibility
        if prompt.primary_asset:
            if (prompt.primary_asset not in strategy_reqs['required_assets'] and 
                prompt.primary_asset not in strategy_reqs['optional_assets']):
                errors.append(
                    f"Primary asset {prompt.primary_asset.value} not compatible with "
                    f"strategy type {prompt.strategy_type.value}"
                )
        
        # Check secondary assets compatibility
        for asset in prompt.secondary_assets:
            if (asset not in strategy_reqs['required_assets'] and 
                asset not in strategy_reqs['optional_assets']):
                errors.append(
                    f"Secondary asset {asset.value} not compatible with "
                    f"strategy type {prompt.strategy_type.value}"
                )
        
        # Check for required assets
        if prompt.primary_asset not in strategy_reqs['required_assets']:
            errors.append(
                f"Strategy {prompt.strategy_type.value} requires one of: "
                f"{[a.value for a in strategy_reqs['required_assets']]}"
            )
        
        # Check numerical constraints
        if prompt.target_apy is not None:
            if prompt.target_apy < 0 or prompt.target_apy > 1000:
                errors.append("Target APY must be between 0% and 1000%")
        
        if prompt.duration_days is not None:
            if prompt.duration_days < 1 or prompt.duration_days > 3650:  # 10 years max
                errors.append("Duration must be between 1 and 3650 days")
        
        # Check NEAR protocol compatibility
        if prompt.near_protocol != "NEAR":
            errors.append("Protocol must be NEAR for Shade AI compatibility")
        
        # Check Shade AI compatibility flag
        if not prompt.shade_ai_compatible:
            errors.append("Prompt must be marked as Shade AI compatible")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_validation_schema(self) -> Dict[str, Any]:
        """
        Get the validation schema for Shade AI compatibility.
        
        Returns:
            Dictionary containing the validation schema
        """
        return {
            "required_fields": self.required_fields,
            "strategy_combinations": {
                strategy.value: {
                    "required_assets": [asset.value for asset in reqs['required_assets']],
                    "optional_assets": [asset.value for asset in reqs['optional_assets']],
                    "min_confidence": reqs['min_confidence']
                }
                for strategy, reqs in self.valid_strategy_combinations.items()
            },
            "constraints": {
                "target_apy_range": [0, 1000],
                "duration_days_range": [1, 3650],
                "confidence_score_range": [0.0, 1.0]
            }
        }


class PromptQualityValidator:
    """
    Validates the quality and completeness of transformed prompts.
    """
    
    def __init__(self):
        self.quality_thresholds = {
            'min_confidence': 0.5,
            'min_assets': 1,
            'max_secondary_assets': 5,
            'min_transformation_notes': 1
        }
    
    def assess_quality(self, prompt: TransformedPrompt) -> Dict[str, Any]:
        """
        Assess the quality of a transformed prompt.
        
        Args:
            prompt: The transformed prompt to assess
            
        Returns:
            Dictionary containing quality metrics and recommendations
        """
        quality_score = 0.0
        max_score = 100.0
        recommendations = []
        
        # Confidence score (30 points)
        if prompt.confidence_score >= 0.8:
            quality_score += 30
        elif prompt.confidence_score >= 0.6:
            quality_score += 20
        elif prompt.confidence_score >= 0.4:
            quality_score += 10
        
        if prompt.confidence_score < 0.6:
            recommendations.append("Consider improving prompt clarity for better confidence")
        
        # Asset completeness (25 points)
        if prompt.primary_asset:
            quality_score += 15
        if prompt.secondary_assets:
            quality_score += min(len(prompt.secondary_assets) * 2, 10)
        
        if not prompt.secondary_assets:
            recommendations.append("Consider adding secondary assets for strategy diversification")
        
        # Strategy parameters (25 points)
        if prompt.target_apy is not None:
            quality_score += 15
        if prompt.duration_days is not None:
            quality_score += 10
        
        if prompt.target_apy is None:
            recommendations.append("Consider specifying target APY for better strategy definition")
        
        # Transformation notes (20 points)
        if prompt.transformation_notes:
            quality_score += min(len(prompt.transformation_notes) * 4, 20)
        
        if not prompt.transformation_notes:
            recommendations.append("Add transformation notes for better traceability")
        
        # Quality level classification
        if quality_score >= 80:
            quality_level = "Excellent"
        elif quality_score >= 60:
            quality_level = "Good"
        elif quality_score >= 40:
            quality_level = "Fair"
        else:
            quality_level = "Poor"
        
        return {
            "quality_score": quality_score,
            "max_score": max_score,
            "quality_level": quality_level,
            "recommendations": recommendations,
            "confidence_score": prompt.confidence_score,
            "asset_completeness": bool(prompt.primary_asset),
            "parameter_completeness": prompt.target_apy is not None or prompt.duration_days is not None,
            "transformation_notes_count": len(prompt.transformation_notes)
        }
