#!/usr/bin/env python3
"""
Investigate heading level detection in LlamaParse output to understand
why we're only seeing H1 headings when the document clearly has hierarchy.
"""

import json
from collections import defaultdict

def investigate_heading_levels(llama_parse_json, toc_json):
    """Investigate heading detection vs actual document structure"""
    
    # Load LlamaParse output
    with open(llama_parse_json, 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    # Load our TOC structure
    with open(toc_json, 'r', encoding='utf-8') as f:
        toc_data = json.load(f)
    
    print("=== HEADING LEVEL INVESTIGATION ===\n")
    
    # Show actual TOC structure
    print("=== EXPECTED HIERARCHY FROM TOC ===")
    for chapter_id, chapter_info in toc_data.items():
        title = chapter_info['title']
        start_page = chapter_info.get('start_page', 'unknown')
        end_page = chapter_info.get('end_page', 'unknown')
        
        # Determine expected level based on chapter ID structure
        if '.' not in chapter_id:
            expected_level = 1  # Main chapter
        elif chapter_id.count('.') == 1:
            expected_level = 2  # First-level subsection
        elif chapter_id.count('.') == 2:
            expected_level = 3  # Second-level subsection
        else:
            expected_level = 4  # Deeper nesting
        
        print(f"  {chapter_id}: '{title}' (Expected H{expected_level}) - Pages {start_page}-{end_page}")
    
    print(f"\n=== WHAT LLAMAPARSE DETECTED ===")
    
    # Extract all headings from LlamaParse and organize by page
    headings_by_page = defaultdict(list)
    
    for page in llama_data['pages']:
        page_num = page['page']
        for item in page.get('items', []):
            if item.get('type') == 'heading':
                headings_by_page[page_num].append({
                    'text': item.get('value', ''),
                    'level': item.get('lvl'),
                    'bbox': item.get('bBox', {}),
                    'y_pos': item.get('bBox', {}).get('y', 0)
                })
    
    # Check a few key pages to see heading patterns
    key_pages = [3, 4, 5, 10, 15, 20]  # Sample pages where we expect sections
    
    for page_num in key_pages:
        if page_num in headings_by_page:
            print(f"\nPage {page_num} headings:")
            # Sort by Y position (top to bottom)
            headings = sorted(headings_by_page[page_num], key=lambda x: x['y_pos'])
            for heading in headings:
                y_pos = heading['y_pos']
                level = heading['level']
                text = heading['text'][:60] + '...' if len(heading['text']) > 60 else heading['text']
                print(f"  H{level} at y={y_pos:.0f}: '{text}'")
    
    print(f"\n=== ANALYSIS ===")
    
    # Look for potential section patterns in headings
    section_patterns = []
    for page_num, headings in headings_by_page.items():
        for heading in headings:
            text = heading['text']
            if any(pattern in text.upper() for pattern in ['2.1', '2.2', '3.1', '3.2', 'WERFINRICHTING', 'BESCHRIJVING']):
                section_patterns.append({
                    'page': page_num,
                    'text': text,
                    'detected_level': heading['level'],
                    'y_pos': heading['y_pos']
                })
    
    print("Potential subsection headings detected as H1:")
    for pattern in section_patterns[:10]:  # Show first 10
        print(f"  Page {pattern['page']}: H{pattern['detected_level']} - '{pattern['text']}'")
    
    print(f"\n=== POTENTIAL ISSUES ===")
    print("1. Document may not use semantic heading tags")
    print("2. All text might be formatted with same font size")
    print("3. LlamaParse might need different configuration")
    print("4. Manual parsing based on text patterns may be needed")
    
    return {
        'total_headings': sum(len(headings) for headings in headings_by_page.values()),
        'pages_with_headings': len(headings_by_page),
        'section_patterns': section_patterns
    }

if __name__ == "__main__":
    result = investigate_heading_levels(
        'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed.json',
        'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    ) 