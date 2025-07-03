#!/usr/bin/env python3
"""
Clean version of intelligent content splitter
"""

import json
import re
from collections import defaultdict

def split_content_intelligently(corrected_llamaparse_json, toc_json, output_json):
    """Split content intelligently using corrected heading hierarchy"""
    
    print("=== INTELLIGENT CONTENT SPLITTING V2 ===\n")
    
    # Load data
    with open(corrected_llamaparse_json, 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    with open(toc_json, 'r', encoding='utf-8') as f:
        toc_data = json.load(f)
    
    print(f"Loaded {len(llama_data['pages'])} pages from LlamaParse")
    print(f"Loaded {len(toc_data)} main sections from TOC")
    
    # Build flattened section map
    all_sections = {}
    for section_id, section_info in toc_data.items():
        all_sections[section_id] = section_info
        if 'sections' in section_info:
            for sub_id, sub_info in section_info['sections'].items():
                all_sections[sub_id] = sub_info
    
    print(f"Total sections (including subsections): {len(all_sections)}")
    
    # Map pages to sections  
    page_to_sections = defaultdict(list)
    for section_id, section_info in all_sections.items():
        start_page = section_info.get('start')
        end_page = section_info.get('end')
        if start_page and end_page:
            for page_num in range(start_page, end_page + 1):
                page_to_sections[page_num].append(section_id)
    
    print(f"Mapped {len(page_to_sections)} pages to sections")
    
    # Process pages
    results = {}
    total_original = 0
    total_split = 0
    
    for page_data in llama_data['pages']:
        page_num = page_data['page']
        
        if page_num not in page_to_sections:
            continue
            
        page_text = page_data.get('text', '')
        total_original += len(page_text)
        
        sections_on_page = page_to_sections[page_num]
        print(f"Page {page_num}: {len(sections_on_page)} sections, {len(page_text):,} chars")
        
        # For now, assign full page content to each section (we'll improve this later)
        for section_id in sections_on_page:
            if section_id not in results:
                results[section_id] = {
                    'title': all_sections[section_id]['title'],
                    'text': '',
                    'pages': []
                }
            
            results[section_id]['text'] += page_text + '\n\n'
            results[section_id]['pages'].append(page_num)
            total_split += len(page_text)
    
    # Create final output
    final_output = {}
    for section_id, result in results.items():
        section_info = all_sections[section_id]
        final_output[section_id] = {
            'title': result['title'],
            'start_page': section_info.get('start'),
            'end_page': section_info.get('end'),
            'text': result['text'].strip(),
            'character_count': len(result['text'].strip()),
            'pages_processed': result['pages'],
            'splitting_method': 'full_page_assignment_v2'
        }
    
    # Save results
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    # Report
    duplication_ratio = (total_split / total_original) if total_original > 0 else 0
    print(f"\n=== RESULTS ===")
    print(f"Original chars: {total_original:,}")
    print(f"Split chars: {total_split:,}")
    print(f"Duplication ratio: {duplication_ratio:.1%}")
    print(f"Sections processed: {len(results)}")
    print(f"Saved to: {output_json}")
    
    return results

if __name__ == "__main__":
    corrected_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
    toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    output_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_v2.json'
    
    result = split_content_intelligently(corrected_file, toc_file, output_file) 