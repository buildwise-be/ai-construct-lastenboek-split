#!/usr/bin/env python3
"""
Compare the new intelligent splitting results with the original extract_chapter_text output
"""

import json

def compare_splitting_results():
    """Compare old vs new content splitting results"""
    
    print("=== COMPARING SPLITTING RESULTS ===\n")
    
    # Load original results
    original_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text.json'
    new_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_v2.json'
    
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(new_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    print("=== SECTION COUNT COMPARISON ===")
    print(f"Original method: {len(original_data)} sections")
    print(f"New method: {len(new_data)} sections")
    
    # Compare character counts
    original_total_chars = sum(section.get('character_count', 0) for section in original_data.values())
    new_total_chars = sum(section.get('character_count', 0) for section in new_data.values())
    
    print(f"\n=== CHARACTER COUNT COMPARISON ===")
    print(f"Original total chars: {original_total_chars:,}")
    print(f"New total chars: {new_total_chars:,}")
    
    if original_total_chars > 0:
        print(f"Reduction: {(1 - new_total_chars/original_total_chars)*100:.1f}%")
    else:
        print("⚠️  Original method has 0 characters - it didn't extract any content!")
        print("✅ New method successfully extracted content")
    
    # Analyze why original has 0 chars
    if original_total_chars == 0:
        print(f"\n=== ANALYZING ORIGINAL METHOD FAILURE ===")
        for section_id, section_data in original_data.items():
            char_count = section_data.get('character_count', 0)
            text_length = len(section_data.get('text', ''))
            print(f"Section {section_id}: char_count={char_count}, actual_text_length={text_length}")
            if text_length > 100:  # Show sample if there's text
                sample_text = section_data.get('text', '')[:100]
                print(f"  Sample text: '{sample_text}...'")
    
    # Compare some specific sections
    print(f"\n=== SECTION COMPARISON ===")
    
    common_sections = set(original_data.keys()) & set(new_data.keys())
    print(f"Common sections: {len(common_sections)}")
    
    if common_sections:
        for section_id in sorted(list(common_sections))[:10]:
            orig_chars = original_data[section_id].get('character_count', 0)
            new_chars = new_data[section_id].get('character_count', 0)
            
            if orig_chars > 0:
                reduction = (1 - new_chars/orig_chars)*100
                print(f"{section_id}: {orig_chars:,} → {new_chars:,} chars ({reduction:+.1f}%)")
            else:
                print(f"{section_id}: {orig_chars:,} → {new_chars:,} chars (NEW CONTENT!)")
    
    # Show new method section breakdown
    print(f"\n=== NEW METHOD SECTION BREAKDOWN ===")
    new_sections_by_level = {}
    for section_id, section_data in new_data.items():
        level = section_id.count('.') + 1
        if level not in new_sections_by_level:
            new_sections_by_level[level] = []
        new_sections_by_level[level].append((section_id, section_data.get('character_count', 0)))
    
    for level in sorted(new_sections_by_level.keys()):
        sections = new_sections_by_level[level]
        total_chars = sum(chars for _, chars in sections)
        print(f"Level {level}: {len(sections)} sections, {total_chars:,} chars")
        
        # Show top 3 sections by character count
        top_sections = sorted(sections, key=lambda x: x[1], reverse=True)[:3]
        for section_id, chars in top_sections:
            title = new_data[section_id].get('title', 'No title')
            print(f"  {section_id}: {chars:,} chars - {title[:50]}...")
    
    # Check sections only in one method
    only_original = set(original_data.keys()) - set(new_data.keys())
    only_new = set(new_data.keys()) - set(original_data.keys())
    
    if only_original:
        print(f"\n=== SECTIONS ONLY IN ORIGINAL ===")
        for section_id in sorted(only_original):
            print(f"  {section_id}: {original_data[section_id].get('title', 'No title')}")
    
    if only_new:
        print(f"\n=== SECTIONS ONLY IN NEW ===")
        for section_id in sorted(only_new):
            print(f"  {section_id}: {new_data[section_id].get('title', 'No title')}")
    
    # Check pages processed
    print(f"\n=== PAGE PROCESSING COMPARISON ===")
    original_pages = set()
    new_pages = set()
    
    for section in original_data.values():
        pages = section.get('pages_processed', [])
        if isinstance(pages, list):
            original_pages.update(pages)
    
    for section in new_data.values():
        pages = section.get('pages_processed', [])
        if isinstance(pages, list):
            new_pages.update(pages)
    
    print(f"Original method processed: {len(original_pages)} unique pages")
    print(f"New method processed: {len(new_pages)} unique pages")
    
    return {
        'original_sections': len(original_data),
        'new_sections': len(new_data),
        'original_chars': original_total_chars,
        'new_chars': new_total_chars,
        'reduction_percent': (1 - new_total_chars/original_total_chars)*100,
        'original_pages': len(original_pages),
        'new_pages': len(new_pages)
    }

if __name__ == "__main__":
    result = compare_splitting_results() 