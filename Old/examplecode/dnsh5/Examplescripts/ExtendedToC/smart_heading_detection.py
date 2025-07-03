#!/usr/bin/env python3
"""
Smart heading level detection that corrects LlamaParse's H1-only output
by analyzing numbering patterns and contextual clues.
"""

import json
import re
from collections import defaultdict

def detect_smart_heading_level(heading_text, context=None):
    """
    Determine the correct heading level based on numbering patterns and context.
    
    Args:
        heading_text (str): The heading text to analyze
        context (dict, optional): Additional context like position, surrounding headings
    
    Returns:
        int: The detected heading level (1-6)
    """
    text = heading_text.strip()
    
    # Skip obvious page headers/footers
    if any(skip_term in text.upper() for skip_term in [
        'LASTENBOEK ARCHITECTUUR',
        'PAGINA',
        'BLADZIJDE'
    ]):
        return None  # Not a content heading
    
    # Pattern 1: Numbered sections
    numbered_level = detect_numbered_level(text)
    if numbered_level:
        return numbered_level
    
    # Pattern 2: Context-based detection for non-numbered headings
    contextual_level = detect_contextual_level(text, context)
    if contextual_level:
        return contextual_level
    
    # Pattern 3: Formatting clues (if available in context)
    formatting_level = detect_formatting_level(text, context)
    if formatting_level:
        return formatting_level
    
    # Default: assume H2 for unclassified headings (safer than H1)
    return 2

def detect_numbered_level(text):
    """Detect heading level based on numbering patterns"""
    
    # Pattern for "1.", "2.", etc. → H1
    if re.match(r'^\d+\.\s+', text):
        return 1
    
    # Pattern for "2.1.", "3.4.", etc. → H2  
    elif re.match(r'^\d+\.\d+\.\s+', text):
        return 2
    
    # Pattern for "2.1.1.", "3.4.2.", etc. → H3
    elif re.match(r'^\d+\.\d+\.\d+\.\s+', text):
        return 3
    
    # Pattern for "2.1.1.1.", etc. → H4
    elif re.match(r'^\d+\.\d+\.\d+\.\d+\.\s+', text):
        return 4
    
    # Pattern for even deeper nesting → H5
    elif re.match(r'^\d+(?:\.\d+){4,}\.\s+', text):
        return 5
    
    return None

def detect_contextual_level(text, context):
    """Detect heading level based on context and content clues"""
    if not context:
        return None
    
    # Get surrounding headings for context
    prev_headings = context.get('previous_headings', [])
    page_position = context.get('y_position', 0)
    page_height = context.get('page_height', 1000)
    
    # Check for common subsection patterns
    subsection_patterns = [
        r'^(Algemeen|General)$',
        r'^(Omschrijving|Description)$', 
        r'^(Toepasselijke|Applicable)',
        r'^(Referentienormen|Reference)',
        r'.*plan.*:$',
        r'.*bord.*:$',
        r'.*voorzieningen.*',
    ]
    
    for pattern in subsection_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            # These are typically subsections → H3
            return 3
    
    # Check for main topic indicators
    main_topic_patterns = [
        r'^[A-Z\s]{3,}$',  # ALL CAPS titles
        r'.*WERKEN.*',
        r'.*MATERIALEN.*',
        r'.*STABILITEIT.*',
    ]
    
    for pattern in main_topic_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            # These are typically main sections → H2
            return 2
    
    # Position-based heuristics
    if page_position < page_height * 0.2:  # Top 20% of page
        return 2  # Likely a section header
    elif page_position > page_height * 0.8:  # Bottom 20% of page  
        return 4  # Likely a small subsection
    
    return None

def detect_formatting_level(text, context):
    """Detect heading level based on formatting clues from context"""
    if not context or 'bbox' not in context:
        return None
    
    bbox = context['bbox']
    text_length = len(text)
    
    # Very short text (< 5 chars) is likely a label → H4
    if text_length < 5:
        return 4
    
    # Very long text (> 50 chars) is likely a detailed subsection → H3
    elif text_length > 50:
        return 3
    
    # Medium length could be H2
    elif 10 < text_length < 30:
        return 2
    
    return None

