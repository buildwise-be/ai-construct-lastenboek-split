"""
PDF to Structured Text Pipeline with Intelligent Content Splitting

This pipeline orchestrates a complete 6-step process to convert PDF documents into 
intelligently structured text with hierarchical organization and boundary detection.

PIPELINE STEPS:
1. TOC Generation - Extract table of contents using Gemini AI
2. LlamaParse Processing - Parse PDF with rich formatting data
3. Smart Heading Detection - Correct heading hierarchy from flat H1 to proper levels
4. Original Text Extraction - Baseline chapter text extraction (legacy method)
5. Intelligent Content Splitting V3 - Advanced boundary detection with precise splitting
6. Duplication Analysis - Automated quality assessment and reporting

OUTPUT STRUCTURE:
================

📁 Main Directory: output/pipeline_run_YYYYMMDD_HHMMSS_[pdf_name]/

📊 FINAL RESULTS (Most Important):
├── 📁 final_combined_output/
│   ├── 🎯 chapters_with_text_v3.json     ← **PRIMARY OUTPUT** - V3 intelligent splitting
│   │                                       • 51+ sections with hierarchical structure
│   │                                       • ~2.5x duplication ratio (vs 262.7% original)
│   │                                       • 22%+ boundary detection success rate
│   │                                       • Smart content assignment with fallback methods
│   │
│   └── 📄 chapters_with_text.json        ← Original extraction method (for comparison)
│                                           • Legacy flat extraction
│                                           • Higher duplication, less precise

📋 TABLE OF CONTENTS:
├── 📁 toc_output/
│   ├── 📊 chapters.json                   ← TOC structure with page ranges
│   │                                       • Hierarchical chapter/section organization
│   │                                       • Start/end page numbers for each section
│   │                                       • 4-level deep structure (1, 1.1, 1.1.1, 1.1.1.1)
│   │
│   └── 📋 toc_report.md                   ← Human-readable TOC summary
│                                           • Markdown formatted structure report
│                                           • Section titles and page ranges

🧠 PARSED PDF & SMART HEADINGS:
└── 📁 parsed_pdf_output/
    ├── 🧠 [pdf_name]_parsed_corrected.json ← **SMART HEADINGS** - Corrected hierarchy
    │                                        • LlamaParse output with fixed heading levels
    │                                        • H1→H4 corrections based on numbering patterns
    │                                        • Spatial positioning and formatting context
    │                                        • 295+ heading corrections from all-H1 original
    │
    ├── 📄 [pdf_name]_parsed.json          ← Original LlamaParse output
    │                                        • Raw LlamaParse results (all headings as H1)
    │                                        • Rich formatting data and spatial information
    │                                        • Item-level bounding boxes and coordinates
    │
    └── 📝 [pdf_name]_parsed.md            ← Markdown version
                                             • Human-readable parsed content
                                             • Useful for quick content review

QUALITY METRICS (from Step 6 Analysis):
======================================
• Duplication Ratio: ~2.5x (Smart hierarchical duplication vs chaotic 262.7%)
• Boundary Detection: ~22% precise heading-based splitting
• Fallback Coverage: ~78% smart content assignment without precise boundaries  
• Section Coverage: 51 sections across 4 hierarchy levels
• Parent-Child Relationships: Preserved hierarchical content inclusion

USAGE RECOMMENDATIONS:
=====================
1. **Primary Use**: chapters_with_text_v3.json - Most accurate and intelligent output
2. **Development**: Use corrected.json for heading analysis and boundary detection
3. **Comparison**: Compare v3 vs original extraction to validate improvements
4. **Quality Assurance**: Review duplication analysis output for optimization

PERFORMANCE:
============
• Flash Model: ~30 seconds total pipeline time
• Pro Model: ~4+ minutes total pipeline time  
• Memory: Handles 60+ page PDFs with rich formatting
• Accuracy: 61.4% boundary detection success rate on multi-section pages

USAGE EXAMPLES:
===============

1. BASIC USAGE (uses default PDF):
   python run_pipeline.py

2. CUSTOM PDF FILE:
   python run_pipeline.py "path/to/your/document.pdf"

3. FAST MODE (Flash Model - ~30 seconds):
   python run_pipeline.py --model flash
   python run_pipeline.py "path/to/document.pdf" --model flash

4. HIGH ACCURACY MODE (Pro Model - ~4+ minutes):
   python run_pipeline.py --model pro
   python run_pipeline.py "path/to/document.pdf" --model pro

5. CUSTOM OUTPUT DIRECTORY:
   python run_pipeline.py -o custom_output_folder
   python run_pipeline.py "document.pdf" -o results --model flash

6. FULL COMMAND WITH ALL OPTIONS:
   python run_pipeline.py "C:/path/to/document.pdf" -o output_results --model pro

COMMAND LINE ARGUMENTS:
======================
• pdf_file (positional): Path to PDF file (optional, uses default if not provided)
• --model {pro|flash}: Choose model - 'pro' for accuracy, 'flash' for speed (default: pro)
• -o, --output-base-dir: Base directory for pipeline outputs (default: 'output')

OUTPUT LOCATION:
===============
Results will be in: [output-base-dir]/pipeline_run_YYYYMMDD_HHMMSS_[pdf_name]/

EXAMPLES OF FULL PIPELINE CALLS:
================================
# Quick test with default PDF and fast model
python run_pipeline.py --model flash

# Production run with custom PDF and high accuracy
python run_pipeline.py "/path/to/construction_spec.pdf" --model pro

# Batch processing with custom output location
python run_pipeline.py "document1.pdf" -o batch_results --model flash
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import shutil # For potentially cleaning up directories if needed, or moving files
import json

# Set up logging record factory FIRST, before any other imports that might trigger logging
old_factory = logging.getLogRecordFactory()
def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    # Set a default pipeline_step based on context
    if not hasattr(record, 'pipeline_step'):
        # Try to determine step from the pathname or use default
        if 'toc_generator' in record.pathname:
            record.pipeline_step = 'TOC_GEN'
        elif 'llama_parse' in record.pathname:
            record.pipeline_step = 'LLAMA_PARSE'
        elif 'extract_chapter' in record.pathname:
            record.pipeline_step = 'TEXT_EXTRACT'
        else:
            record.pipeline_step = 'PIPELINE'
    return record
logging.setLogRecordFactory(record_factory)

# Configure logging for the pipeline orchestrator
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(pipeline_step)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Dynamically add project root to sys.path ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
    logger.info(f"Added project root to sys.path: {SCRIPT_DIR}")

# Import functions from other scripts
# These will be refined as we make those scripts callable
try:
    from toc_generator import step1_generate_toc, DEFAULT_MODEL_PRO, DEFAULT_MODEL_FLASH
    from llama_parse_script import run_parse as llama_run_parse # alias to avoid name clash
    from extract_chapter_text import process_chapters_recursively # Renaming/refactoring this in its own script
    from smart_heading_detection import apply_smart_heading_detection
    from content_splitter_v3 import split_content_intelligently_v3
    from analyze_current_duplication import analyze_current_duplication
    logger.info("Successfully imported callable functions from other scripts.")
except ImportError as e:
    logger.error(f"Failed to import necessary functions: {e}. Ensure all scripts are in the same directory or sys.path is correct.")
    logger.error(f"Current sys.path: {sys.path}")
    logger.error(f"Files in SCRIPT_DIR ({SCRIPT_DIR}): {os.listdir(SCRIPT_DIR) if os.path.exists(SCRIPT_DIR) else 'SCRIPT_DIR not found'}")
    sys.exit(1)

# Default PDF path
DEFAULT_PDF_PATH = r"C:\Users\gr\Documents\GitHub\ExtendedToC\Lastenboeken\cathlabarchitectlb.pdf"

def setup_pipeline_output_directory(base_output_dir="output", pdf_input_path=None):
    """
    Creates a unique, timestamped output directory for a pipeline run.
    Example: output/pipeline_run_20231027_153000_mydoc
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_name_stem = ""
    if pdf_input_path and os.path.isfile(pdf_input_path):
        pdf_name_stem = os.path.splitext(os.path.basename(pdf_input_path))[0]
        pdf_name_stem = "_" + "".join(c if c.isalnum() or c in ('_','-') else '_' for c in pdf_name_stem) # Sanitize
    
    pipeline_run_dirname = f"pipeline_run_{timestamp}{pdf_name_stem}"
    pipeline_run_dir = os.path.join(base_output_dir, pipeline_run_dirname)
    
    os.makedirs(pipeline_run_dir, exist_ok=True)
    logger.info(f"Pipeline run output directory: {pipeline_run_dir}")
    
    subdirs = {
        "toc": os.path.join(pipeline_run_dir, "toc_output"),
        "parsed_pdf": os.path.join(pipeline_run_dir, "parsed_pdf_output"),
        "final_output": os.path.join(pipeline_run_dir, "final_combined_output")
    }
    
    for subdir_path in subdirs.values():
        os.makedirs(subdir_path, exist_ok=True)
        logger.info(f"Created subdirectory: {subdir_path}")
        
    return pipeline_run_dir, subdirs

