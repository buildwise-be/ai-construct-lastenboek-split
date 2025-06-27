"""
Validation Utilities

This module provides utilities to validate the refactored application setup.
"""

import sys
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= min_version:
        return True, f"Python {'.'.join(map(str, current_version))} ✓"
    else:
        return False, f"Python {'.'.join(map(str, current_version))} (requires {'.'.join(map(str, min_version))}+)"


def check_dependencies() -> Tuple[bool, List[str], List[str]]:
    """Check if all required dependencies are available."""
    dependencies = {
        'pandas': 'pandas',
        'PyPDF2': 'PyPDF2', 
        'python-dotenv': 'dotenv',
        'google-cloud-aiplatform': 'google.cloud.aiplatform',
        'google-generativeai': 'google.generativeai',
        'PyMuPDF': 'fitz',
        'PySide6': 'PySide6.QtWidgets',
        'typing-extensions': 'typing_extensions'
    }
    
    available = []
    missing = []
    
    for package_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            available.append(package_name)
        except ImportError:
            missing.append(package_name)
    
    success = len(missing) == 0
    return success, available, missing


def check_file_structure() -> Tuple[bool, List[str], List[str]]:
    """Check if the modular file structure is correct."""
    required_files = [
        'src/main.py',
        'src/config/settings.py',
        'src/core/ai_client.py',
        'src/core/pdf_processor.py', 
        'src/core/category_matcher.py',
        'src/core/file_utils.py',
        'src/gui/main_window.py',
        'src/gui/components/styled_components.py',
        'src/gui/workers/processing_worker.py',
        'src/models/categories.py',
        'src/requirements.txt'
    ]
    
    base_path = Path(__file__).parent.parent.parent
    existing = []
    missing = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            existing.append(file_path)
        else:
            missing.append(file_path)
    
    success = len(missing) == 0
    return success, existing, missing


def check_imports() -> Tuple[bool, List[str], List[str]]:
    """Check if our modules can be imported correctly."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    modules_to_test = [
        'config.settings',
        'core.ai_client',
        'core.file_utils',
        'models.categories'
    ]
    
    successful = []
    failed = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            successful.append(module_name)
        except Exception as e:
            failed.append(f"{module_name}: {str(e)}")
    
    success = len(failed) == 0
    return success, successful, failed


def check_configuration() -> Tuple[bool, List[str], List[str]]:
    """Check if configuration is valid."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config.settings import validate_config, ASSETS_CONFIG, DEFAULT_CATEGORY_FILE
        
        issues = validate_config()
        valid_items = []
        
        # Check if default category file exists
        if Path(DEFAULT_CATEGORY_FILE).exists():
            valid_items.append("Default category file found")
        else:
            issues.append(f"Default category file missing: {DEFAULT_CATEGORY_FILE}")
        
        # Check assets
        for asset_name, asset_path in ASSETS_CONFIG.items():
            if asset_path.exists():
                valid_items.append(f"Asset found: {asset_name}")
            else:
                valid_items.append(f"Asset missing (optional): {asset_name}")
        
        success = len([issue for issue in issues if 'missing' in issue.lower()]) == 0
        return success, valid_items, issues
        
    except Exception as e:
        return False, [], [f"Configuration check failed: {str(e)}"]


def run_validation() -> Dict[str, Any]:
    """Run comprehensive validation of the refactored application."""
    results = {}
    
    print("🔍 Validating AI Construct PDF Opdeler - Refactored Setup")
    print("=" * 60)
    
    # Python version check
    print("\n📍 Checking Python Version...")
    py_ok, py_msg = check_python_version()
    results['python'] = {'success': py_ok, 'message': py_msg}
    print(f"  {py_msg}")
    
    # Dependencies check
    print("\n📦 Checking Dependencies...")
    deps_ok, available, missing = check_dependencies()
    results['dependencies'] = {'success': deps_ok, 'available': available, 'missing': missing}
    print(f"  Available: {len(available)} packages")
    for pkg in available:
        print(f"    ✓ {pkg}")
    if missing:
        print(f"  Missing: {len(missing)} packages")
        for pkg in missing:
            print(f"    ✗ {pkg}")
    
    # File structure check
    print("\n📁 Checking File Structure...")
    files_ok, existing, missing_files = check_file_structure()
    results['file_structure'] = {'success': files_ok, 'existing': existing, 'missing': missing_files}
    print(f"  Found: {len(existing)}/{len(existing) + len(missing_files)} required files")
    if missing_files:
        print("  Missing files:")
        for file in missing_files:
            print(f"    ✗ {file}")
    
    # Imports check
    print("\n🔗 Checking Module Imports...")
    imports_ok, successful, failed = check_imports()
    results['imports'] = {'success': imports_ok, 'successful': successful, 'failed': failed}
    print(f"  Successful: {len(successful)} modules")
    if failed:
        print(f"  Failed: {len(failed)} modules")
        for failure in failed:
            print(f"    ✗ {failure}")
    
    # Configuration check
    print("\n⚙️  Checking Configuration...")
    config_ok, valid_items, issues = check_configuration()
    results['configuration'] = {'success': config_ok, 'valid': valid_items, 'issues': issues}
    for item in valid_items:
        print(f"  ✓ {item}")
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    
    # Overall result
    all_critical_ok = py_ok and deps_ok and files_ok and imports_ok
    results['overall'] = {'success': all_critical_ok}
    
    print("\n" + "=" * 60)
    if all_critical_ok:
        print("✅ VALIDATION PASSED - Application is ready to run!")
        print("   You can start the application with: python src/main.py")
    else:
        print("❌ VALIDATION FAILED - Please fix the issues above")
        
        if not deps_ok:
            print("\n💡 To install missing dependencies:")
            print("   pip install -r src/requirements.txt")
            
        if not files_ok:
            print("\n💡 Some files are missing from the refactored structure")
            
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    run_validation()