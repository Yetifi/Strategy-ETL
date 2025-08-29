#!/usr/bin/env python3
"""
Enhanced Command-line interface for the Strategy ETL system.
"""
import argparse
import sys
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from .etl_processor import ETLProcessor
from .validators import ShadeAIValidator, PromptQualityValidator
from .prompt_storage import PromptStorageManager


class EnhancedCLI:
    """
    Enhanced CLI with prompt history, search, and better input capture.
    """
    
    def __init__(self, storage_type: str = "sqlite"):
        self.storage_manager = PromptStorageManager(storage_type=storage_type)
        self.processor = ETLProcessor(storage_manager=self.storage_manager)
        self.current_user_id = None
    
    def set_user_id(self, user_id: str):
        """Set the current user ID for session."""
        self.current_user_id = user_id
        print(f"👤 User ID set to: {user_id}")
    
    def capture_prompt(self, prompt_text: str = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Capture a prompt from user input with validation and suggestions.
        
        Args:
            prompt_text: Pre-provided prompt text
            metadata: Optional metadata
            
        Returns:
            The captured prompt text or None if cancelled
        """
        if prompt_text:
            # Use provided prompt
            return self._validate_and_suggest(prompt_text, metadata)
        
        print("\n📝 Prompt Input Mode")
        print("Enter your DeFi strategy prompt below.")
        print("Type 'help' for examples, 'cancel' to abort, or 'done' when finished.")
        print("-" * 60)
        
        lines = []
        line_number = 1
        
        while True:
            try:
                if line_number == 1:
                    line = input(f"Line {line_number}: ").strip()
                else:
                    line = input(f"Line {line_number}: ").strip()
                
                if line.lower() == 'cancel':
                    print("❌ Prompt capture cancelled.")
                    return None
                
                if line.lower() == 'done':
                    break
                
                if line.lower() == 'help':
                    self._show_prompt_examples()
                    continue
                
                if line.lower() == 'clear':
                    lines = []
                    line_number = 1
                    print("🧹 Cleared all lines. Starting fresh.")
                    continue
                
                if line.lower() == 'back':
                    if lines:
                        removed = lines.pop()
                        line_number -= 1
                        print(f"↩️  Removed: {removed}")
                    else:
                        print("⚠️  No lines to remove.")
                    continue
                
                if line.lower() == 'show':
                    if lines:
                        print("\n📋 Current prompt:")
                        for i, l in enumerate(lines, 1):
                            print(f"  {i}: {l}")
                    else:
                        print("📝 No lines captured yet.")
                    continue
                
                if line:
                    lines.append(line)
                    line_number += 1
                else:
                    print("⚠️  Empty line ignored. Use 'done' to finish or 'cancel' to abort.")
                
            except KeyboardInterrupt:
                print("\n\n❌ Prompt capture interrupted.")
                return None
        
        if not lines:
            print("❌ No prompt text captured.")
            return None
        
        full_prompt = "\n".join(lines)
        print(f"\n📝 Captured prompt ({len(lines)} lines, {len(full_prompt)} characters):")
        print("-" * 60)
        print(full_prompt)
        print("-" * 60)
        
        return self._validate_and_suggest(full_prompt, metadata)
    
    def _validate_and_suggest(self, prompt_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Validate prompt and provide suggestions for improvement.
        
        Args:
            prompt_text: The prompt text to validate
            metadata: Optional metadata
            
        Returns:
            The validated prompt text
        """
        print("\n🔍 Validating prompt...")
        
        # Basic validation
        if len(prompt_text.strip()) < 10:
            print("⚠️  Warning: Prompt seems very short. Consider adding more details.")
        
        if len(prompt_text.split()) < 3:
            print("⚠️  Warning: Prompt has very few words. Consider being more descriptive.")
        
        # Check for common DeFi terms
        defi_terms = ['yield', 'farm', 'liquidity', 'stake', 'swap', 'borrow', 'lend', 'near', 'usdc', 'apy', 'apr']
        found_terms = [term for term in defi_terms if term.lower() in prompt_text.lower()]
        
        if found_terms:
            print(f"✅ Detected DeFi terms: {', '.join(found_terms)}")
        else:
            print("⚠️  Warning: No common DeFi terms detected. Make sure this is a DeFi strategy prompt.")
        
        # Check for numerical values
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', prompt_text)
        if numbers:
            print(f"✅ Detected numerical values: {', '.join(numbers)}")
        else:
            print("💡 Tip: Consider adding specific numbers (APY, amounts, durations) for better strategy definition.")
        
        # Ask for confirmation
        while True:
            response = input("\n🤔 Does this look correct? (y/n/edit): ").strip().lower()
            
            if response in ['y', 'yes']:
                return prompt_text
            elif response in ['n', 'no']:
                print("❌ Prompt rejected. Please try again.")
                return None
            elif response in ['e', 'edit']:
                return self.capture_prompt(metadata=metadata)
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'e' for edit.")
    
    def _show_prompt_examples(self):
        """Show example prompts to help users."""
        examples = [
            "yield farming with NEAR for 20% APY over 30 days",
            "provide liquidity to NEAR-USDC pool with medium risk tolerance",
            "stake my NEAR tokens for compound interest",
            "arbitrage between NEAR and USDC on different exchanges",
            "borrow USDC against my NEAR collateral at 5% interest",
            "swap NEAR for USDC to take profits"
        ]
        
        print("\n💡 Example DeFi Strategy Prompts:")
        print("-" * 60)
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print("-" * 60)
        print("💡 Tips:")
        print("  - Be specific about assets, amounts, and timeframes")
        print("  - Mention risk tolerance if relevant")
        print("  - Include target APY/APR if you have one")
        print("  - Specify if you want auto-compounding")
    
    def process_prompt(self, prompt_text: str, metadata: Optional[Dict[str, Any]] = None, 
                      output_format: str = "text") -> None:
        """
        Process a single prompt and display results.
        
        Args:
            prompt_text: The raw prompt text to process
            metadata: Optional metadata
            output_format: Output format ('text' or 'json')
        """
        # Add user_id to metadata if available
        if self.current_user_id:
            if metadata is None:
                metadata = {}
            metadata['user_id'] = self.current_user_id
        
        # Process the prompt
        result = self.processor.process(prompt_text, self.current_user_id, metadata)
        
        if output_format == "json":
            self._output_json(result)
        else:
            self._output_text(result)
    
    def _output_json(self, result):
        """Output results in JSON format."""
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
    
    def _output_text(self, result):
        """Output results in text format."""
        print(f"📝 Original Prompt: {result.original_prompt.raw_text}")
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
    
    def show_history(self, limit: int = 20, user_id: Optional[str] = None):
        """Show prompt history."""
        user_id = user_id or self.current_user_id
        history = self.storage_manager.get_prompt_history(user_id=user_id, limit=limit)
        
        if not history:
            print("📝 No prompt history found.")
            return
        
        print(f"\n📚 Prompt History ({len(history)} prompts):")
        print("-" * 80)
        
        for i, prompt in enumerate(history, 1):
            timestamp = prompt['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            user_display = prompt['user_id'] or 'Anonymous'
            preview = prompt['raw_text']
            
            print(f"{i:2d}. [{timestamp}] {user_display}")
            print(f"    {preview}")
            print(f"    📊 Length: {prompt['length']} chars, {prompt['word_count']} words")
            print()
    
    def search_prompts(self, query: str, user_id: Optional[str] = None):
        """Search prompts by content."""
        user_id = user_id or self.current_user_id
        results = self.storage_manager.search_prompts(query, user_id=user_id)
        
        if not results:
            print(f"🔍 No prompts found matching '{query}'")
            return
        
        print(f"\n🔍 Search Results for '{query}' ({len(results)} matches):")
        print("-" * 80)
        
        for i, prompt in enumerate(results, 1):
            timestamp = prompt.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            user_display = prompt.user_id or 'Anonymous'
            
            print(f"{i:2d}. [{timestamp}] {user_display}")
            print(f"    {prompt.raw_text}")
            print()
    
    def show_stats(self):
        """Show storage statistics."""
        stats = self.storage_manager.get_storage_stats()
        
        if "error" in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        print(f"\n📊 Storage Statistics:")
        print("-" * 40)
        print(f"Storage Type: {stats['storage_type']}")
        print(f"Total Prompts: {stats['total_prompts']}")
        print(f"Total Transformed: {stats['total_transformed']}")
        print(f"Total Results: {stats['total_results']}")
        
        if 'user_prompts' in stats:
            print(f"User Prompts: {stats['user_prompts']}")
            print(f"Anonymous Prompts: {stats['anonymous_prompts']}")
    
    def interactive_mode(self):
        """Run the CLI in interactive mode."""
        print("🚀 Strategy ETL Enhanced Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 60)
        
        while True:
            try:
                command = input("\n🎯 Command: ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command in ['help', 'h', '?']:
                    self._show_interactive_help()
                    continue
                
                if command in ['user', 'setuser']:
                    user_id = input("Enter user ID: ").strip()
                    if user_id:
                        self.set_user_id(user_id)
                    continue
                
                if command in ['history', 'h']:
                    limit = input("Number of prompts to show (default 20): ").strip()
                    try:
                        limit = int(limit) if limit else 20
                    except ValueError:
                        limit = 20
                    self.show_history(limit=limit)
                    continue
                
                if command in ['search', 's']:
                    query = input("Search query: ").strip()
                    if query:
                        self.search_prompts(query)
                    continue
                
                if command in ['stats', 'statistics']:
                    self.show_stats()
                    continue
                
                if command in ['capture', 'c', 'prompt']:
                    prompt_text = self.capture_prompt()
                    if prompt_text:
                        self.process_prompt(prompt_text)
                    continue
                
                if command in ['clear', 'cls']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                if command:
                    # Treat as a direct prompt
                    self.process_prompt(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n💥 Unexpected error: {e}")
    
    def _show_interactive_help(self):
        """Show interactive mode help."""
        print("\n📚 Available Commands:")
        print("  help, h, ?        - Show this help message")
        print("  quit, exit, q     - Exit the program")
        print("  user, setuser     - Set user ID for session")
        print("  history, h        - Show prompt history")
        print("  search, s         - Search prompts")
        print("  stats, statistics - Show storage statistics")
        print("  capture, c, prompt - Capture a new prompt")
        print("  clear, cls        - Clear screen")
        print("  <text>            - Process text as a prompt")
        print("\n💡 Example usage:")
        print("  > user")
        print("  > capture")
        print("  > history")
        print("  > search NEAR")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Strategy ETL - Process DeFi strategy prompts with storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive
  %(prog)s --capture
  %(prog)s --history
  %(prog)s --search "NEAR"
  %(prog)s --stats
  %(prog)s --user-id user123 "yield farming with NEAR"
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
        "--capture", "-c",
        action="store_true",
        help="Capture a new prompt interactively"
    )
    
    parser.add_argument(
        "--history", "-h",
        action="store_true",
        help="Show prompt history"
    )
    
    parser.add_argument(
        "--search",
        help="Search prompts by content"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show storage statistics"
    )
    
    parser.add_argument(
        "--storage-type",
        choices=["sqlite", "json"],
        default="sqlite",
        help="Storage backend type (default: sqlite)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Enhanced Strategy ETL v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = EnhancedCLI(storage_type=args.storage_type)
    
    # Set user ID if provided
    if args.user_id:
        cli.set_user_id(args.user_id)
    
    # Parse metadata if provided
    parsed_metadata = None
    if args.metadata:
        try:
            parsed_metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON metadata: {args.metadata}")
            sys.exit(1)
    
    # Handle different modes
    if args.interactive:
        cli.interactive_mode()
    elif args.capture:
        prompt_text = cli.capture_prompt(metadata=parsed_metadata)
        if prompt_text:
            cli.process_prompt(prompt_text, parsed_metadata, args.output)
    elif args.history:
        cli.show_history()
    elif args.search:
        cli.search_prompts(args.search)
    elif args.stats:
        cli.show_stats()
    elif args.prompt:
        cli.process_prompt(args.prompt, parsed_metadata, args.output)
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for interactive mode or --capture to capture a new prompt")


if __name__ == "__main__":
    main()
