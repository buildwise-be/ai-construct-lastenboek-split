#!/usr/bin/env python3
"""
Intelligent content splitter that uses corrected heading hierarchy
to assign page content to the appropriate sections without duplication.
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

def split_content_intelligently(corrected_llamaparse_json, toc_json, output_json):
    """
    Split content intelligently using corrected heading hierarchy.
    Each section gets only its relevant content portion.
    """
    # Load data
    with open(corrected_llamaparse_json, 'r', encoding='utf-8') as f:
        llama_data = json.load(f)
    
    with open(toc_json, 'r', encoding='utf-8') as f:
        toc_data = json.load(f)
    
    print("=== INTELLIGENT CONTENT SPLITTING ===\n")
    
    # Build section hierarchy and page mappings
    try:
        section_hierarchy = build_section_hierarchy(toc_data)
        print(f"✅ Built hierarchy for {len(section_hierarchy)} sections")
    except Exception as e:
        print(f"❌ Error building hierarchy: {e}")
        raise e
    
    try:
        page_to_sections = map_pages_to_sections(toc_data)
        print(f"✅ Mapped {len(page_to_sections)} pages to sections")
    except Exception as e:
        print(f"❌ Error mapping pages: {e}")
        raise e
    
    try:
        section_titles = build_section_title_map(toc_data)
        print(f"✅ Built title map for {len(section_titles)} sections")
    except Exception as e:
        print(f"❌ Error building title map: {e}")
        raise e
    
    # Process each page and split content
    split_results = {}
    total_original_chars = 0
    total_split_chars = 0
    
    for page_data in llama_data['pages']:
        page_num = page_data['page']
        
        # Skip pages not assigned to any section
        if page_num not in page_to_sections:
            continue
            
        sections_on_page = page_to_sections[page_num]
        page_text_length = len(page_data.get('text', ''))
        total_original_chars += page_text_length
        
        print(f"Processing page {page_num}: {len(sections_on_page)} sections, {page_text_length:,} chars")
        
        # Split page content among sections
        page_splits = split_page_content(page_data, sections_on_page, section_hierarchy, section_titles)
        
        # Add to results
        for section_id, content_data in page_splits.items():
            if section_id not in split_results:
                split_results[section_id] = {
                    'title': toc_data[section_id]['title'],
                    'section_id': section_id,
                    'pages': {},
                    'total_text': '',
                    'total_chars': 0
                }
            
            split_results[section_id]['pages'][page_num] = content_data
            split_results[section_id]['total_text'] += content_data['text']
            split_results[section_id]['total_chars'] += len(content_data['text'])
            total_split_chars += len(content_data['text'])
    
    # Create final output format matching existing structure
    final_output = create_final_output_format(split_results, toc_data)
    
    # Save results
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    # Report statistics
    duplication_ratio = (total_split_chars / total_original_chars) if total_original_chars > 0 else 0
    
    print(f"\n=== CONTENT SPLITTING RESULTS ===")
    print(f"Original total chars: {total_original_chars:,}")
    print(f"Split total chars: {total_split_chars:,}")
    print(f"Duplication ratio: {duplication_ratio:.1%}")
    print(f"Sections processed: {len(split_results)}")
    print(f"Results saved to: {output_json}")
    
    return {
        'sections_processed': len(split_results),
        'duplication_ratio': duplication_ratio,
        'original_chars': total_original_chars,
        'split_chars': total_split_chars
    }

def build_section_hierarchy(toc_data):
    """Build section hierarchy to understand parent-child relationships"""
    hierarchy = {}
    
    # First, add all main sections
    for section_id, section_info in toc_data.items():
        level = section_id.count('.') + 1
        parent_id = None
        
        if level > 1:
            # Find parent section
            parts = section_id.split('.')
            parent_parts = parts[:-1]
            parent_id = '.'.join(parent_parts)
        
        hierarchy[section_id] = {
            'level': level,
            'parent': parent_id,
            'title': section_info['title'],
            'children': []
        }
    
    # Then, add all nested subsections
    for section_id, section_info in toc_data.items():
        if 'sections' in section_info:
            for subsection_id, subsection_info in section_info['sections'].items():
                level = subsection_id.count('.') + 1
                parent_id = None
                
                if level > 1:
                    # Find parent section
                    parts = subsection_id.split('.')
                    parent_parts = parts[:-1]
                    parent_id = '.'.join(parent_parts)
                
                hierarchy[subsection_id] = {
                    'level': level,
                    'parent': parent_id,
                    'title': subsection_info['title'],
                    'children': []
                }
    
    # Build children lists
    for section_id, section_info in hierarchy.items():
        parent_id = section_info['parent']
        if parent_id and parent_id in hierarchy:
            hierarchy[parent_id]['children'].append(section_id)
    
    return hierarchy

def map_pages_to_sections(toc_data):
    """Map each page to the sections that appear on it"""
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
    
    # Map pages to sections
    for section_id, section_info in all_sections.items():
        # Use 'start' and 'end' fields (not 'start_page' and 'end_page')
        start_page = section_info.get('start')
        end_page = section_info.get('end')
        
        if start_page and end_page:
            for page_num in range(start_page, end_page + 1):
                page_to_sections[page_num].append(section_id)
    
    return page_to_sections

def build_section_title_map(toc_data):
    """Build a map of section IDs to titles for matching"""
    title_map = {}
    
    # Flatten all sections including nested ones
    for section_id, section_info in toc_data.items():
        # Add main section
        title_map[section_id] = section_info['title']
        
        # Add subsections if they exist
        if 'sections' in section_info:
            for subsection_id, subsection_info in section_info['sections'].items():
                title_map[subsection_id] = subsection_info['title']
    
    return title_map

def split_page_content(page_data, sections_on_page, section_hierarchy, section_titles):
    """
    Split a single page's content among the sections that appear on it.
    Uses heading boundaries to determine content ownership.
    """
    page_num = page_data['page']
    items = page_data.get('items', [])
    
    # Sort items by Y position (top to bottom)
    sorted_items = sorted(
        [item for item in items if item.get('bBox')],
        key=lambda x: x.get('bBox', {}).get('y', 0)
    )
    
    # Find heading boundaries for each section
    section_boundaries = find_section_boundaries(sorted_items, sections_on_page, section_titles)
    
    # Assign content to sections based on boundaries
    page_splits = {}
    
    for section_id in sections_on_page:
        try:
            section_level = section_hierarchy[section_id]['level']
            section_content = extract_section_content(
                sorted_items, section_id, section_boundaries, section_level
            )
            
            page_splits[section_id] = {
                'text': section_content['text'],
                'items_count': section_content['items_count'],
                'boundary_method': section_content['method'],
                'y_start': section_content.get('y_start'),
                'y_end': section_content.get('y_end')
            }
        except KeyError as e:
            print(f"❌ KeyError on page {page_num}: section '{section_id}' not found in hierarchy")
            print(f"Available sections on this page: {sections_on_page}")
            print(f"Hierarchy keys: {sorted(section_hierarchy.keys())}")
            raise e
    
    return page_splits

def find_section_boundaries(sorted_items, sections_on_page, section_titles):
    """
    Find Y-coordinate boundaries for each section based on heading positions.
    """
    boundaries = {}
    
    # Find headings that match section titles
    section_headings = []
    
    for item in sorted_items:
        if item.get('type') == 'heading':
            heading_text = item.get('value', '').strip()
            heading_level = item.get('lvl', 1)
            y_pos = item.get('bBox', {}).get('y', 0)
            
            # Try to match this heading to a section
            matched_section = match_heading_to_section(heading_text, sections_on_page, section_titles)
            if matched_section:
                section_headings.append({
                    'section_id': matched_section,
                    'y_pos': y_pos,
                    'level': heading_level,
                    'text': heading_text
                })
    
    # Sort headings by position
    section_headings.sort(key=lambda x: x['y_pos'])
    
    # Create boundaries
    for i, heading in enumerate(section_headings):
        section_id = heading['section_id']
        y_start = heading['y_pos']
        
        # Find end position (next heading of same or higher level)
        y_end = None
        for j in range(i + 1, len(section_headings)):
            next_heading = section_headings[j]
            if next_heading['level'] <= heading['level']:
                y_end = next_heading['y_pos']
                break
        
        boundaries[section_id] = {
            'y_start': y_start,
            'y_end': y_end,  # None means continues to end of page
            'heading_level': heading['level']
        }
    
    return boundaries

def match_heading_to_section(heading_text, sections_on_page, section_titles):
    """
    Match a heading text to one of the sections on the page.
    Uses numbering patterns and title matching.
    """
    heading_clean = clean_text_for_matching(heading_text)
    
    # Try exact numbering pattern match first
    for section_id in sections_on_page:
        # Check if heading starts with section number
        if heading_text.strip().startswith(section_id + '.') or heading_text.strip().startswith(section_id + ' '):
            return section_id
    
    # Try title matching
    for section_id in sections_on_page:
        section_title = section_titles.get(section_id, '')
        title_clean = clean_text_for_matching(section_title)
        
        # Check for partial title match
        if title_clean in heading_clean or heading_clean in title_clean:
            # Additional check: ensure it's a substantial match
            if len(title_clean) > 5 and len(heading_clean) > 5:
                return section_id
    
    # Try to extract section number from heading
    section_pattern = r'^(\d+(?:\.\d+)*)\.'
    match = re.match(section_pattern, heading_text.strip())
    if match:
        potential_section = match.group(1)
        if potential_section in sections_on_page:
            return potential_section
    
    return None

def extract_section_content(sorted_items, section_id, section_boundaries, section_level):
    """
    Extract content for a specific section based on boundaries.
    """
    if section_id in section_boundaries:
        # Use precise boundaries
        boundary = section_boundaries[section_id]
        y_start = boundary['y_start']
        y_end = boundary['y_end']
        method = 'heading_boundary'
    else:
        # Use fallback method - assign based on section level
        y_start = 0
        y_end = None
        method = 'fallback_full_page'
    
    # Collect items within boundaries
    section_items = []
    section_text_parts = []
    
    for item in sorted_items:
        item_y = item.get('bBox', {}).get('y', 0)
        
        # Check if item is within section boundaries
        if y_start is not None and item_y < y_start:
            continue
        if y_end is not None and item_y >= y_end:
            continue
        
        section_items.append(item)
        
        # Extract text based on item type
        if item.get('type') in ['text', 'heading']:
            item_text = item.get('value', '')
            if item_text and item_text.strip():
                section_text_parts.append(item_text.strip())
    
    return {
        'text': '\n\n'.join(section_text_parts),
        'items_count': len(section_items),
        'method': method,
        'y_start': y_start,
        'y_end': y_end
    }

def clean_text_for_matching(text):
    """Clean text for fuzzy matching"""
    return re.sub(r'[^\w\s]', '', text.lower()).strip()

def create_final_output_format(split_results, toc_data):
    """
    Create final output format matching the existing structure.
    """
    final_output = {}
    
    # Build a flattened section info map first
    all_section_info = {}
    
    for section_id, section_info in toc_data.items():
        # Add main section
        all_section_info[section_id] = section_info
        
        # Add subsections if they exist
        if 'sections' in section_info:
            for subsection_id, subsection_info in section_info['sections'].items():
                all_section_info[subsection_id] = subsection_info
    
    for section_id, section_data in split_results.items():
        # Get original TOC data from flattened map
        toc_info = all_section_info.get(section_id, {})
        
        final_output[section_id] = {
            'title': section_data['title'],
            'start_page': toc_info.get('start'),
            'end_page': toc_info.get('end'),
            'text': section_data['total_text'],
            'character_count': section_data['total_chars'],
            'pages_processed': list(section_data['pages'].keys()),
            'splitting_method': 'intelligent_boundary_detection'
        }
    
    return final_output

if __name__ == "__main__":
    corrected_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
    toc_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/toc_output/chapters.json'
    output_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_intelligent.json'
    
    result = split_content_intelligently(corrected_file, toc_file, output_file) 