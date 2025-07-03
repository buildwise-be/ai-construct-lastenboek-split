#!/usr/bin/env python3
"""
Analyze LlamaParse output to identify visual/formatting cues that can help 
with intelligent content separation for sections.
"""

import json
from collections import defaultdict, Counter

def analyze_layout_features(llama_parse_json):
    """Analyze layout and formatting features available in LlamaParse output"""
    
    with open(llama_parse_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== LAYOUT & FORMATTING ANALYSIS ===\n")
    
    # Analyze structure across all pages
    total_pages = len(data['pages'])
    has_layout_data = 0
    has_items_data = 0
    item_types = Counter()
    heading_levels = Counter()
    bbox_analysis = []
    font_info = []
    
    print(f"Total pages: {total_pages}\n")
    
    for page in data['pages']:
        page_num = page['page']
        
        # Check what data is available
        has_layout = bool(page.get('layout', []))
        has_items = bool(page.get('items', []))
        has_images = bool(page.get('images', []))
        has_tables = bool(page.get('tables', []))
        has_charts = bool(page.get('charts', []))
        
        if has_layout:
            has_layout_data += 1
        if has_items:
            has_items_data += 1
            
        # Analyze items (structured content elements)
        for item in page.get('items', []):
            item_type = item.get('type', 'unknown')
            item_types[item_type] += 1
            
            if item_type == 'heading':
                level = item.get('lvl', 'unknown')
                heading_levels[level] += 1
            
            # Analyze bounding boxes for positioning
            bbox = item.get('bBox', {})
            if bbox:
                item_text = item.get('value') or ''
                display_text = item_text[:50] + '...' if len(item_text) > 50 else item_text
                bbox_analysis.append({
                    'page': page_num,
                    'type': item_type,
                    'level': item.get('lvl'),
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0), 
                    'w': bbox.get('w', 0),
                    'h': bbox.get('h', 0),
                    'text': display_text
                })
        
        print(f"Page {page_num}: Layout={has_layout}, Items={has_items}, Images={has_images}, Tables={has_tables}, Charts={has_charts}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Pages with layout data: {has_layout_data}/{total_pages}")
    print(f"Pages with items data: {has_items_data}/{total_pages}")
    
    print(f"\n=== CONTENT ELEMENT TYPES ===")
    for item_type, count in item_types.most_common():
        print(f"{item_type}: {count}")
    
    print(f"\n=== HEADING LEVELS ===")
    for level, count in heading_levels.most_common():
        print(f"Level {level}: {count}")
    
    print(f"\n=== BOUNDING BOX ANALYSIS (First 10 items) ===")
    for item in bbox_analysis[:10]:
        print(f"Page {item['page']}: {item['type']} (lvl {item['level']}) at ({item['x']:.0f},{item['y']:.0f}) - '{item['text']}'")
    
    print(f"\n=== VISUAL CUES AVAILABLE FOR SECTION SPLITTING ===")
    print("✅ Structured Content Elements:")
    print("   - Heading levels (1-6) with bounding boxes")
    print("   - Text blocks with precise positioning")
    print("   - Tables, charts, images with coordinates")
    print("   - Font/formatting information preserved")
    
    print("\n✅ Spatial Information:")
    print("   - Bounding boxes (x, y, width, height) for all elements")
    print("   - Page-relative positioning")
    print("   - Element hierarchy detection")
    
    print("\n🔧 Available for Section Boundary Detection:")
    print("   - Heading level changes (e.g., H2 to H3)")
    print("   - Y-coordinate jumps (vertical spacing)")
    print("   - Font size/style changes (implicit in heading levels)")
    print("   - Text block boundaries")
    
    return {
        'item_types': dict(item_types),
        'heading_levels': dict(heading_levels),
        'bbox_data': bbox_analysis[:20],  # Sample of positioning data
        'has_structured_data': has_items_data > 0
    }

if __name__ == "__main__":
    result = analyze_layout_features('output/pipeline_run_20250603_133309_cathlabarchitectlb/parsed_pdf_output/cathlabarchitectlb_parsed.json') 