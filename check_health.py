#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Construct PDF Opdeler - Health Check

Quick health check script to verify if the refactored application is ready to run.
This is a simplified version of the full validation.
"""

import sys
import os
from pathlib import Path

def quick_health_check():
    """Perform a quick health check of the application."""
    print("🏥 AI Construct PDF Opdeler - Health Check")
    print("=" * 45)
    
    issues = []
    checks_passed = 0
    total_checks = 6
    
    # Check 1: Python version
    print("📍 Checking Python version...", end=" ")
    if sys.version_info >= (3, 8):
        print("✅")
        checks_passed += 1
    else:
        print("❌")
        issues.append(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check 2: Core files exist
    print("📁 Checking core files...", end=" ")
    core_files = [
        "src/main.py",
        "src/config/settings.py", 
        "src/core/ai_client.py",
        "src/gui/main_window.py"
    ]
    
    missing_files = []
    for file_path in core_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅")
        checks_passed += 1
    else:
        print("❌")
        issues.append(f"Missing files: {', '.join(missing_files)}")
    
    # Check 3: Dependencies (basic check)
    print("📦 Checking basic dependencies...", end=" ")
    try:
        import pandas
        import PySide6
        import google.cloud.aiplatform
        print("✅")
        checks_passed += 1
    except ImportError as e:
        print("❌")
        issues.append(f"Missing dependencies: {str(e)}")
    
    # Check 4: Output directory
    print("📂 Checking output directory...", end=" ")
    output_dir = Path("output")
    if output_dir.exists() or output_dir.parent.exists():
        print("✅")
        checks_passed += 1
    else:
        print("❌")
        issues.append("Cannot create output directory")
    
    # Check 5: Permissions
    print("🔐 Checking file permissions...", end=" ")
    try:
        test_file = Path("temp_permission_test.txt")
        test_file.write_text("test")
        test_file.unlink()
        print("✅")
        checks_passed += 1
    except Exception:
        print("❌")
        issues.append("Insufficient file permissions")
    
    # Check 6: Module imports
    print("🔗 Checking module imports...", end=" ")
    try:
        sys.path.insert(0, "src")
        import config.settings
        print("✅")
        checks_passed += 1
    except ImportError:
        print("❌")
        issues.append("Cannot import application modules")
    
    # Results
    print("\n" + "=" * 45)
    print(f"📊 Health Check Results: {checks_passed}/{total_checks} passed")
    
    if checks_passed == total_checks:
        print("🎉 HEALTHY - Application is ready to run!")
        print("\n🚀 You can start the application with:")
        print("   python src/main.py")
        print("   or")
        print("   python launch.py")
        return True
    else:
        print("⚠️  ISSUES FOUND - Please fix the following:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 Quick fixes:")
        if any("dependencies" in issue.lower() for issue in issues):
            print("   pip install -r src/requirements.txt")
        if any("missing files" in issue.lower() for issue in issues):
            print("   Run setup: python setup.py")
        if any("python" in issue.lower() for issue in issues):
            print("   Upgrade Python to 3.8 or higher")
        
        return False

if __name__ == "__main__":
    healthy = quick_health_check()
    sys.exit(0 if healthy else 1)