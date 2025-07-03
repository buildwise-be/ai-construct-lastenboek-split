#!/usr/bin/env python3
"""
Debug script to understand why the content splitter isn't finding any sections.
"""

import json
from collections import defaultdict

def debug_content_mapping():
    """Debug the content mapping process"""
    
    # Load data
    corrected_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
    toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    
    print("=== DEBUGGING CONTENT MAPPING ===\n")
    
    # Check TOC data structure
    with open(toc_file, 'r', encoding='utf-8') as f:
        toc_data = json.load(f)
    
    print("=== TOC DATA STRUCTURE ===")
    for section_id, section_info in list(toc_data.items())[:5]:  # First 5 items
        print(f"Section {section_id}:")
        for key, value in section_info.items():
            print(f"  {key}: {value}")
        print()
    
    # Check for page information in TOC
    has_page_info = False
    page_fields = ['start_page', 'end_page', 'start_page_used', 'end_page_used']
    
    for section_id, section_info in toc_data.items():
        for field in page_fields:
            if field in section_info and section_info[field] is not None:
                has_page_info = True
                print(f"Found page info: {section_id} has {field} = {section_info[field]}")
                break
        if has_page_info:
            break
    
    if not has_page_info:
        print("⚠️  NO PAGE INFORMATION FOUND in TOC data!")
        print("Available fields in TOC:")
        if toc_data:
            first_section = list(toc_data.values())[0]
            for key in first_section.keys():
                print(f"  - {key}")
    
    # Check LlamaParse data structure
    with open(corrected_file, 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    print(f"\n=== LLAMAPARSE DATA STRUCTURE ===")
    print(f"Total pages in LlamaParse: {len(llama_data['pages'])}")
    
    # Check a sample page
    if llama_data['pages']:
        sample_page = llama_data['pages'][0]
        print(f"Sample page {sample_page['page']} structure:")
        for key in sample_page.keys():
            if key == 'items':
                print(f"  {key}: {len(sample_page[key])} items")
            elif key == 'text':
                print(f"  {key}: {len(sample_page[key])} chars")
            else:
                print(f"  {key}: {type(sample_page[key])}")
    
    # Manual page mapping attempt
    print(f"\n=== MANUAL PAGE MAPPING ===")
    page_to_sections = defaultdict(list)
    
    for section_id, section_info in toc_data.items():
        print(f"Processing section {section_id}: {section_info.get('title', 'No title')}")
        
        # Try different page field combinations
        start_page = None
        end_page = None
        
        for start_field in ['start_page_used', 'start_page']:
            if start_field in section_info and section_info[start_field] is not None:
                start_page = section_info[start_field]
                break
        
        for end_field in ['end_page_used', 'end_page']:
            if end_field in section_info and section_info[end_field] is not None:
                end_page = section_info[end_field]
                break
        
        print(f"  start_page: {start_page}, end_page: {end_page}")
        
        if start_page and end_page:
            for page_num in range(start_page, end_page + 1):
                page_to_sections[page_num].append(section_id)
            print(f"  ✅ Mapped to pages {start_page}-{end_page}")
        else:
            print(f"  ❌ No valid page range")
    
    print(f"\n=== FINAL PAGE MAPPING ===")
    print(f"Pages with sections: {len(page_to_sections)}")
    
    for page_num in sorted(list(page_to_sections.keys())[:10]):  # First 10 pages
        sections = page_to_sections[page_num]
        print(f"Page {page_num}: {len(sections)} sections - {sections}")
    
    return {
        'toc_sections': len(toc_data),
        'llama_pages': len(llama_data['pages']),
        'mapped_pages': len(page_to_sections),
        'has_page_info': has_page_info
    }

if __name__ == "__main__":
    result = debug_content_mapping() 