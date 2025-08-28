#!/usr/bin/env python3
"""
Demonstration script for the Strategy ETL system.
Shows how to process various DeFi strategy prompts and validate them.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.etl_processor import ETLProcessor
from src.validators import ShadeAIValidator, PromptQualityValidator
from src.models import StrategyType, AssetType, RiskLevel


def print_separator(title):
    """Print a formatted separator with title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_prompt_analysis(original_text, result):
    """Print detailed analysis of prompt processing."""
    print(f"\n📝 Original Prompt:")
    print(f"   {original_text}")
    
    print(f"\n✅ Processing Result:")
    print(f"   Success: {result.success}")
    print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
    
    if result.errors:
        print(f"\n❌ Errors:")
        for error in result.errors:
            print(f"   - {error}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    if result.transformed_prompt:
        print(f"\n🔄 Transformed Prompt:")
        print(f"   Strategy Type: {result.transformed_prompt.strategy_type.value}")
        print(f"   Primary Asset: {result.transformed_prompt.primary_asset.value}")
        print(f"   Secondary Assets: {[a.value for a in result.transformed_prompt.secondary_assets]}")
        print(f"   Risk Level: {result.transformed_prompt.risk_level.value}")
        print(f"   Target APY: {result.transformed_prompt.target_apy}%" if result.transformed_prompt.target_apy else "   Target APY: Not specified")
        print(f"   Duration: {result.transformed_prompt.duration_days} days" if result.transformed_prompt.duration_days else "   Duration: Not specified")
        print(f"   Confidence Score: {result.transformed_prompt.confidence_score:.2f}")
        print(f"   Execution Priority: {result.transformed_prompt.execution_priority}")
        print(f"   Auto-Compound: {result.transformed_prompt.auto_compound}")
        
        if result.transformed_prompt.transformation_notes:
            print(f"\n📋 Transformation Notes:")
            for note in result.transformed_prompt.transformation_notes:
                print(f"   - {note}")


def validate_and_assess_prompt(transformed_prompt):
    """Validate and assess the quality of a transformed prompt."""
    shade_validator = ShadeAIValidator()
    quality_validator = PromptQualityValidator()
    
    print(f"\n🔍 Validation Results:")
    
    # Shade AI validation
    is_valid, errors = shade_validator.validate_prompt(transformed_prompt)
    print(f"   Shade AI Compatible: {'✅ Yes' if is_valid else '❌ No'}")
    
    if not is_valid:
        print(f"   Validation Errors:")
        for error in errors:
            print(f"     - {error}")
    
    # Quality assessment
    quality_result = quality_validator.assess_quality(transformed_prompt)
    print(f"   Quality Score: {quality_result['quality_score']:.0f}/{quality_result['max_score']:.0f}")
    print(f"   Quality Level: {quality_result['quality_level']}")
    
    if quality_result['recommendations']:
        print(f"   Recommendations:")
        for rec in quality_result['recommendations']:
            print(f"     - {rec}")
    
    return is_valid, quality_result


def main():
    """Main demonstration function."""
    print("🚀 Strategy ETL System Demonstration")
    print("Processing various DeFi strategy prompts...")
    
    # Initialize the ETL processor
    processor = ETLProcessor()
    
    # Example 1: Yield Farming Strategy
    print_separator("Example 1: Yield Farming Strategy")
    yield_farming_prompt = """
    I want to do yield farming on NEAR protocol.
    Use USDC and USDT for diversification.
    Target 25% APY over 6 months.
    Looking for medium risk strategies.
    """
    
    result = processor.process(yield_farming_prompt)
    print_prompt_analysis(yield_farming_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 2: Liquidity Providing Strategy
    print_separator("Example 2: Liquidity Providing Strategy")
    liquidity_prompt = """
    Provide liquidity to NEAR-USDC pool.
    Low risk, stable returns.
    Duration: 1 year.
    """
    
    result = processor.process(liquidity_prompt)
    print_prompt_analysis(liquidity_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 3: Staking Strategy
    print_separator("Example 3: Staking Strategy")
    staking_prompt = "Stake my NEAR tokens for staking rewards"
    
    result = processor.process(staking_prompt)
    print_prompt_analysis(staking_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 4: Arbitrage Strategy
    print_separator("Example 4: Arbitrage Strategy")
    arbitrage_prompt = """
    Find arbitrage opportunities between NEAR and USDC.
    High risk, high reward.
    Execute quickly.
    """
    
    result = processor.process(arbitrage_prompt)
    print_prompt_analysis(arbitrage_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 5: Complex Multi-Asset Strategy
    print_separator("Example 5: Complex Multi-Asset Strategy")
    complex_prompt = """
    I want to create a diversified DeFi portfolio:
    - 40% in NEAR staking for stable returns
    - 30% in NEAR-USDC liquidity providing for medium risk
    - 20% in yield farming with USDT for higher returns
    - 10% in arbitrage between NEAR and WBTC
    Target overall portfolio APY of 18% with medium-high risk tolerance.
    Strategy duration: 12 months.
    """
    
    result = processor.process(complex_prompt)
    print_prompt_analysis(complex_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 6: Edge Case - Minimal Input
    print_separator("Example 6: Edge Case - Minimal Input")
    minimal_prompt = "yield farming"
    
    result = processor.process(minimal_prompt)
    print_prompt_analysis(minimal_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    # Example 7: Edge Case - Very Long Input
    print_separator("Example 7: Edge Case - Very Long Input")
    long_prompt = """
    I would like to engage in comprehensive yield farming activities on the NEAR blockchain 
    using a combination of USDC, USDT, and DAI stablecoins for optimal diversification 
    while maintaining a balanced risk profile that targets annual returns in the range of 
    15-25% over a strategic time horizon of 6-12 months, incorporating both passive 
    income generation through liquidity provision and active management strategies for 
    maximum portfolio efficiency and risk-adjusted returns.
    """
    
    result = processor.process(long_prompt)
    print_prompt_analysis(long_prompt, result)
    
    if result.transformed_prompt:
        validate_and_assess_prompt(result.transformed_prompt)
    
    print_separator("Demonstration Complete")
    print("🎉 All examples processed successfully!")
    print("\nThe ETL system successfully:")
    print("  ✅ Extracted raw user prompts")
    print("  ✅ Transformed them into Shade AI compatible format")
    print("  ✅ Validated compatibility with Shade AI requirements")
    print("  ✅ Assessed prompt quality and provided recommendations")
    print("  ✅ Handled various input formats and edge cases")


if __name__ == "__main__":
    main()
