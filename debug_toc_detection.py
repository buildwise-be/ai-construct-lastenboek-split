#!/usr/bin/env python3
"""
Debug script to analyze TOC detection quality and identify potentially missing sections.
Specifically designed to diagnose issues with VMSW pipeline TOC detection.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_toc_detection(chapters_json_path):
    """
    Analyze the quality of TOC detection for VMSW template matching.
    
    Args:
        chapters_json_path (str): Path to the chapters.json file from TOC detection
    """
    if not os.path.exists(chapters_json_path):
        logger.error(f"Chapters file not found: {chapters_json_path}")
        return
    
    with open(chapters_json_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    
    logger.info("=" * 60)
    logger.info("📋 TOC DETECTION QUALITY ANALYSIS")
    logger.info("=" * 60)
    
    # Overall statistics
    total_chapters = len(chapters)
    total_sections = sum(len(ch.get('sections', {})) for ch in chapters.values())
    total_pages = max(ch.get('end', 0) for ch in chapters.values()) if chapters else 0
    
    logger.info(f"📊 Overall Statistics:")
    logger.info(f"   Total chapters: {total_chapters}")
    logger.info(f"   Total sections: {total_sections}")
    logger.info(f"   Total pages: {total_pages}")
    logger.info(f"   Avg sections per chapter: {total_sections/total_chapters:.1f}")
    logger.info(f"   Avg sections per page: {total_sections/total_pages:.2f}")
    
    # Analyze chapter density
    logger.info(f"\n🔍 Chapter Section Density Analysis:")
    sparse_chapters = []
    dense_chapters = []
    
    for chapter_id, chapter_data in sorted(chapters.items()):
        if not chapter_id.isdigit() or len(chapter_id) != 2:
            continue
            
        sections = chapter_data.get('sections', {})
        section_count = len(sections)
        page_range = chapter_data.get('end', 0) - chapter_data.get('start', 0) + 1
        density = section_count / page_range if page_range > 0 else 0
        
        chapter_info = {
            'id': chapter_id,
            'title': chapter_data.get('title', ''),
            'pages': page_range,
            'sections': section_count,
            'density': density
        }
        
        if page_range > 2 and section_count < 2:  # Sparse: less than 1 section per page
            sparse_chapters.append(chapter_info)
        elif density > 2:  # Dense: more than 2 sections per page
            dense_chapters.append(chapter_info)
    
    # Report sparse chapters (potential missing sections)
    if sparse_chapters:
        logger.warning(f"\n⚠️  SPARSE CHAPTERS (Potentially Missing Sections):")
        for ch in sorted(sparse_chapters, key=lambda x: x['density'])[:10]:
            logger.warning(f"   Chapter {ch['id']}: {ch['title'][:50]}")
            logger.warning(f"      {ch['pages']} pages → {ch['sections']} sections (density: {ch['density']:.2f})")
    
    # Report well-detected chapters
    if dense_chapters:
        logger.info(f"\n✅ WELL-DETECTED CHAPTERS (Good Section Detection):")
        for ch in sorted(dense_chapters, key=lambda x: x['density'], reverse=True)[:5]:
            logger.info(f"   Chapter {ch['id']}: {ch['title'][:50]}")
            logger.info(f"      {ch['pages']} pages → {ch['sections']} sections (density: {ch['density']:.2f})")
    
    # Analyze specific VMSW-relevant chapters
    vmsw_critical_chapters = {
        '11': 'STUT- & ONDERVANGINGSWERKEN (BESCHOEIINGEN)',
        '13': 'SPECIALE FUNDERINGEN (PAALFUNDERING)', 
        '20': 'BOUWMATERIALEN (KALKZANDSTEEN)',
        '27': 'STRUCTUURELEMENTEN STAAL (STAAL)',
        '33': 'BETON/GEWAPEND BETON (HELLINGSBETON)',
        '40': 'DAKLICHTOPENINGEN',
        '51': 'BINNENPLAATAFWERKINGEN',
        '52': 'BINNENDEUREN en -RAMEN',
        '53': 'VAST BINNENMEUBILAIR'
    }
    
    logger.info(f"\n🎯 VMSW-CRITICAL CHAPTERS ANALYSIS:")
    for chapter_id, expected_category in vmsw_critical_chapters.items():
        if chapter_id in chapters:
            ch = chapters[chapter_id]
            sections = ch.get('sections', {})
            page_range = ch.get('end', 0) - ch.get('start', 0) + 1
            
            status = "✅" if len(sections) >= 3 else "⚠️" if len(sections) >= 1 else "❌"
            logger.info(f"   {status} Chapter {chapter_id}: {ch.get('title', '')}")
            logger.info(f"      Expected: {expected_category}")
            logger.info(f"      Detection: {page_range} pages → {len(sections)} sections")
            
            if len(sections) > 0:
                logger.info(f"      Found sections: {list(sections.keys())[:5]}{'...' if len(sections) > 5 else ''}")
        else:
            logger.warning(f"   ❌ Chapter {chapter_id}: NOT DETECTED")
            logger.warning(f"      Expected: {expected_category}")

def analyze_section_numbering_patterns(chapters_json_path):
    """
    Analyze the section numbering patterns to see if we're missing subsection levels.
    """
    if not os.path.exists(chapters_json_path):
        logger.error(f"Chapters file not found: {chapters_json_path}")
        return
    
    with open(chapters_json_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    
    logger.info(f"\n🔢 SECTION NUMBERING PATTERN ANALYSIS:")
    
    # Collect all section IDs
    all_sections = []
    for chapter_data in chapters.values():
        sections = chapter_data.get('sections', {})
        all_sections.extend(sections.keys())
    
    # Analyze numbering depth
    depth_counts = {1: 0, 2: 0, 3: 0, 4: 0}  # XX, XX.YY, XX.YY.ZZ, XX.YY.ZZ.AA
    
    for section_id in all_sections:
        depth = len(section_id.split('.'))
        if depth in depth_counts:
            depth_counts[depth] += 1
    
    logger.info(f"   Section depth distribution:")
    logger.info(f"      Level 1 (XX.YY): {depth_counts[2]} sections")
    logger.info(f"      Level 2 (XX.YY.ZZ): {depth_counts[3]} sections") 
    logger.info(f"      Level 3 (XX.YY.ZZ.AA): {depth_counts[4]} sections")
    
    # Show examples of each depth level
    examples = {1: [], 2: [], 3: [], 4: []}
    for section_id in all_sections:
        depth = len(section_id.split('.'))
        if depth in examples and len(examples[depth]) < 3:
            examples[depth].append(section_id)
    
    logger.info(f"   Examples by depth:")
    for depth, example_list in examples.items():
        if example_list and depth > 1:
            logger.info(f"      Level {depth-1}: {', '.join(example_list)}")
    
    # Check for potential missing subsections
    potential_parents = set()
    all_section_ids = set(all_sections)
    
    for section_id in all_sections:
        parts = section_id.split('.')
        if len(parts) >= 3:  # XX.YY.ZZ or deeper
            parent = '.'.join(parts[:-1])  # XX.YY
            if parent not in all_section_ids:
                potential_parents.add(parent)
    
    if potential_parents:
        logger.warning(f"   ⚠️  Potential missing parent sections: {sorted(list(potential_parents))[:10]}")

def main():
    """
    Main function to run TOC detection analysis.
    """
    if len(sys.argv) < 2:
        print("Usage: python debug_toc_detection.py <path_to_chapters.json>")
        print("   or: python debug_toc_detection.py <path_to_output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Handle both direct file path and directory path
    if os.path.isfile(input_path) and input_path.endswith('.json'):
        chapters_json_path = input_path
    elif os.path.isdir(input_path):
        # Look for the most recent chapters.json file
        potential_paths = []
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file == 'chapters.json':
                    potential_paths.append(os.path.join(root, file))
        
        if not potential_paths:
            logger.error(f"No chapters.json file found in directory: {input_path}")
            sys.exit(1)
        
        # Use the most recently modified one
        chapters_json_path = max(potential_paths, key=os.path.getmtime)
        logger.info(f"Found chapters.json: {chapters_json_path}")
    else:
        logger.error(f"Invalid input path: {input_path}")
        sys.exit(1)
    
    # Run the analysis
    analyze_toc_detection(chapters_json_path)
    analyze_section_numbering_patterns(chapters_json_path)
    
    logger.info(f"\n✅ TOC detection analysis completed!")

if __name__ == "__main__":
    main() 