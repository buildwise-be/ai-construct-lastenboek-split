#!/usr/bin/env python3
"""
Debug script to check hierarchy building
"""

import json
from collections import defaultdict

def debug_hierarchy():
    """Debug the hierarchy building process"""
    
    toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    
    with open(toc_file, 'r', encoding='utf-8') as f:
        toc_data = json.load(f)
    
    print("=== TOC DATA STRUCTURE ===")
    print(f"Main sections: {list(toc_data.keys())}")
    
    # Show structure of each main section
    for section_id, section_info in toc_data.items():
        print(f"\nSection {section_id}: {section_info['title']}")
        print(f"  Pages: {section_info['start']}-{section_info['end']}")
        
        if 'sections' in section_info:
            print(f"  Subsections: {len(section_info['sections'])}")
            for sub_id, sub_info in section_info['sections'].items():
                print(f"    {sub_id}: {sub_info['title']} (pages {sub_info['start']}-{sub_info['end']})")
    
    # Build hierarchy manually with debug info
    print(f"\n=== BUILDING HIERARCHY ===")
    hierarchy = {}
    
    # First, add all main sections
    print("Adding main sections:")
    for section_id, section_info in toc_data.items():
        hierarchy[section_id] = {
            'level': section_id.count('.') + 1,
            'title': section_info['title'],
            'children': []
        }
        print(f"  Added: {section_id}")
    
    # Then, add all nested subsections
    print("\nAdding subsections:")
    for section_id, section_info in toc_data.items():
        if 'sections' in section_info:
            for subsection_id, subsection_info in section_info['sections'].items():
                hierarchy[subsection_id] = {
                    'level': subsection_id.count('.') + 1,
                    'title': subsection_info['title'],
                    'children': []
                }
                print(f"  Added: {subsection_id}")
    
    print(f"\nTotal sections in hierarchy: {len(hierarchy)}")
    print(f"Hierarchy keys: {sorted(hierarchy.keys())}")
    
    # Check page mapping
    print(f"\n=== PAGE MAPPING ===")
    page_to_sections = defaultdict(list)
    
    # Flatten all sections including nested ones
    all_sections = {}
    
    for section_id, section_info in toc_data.items():
        # Add main section
        all_sections[section_id] = section_info
        
        # Add subsections if they exist
        if 'sections' in section_info:
            for subsection_id, subsection_info in section_info['sections'].items():
                all_sections[subsection_id] = subsection_info
    
    print(f"All sections: {sorted(all_sections.keys())}")
    
    # Map pages to sections
    for section_id, section_info in all_sections.items():
        start_page = section_info.get('start')
        end_page = section_info.get('end')
        
        if start_page and end_page:
            for page_num in range(start_page, end_page + 1):
                page_to_sections[page_num].append(section_id)
    
    # Check problematic page 6
    print(f"\nPage 6 sections: {page_to_sections[6]}")
    
    # Check if all sections on page 6 exist in hierarchy
    for section_id in page_to_sections[6]:
        if section_id in hierarchy:
            print(f"  ✅ {section_id} exists in hierarchy")
        else:
            print(f"  ❌ {section_id} NOT in hierarchy")

if __name__ == "__main__":
    debug_hierarchy() 