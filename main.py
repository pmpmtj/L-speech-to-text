#!/usr/bin/env python3
"""
Speech-to-Text Main Entry Point

This is the main entry point for the speech-to-text application.
It starts the hotkey detector. Dependency checks are optional.

Usage:
    python main.py
    
Or to run dependency checks:
    python main.py --apply-checks
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Early error catching for startup issues
try:
    from common.logging_utils import get_logger
    from common.config import config
    from src.check_dependencies import check_all_dependencies, print_results
    from src.hotkey_detect.hotkey_detector import HotkeyDetector
    
    logger = get_logger("main")
except Exception as e:
    print("\n" + "="*70)
    print("CRITICAL ERROR DURING STARTUP")
    print("="*70)
    print(f"\nFailed to import required modules: {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    print("\n" + "="*70)
    print("\nPossible causes:")
    print("1. Missing dependencies (run: pip install -r requirements.txt)")
    print("2. Incorrect Python path configuration")
    print("3. Corrupted installation")
    print("="*70)
    input("\n\nPress ENTER to exit...")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Speech-to-Text Application with Hotkey Recording"
    )
    parser.add_argument(
        "--apply-checks",
        action="store_true",
        help="Run dependency checks before starting the application"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        print("\n" + "="*70)
        print("L-SPEECH-TO-TEXT - Starting...")
        print("="*70)
        
        args = parse_args()
        
        # Run dependency checks only if requested
        if args.apply_checks:
            logger.info("Running dependency checks as requested")
            # Log which checks are enabled
            enabled_checks = config.dependency_checks.get_enabled_checks()
            logger.info(f"Running dependency checks (enabled: {', '.join(enabled_checks) if enabled_checks else 'none'})")
            print("\nChecking dependencies...")
            
            results = check_all_dependencies()
            all_ok = print_results(results)
            
            if not all_ok:
                logger.error("Dependency checks failed. Please fix the issues above.")
                print("\nCannot start application due to missing dependencies.")
                print("Fix the issues above and try again.\n")
                input("\nPress ENTER to exit...")
                return 1
            
            print("\nStarting application...\n")
        else:
            logger.info("Skipping dependency checks by default")
            print("\nSkipping dependency checks (run with --apply-checks to verify dependencies)...\n")
        
        # Start the hotkey detector
        logger.info("Initializing hotkey detector")
        print("Initializing hotkey detector...")
        detector = HotkeyDetector()
        detector.start()
        
        # This should never be reached unless there's an error
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nApplication stopped by user.")
        return 0
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print("\n" + "="*70)
        print("FATAL ERROR")
        print("="*70)
        print(f"\nError: {e}")
        print(f"\nError type: {type(e).__name__}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("="*70)
        print("\nCheck logs for more details (if logs were created).")
        print("="*70)
        input("\n\nPress ENTER to exit...")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print("\n" + "="*70)
        print("UNHANDLED EXCEPTION AT TOP LEVEL")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("="*70)
        input("\n\nPress ENTER to exit...")
        sys.exit(1)

