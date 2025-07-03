#!/usr/bin/env python3
import json

with open('output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== STRUCTURE ANALYSIS ===')
total_duplicated_chars = 0
pages_with_multiple_assignments = {}

for chapter_id, chapter_data in data.items():
    print(f'Chapter {chapter_id}: {chapter_data["title"]}')
    
    # Track which pages are used by this chapter
    start_page = chapter_data["start_page_used"]
    end_page = chapter_data["end_page_used"]
    chapter_pages = end_page - start_page + 1
    
    text_length = len(chapter_data.get('text', ''))
    print(f'  Main text: Pages {start_page}-{end_page} ({chapter_pages} pages) | Text: {text_length:,} chars')
    
    # Record page usage for chapter
    for page in range(start_page, end_page + 1):
        if page not in pages_with_multiple_assignments:
            pages_with_multiple_assignments[page] = []
        pages_with_multiple_assignments[page].append(f"Chapter {chapter_id}")
    
    if 'sections' in chapter_data:
        print(f'  Sections: {len(chapter_data["sections"])}')
        for section_id, section_data in chapter_data['sections'].items():
            sect_start = section_data['start_page_used']
            sect_end = section_data['end_page_used']
            section_pages = sect_end - sect_start + 1
            section_text_length = len(section_data.get('text', ''))
            print(f'    {section_id}: {section_data["title"]} | Pages: {sect_start}-{sect_end} ({section_pages} pages) | Text: {section_text_length:,} chars')
            
            # Record page usage for sections
            for page in range(sect_start, sect_end + 1):
                if page not in pages_with_multiple_assignments:
                    pages_with_multiple_assignments[page] = []
                pages_with_multiple_assignments[page].append(f"Section {section_id}")
    print()

print('=== PAGES WITH MULTIPLE ASSIGNMENTS ===')
for page_num in sorted(pages_with_multiple_assignments.keys()):
    assignments = pages_with_multiple_assignments[page_num]
    if len(assignments) > 1:
        print(f'Page {page_num}: {assignments}')

print('\n=== PAGE COVERAGE OVERLAP ANALYSIS ===')
# Find the most problematic overlaps
overlap_count = 0
for page_num, assignments in pages_with_multiple_assignments.items():
    if len(assignments) > 1:
        overlap_count += len(assignments) - 1

print(f"Total page assignments: {sum(len(assignments) for assignments in pages_with_multiple_assignments.values())}")
print(f"Unique pages: {len(pages_with_multiple_assignments)}")
print(f"Overlapping assignments: {overlap_count}")
print(f"Duplication factor: {(sum(len(assignments) for assignments in pages_with_multiple_assignments.values()) / len(pages_with_multiple_assignments)):.1f}x") 