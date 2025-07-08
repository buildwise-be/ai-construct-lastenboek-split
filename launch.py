#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Construct PDF Opdeler - Launcher Script

Simple launcher script for the refactored PDF processing application.
This script provides an easy way to start the application from the root directory.

Usage:
    python launch.py
    
Or with validation:
    python launch.py --validate
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher function."""
    # Add src directory to path
    src_dir = Path(__file__).parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Check for validation flag
    if "--validate" in sys.argv or "-v" in sys.argv:
        print("🔍 Running validation check...")
        try:
            from utils.validation import run_validation
            results = run_validation()
            if results.get('overall', {}).get('success', False):
                print("\n🚀 Validation passed! Starting application...")
            else:
                print("\n❌ Validation failed! Please fix issues before running.")
                return 1
        except ImportError as e:
            print(f"❌ Could not import validation module: {e}")
            return 1
    
    # Start the main application
    try:
        print("🚀 Starting AI Construct PDF Opdeler...")
        from main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("💡 Make sure you're in the correct directory and dependencies are installed:")
        print("   pip install -r src/requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())