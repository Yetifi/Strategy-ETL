#!/usr/bin/env python3
"""
Command-line interface for the Strategy ETL system.
"""
import argparse
import sys
import json
from typing import Optional
from .etl_processor import ETLProcessor
from .validators import ShadeAIValidator, PromptQualityValidator


def process_prompt(prompt_text: str, user_id: Optional[str] = None, 
                  metadata: Optional[str] = None, output_format: str = "text") -> None:
    """
    Process a single prompt and display results.
    
    Args:
        prompt_text: The raw prompt text to process
        user_id: Optional user identifier
        metadata: Optional metadata as JSON string
        output_format: Output format ('text' or 'json')
    """
    processor = ETLProcessor()
    
    # Parse metadata if provided
    parsed_metadata = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON metadata: {metadata}")
            sys.exit(1)
    
    # Process the prompt
    result = processor.process(prompt_text, user_id, parsed_metadata)
    
    if output_format == "json":
        # JSON output
        output_data = {
            "success": result.success,
            "processing_time_ms": result.processing_time_ms,
            "errors": result.errors,
            "warnings": result.warnings,
            "original_prompt": {
                "id": result.original_prompt.id,
                "raw_text": result.original_prompt.raw_text,
                "user_id": result.original_prompt.user_id,
                "timestamp": result.original_prompt.timestamp.isoformat() if result.original_prompt.timestamp else None
            }
        }
        
        if result.transformed_prompt:
            output_data["transformed_prompt"] = {
                "id": result.transformed_prompt.id,
                "strategy_type": result.transformed_prompt.strategy_type.value,
                "primary_asset": result.transformed_prompt.primary_asset.value if result.transformed_prompt.primary_asset else None,
                "secondary_assets": [asset.value for asset in result.transformed_prompt.secondary_assets],
                "risk_level": result.transformed_prompt.risk_level.value,
                "target_apy": result.transformed_prompt.target_apy,
                "duration_days": result.transformed_prompt.duration_days,
                "confidence_score": result.transformed_prompt.confidence_score,
                "execution_priority": result.transformed_prompt.execution_priority,
                "auto_compound": result.transformed_prompt.auto_compound,
                "transformation_notes": result.transformed_prompt.transformation_notes
            }
            
            # Add validation results
            shade_validator = ShadeAIValidator()
            quality_validator = PromptQualityValidator()
            
            is_valid, errors = shade_validator.validate_prompt(result.transformed_prompt)
            quality_result = quality_validator.assess_quality(result.transformed_prompt)
            
            output_data["validation"] = {
                "shade_ai_compatible": is_valid,
                "validation_errors": errors,
                "quality_score": quality_result["quality_score"],
                "quality_level": quality_result["quality_level"],
                "recommendations": quality_result["recommendations"]
            }
        
        print(json.dumps(output_data, indent=2))
        
    else:
        # Text output
        print(f"📝 Original Prompt: {prompt_text}")
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Processing Time: {result.processing_time_ms:.2f}ms")
        
        if result.errors:
            print(f"\n❌ Errors:")
            for error in result.errors:
                print(f"   - {error}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")
        
        if result.transformed_prompt:
            tp = result.transformed_prompt
            print(f"\n🔄 Transformed Prompt:")
            print(f"   Strategy Type: {tp.strategy_type.value}")
            print(f"   Primary Asset: {tp.primary_asset.value if tp.primary_asset else 'None'}")
            print(f"   Secondary Assets: {[a.value for a in tp.secondary_assets]}")
            print(f"   Risk Level: {tp.risk_level.value}")
            print(f"   Target APY: {tp.target_apy}%" if tp.target_apy else "   Target APY: Not specified")
            print(f"   Duration: {tp.duration_days} days" if tp.duration_days else "   Duration: Not specified")
            print(f"   Confidence Score: {tp.confidence_score:.2f}")
            print(f"   Execution Priority: {tp.execution_priority}")
            print(f"   Auto-Compound: {tp.auto_compound}")
            
            if tp.transformation_notes:
                print(f"\n📋 Transformation Notes:")
                for note in tp.transformation_notes:
                    print(f"   - {note}")
            
            # Validation results
            print(f"\n🔍 Validation Results:")
            shade_validator = ShadeAIValidator()
            quality_validator = PromptQualityValidator()
            
            is_valid, errors = shade_validator.validate_prompt(tp)
            print(f"   Shade AI Compatible: {'✅ Yes' if is_valid else '❌ No'}")
            
            if not is_valid:
                print(f"   Validation Errors:")
                for error in errors:
                    print(f"     - {error}")
            
            quality_result = quality_validator.assess_quality(tp)
            print(f"   Quality Score: {quality_result['quality_score']:.0f}/{quality_result['max_score']:.0f}")
            print(f"   Quality Level: {quality_result['quality_level']}")
            
            if quality_result['recommendations']:
                print(f"   Recommendations:")
                for rec in quality_result['recommendations']:
                    print(f"     - {rec}")


def interactive_mode():
    """Run the CLI in interactive mode."""
    print("🚀 Strategy ETL Interactive Mode")
    print("Type 'quit' or 'exit' to exit, 'help' for commands")
    print("-" * 50)
    
    processor = ETLProcessor()
    
    while True:
        try:
            prompt = input("\n📝 Enter DeFi strategy prompt: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if prompt.lower() in ['help', 'h', '?']:
                print("\n📚 Available Commands:")
                print("  help, h, ?     - Show this help message")
                print("  quit, exit, q  - Exit the program")
                print("  <prompt>       - Process a DeFi strategy prompt")
                print("\n💡 Example prompts:")
                print("  - 'yield farming with NEAR for 20% APY'")
                print("  - 'provide liquidity to NEAR-USDC pool'")
                print("  - 'stake my NEAR tokens'")
                continue
            
            if not prompt:
                continue
            
            # Process the prompt
            result = processor.process(prompt)
            
            if result.success:
                tp = result.transformed_prompt
                print(f"\n✅ Processed successfully!")
                print(f"   Strategy: {tp.strategy_type.value}")
                print(f"   Asset: {tp.primary_asset.value if tp.primary_asset else 'None'}")
                print(f"   Risk: {tp.risk_level.value}")
                print(f"   Confidence: {tp.confidence_score:.2f}")
                
                if tp.target_apy:
                    print(f"   Target APY: {tp.target_apy}%")
                if tp.duration_days:
                    print(f"   Duration: {tp.duration_days} days")
            else:
                print(f"\n❌ Processing failed:")
                for error in result.errors:
                    print(f"   - {error}")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Strategy ETL - Process DeFi strategy prompts for Shade AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "yield farming with NEAR for 20% APY"
  %(prog)s "provide liquidity to NEAR-USDC pool" --user-id user123
  %(prog)s "stake NEAR tokens" --metadata '{"source": "web"}'
  %(prog)s --interactive
  %(prog)s "arbitrage between NEAR and USDC" --output json
        """
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="DeFi strategy prompt to process"
    )
    
    parser.add_argument(
        "--user-id", "-u",
        help="User identifier for the prompt"
    )
    
    parser.add_argument(
        "--metadata", "-m",
        help="Metadata as JSON string (e.g., '{\"source\": \"web\"}')"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Strategy ETL v1.0.0"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.prompt:
        process_prompt(args.prompt, args.user_id, args.metadata, args.output)
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for interactive mode or provide a prompt as argument")


if __name__ == "__main__":
    main()
