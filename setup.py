#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Construct PDF Opdeler - Setup Script

This script helps with installing dependencies and setting up the refactored application.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"❌ Python {'.'.join(map(str, min_version))} or higher is required")
        print(f"   Currently running Python {'.'.join(map(str, current_version))}")
        return False
    
    print(f"✅ Python {'.'.join(map(str, current_version))} - Compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    requirements_file = Path("src/requirements.txt")
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📦 Installing dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "output",
        "logs",
        "config"
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(exist_ok=True)
            print(f"  ✅ {directory}/")
        except Exception as e:
            print(f"  ❌ Failed to create {directory}/: {e}")
            return False
    
    return True


def setup_environment():
    """Set up environment configuration."""
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if not env_path.exists() and env_example_path.exists():
        print("⚙️  Setting up environment configuration...")
        try:
            with open(env_example_path, 'r') as src:
                content = src.read()
            
            with open(env_path, 'w') as dst:
                dst.write(content)
            
            print(f"  ✅ Created {env_path}")
            print(f"  💡 Please edit {env_path} with your configuration")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to create {env_path}: {e}")
            return False
    
    return True


def run_validation():
    """Run validation check."""
    print("🔍 Running validation check...")
    
    # Add src to path
    src_dir = Path("src")
    sys.path.insert(0, str(src_dir))
    
    try:
        from utils.validation import run_validation
        results = run_validation()
        return results.get('overall', {}).get('success', False)
    except ImportError as e:
        print(f"❌ Could not import validation module: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 AI Construct PDF Opdeler - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    if not create_directories():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Setup environment
    setup_environment()
    
    # Run validation
    print("\n" + "=" * 40)
    if run_validation():
        print("\n✅ SETUP COMPLETED SUCCESSFULLY!")
        print("\n🎯 Next steps:")
        print("   1. Edit .env file with your Google Cloud Project ID (optional)")
        print("   2. Run the application: python src/main.py")
        print("   3. Or use the launcher: python launch.py")
        return 0
    else:
        print("\n❌ SETUP COMPLETED WITH ISSUES")
        print("\n💡 Please check the validation results above")
        return 1


if __name__ == "__main__":
    sys.exit(main())