def apply_smart_heading_detection(llama_parse_json, output_json):
    """
    Apply smart heading detection to LlamaParse output and save corrected version.
    """
    with open(llama_parse_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== APPLYING SMART HEADING DETECTION ===\n")
    
    corrections_made = 0
    level_changes = defaultdict(int)
    
    for page in data['pages']:
        page_num = page['page']
        page_height = 800  # Approximate page height
        
        # Collect headings on this page for context
        page_headings = []
        for item in page.get('items', []):
            if item.get('type') == 'heading':
                page_headings.append(item)
        
        # Apply smart detection to each heading
        for i, item in enumerate(page.get('items', [])):
            if item.get('type') == 'heading':
                original_level = item.get('lvl', 1)
                heading_text = item.get('value', '')
                
                # Build context
                context = {
                    'bbox': item.get('bBox', {}),
                    'y_position': item.get('bBox', {}).get('y', 0),
                    'page_height': page_height,
                    'previous_headings': page_headings[:i],  # Headings before this one
                    'page_number': page_num
                }
                
                # Detect correct level
                smart_level = detect_smart_heading_level(heading_text, context)
                
                if smart_level and smart_level != original_level:
                    item['lvl'] = smart_level
                    item['original_lvl'] = original_level  # Keep track of original
                    corrections_made += 1
                    level_changes[f"H{original_level}→H{smart_level}"] += 1
                    
                    if corrections_made <= 10:  # Show first 10 corrections
                        print(f"Page {page_num}: '{heading_text[:40]}...' H{original_level}→H{smart_level}")
    
    # Save corrected data
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== CORRECTION SUMMARY ===")
    print(f"Total corrections made: {corrections_made}")
    print(f"Level changes:")
    for change, count in level_changes.items():
        print(f"  {change}: {count}")
    
    print(f"\nCorrected data saved to: {output_json}")
    
    return {
        'corrections_made': corrections_made,
        'level_changes': dict(level_changes),
        'output_file': output_json
    }

def validate_heading_hierarchy(llama_parse_json):
    """Validate the heading hierarchy makes sense"""
    with open(llama_parse_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== HEADING HIERARCHY VALIDATION ===\n")
    
    level_counts = defaultdict(int)
    hierarchy_issues = []
    
    for page in data['pages']:
        page_num = page['page']
        page_headings = []
        
        for item in page.get('items', []):
            if item.get('type') == 'heading':
                level = item.get('lvl', 1)
                text = item.get('value', '')
                level_counts[level] += 1
                page_headings.append((level, text, page_num))
        
        # Check for hierarchy jumps (e.g., H1 directly to H4)
        for i in range(1, len(page_headings)):
            prev_level, prev_text, _ = page_headings[i-1]
            curr_level, curr_text, _ = page_headings[i]
            
            if curr_level > prev_level + 1:  # Jumped more than 1 level
                hierarchy_issues.append({
                    'page': page_num,
                    'issue': f"Jump from H{prev_level} to H{curr_level}",
                    'from': prev_text[:30],
                    'to': curr_text[:30]
                })
    
    print("Level distribution after correction:")
    for level in sorted(level_counts.keys()):
        print(f"  H{level}: {level_counts[level]} headings")
    
    if hierarchy_issues:
        print(f"\n⚠️  Potential hierarchy issues found:")
        for issue in hierarchy_issues[:5]:  # Show first 5 issues
            print(f"  Page {issue['page']}: {issue['issue']}")
            print(f"    From: '{issue['from']}...'")
            print(f"    To: '{issue['to']}...'")
    else:
        print("\n✅ No obvious hierarchy issues detected")

if __name__ == "__main__":
    input_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed.json'
    output_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed_corrected.json'
    
    result = apply_smart_heading_detection(input_file, output_file)
    validate_heading_hierarchy(output_file) 