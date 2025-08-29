#!/usr/bin/env python3
"""
Enhanced Demo for Strategy ETL with Prompt Capture and Storage

This demo showcases the new user prompt input capture and storage features.
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhanced_cli import EnhancedCLI
from config import Config


def demo_basic_usage():
    """Demonstrate basic usage of the enhanced CLI."""
    print("🚀 Strategy ETL Enhanced Demo - Basic Usage")
    print("=" * 60)
    
    # Initialize CLI with SQLite storage
    cli = EnhancedCLI(storage_type="sqlite")
    
    # Set a user ID
    cli.set_user_id("demo_user_001")
    
    # Process a simple prompt
    print("\n📝 Processing a simple prompt...")
    cli.process_prompt("yield farming with NEAR for 15% APY")
    
    # Show storage stats
    print("\n📊 Storage Statistics:")
    cli.show_stats()
    
    # Show history
    print("\n📚 Prompt History:")
    cli.show_history(limit=5)


def demo_prompt_capture():
    """Demonstrate the interactive prompt capture feature."""
    print("\n\n🎯 Strategy ETL Enhanced Demo - Prompt Capture")
    print("=" * 60)
    
    cli = EnhancedCLI(storage_type="sqlite")
    cli.set_user_id("demo_user_002")
    
    print("This demo will show the interactive prompt capture feature.")
    print("You can type 'cancel' to skip this demo.")
    
    # Capture a prompt interactively
    prompt_text = cli.capture_prompt()
    
    if prompt_text:
        print(f"\n✅ Captured prompt: {prompt_text}")
        
        # Process the captured prompt
        print("\n🔄 Processing captured prompt...")
        cli.process_prompt(prompt_text)
        
        # Show updated history
        print("\n📚 Updated Prompt History:")
        cli.show_history(limit=3)
    else:
        print("❌ Prompt capture was cancelled or failed.")


def demo_search_and_history():
    """Demonstrate search and history features."""
    print("\n\n🔍 Strategy ETL Enhanced Demo - Search & History")
    print("=" * 60)
    
    cli = EnhancedCLI(storage_type="sqlite")
    cli.set_user_id("demo_user_003")
    
    # Add some sample prompts
    sample_prompts = [
        "stake NEAR tokens for compound interest",
        "provide liquidity to NEAR-USDC pool with low risk",
        "arbitrage between NEAR and USDC exchanges",
        "borrow USDC against NEAR collateral",
        "swap NEAR for USDC to take profits"
    ]
    
    print("📝 Adding sample prompts...")
    for prompt in sample_prompts:
        cli.process_prompt(prompt)
    
    # Show history
    print("\n📚 Full Prompt History:")
    cli.show_history(limit=10)
    
    # Search for specific terms
    print("\n🔍 Searching for 'NEAR'...")
    cli.search_prompts("NEAR")
    
    print("\n🔍 Searching for 'liquidity'...")
    cli.search_prompts("liquidity")
    
    # Show final stats
    print("\n📊 Final Storage Statistics:")
    cli.show_stats()


def demo_storage_backends():
    """Demonstrate different storage backends."""
    print("\n\n💾 Strategy ETL Enhanced Demo - Storage Backends")
    print("=" * 60)
    
    # SQLite storage
    print("📊 SQLite Storage Demo:")
    cli_sqlite = EnhancedCLI(storage_type="sqlite")
    cli_sqlite.set_user_id("storage_demo_user")
    cli_sqlite.process_prompt("test prompt for SQLite storage")
    cli_sqlite.show_stats()
    
    # JSON storage
    print("\n📄 JSON Storage Demo:")
    cli_json = EnhancedCLI(storage_type="json")
    cli_json.set_user_id("storage_demo_user")
    cli_json.process_prompt("test prompt for JSON storage")
    cli_json.show_stats()


def demo_configuration():
    """Demonstrate configuration features."""
    print("\n\n⚙️ Strategy ETL Enhanced Demo - Configuration")
    print("=" * 60)
    
    # Create default configuration
    print("📝 Creating default configuration...")
    config = Config.create_default_config("demo_config.json")
    
    print("✅ Configuration created with the following settings:")
    for section, settings in config.items():
        if section != "description":
            print(f"\n{section.upper()}:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
    
    # Show environment variable help
    print("\n🌍 Environment Variables:")
    from config import print_env_help
    print_env_help()
    
    # Clean up demo config
    try:
        os.remove("demo_config.json")
        print("\n🧹 Demo configuration file cleaned up.")
    except:
        pass


def main():
    """Run the enhanced demo."""
    print("🎉 Welcome to the Strategy ETL Enhanced Demo!")
    print("This demo showcases the new user prompt input capture and storage features.")
    print("\n" + "=" * 80)
    
    try:
        # Run demos
        demo_basic_usage()
        demo_prompt_capture()
        demo_search_and_history()
        demo_storage_backends()
        demo_configuration()
        
        print("\n\n🎊 Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Interactive prompt capture with validation")
        print("  ✅ Persistent storage (SQLite and JSON)")
        print("  ✅ Prompt history and search")
        print("  ✅ User management and metadata")
        print("  ✅ Configuration management")
        print("  ✅ Enhanced CLI with multiple modes")
        
        print("\n🚀 To try the enhanced CLI:")
        print("  python -m src.enhanced_cli --interactive")
        print("  python -m src.enhanced_cli --capture")
        print("  python -m src.enhanced_cli --history")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
