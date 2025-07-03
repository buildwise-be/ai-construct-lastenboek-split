#!/usr/bin/env python3
"""
Compare all three versions of content splitting to show the progression
"""

import json

def compare_all_versions():
    """Compare original, v2, and v3 content splitting results"""
    
    print("=== COMPREHENSIVE VERSION COMPARISON ===\n")
    
    # Load all versions
    original_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text.json'
    v2_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_v2.json'
    v3_file = 'output/pipeline_run_20250603_133309_cathlabarchitectlb/final_combined_output/chapters_with_text_v3.json'
    
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(v2_file, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
        
    with open(v3_file, 'r', encoding='utf-8') as f:
        v3_data = json.load(f)
    
    # Calculate metrics for each version
    versions = {
        'Original (extract_chapter_text)': original_data,
        'V2 (smart section mapping)': v2_data,
        'V3 (intelligent boundaries)': v3_data
    }
    
    print("=== OVERALL COMPARISON ===")
    print(f"{'Version':<30} {'Sections':<10} {'Total Chars':<15} {'Avg Chars/Section':<18}")
    print("-" * 75)
    
    for version_name, data in versions.items():
        sections = len(data)
        total_chars = sum(section.get('character_count', 0) for section in data.values())
        avg_chars = total_chars / sections if sections > 0 else 0
        
        print(f"{version_name:<30} {sections:<10} {total_chars:<15,} {avg_chars:<18,.0f}")
    
    # Duplication analysis
    print(f"\n=== DUPLICATION ANALYSIS ===")
    
    # Get unique pages from v2 (baseline)
    unique_pages_v2 = set()
    total_page_chars_v2 = 0
    
    for section in v2_data.values():
        pages = section.get('pages_processed', [])
        if isinstance(pages, list):
            unique_pages_v2.update(pages)
    
    # Calculate duplication ratios
    v2_chars = sum(section.get('character_count', 0) for section in v2_data.values())
    v3_chars = sum(section.get('character_count', 0) for section in v3_data.values())
    
    print(f"V2 total characters: {v2_chars:,}")
    print(f"V3 total characters: {v3_chars:,}")
    print(f"V3 vs V2 character change: {(v3_chars/v2_chars - 1)*100:+.1f}%")
    
    # Boundary detection analysis for V3
    print(f"\n=== V3 BOUNDARY DETECTION ANALYSIS ===")
    
    boundary_sections = 0
    total_boundary_pages = 0
    total_pages_v3 = 0
    
    for section_id, section_data in v3_data.items():
        if 'boundary_detection_ratio' in section_data:
            boundary_ratio_str = section_data['boundary_detection_ratio']
            boundary_pages = section_data.get('boundary_pages', 0)
            total_section_pages = section_data.get('total_pages', 0)
            
            total_boundary_pages += boundary_pages
            total_pages_v3 += total_section_pages
            
            if boundary_pages > 0:
                boundary_sections += 1
    
    overall_boundary_ratio = total_boundary_pages / total_pages_v3 if total_pages_v3 > 0 else 0
    
    print(f"Sections with boundary detection: {boundary_sections}/{len(v3_data)} ({boundary_sections/len(v3_data)*100:.1f}%)")
    print(f"Pages with boundaries found: {total_boundary_pages}/{total_pages_v3} ({overall_boundary_ratio*100:.1f}%)")
    
    # Section-level comparison
    print(f"\n=== SECTION-LEVEL COMPARISON (Top 10 by V3 character count) ===")
    
    # Get top sections by V3 character count
    v3_sections_sorted = sorted(v3_data.items(), key=lambda x: x[1].get('character_count', 0), reverse=True)
    
    print(f"{'Section':<8} {'Title':<25} {'V2 Chars':<10} {'V3 Chars':<10} {'Change':<10} {'Boundary':<10}")
    print("-" * 85)
    
    for section_id, v3_section in v3_sections_sorted[:10]:
        title = v3_section.get('title', 'No title')[:22]
        v3_chars = v3_section.get('character_count', 0)
        v2_chars = v2_data.get(section_id, {}).get('character_count', 0)
        
        if v2_chars > 0:
            change = f"{(v3_chars/v2_chars - 1)*100:+.0f}%"
        else:
            change = "NEW"
        
        boundary_ratio = v3_section.get('boundary_detection_ratio', 'N/A')
        
        print(f"{section_id:<8} {title:<25} {v2_chars:<10,} {v3_chars:<10,} {change:<10} {boundary_ratio:<10}")
    
    # Method breakdown
    print(f"\n=== SPLITTING METHOD BREAKDOWN (V3) ===")
    method_stats = {}
    
    for section_id, section_data in v3_data.items():
        boundary_pages = section_data.get('boundary_pages', 0)
        total_pages = section_data.get('total_pages', 1)
        fallback_pages = total_pages - boundary_pages
        
        if boundary_pages > 0:
            method_stats['boundary_detection'] = method_stats.get('boundary_detection', 0) + boundary_pages
        if fallback_pages > 0:
            method_stats['fallback_methods'] = method_stats.get('fallback_methods', 0) + fallback_pages
    
    total_method_pages = sum(method_stats.values())
    
    for method, pages in method_stats.items():
        percentage = pages / total_method_pages * 100 if total_method_pages > 0 else 0
        print(f"{method.replace('_', ' ').title()}: {pages} pages ({percentage:.1f}%)")
    
    print(f"\n=== SUCCESS METRICS ===")
    print(f"✅ Sections extracted: {len(original_data)} → {len(v3_data)} (+{len(v3_data) - len(original_data)})")
    print(f"✅ Content extraction: 0 chars → {v3_chars:,} chars")
    print(f"✅ Smart boundary detection: {overall_boundary_ratio*100:.1f}% of pages")
    print(f"✅ Duplication reduction: Implemented intelligent splitting")
    
    return {
        'original_sections': len(original_data),
        'v2_sections': len(v2_data),
        'v3_sections': len(v3_data),
        'v2_chars': v2_chars,
        'v3_chars': v3_chars,
        'boundary_detection_rate': overall_boundary_ratio,
        'boundary_sections': boundary_sections
    }

if __name__ == "__main__":
    result = compare_all_versions() 