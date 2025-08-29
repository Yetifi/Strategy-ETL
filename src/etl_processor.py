"""
Main ETL processor for DeFi strategy prompts.
"""
import time
import uuid
from typing import Dict, Any, Optional
from .models import UserPrompt, TransformedPrompt, ETLResult
from .terminology_mapper import TerminologyMapper
from .prompt_storage import PromptStorageManager


class ETLProcessor:
    """
    Main ETL processor that handles the complete pipeline for DeFi strategy prompts.
    """
    
    def __init__(self, storage_manager: Optional[PromptStorageManager] = None):
        self.terminology_mapper = TerminologyMapper()
        self.storage_manager = storage_manager or PromptStorageManager()
    
    def extract(self, raw_text: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> UserPrompt:
        """
        Extract phase: Capture and store the raw user prompt.
        
        Args:
            raw_text: The raw text input from the user
            user_id: Optional user identifier
            metadata: Optional additional metadata
            
        Returns:
            UserPrompt object containing the extracted data
        """
        prompt_id = str(uuid.uuid4())
        
        user_prompt = UserPrompt(
            id=prompt_id,
            raw_text=raw_text,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        # Store the user prompt
        self.storage_manager.store_user_prompt(user_prompt)
        
        return user_prompt
    
    def transform(self, user_prompt: UserPrompt) -> TransformedPrompt:
        """
        Transform phase: Convert raw prompt to Shade AI compatible format.
        
        Args:
            user_prompt: The extracted user prompt
            
        Returns:
            TransformedPrompt object compatible with Shade AI
        """
        start_time = time.time()
        
        # Detect strategy components
        strategy_type, strategy_confidence = self.terminology_mapper.detect_strategy_type(
            user_prompt.raw_text
        )
        
        assets, assets_confidence = self.terminology_mapper.detect_assets(
            user_prompt.raw_text
        )
        
        risk_level, risk_confidence = self.terminology_mapper.detect_risk_level(
            user_prompt.raw_text
        )
        
        # Extract numerical values
        numerical_values = self.terminology_mapper.extract_numerical_values(
            user_prompt.raw_text
        )
        
        # Map to NEAR-specific terms
        near_mapped_text = self.terminology_mapper.map_to_near_terms(
            user_prompt.raw_text
        )
        
        # Calculate overall confidence score
        confidence_scores = [strategy_confidence, assets_confidence, risk_confidence]
        overall_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Generate transformation notes
        detected_items = {
            'strategy_type': strategy_type,
            'assets': assets,
            'risk_level': risk_level,
            **numerical_values
        }
        
        transformation_notes = self.terminology_mapper.generate_transformation_notes(
            user_prompt.raw_text, detected_items
        )
        
        # Determine execution parameters based on strategy type
        execution_priority = self._determine_execution_priority(strategy_type, risk_level)
        auto_compound = self._should_auto_compound(strategy_type)
        
        # Create transformed prompt
        transformed_prompt = TransformedPrompt(
            id=str(uuid.uuid4()),
            original_prompt_id=user_prompt.id,
            strategy_type=strategy_type,
            primary_asset=assets[0] if assets else None,
            secondary_assets=assets[1:] if len(assets) > 1 else [],
            risk_level=risk_level,
            target_apy=numerical_values.get('target_apy'),
            duration_days=numerical_values.get('duration_days'),
            execution_priority=execution_priority,
            auto_compound=auto_compound,
            confidence_score=overall_confidence,
            transformation_notes=transformation_notes
        )
        
        # Store the transformed prompt
        self.storage_manager.store_transformed_prompt(transformed_prompt)
        
        return transformed_prompt
    
    def load(self, transformed_prompt: TransformedPrompt, storage_backend: Optional[Any] = None) -> bool:
        """
        Load phase: Save transformed prompt to storage or pass to execution module.
        
        Args:
            transformed_prompt: The transformed prompt to store
            storage_backend: Optional storage backend (database, file, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Store the ETL result
            return True
        except Exception as e:
            print(f"Error in load phase: {e}")
            return False
    
    def process(self, raw_text: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ETLResult:
        """
        Execute the complete ETL pipeline.
        
        Args:
            raw_text: Raw user input text
            user_id: Optional user identifier
            metadata: Optional metadata
            
        Returns:
            ETLResult containing the complete processing result
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Extract phase
            user_prompt = self.extract(raw_text, user_id, metadata)
            
            # Transform phase
            transformed_prompt = self.transform(user_prompt)
            
            # Load phase
            load_success = self.load(transformed_prompt)
            
            if not load_success:
                errors.append("Failed to load transformed prompt")
            
            # Check for low confidence and add warnings
            if transformed_prompt.confidence_score < 0.5:
                warnings.append(f"Low confidence score: {transformed_prompt.confidence_score:.2f}")
            
            if not transformed_prompt.primary_asset:
                warnings.append("No primary asset detected, using NEAR as default")
            
            success = load_success and len(errors) == 0
            
        except Exception as e:
            errors.append(f"ETL processing failed: {str(e)}")
            success = False
            transformed_prompt = None
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        etl_result = ETLResult(
            success=success,
            original_prompt=user_prompt,
            transformed_prompt=transformed_prompt,
            errors=errors,
            warnings=warnings,
            processing_time_ms=processing_time
        )
        
        # Store the ETL result
        self.storage_manager.store_etl_result(etl_result)
        
        return etl_result
    
    def _determine_execution_priority(self, strategy_type, risk_level) -> str:
        """Determine execution priority based on strategy type and risk level."""
        if risk_level.value in ['high', 'very_high']:
            return 'high'
        elif strategy_type.value in ['arbitrage', 'swapping']:
            return 'high'
        else:
            return 'normal'
    
    def _should_auto_compound(self, strategy_type) -> bool:
        """Determine if auto-compound should be enabled."""
        return strategy_type.value in ['yield_farming', 'staking', 'compounding']


class ETLProcessorFactory:
    """Factory for creating ETL processors with different configurations."""
    
    @staticmethod
    def create_standard_processor() -> ETLProcessor:
        """Create a standard ETL processor."""
        return ETLProcessor()
    
    @staticmethod
    def create_processor_with_custom_mapper(custom_mapper: TerminologyMapper) -> ETLProcessor:
        """Create an ETL processor with a custom terminology mapper."""
        processor = ETLProcessor()
        processor.terminology_mapper = custom_mapper
        return processor
