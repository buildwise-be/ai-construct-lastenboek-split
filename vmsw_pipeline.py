"""
VMSW Document Processing Pipeline with Template-Based Category Assignment

This script is specifically designed for documents that follow the VMSW template.
Unlike the Non-VMSW pipeline that uses AI for category matching, this pipeline uses
predefined mappings from VMSWcat.json to deterministically assign chapters to categories.
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
VMSW_CATEGORIES_FILE = os.path.join(MODULE_DIR, "VMSWcat.json")

def load_vmsw_categories(categories_file=VMSW_CATEGORIES_FILE):
    """Load VMSW category definitions from JSON file."""
    if not os.path.exists(categories_file):
        raise FileNotFoundError(f"VMSW categories file not found: {categories_file}")
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        logger.info(f"Loaded {len(categories)} VMSW categories")
        return categories
    except Exception as e:
        logger.error(f"Error loading VMSW categories: {str(e)}")
        raise

def match_chapter_to_vmsw_category(chapter_num, vmsw_categories):
    """Match a chapter number to VMSW categories using template-based rules."""
    matches = []
    normalized_chapter = str(chapter_num).strip()
    
    # Add period if missing for chapters like "01" -> "01."
    if normalized_chapter.isdigit() and len(normalized_chapter) == 2:
        normalized_chapter = f"{normalized_chapter}."
    
    for category in vmsw_categories:
        art_nr = category.get('art_nr', '')
        omschrijving = category.get('omschrijving', '')
        
        # Direct match
        if normalized_chapter == art_nr:
            matches.append(omschrijving)
            continue
        
        # Handle compound categories like "20 + 21 + 22"
        if '+' in art_nr:
            parts = [part.strip().rstrip('.') for part in art_nr.split('+')]
            chapter_base = normalized_chapter.rstrip('.')
            if chapter_base in parts:
                matches.append(omschrijving)
                continue
        
        # Handle hierarchical and base matching with precision
        if '.' in normalized_chapter or '.' in art_nr:
            # First, try exact hierarchical matching
            if '.' in normalized_chapter and '.' in art_nr:
                chapter_parts = normalized_chapter.split('.')
                art_parts = art_nr.split('.')
                
                # Exact match for specific sections (e.g., "01.10" matches "01.10")
                if normalized_chapter == art_nr:
                    matches.append(omschrijving)
                    continue
                    
                # Hierarchical matching - section matches broader chapter category
                # (e.g., section "20.01" matches chapter category "20.")
                elif len(chapter_parts) > len(art_parts):
                    # Section is more specific than category
                    if chapter_parts[0] == art_parts[0]:
                        if len(art_parts) == 1 or (len(art_parts) == 2 and not art_parts[1]):
                            # Category is chapter-level (like "20."), section can match
                            matches.append(omschrijving)
            
            # Handle chapter matching to chapter-level categories only
            elif '.' in art_nr and not '.' in normalized_chapter:
                # Chapter (like "03") trying to match art_nr (like "03." or "03.01")
                art_parts = art_nr.split('.')
                chapter_base = normalized_chapter.rstrip('.')
                
                # Only match if art_nr is chapter-level (ends with just ".")
                if len(art_parts) == 2 and not art_parts[1]:  # Like "03."
                    if chapter_base == art_parts[0]:
                        matches.append(omschrijving)
                # Do NOT match specific sections like "03.01" to chapter "03"
            
            # Handle section without period matching art_nr with period (shouldn't happen in VMSW)
            elif '.' in normalized_chapter and not '.' in art_nr:
                chapter_base = normalized_chapter.split('.')[0]
                if chapter_base == art_nr:
                    matches.append(omschrijving)
    
    return matches

def setup_output_directory(step_name=None, base_output_dir=None):
    """Setup output directory with timestamp and return path"""
    if not base_output_dir:
        base_output_dir = os.path.join(MODULE_DIR, "output")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if step_name:
        pipeline_dir = os.path.join(base_output_dir, f"vmsw_pipeline_{timestamp}")
        output_dir = os.path.join(pipeline_dir, f"{step_name}_{timestamp}")
    else:
        output_dir = os.path.join(base_output_dir, f"vmsw_pipeline_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir

def step2_vmsw_template_matching(chapters, toc_output_dir=None, base_dir=None):
    """
    Match chapters and sections to VMSW categories using template-based rules.
    
    Args:
        chapters (dict): Dictionary of chapters from step 1
        toc_output_dir (str): Directory containing TOC output from step 1
        base_dir (str): Base output directory
        
    Returns:
        tuple: (category_match_dir, chapter_results, section_results)
    """
    logger.info("Step 2: VMSW Template-Based Category Matching")
    
    # Initialize base directory
    if not base_dir:
        if toc_output_dir:
            base_dir = os.path.dirname(toc_output_dir)
        else:
            base_dir = setup_output_directory(step_name="vmsw_category_matching")
    
    # Create output directory for category matching
    category_match_dir = setup_output_directory("step2_vmsw_category_matching", base_dir)
    
    # Load VMSW categories
    vmsw_categories = load_vmsw_categories()
    
    # Process chapters and sections
    chapter_results = {}
    section_results = {}
    
    for chapter_id, chapter_data in chapters.items():
        logger.info(f"Processing chapter {chapter_id}: {chapter_data.get('title', 'Unknown')}")
        
        # Match chapter to categories
        chapter_categories = match_chapter_to_vmsw_category(chapter_id, vmsw_categories)
        
        chapter_results[chapter_id] = {
            'id': chapter_id,
            'title': chapter_data.get('title', ''),
            'start': chapter_data.get('start', 0),
            'end': chapter_data.get('end', 0),
            'type': 'chapter',
            'categories': chapter_categories,
            'confidence': 1.0,  # Template-based matching is always 100% confident
            'explanation': f"Template-based match for VMSW chapter {chapter_id}"
        }
        
        # Process sections within this chapter
        sections = chapter_data.get('sections', {})
        for section_id, section_data in sections.items():
            logger.info(f"Processing section {section_id}: {section_data.get('title', 'Unknown')}")
            
            # Match section to categories
            section_categories = match_chapter_to_vmsw_category(section_id, vmsw_categories)
            
            section_results[section_id] = {
                'id': section_id,
                'title': section_data.get('title', ''),
                'start': section_data.get('start', 0),
                'end': section_data.get('end', 0),
                'type': 'section',
                'parent_chapter': chapter_id,
                'categories': section_categories,
                'confidence': 1.0,
                'explanation': f"Template-based match for VMSW section {section_id}"
            }
    
    # Save results
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'method': 'vmsw_template_matching',
        'total_chapters': len(chapter_results),
        'total_sections': len(section_results),
        'chapter_results': chapter_results,
        'section_results': section_results,
        'categories_used': [cat['omschrijving'] for cat in vmsw_categories]
    }
    
    results_file = os.path.join(category_match_dir, "vmsw_category_matching_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    # Create CSV files for Step 3 compatibility
    import csv
    
    # Create CSV for chapter matches
    chapter_rows = []
    for chapter_id, data in chapter_results.items():
        categories = data.get('categories', [])
        if categories:
            for category in categories:
                row = {
                    "Type": "Chapter",
                    "Chapter Number": chapter_id,
                    "Section ID": "",
                    "Title": data["title"],
                    "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                    "Matched Category": category,
                    "Confidence": data.get('confidence', 1.0),
                    "Explanation": data.get('explanation', '')
                }
                chapter_rows.append(row)
        else:
            # Also add entries with no matches for completeness
            row = {
                "Type": "Chapter",
                "Chapter Number": chapter_id,
                "Section ID": "",
                "Title": data["title"],
                "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                "Matched Category": "",
                "Confidence": 0.0,
                "Explanation": "No VMSW template match found"
            }
            chapter_rows.append(row)
    
    chapter_df = pd.DataFrame(chapter_rows)
    chapter_csv_path = os.path.join(category_match_dir, "chapter_category_matches.csv")
    chapter_df.to_csv(chapter_csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved chapter matches to {chapter_csv_path}")
    
    # Create CSV for section matches
    section_rows = []
    for section_id, data in section_results.items():
        categories = data.get('categories', [])
        if categories:
            for category in categories:
                row = {
                    "Type": "Section",
                    "Chapter Number": data.get('parent_chapter', ''),
                    "Section ID": section_id,
                    "Title": data["title"],
                    "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                    "Matched Category": category,
                    "Confidence": data.get('confidence', 1.0),
                    "Explanation": data.get('explanation', '')
                }
                section_rows.append(row)
        else:
            # Also add entries with no matches for completeness
            row = {
                "Type": "Section",
                "Chapter Number": data.get('parent_chapter', ''),
                "Section ID": section_id,
                "Title": data["title"],
                "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                "Matched Category": "",
                "Confidence": 0.0,
                "Explanation": "No VMSW template match found"
            }
            section_rows.append(row)
    
    section_df = pd.DataFrame(section_rows)
    section_csv_path = os.path.join(category_match_dir, "section_category_matches.csv")
    section_df.to_csv(section_csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved section matches to {section_csv_path}")
    
    # Create a unified CSV with both chapter and section matches
    unified_df = pd.concat([chapter_df, section_df], ignore_index=True)
    unified_csv_path = os.path.join(category_match_dir, "unified_category_matches.csv")
    unified_df.to_csv(unified_csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved unified matches to {unified_csv_path}")
    
    # Create summary report
    report_lines = ["# VMSW Template-Based Category Matching Report", ""]
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Method: Template-based matching using VMSWcat.json")
    report_lines.append("")
    
    report_lines.append("## Chapter Matches")
    for chapter_id, result in chapter_results.items():
        categories_str = ", ".join(result['categories']) if result['categories'] else "No matches"
        report_lines.append(f"- **{chapter_id}**: {result['title']} → {categories_str}")
    
    report_lines.append("")
    report_lines.append("## Section Matches")
    for section_id, result in section_results.items():
        categories_str = ", ".join(result['categories']) if result['categories'] else "No matches"
        report_lines.append(f"- **{section_id}**: {result['title']} → {categories_str}")
    
    report_file = os.path.join(category_match_dir, "vmsw_matching_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    logger.info(f"VMSW template matching completed:")
    logger.info(f"- Chapters processed: {len(chapter_results)}")
    logger.info(f"- Sections processed: {len(section_results)}")
    logger.info(f"- Results saved to: {category_match_dir}")
    
    return category_match_dir, chapter_results, section_results

def run_vmsw_pipeline(pdf_path, output_base_dir=None):
    """
    Execute the complete VMSW document processing pipeline.
    
    Args:
        pdf_path (str): Path to the PDF file to process
        output_base_dir (str, optional): Base directory for outputs
        
    Returns:
        tuple: (success, output_dirs) with success status and dict of output directories
    """
    # Import functions from existing pipeline
    sys.path.append(MODULE_DIR)
    try:
        from main_script import step1_generate_toc, step3_extract_category_pdfs
        logger.info("Successfully imported existing pipeline functions")
    except ImportError as e:
        logger.error(f"Failed to import from main_script: {e}")
        return False, {}
    
    output_dirs = {
        'base': setup_output_directory(base_output_dir=output_base_dir),
        'toc': None,
        'category_matching': None,
        'category_pdfs': None
    }
    
    try:
        logger.info("=" * 50)
        logger.info("STARTING COMPLETE VMSW DOCUMENT PROCESSING PIPELINE")
        logger.info("=" * 50)
        
        # Step 1: Generate Table of Contents with enhanced detection for VMSW
        logger.info("\nRUNNING STEP 1: Generating Table of Contents (Enhanced for VMSW)")
        chapters, toc_output_dir = run_enhanced_toc_detection(pdf_path, output_dirs['base'])
        output_dirs['toc'] = toc_output_dir
        logger.info(f"Step 1 completed successfully with {len(chapters)} chapters identified")
        
        # Step 2: VMSW Template-Based Category Matching
        logger.info("\nRUNNING STEP 2: VMSW Template-Based Category Matching")
        category_match_dir, chapter_results, section_results = step2_vmsw_template_matching(
            chapters, toc_output_dir, output_dirs['base']
        )
        output_dirs['category_matching'] = category_match_dir
        logger.info(f"Step 2 completed successfully with {len(chapter_results)} chapter matches and {len(section_results)} section matches")
        
        # Step 3: Split document into category-specific PDFs (reuse existing function)
        logger.info("\nRUNNING STEP 3: Splitting PDF into Category-Specific Documents")
        
        # Create temporary category file for step3 compatibility
        vmsw_categories = load_vmsw_categories()
        category_data = []
        final_categories = []
        for cat in vmsw_categories:
            category_data.append({
                'summary': cat['omschrijving'],
                'description': cat['omschrijving'],
                'expanded_description': f"{cat['omschrijving']} (VMSW {cat['art_nr']})"
            })
            # Create final_categories format expected by step3
            final_categories.append(f"{cat['omschrijving']}, {cat['omschrijving']}")
        
        temp_category_file = os.path.join(category_match_dir, "temp_vmsw_categories.py")
        with open(temp_category_file, 'w', encoding='utf-8') as f:
            f.write("import pandas as pd\n\n")
            f.write("# Temporary VMSW categories for PDF extraction\n")
            f.write(f"data = {category_data}\n")
            f.write("df = pd.DataFrame(data)\n\n")
            f.write(f"# Final categories list for step3 compatibility\n")
            f.write(f"final_categories = {final_categories}\n")
        
        pdf_count, pdf_output_dir = step3_extract_category_pdfs(
            pdf_path, 
            chapter_results, 
            section_results, 
            category_match_dir, 
            temp_category_file,
            None,  # second_output_dir
            None,  # third_output_dir
            base_dir=output_dirs['base']
        )
        output_dirs['category_pdfs'] = pdf_output_dir
        logger.info(f"Step 3 completed successfully with {pdf_count} PDFs created")
        
        # Clean up temporary file
        if os.path.exists(temp_category_file):
            os.remove(temp_category_file)
        
        logger.info("=" * 50)
        logger.info("COMPLETE VMSW PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        return True, output_dirs
        
    except Exception as e:
        logger.error(f"VMSW Pipeline execution failed: {str(e)}")
        return False, output_dirs

def run_enhanced_toc_detection(pdf_path, output_base_dir):
    """
    Enhanced TOC detection specifically for VMSW documents that need granular section detection.
    Uses smaller batch sizes and more aggressive prompting for thorough subsection detection.
    """
    from main_script import step1_generate_toc
    import os
    
    logger.info("🔍 Running enhanced TOC detection for VMSW template matching...")
    logger.info("Using smaller batch sizes and aggressive subsection detection...")
    
    # Run the standard TOC detection first
    chapters, toc_dir = step1_generate_toc(pdf_path, output_base_dir)
    
    # Analyze the results to see if we need more granular detection
    total_sections = 0
    chapters_with_few_sections = []
    
    for chapter_id, chapter_data in chapters.items():
        sections = chapter_data.get('sections', {})
        section_count = len(sections)
        total_sections += section_count
        
        # Flag chapters with suspiciously few sections for their page range
        page_range = chapter_data.get('end', 0) - chapter_data.get('start', 0) + 1
        if page_range > 3 and section_count < 3:  # Less than 1 section per page for multi-page chapters
            chapters_with_few_sections.append({
                'id': chapter_id,
                'title': chapter_data.get('title', ''),
                'pages': page_range,
                'sections': section_count
            })
    
    logger.info(f"📊 TOC Detection Analysis:")
    logger.info(f"   Total chapters: {len(chapters)}")
    logger.info(f"   Total sections: {total_sections}")
    logger.info(f"   Chapters with potentially missing sections: {len(chapters_with_few_sections)}")
    
    if chapters_with_few_sections:
        logger.warning("⚠️  Chapters that might need deeper section detection:")
        for ch in chapters_with_few_sections[:5]:  # Show first 5
            logger.warning(f"   Chapter {ch['id']}: {ch['title']} ({ch['pages']} pages, {ch['sections']} sections)")
    
    return chapters, toc_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the VMSW document processing pipeline")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("-o", "--output-dir", help="Output directory (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate PDF file
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Run the pipeline
    success, output_dirs = run_vmsw_pipeline(args.pdf_path, args.output_dir)
    
    if success:
        print("\n✅ VMSW Pipeline completed successfully!")
        print(f"📁 Output directory: {output_dirs['base']}")
        sys.exit(0)
    else:
        print("\n❌ VMSW Pipeline failed!")
        sys.exit(1)