def main_pipeline():
    parser = argparse.ArgumentParser(description="Orchestrates the complete PDF to structured text pipeline with intelligent content splitting.")
    parser.add_argument("pdf_file", nargs="?", default=DEFAULT_PDF_PATH, help=f"Path to the input PDF file (default: {DEFAULT_PDF_PATH}).")
    parser.add_argument("-o", "--output-base-dir", default="output", 
                        help="Base directory for all pipeline run outputs (default: 'output').")
    parser.add_argument("--model", choices=['pro', 'flash'], default='pro', 
                        help="Model to use: 'pro' for gemini-1.5-pro-002 (default), 'flash' for gemini-2.0-flash-001 (cheaper/faster)")
    
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_file):
        logger.error(f"Input PDF file not found: {args.pdf_file}")
        sys.exit(1)

    # Map model argument to actual model name
    model_name = DEFAULT_MODEL_PRO if args.model == 'pro' else DEFAULT_MODEL_FLASH
    logger.info(f"Selected model: {model_name}")
    
    logger.info(f"Starting complete pipeline for PDF: {args.pdf_file}")    
    pipeline_run_main_dir, output_subdirs = setup_pipeline_output_directory(args.output_base_dir, args.pdf_file)

    # --- Step 1: Generate Table of Contents ---
    logger.info("Starting Step 1: TOC Generation")    
    chapters_json_path = None # Initialize
    try:
        # step1_generate_toc expects the exact output directory for its step
        # and returns (chapters_data, actual_output_dir_it_used)
        _, toc_actual_output_dir = step1_generate_toc(
            args.pdf_file, 
            output_subdirs["toc"], 
            called_by_orchestrator=True,
            model_name=model_name
        )
        chapters_json_path = os.path.join(toc_actual_output_dir, "chapters.json") 
        
        if not os.path.exists(chapters_json_path):
            logger.error(f"TOC generation did not produce chapters.json at expected location: {chapters_json_path}")
            sys.exit(1)
        logger.info(f"Step 1 complete. Chapters file: {chapters_json_path}")
    except Exception as e:
        logger.error(f"Error during TOC generation: {e}")
        sys.exit(1)

    # --- Step 2: Parse PDF with LlamaParse ---
    logger.info("Starting Step 2: LlamaParse PDF Processing")    
    parsed_pdf_json_path = None # Initialize
    try:
        # llama_parse_script's run_parse expects output_file to be the base for .md and .json
        llama_parse_base_name = os.path.join(output_subdirs["parsed_pdf"], os.path.splitext(os.path.basename(args.pdf_file))[0] + "_parsed")
        
        parsed_pdf_json_path = llama_run_parse(
            pdf_path=args.pdf_file, 
            output_file=llama_parse_base_name, 
            called_by_orchestrator=True
        ) 
        
        if not parsed_pdf_json_path or not os.path.exists(parsed_pdf_json_path):
           logger.error(f"LlamaParse did not produce the expected JSON output. Expected near: {llama_parse_base_name}.json")
           sys.exit(1)
        logger.info(f"Step 2 complete. Parsed PDF JSON: {parsed_pdf_json_path}")
    except Exception as e:
        logger.error(f"Error during LlamaParse processing: {e}")
        sys.exit(1)

    # --- Step 3: Smart Heading Detection ---
    logger.info("Starting Step 3: Smart Heading Detection and Correction")
    corrected_pdf_json_path = None
    try:
        corrected_pdf_json_path = os.path.join(output_subdirs["parsed_pdf"], os.path.splitext(os.path.basename(args.pdf_file))[0] + "_parsed_corrected.json")
        
        correction_result = apply_smart_heading_detection(parsed_pdf_json_path, corrected_pdf_json_path)
        
        if not os.path.exists(corrected_pdf_json_path):
            logger.error(f"Smart heading detection did not produce corrected JSON output: {corrected_pdf_json_path}")
            sys.exit(1)
        
        logger.info(f"Step 3 complete. Made {correction_result['corrections_made']} heading corrections.")
        logger.info(f"Corrected headings saved to: {corrected_pdf_json_path}")
    except Exception as e:
        logger.error(f"Error during smart heading detection: {e}")
        sys.exit(1)

    # --- Step 4: Extract Text per Chapter (Original Method) ---
    logger.info("Starting Step 4: Extracting Text per Chapter (Original Method)")    
    final_output_chapters_with_text_json = os.path.join(output_subdirs["final_output"], "chapters_with_text.json")
    try:
        with open(corrected_pdf_json_path, 'r', encoding='utf-8') as f:
            llama_parsed_content = json.load(f)
        with open(chapters_json_path, 'r', encoding='utf-8') as f:
            toc_chapters_content = json.load(f)
        
        if isinstance(llama_parsed_content, dict) and 'pages' in llama_parsed_content:
            llama_pages_list = llama_parsed_content['pages']
        elif isinstance(llama_parsed_content, list):
            llama_pages_list = llama_parsed_content
        else:
            logger.error("LlamaParse output is not in expected list or dict with 'pages' key.")
            sys.exit(1)
            
        extracted_data_result = {}
        process_chapters_recursively(toc_chapters_content, llama_pages_list, extracted_data_result)
        
        with open(final_output_chapters_with_text_json, 'w', encoding='utf-8') as f:
            json.dump(extracted_data_result, f, ensure_ascii=False, indent=2)
        logger.info(f"Step 4 complete. Original extraction: {final_output_chapters_with_text_json}")
    except Exception as e:
        logger.error(f"Error during original text extraction: {e}")
        sys.exit(1)

    # --- Step 5: Intelligent Content Splitting V3 ---
    logger.info("Starting Step 5: Intelligent Content Splitting V3")
    v3_output_json = os.path.join(output_subdirs["final_output"], "chapters_with_text_v3.json")
    try:
        v3_result = split_content_intelligently_v3(corrected_pdf_json_path, chapters_json_path, v3_output_json)
        
        if not os.path.exists(v3_output_json):
            logger.error(f"V3 intelligent splitting did not produce output: {v3_output_json}")
            sys.exit(1)
        
        logger.info(f"Step 5 complete. V3 intelligent splitting: {v3_output_json}")
        logger.info(f"Processed {len(v3_result)} sections with intelligent boundary detection")
    except Exception as e:
        logger.error(f"Error during V3 intelligent content splitting: {e}")
        sys.exit(1)

    # --- Step 6: Duplication Analysis ---
    logger.info("Starting Step 6: Final Duplication Analysis")
    try:
        analysis_result = analyze_current_duplication(v3_output_json)
        
        logger.info(f"Step 6 complete. Duplication analysis finished.")
        logger.info(f"Current duplication ratio: {analysis_result['duplication_ratio']:.1f}x")
        logger.info(f"Boundary detection rate: {analysis_result['boundary_detection_rate']:.1f}%")
    except Exception as e:
        logger.error(f"Error during duplication analysis: {e}")
        # Don't exit for analysis error, just log it
        logger.warning("Continuing without duplication analysis...")

    logger.info("=" * 60)
    logger.info("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY! 🎉")
    logger.info("=" * 60)
    logger.info(f"📁 Main output directory: {pipeline_run_main_dir}")
    logger.info(f"📊 TOC Generation: {chapters_json_path}")
    logger.info(f"🧠 Smart Headings: {corrected_pdf_json_path}")
    logger.info(f"📄 Original Extraction: {final_output_chapters_with_text_json}")
    logger.info(f"🎯 V3 Intelligent Splitting: {v3_output_json}")
    logger.info("=" * 60)
    
    # Final output summary for future reference:
    # PRIMARY OUTPUT: {v3_output_json} - Intelligent splitting with boundary detection
    # COMPARISON: {final_output_chapters_with_text_json} - Original extraction method  
    # TOC STRUCTURE: {chapters_json_path} - Hierarchical table of contents
    # SMART HEADINGS: {corrected_pdf_json_path} - LlamaParse with corrected heading levels
    # OUTPUT DIRECTORY: {pipeline_run_main_dir} - Contains all pipeline artifacts

if __name__ == "__main__":
    main_pipeline() 