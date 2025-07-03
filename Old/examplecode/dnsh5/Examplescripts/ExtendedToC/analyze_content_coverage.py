#!/usr/bin/env python3
"""
Analyze content coverage: compare LlamaParse output with final chapter assignments
to check if any text was missed or unassigned.
"""

import json
import sys
from collections import defaultdict

def analyze_content_coverage(llama_parse_json, chapters_with_text_json):
    """Compare total content between LlamaParse and final chapters"""
    
    # Load LlamaParse output
    with open(llama_parse_json, 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    # Load final chapters with text
    with open(chapters_with_text_json, 'r', encoding='utf-8') as f:
        chapters_data = json.load(f)
    
    # Analyze LlamaParse content
    total_pages = len(llama_data['pages'])
    page_content = {}
    total_llama_chars = 0
    
    for page in llama_data['pages']:
        page_num = page.get('page', 0)
        text_content = page.get('text', '')
        page_content[page_num] = text_content
        total_llama_chars += len(text_content)
    
    print(f"=== LLAMAPARSE ANALYSIS ===")
    print(f"Total pages: {total_pages}")
    print(f"Total characters: {total_llama_chars:,}")
    print(f"Average chars per page: {total_llama_chars // total_pages:,}")
    
    # Analyze chapter assignments
    total_chapter_chars = 0
    page_coverage = defaultdict(bool)  # Track which pages are covered
    chapter_count = 0
    section_count = 0
    
    def count_text_in_item(item_data, item_id=""):
        nonlocal total_chapter_chars, chapter_count, section_count
        
        if isinstance(item_data, dict):
            # Count text in this item
            text_content = item_data.get('text', '')
            total_chapter_chars += len(text_content)
            
            # Track page coverage
            start_page = item_data.get('start_page_used', 0)
            end_page = item_data.get('end_page_used', 0)
            for page_num in range(start_page, end_page + 1):
                page_coverage[page_num] = True
            
            # Count items
            if '.' not in item_id:  # Main chapter
                chapter_count += 1
            else:  # Section
                section_count += 1
            
            # Process nested sections
            if 'sections' in item_data:
                for section_id, section_data in item_data['sections'].items():
                    count_text_in_item(section_data, section_id)
    
    for chapter_id, chapter_data in chapters_data.items():
        count_text_in_item(chapter_data, chapter_id)
    
    print(f"\n=== CHAPTER ASSIGNMENT ANALYSIS ===")
    print(f"Total chapters: {chapter_count}")
    print(f"Total sections: {section_count}")
    print(f"Total assigned characters: {total_chapter_chars:,}")
    print(f"Coverage ratio: {total_chapter_chars / total_llama_chars * 100:.1f}%")
    
    # Find uncovered pages
    uncovered_pages = []
    for page_num in range(1, total_pages + 1):
        if not page_coverage[page_num]:
            uncovered_pages.append(page_num)
    
    if uncovered_pages:
        print(f"\n=== UNCOVERED PAGES ===")
        print(f"Pages not assigned to any chapter: {uncovered_pages}")
        uncovered_chars = sum(len(page_content.get(p, '')) for p in uncovered_pages)
        print(f"Characters in uncovered pages: {uncovered_chars:,}")
        print(f"Percentage of content uncovered: {uncovered_chars / total_llama_chars * 100:.1f}%")
    else:
        print(f"\n✅ All pages are covered by chapter assignments!")
    
    # Detailed page-by-page analysis
    print(f"\n=== PAGE-BY-PAGE COVERAGE ===")
    for page_num in range(1, min(11, total_pages + 1)):  # Show first 10 pages
        is_covered = page_coverage[page_num]
        char_count = len(page_content.get(page_num, ''))
        status = "✅ COVERED" if is_covered else "❌ UNCOVERED"
        print(f"Page {page_num:2d}: {char_count:4d} chars - {status}")
    
    if total_pages > 10:
        print(f"... (showing first 10 of {total_pages} pages)")
    
    return {
        'total_llama_chars': total_llama_chars,
        'total_chapter_chars': total_chapter_chars,
        'coverage_ratio': total_chapter_chars / total_llama_chars,
        'uncovered_pages': uncovered_pages,
        'total_pages': total_pages,
        'chapters': chapter_count,
        'sections': section_count
    }

if __name__ == "__main__":
    llama_parse_file = "output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed.json"
    chapters_file = "output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text.json"
    
    try:
        result = analyze_content_coverage(llama_parse_file, chapters_file)
        print(f"\n=== SUMMARY ===")
        print(f"Coverage: {result['coverage_ratio']*100:.1f}% of content assigned to chapters")
        if result['coverage_ratio'] > 0.95:
            print("✅ Excellent coverage - minimal content loss")
        elif result['coverage_ratio'] > 0.85:
            print("⚠️  Good coverage - some content may be in headers/footers")
        else:
            print("❌ Significant content missing - investigation needed")
            
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error analyzing content: {e}") 