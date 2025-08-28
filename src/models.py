"""
Data models for the Strategy ETL system.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class StrategyType(str, Enum):
    """Types of DeFi strategies supported by Shade AI."""
    YIELD_FARMING = "yield_farming"
    LIQUIDITY_PROVIDING = "liquidity_providing"
    LENDING = "lending"
    BORROWING = "borrowing"
    STAKING = "staking"
    SWAPPING = "swapping"
    ARBITRAGE = "arbitrage"
    COMPOUNDING = "compounding"


class AssetType(str, Enum):
    """Types of assets supported by NEAR protocol."""
    NEAR = "NEAR"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    WBTC = "WBTC"
    ETH = "ETH"
    SHADE = "SHADE"
    STNEAR = "stNEAR"
    LINEAR = "LINEAR"
    META = "META"


class RiskLevel(str, Enum):
    """Risk levels for strategies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UserPrompt(BaseModel):
    """Raw user input prompt."""
    id: str = Field(..., description="Unique identifier for the prompt")
    raw_text: str = Field(..., description="Original user input text")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransformedPrompt(BaseModel):
    """Transformed prompt compatible with Shade AI."""
    id: str = Field(..., description="Unique identifier")
    original_prompt_id: str = Field(..., description="Reference to original prompt")
    
    # Core strategy parameters
    strategy_type: StrategyType = Field(..., description="Type of DeFi strategy")
    primary_asset: AssetType = Field(..., description="Primary asset to trade/manage")
    secondary_assets: List[AssetType] = Field(default_factory=list, description="Secondary assets")
    
    # Strategy configuration
    risk_level: RiskLevel = Field(..., description="Risk level of the strategy")
    target_apy: Optional[float] = Field(None, description="Target annual percentage yield")
    duration_days: Optional[int] = Field(None, description="Strategy duration in days")
    
    # NEAR-specific parameters
    near_protocol: str = Field(default="NEAR", description="NEAR protocol identifier")
    shade_ai_compatible: bool = Field(default=True, description="Compatibility flag")
    
    # Execution parameters
    execution_priority: str = Field(default="normal", description="Execution priority")
    auto_compound: bool = Field(default=False, description="Auto-compound flag")
    
    # Metadata
    confidence_score: float = Field(..., description="Confidence in transformation accuracy")
    transformation_notes: List[str] = Field(default_factory=list, description="Notes about transformation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence score must be between 0.0 and 1.0')
        return v


class ETLResult(BaseModel):
    """Result of the ETL process."""
    success: bool = Field(..., description="Whether the ETL process succeeded")
    original_prompt: UserPrompt = Field(..., description="Original user prompt")
    transformed_prompt: Optional[TransformedPrompt] = Field(None, description="Transformed prompt")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
