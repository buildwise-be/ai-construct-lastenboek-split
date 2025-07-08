#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify modular component imports work correctly.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test all major component imports."""
    print("🔍 Testing Modular Component Imports")
    print("=" * 40)
    
    try:
        print("📋 Testing config imports...", end=" ")
        from config.settings import APP_NAME, COLORS, GUI_CONFIG
        print("✅")
        
        print("🧠 Testing core imports...", end=" ")
        from core.ai_client import initialize_vertex_model
        from core.file_utils import setup_output_directory
        print("✅")
        
        print("🎨 Testing GUI components...", end=" ")
        from gui.components.styled_components import StyledButton, StyledFrame
        print("✅")
        
        print("📄 Testing PDF processor...", end=" ")
        from core.pdf_processor import step1_generate_toc
        print("✅")
        
        print("🤖 Testing category matcher...", end=" ")
        from core.category_matcher import step2_match_categories
        print("✅")
        
        print("\n✅ ALL IMPORTS SUCCESSFUL!")
        print("\n🚀 Components:")
        print(f"   App Name: {APP_NAME}")
        print(f"   Available Colors: {len(COLORS)} defined")
        print(f"   GUI Config: {len(GUI_CONFIG)} settings")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing Basic Functionality")
    print("=" * 40)
    
    try:
        print("📁 Testing file utilities...", end=" ")
        from core.file_utils import setup_output_directory
        test_dir = setup_output_directory("test", "output")
        if test_dir and os.path.exists(test_dir):
            print("✅")
        else:
            print("❌")
            return False
            
        print("🎨 Testing GUI components...", end=" ")
        from gui.components.styled_components import StyledButton
        test_button = StyledButton("Test", "primary")
        if test_button:
            print("✅")
        else:
            print("❌")
            return False
            
        print("\n✅ BASIC FUNCTIONALITY TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Modular Components Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test functionality
        functionality_ok = test_functionality()
        
        if functionality_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("The modular components are working correctly.")
            sys.exit(0)
        else:
            print("\n⚠️ Functionality tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Import tests failed.")
        print("💡 Try running: python setup.py")
        sys.exit(1) 