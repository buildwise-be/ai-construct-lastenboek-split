#!/usr/bin/env python3
"""
LastenboekOCR Installation Script
Checks dependencies and guides users through setup
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_requirements():
    """Install requirements from requirements.txt"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing requirements")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "LLAMA_CLOUD_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("✅ Environment variables - OK")
        return True

def print_setup_guide():
    """Print setup guide for missing components"""
    print("\n" + "="*60)
    print("🔧 SETUP GUIDE")
    print("="*60)
    
    print("\n1. 🔑 Set up Google Cloud credentials:")
    print("   export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
    
    print("\n2. 🔑 Set up LlamaIndex API key:")
    print("   export LLAMA_CLOUD_API_KEY='your_api_key_here'")
    
    print("\n3. 🚀 Test the installation:")
    print("   python run_pipeline.py --help")
    
    print("\n4. 🎯 Run your first pipeline:")
    print("   python run_pipeline.py --model flash")

def main():
    print("🎯 LastenboekOCR Installation Check")
    print("="*50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Check environment variables
    env_ok = check_environment_variables()
    if not env_ok:
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 Installation completed successfully!")
        print("Your intelligent PDF processing pipeline is ready to use!")
    else:
        print("⚠️  Installation incomplete - see setup guide below")
        if not env_ok:
            print_setup_guide()
    
    print("="*50)

if __name__ == "__main__":
    main() 