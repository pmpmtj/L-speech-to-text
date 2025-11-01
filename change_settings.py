"""
Runtime Settings Changer

This script edits the runtime_config.json file to change settings
while the main application is running.

Changes take effect immediately on the next transcription/paste operation.
"""

import json
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "runtime_config.json"


def load_config():
    """Load the current runtime configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "transcription": {
                "language": "pt",
                "model": "whisper-1"
            },
            "paste": {
                "add_timestamp": False
            }
        }


def save_config(config_data):
    """Save the runtime configuration."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)
    print(f"\nConfiguration saved to: {CONFIG_FILE}")


def show_current_settings(config_data):
    """Display current settings."""
    print("\n" + "="*50)
    print("Current Runtime Settings")
    print("="*50)
    print(f"Language: {config_data['transcription']['language']}")
    print(f"Model: {config_data['transcription']['model']}")
    print(f"Add Timestamp: {config_data['paste']['add_timestamp']}")
    print("="*50)


def main():
    """Main menu."""
    config_data = load_config()
    
    while True:
        print("\n" + "="*50)
        print("Runtime Settings Changer")
        print("="*50)
        show_current_settings(config_data)
        print("\n1. Change language (current: {})".format(config_data['transcription']['language']))
        print("2. Change model (current: {})".format(config_data['transcription']['model']))
        print("3. Toggle timestamp (current: {})".format(config_data['paste']['add_timestamp']))
        print("4. Exit")
        print("="*50)
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("\nCommon language codes:")
            print("  en - English")
            print("  pt - Portuguese  ")
            print("  es - Spanish")
            print("  fr - French")
            print("  de - German")
            print("  it - Italian")
            
            new_lang = input("\nEnter language code: ").strip()
            if new_lang:
                config_data['transcription']['language'] = new_lang
                save_config(config_data)
                print(f"Language set to: {new_lang}")
                print("Will take effect on next transcription!")
        
        elif choice == "2":
            new_model = input("\nEnter model name (default: whisper-1): ").strip()
            if new_model:
                config_data['transcription']['model'] = new_model
                save_config(config_data)
                print(f"Model set to: {new_model}")
                print("Will take effect on next transcription!")
        
        elif choice == "3":
            config_data['paste']['add_timestamp'] = not config_data['paste']['add_timestamp']
            save_config(config_data)
            status = "ENABLED" if config_data['paste']['add_timestamp'] else "DISABLED"
            print(f"Timestamp prefix {status}")
            print("Will take effect on next paste!")
        
        elif choice == "4":
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")

