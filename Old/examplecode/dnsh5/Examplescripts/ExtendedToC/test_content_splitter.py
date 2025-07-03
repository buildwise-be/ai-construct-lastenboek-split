#!/usr/bin/env python3
"""
Simple test to find the KeyError location
"""

import json
import traceback

def test_step_by_step():
    """Test each part of the content splitter step by step"""
    
    try:
        print("Step 1: Loading files...")
        corrected_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
        toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
        
        with open(corrected_file, 'r', encoding='utf-8') as f:
            llama_data = json.load(f)
        print("✅ Loaded LlamaParse data")
        
        with open(toc_file, 'r', encoding='utf-8') as f:
            toc_data = json.load(f)
        print("✅ Loaded TOC data")
        
        print("\nStep 2: Building section hierarchy...")
        
        # Import just the functions we need
        import sys
        sys.path.append('.')
        from intelligent_content_splitter import build_section_hierarchy
        
        hierarchy = build_section_hierarchy(toc_data)
        print(f"✅ Built hierarchy: {len(hierarchy)} sections")
        
        # Check if '2.1.1' is in hierarchy
        if '2.1.1' in hierarchy:
            print("✅ Section '2.1.1' found in hierarchy")
        else:
            print("❌ Section '2.1.1' NOT found in hierarchy")
            print(f"Available sections: {sorted(hierarchy.keys())}")
        
    except Exception as e:
        print(f"❌ Error in step: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_step_by_step() 