#!/usr/bin/env python3
"""
Intelligent content splitter v3 with boundary detection
"""

import json
import re
from collections import defaultdict

def split_content_intelligently_v3(corrected_llamaparse_json, toc_json, output_json):
    """Split content using intelligent boundary detection within pages"""
    
    print("=== INTELLIGENT CONTENT SPLITTING V3 ===\n")
    
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
    
    # Process pages with boundary detection
    results = {}
    total_original = 0
    total_split = 0
    boundary_matches = 0
    
    for page_data in llama_data['pages']:
        page_num = page_data['page']
        
        if page_num not in page_to_sections:
            continue
            
        page_text = page_data.get('text', '')
        total_original += len(page_text)
        
        sections_on_page = page_to_sections[page_num]
        print(f"Page {page_num}: {len(sections_on_page)} sections, {len(page_text):,} chars")
        
        # Use boundary detection for pages with multiple sections
        if len(sections_on_page) > 1:
            page_splits = split_page_content_by_boundaries(page_data, sections_on_page, all_sections)
            
            # Check if we found boundaries
            if any(split['boundary_found'] for split in page_splits.values()):
                boundary_matches += 1
                print(f"  ✅ Found section boundaries")
        else:
            # Single section - assign full page
            page_splits = {sections_on_page[0]: {
                'text': page_text,
                'boundary_found': False,
                'method': 'single_section'
            }}
        
        # Add to results
        for section_id, split_data in page_splits.items():
            if section_id not in results:
                results[section_id] = {
                    'title': all_sections[section_id]['title'],
                    'text': '',
                    'pages': [],
                    'boundary_pages': 0,
                    'total_pages': 0
                }
            
            results[section_id]['text'] += split_data['text'] + '\n\n'
            results[section_id]['pages'].append(page_num)
            results[section_id]['total_pages'] += 1
            if split_data['boundary_found']:
                results[section_id]['boundary_pages'] += 1
            
            total_split += len(split_data['text'])
    
    # Create final output
    final_output = {}
    for section_id, result in results.items():
        section_info = all_sections[section_id]
        boundary_ratio = result['boundary_pages'] / result['total_pages'] if result['total_pages'] > 0 else 0
        
        final_output[section_id] = {
            'title': result['title'],
            'start_page': section_info.get('start'),
            'end_page': section_info.get('end'),
            'text': result['text'].strip(),
            'character_count': len(result['text'].strip()),
            'pages_processed': result['pages'],
            'splitting_method': 'intelligent_boundary_detection_v3',
            'boundary_detection_ratio': f"{boundary_ratio:.1%}",
            'boundary_pages': result['boundary_pages'],
            'total_pages': result['total_pages']
        }
    
    # Save results
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    # Report
    duplication_ratio = (total_split / total_original) if total_original > 0 else 0
    boundary_success_rate = boundary_matches / len([p for p in page_to_sections.values() if len(p) > 1]) if page_to_sections else 0
    
    print(f"\n=== RESULTS V3 ===")
    print(f"Original chars: {total_original:,}")
    print(f"Split chars: {total_split:,}")
    print(f"Duplication ratio: {duplication_ratio:.1%}")
    print(f"Sections processed: {len(results)}")
    print(f"Pages with boundaries found: {boundary_matches}")
    print(f"Boundary detection success rate: {boundary_success_rate:.1%}")
    print(f"Saved to: {output_json}")
    
    return results

def split_page_content_by_boundaries(page_data, sections_on_page, all_sections):
    """Split page content using heading boundary detection"""
    
    page_num = page_data['page']
    items = page_data.get('items', [])
    
    # Sort items by Y position (top to bottom)
    sorted_items = sorted(
        [item for item in items if item.get('bBox')],
        key=lambda x: x.get('bBox', {}).get('y', 0)
    )
    
    # Find section headings on this page
    section_headings = []
    for item in sorted_items:
        if item.get('type') == 'heading':
            heading_text = item.get('value', '').strip()
            y_pos = item.get('bBox', {}).get('y', 0)
            
            # Try to match heading to sections
            matched_section = match_heading_to_section(heading_text, sections_on_page, all_sections)
            if matched_section:
                section_headings.append({
                    'section_id': matched_section,
                    'y_pos': y_pos,
                    'text': heading_text,
                    'item_index': sorted_items.index(item)
                })
    
    # Sort headings by position
    section_headings.sort(key=lambda x: x['y_pos'])
    
    # Create boundaries and extract content
    page_splits = {}
    
    if section_headings:
        # Use heading boundaries
        for i, heading in enumerate(section_headings):
            section_id = heading['section_id']
            start_index = heading['item_index']
            
            # Find end index (next section heading or end of page)
            end_index = len(sorted_items)
            if i + 1 < len(section_headings):
                end_index = section_headings[i + 1]['item_index']
            
            # Extract content between boundaries
            section_items = sorted_items[start_index:end_index]
            section_text = extract_text_from_items(section_items)
            
            page_splits[section_id] = {
                'text': section_text,
                'boundary_found': True,
                'method': 'heading_boundary',
                'start_y': heading['y_pos'],
                'items_count': len(section_items)
            }
        
        # Assign remaining sections (those without headings) fallback content
        for section_id in sections_on_page:
            if section_id not in page_splits:
                page_splits[section_id] = {
                    'text': page_data.get('text', ''),  # Fallback to full page
                    'boundary_found': False,
                    'method': 'fallback_no_heading'
                }
    else:
        # No section headings found - split equally or use fallback
        page_text = page_data.get('text', '')
        for section_id in sections_on_page:
            page_splits[section_id] = {
                'text': page_text,
                'boundary_found': False,
                'method': 'fallback_no_boundaries'
            }
    
    return page_splits

def match_heading_to_section(heading_text, sections_on_page, all_sections):
    """Match a heading to one of the sections on the page"""
    
    # Clean heading text
    heading_clean = heading_text.strip()
    
    # Method 1: Direct section number match
    for section_id in sections_on_page:
        if heading_clean.startswith(section_id + '.') or heading_clean.startswith(section_id + ' '):
            return section_id
    
    # Method 2: Extract section number from heading
    section_pattern = r'^(\d+(?:\.\d+)*)\.'
    match = re.match(section_pattern, heading_clean)
    if match:
        potential_section = match.group(1)
        if potential_section in sections_on_page:
            return potential_section
    
    # Method 3: Title matching
    for section_id in sections_on_page:
        section_title = all_sections[section_id]['title']
        
        # Skip sections with null titles
        if section_title is None:
            continue
        
        # Clean both texts for comparison
        title_clean = re.sub(r'[^\w\s]', '', section_title.lower()).strip()
        heading_lower = re.sub(r'[^\w\s]', '', heading_clean.lower()).strip()
        
        # Check for substantial overlap
        if len(title_clean) > 5 and len(heading_lower) > 5:
            if title_clean in heading_lower or heading_lower in title_clean:
                # Additional check: at least 70% of the shorter text should match
                overlap_ratio = len(set(title_clean.split()) & set(heading_lower.split())) / min(len(title_clean.split()), len(heading_lower.split()))
                if overlap_ratio >= 0.7:
                    return section_id
    
    return None

def extract_text_from_items(items):
    """Extract text content from page items"""
    text_parts = []
    
    for item in items:
        if item.get('type') in ['text', 'heading']:
            item_text = item.get('value', '')
            if item_text and item_text.strip():
                text_parts.append(item_text.strip())
    
    return '\n\n'.join(text_parts)

if __name__ == "__main__":
    corrected_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
    toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    output_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_v3.json'
    
    result = split_content_intelligently_v3(corrected_file, toc_file, output_file) 