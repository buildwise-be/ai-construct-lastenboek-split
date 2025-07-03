"""
PDF Processor Module

This module handles PDF processing operations including TOC generation and PDF splitting.
Extracted from the monolithic main script to improve maintainability.
"""

import os
import json
import base64
import time
import logging
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
from vertexai.generative_models import GenerativeModel, Part

from .ai_client import get_global_client, GENERATION_CONFIG, SAFETY_SETTINGS
from .file_utils import setup_output_directory, sanitize_filename

# Configure logging
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF processing operations including TOC generation and splitting.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.ai_client = get_global_client()
    
    def generate_toc(self, pdf_path, output_base_dir=None, project_id=None):
        """
        Generate table of contents from a PDF document.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_base_dir (str, optional): Base directory for output
            project_id (str, optional): Google Cloud project ID
            
        Returns:
            tuple: (chapters_dict, output_dir)
        """
        logger.info("=" * 50)
        logger.info("STEP 1: Generating Table of Contents...")
        logger.info("=" * 50)
        
        # Setup output directory
        output_dir = setup_output_directory("step1_toc", output_base_dir)
        
        # Validate PDF file
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Processing PDF file: {pdf_path}")
        
        # System instruction for TOC generation
        system_instruction = """You are given a technical specifications PDF document in the construction sector (\"Samengevoegdlastenboek\") that can be a concatenation of multiple different documents, each with their own internal page numbering.\n\nThe document contains numbered chapters in two formats:\n1. Main chapters: formatted as \"XX. TITLE\" (e.g., \"00. ALGEMENE BEPALINGEN\")\n2. Sections: formatted as \"XX.YY TITLE\" (e.g., \"01.10 SECTIETITEL\") or formatted as \"XX.YY.ZZ TITLE\" (e.g., \"01.10.01 SECTIETITEL\") and even \"XX.YY.ZZ.AA TITLE\" (e.g., \"01.10.01.01 SECTIETITEL\")\n\nYour task is to identify both main chapters (00-93) and their sections, using the GLOBAL PDF page numbers (not the internal page numbers that appear within each document section).\n\nFor each main chapter and section:\n1. Record the precise numbering (e.g., \"00\" or \"01.10\")\n2. Record the accurate starting page number based on the GLOBAL PDF page count (starting from 1 for the first page)\n3. Record the accurate ending page number (right before the next chapter/section starts)\n4. Summarize the content of the chapter and sections in 10 keywords or less to help with the categorization process\n\nIMPORTANT: \n- Use the actual PDF page numbers (starting from 1 for the first page of the entire PDF)\n- IGNORE any page numbers printed within the document itself\n- The page numbers in any table of contents (inhoudstafel) are UNRELIABLE - do not use them\n- Determine page numbers by finding where each chapter actually begins and ends in the PDF\n- Be EXTREMELY thorough in identifying ALL sections and subsections, including those with patterns like XX.YY.ZZ.AA\n- Don't miss any chapter or section - this is critical for accurate document processing\n\nFinal output should be a nested Python dictionary structure:```\nchapters = {\n    \"00\": {\n        \"start\": start_page,\n        \"end\": end_page,\n        \"title\": \"CHAPTER TITLE\",\n        \"sections\": {\n            'XX.YY': {'start': start_page, 'end': end_page, 'title': 'section title'},\n            'XX.YY.ZZ': {'start': start_page, 'end': end_page, 'title': 'subsection title'},\n            'XX.YY.ZZ.AA': {'start': start_page, 'end': end_page, 'title': 'sub-subsection title'}\n        }\n    }\n}\n```\n"""
        
        try:
            # Initialize model
            if project_id:
                self.ai_client.update_project_id(project_id)
            
            model = self.ai_client.create_model(system_instruction=system_instruction)
            logger.info("Initialized Vertex AI model successfully")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI model: {str(e)}")
            raise
        
        # Get PDF page count
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {total_pages} pages")
        except Exception as e:
            logger.error(f"Error reading PDF page count: {str(e)}")
            raise
        
        # Prepare PDF for AI processing
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            multimodal_model = GenerativeModel(
                "gemini-2.5-pro",
                generation_config=GENERATION_CONFIG,
                safety_settings=SAFETY_SETTINGS
            )
            logger.info("PDF file loaded and encoded for Vertex AI")
        except Exception as e:
            logger.error(f"Error preparing PDF for Vertex AI: {str(e)}")
            raise
        
        # Process PDF in batches
        chapters = self._process_pdf_in_batches(multimodal_model, pdf_bytes, total_pages)
        
        # Validate and save results
        validated_chapters = self._validate_chapters(chapters)
        
        chapters_json_path = os.path.join(output_dir, "chapters.json")
        with open(chapters_json_path, 'w', encoding='utf-8') as f:
            json.dump(validated_chapters, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved chapters data to {chapters_json_path}")
        
        return validated_chapters, output_dir
    
    def _process_pdf_in_batches(self, model, pdf_bytes, total_pages):
        """
        Process PDF in batches to handle large documents.
        
        Args:
            model: The AI model instance
            pdf_bytes: PDF file bytes
            total_pages: Total number of pages in PDF
            
        Returns:
            dict: Combined chapters from all batches
        """
        page_batch_size = 50
        overlap = 5
        page_batches = []
        
        # Create page batches
        for start_page in range(1, total_pages + 1, page_batch_size - overlap):
            end_page = min(start_page + page_batch_size - 1, total_pages)
            if end_page - start_page < 5 and len(page_batches) > 0:
                page_batches[-1] = (page_batches[-1][0], end_page)
                break
            page_batches.append((start_page, end_page))
        
        logger.info(f"Processing PDF in {len(page_batches)} page batches with size {page_batch_size} and overlap {overlap}")
        
        page_batch_results = {}
        
        try:
            # Initial document structure analysis
            initial_prompt = f"""
            I'll be analyzing a construction-specific PDF document with {total_pages} pages. First, I need you to provide me with a basic structure of this document.
            The PDF file is a technical construction document in Dutch/Flemish called a \"lastenboek\" (specification document).
            It contains chapters numbered like \"XX. TITLE\" (e.g., \"00. ALGEMENE BEPALINGEN\") and sections like \"XX.YY TITLE\".
            Based on the PDF I'm providing, identify the main chapters (like 00, 01, 02, etc.) and their approximate page ranges.
            This will help me analyze the document in more detail with subsequent questions.
            Format the response as a simple outline with page ranges.
            """
            
            chat = model.start_chat()
            response = chat.send_message([
                initial_prompt,
                Part.from_data(data=pdf_bytes, mime_type="application/pdf")
            ])
            logger.info("Received initial document structure")
            
            # Process each batch
            rate_limit_delay = 2.0
            error_backoff_multiplier = 1.0
            
            for batch_idx, (start_page, end_page) in enumerate(page_batches):
                if batch_idx > 0:
                    delay = rate_limit_delay * error_backoff_multiplier
                    logger.info(f"Rate limiting: Waiting {delay:.2f} seconds before processing next batch...")
                    time.sleep(delay)
                
                logger.info(f"Processing page batch {batch_idx+1}/{len(page_batches)}: pages {start_page}-{end_page}")
                
                # Create batch-specific prompt
                if batch_idx < 3:
                    comprehensive_note = "This is one of the first batches, so pay extra attention to identify the document structure and early chapters."
                elif batch_idx >= len(page_batches) - 3:
                    comprehensive_note = "This is one of the final batches, so pay extra attention to identify any closing chapters or sections."
                else:
                    comprehensive_note = ""
                
                page_prompt = f"""
                Analyze pages {start_page}-{end_page} of this PDF document and identify any chapters or sections 
                that appear within these pages.
                {comprehensive_note}
                IMPORTANT INSTRUCTIONS:
                - This document uses chapter numbering like \"XX. TITLE\" (e.g. \"00. ALGEMENE BEPALINGEN\")
                - Sections are formatted as \"XX.YY TITLE\" (e.g., \"01.10 SECTIETITEL\")
                - Subsections may be formatted as \"XX.YY.ZZ TITLE\" or \"XX.YY.ZZ.AA TITLE\"
                - Focus ONLY on pages {start_page} through {end_page}
                - Use the GLOBAL PDF page numbers (starting from 1 for the first page of the PDF)
                - IGNORE any page numbers printed within the document itself
                - For each chapter/section, record its exact start page and end page
                - The end page of a chapter/section is the page right before the next chapter/section begins
                - If a chapter/section starts in this range but continues beyond page {end_page}, set the end page as {end_page} for now
                - If a chapter/section ends in this range but started before page {start_page}, set the start page as {start_page} for now
                - Be thorough, even for sections that appear to be brief
                Format the output as a Python dictionary like this:
                ```python
                chapters = {{
                    "XX": {{'start': X, 'end': Y, 'title': 'CHAPTER TITLE', 'sections': {{
                        'XX.YY': {{'start': X, 'end': Y, 'title': 'section title'}},
                        'XX.YY.ZZ': {{'start': X, 'end': Y, 'title': 'subsection title'}}
                    }}}}
                }}
                ```
                Include ONLY chapters or sections that appear within pages {start_page}-{end_page}.
                """
                
                try:
                    batch_response = chat.send_message(page_prompt)
                    page_batch_dict = self.ai_client._post_process_response(batch_response.text)
                    
                    if page_batch_dict:
                        logger.info(f"Found chapter/section data in pages {start_page}-{end_page}: {len(page_batch_dict)} chapters")
                        self._merge_batch_results(page_batch_results, page_batch_dict)
                    else:
                        logger.info(f"No chapter/section data found in pages {start_page}-{end_page}")
                    
                    error_backoff_multiplier = max(1.0, error_backoff_multiplier * 0.8)
                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_idx+1}: {str(e)}")
                    error_backoff_multiplier *= 2.0
                    logger.warning(f"Increasing rate limit delay multiplier to {error_backoff_multiplier} due to error")
            
        except Exception as e:
            logger.error(f"Error processing with Vertex AI: {str(e)}")
            raise
        
        # Post-process results to adjust page ranges
        self._adjust_page_ranges(page_batch_results)
        
        return page_batch_results
    
    def _merge_batch_results(self, page_batch_results, page_batch_dict):
        """
        Merge results from a batch into the main results dictionary.
        
        Args:
            page_batch_results (dict): Main results dictionary
            page_batch_dict (dict): Results from current batch
        """
        for chapter_id, chapter_data in page_batch_dict.items():
            if chapter_id not in page_batch_results:
                page_batch_results[chapter_id] = chapter_data
            else:
                existing = page_batch_results[chapter_id]
                
                # Update start/end pages
                if chapter_data['start'] < existing['start']:
                    existing['start'] = chapter_data['start']
                if chapter_data['end'] > existing['end']:
                    existing['end'] = chapter_data['end']
                
                # Merge sections
                if 'sections' in chapter_data:
                    if 'sections' not in existing:
                        existing['sections'] = {}
                    
                    for section_id, section_data in chapter_data['sections'].items():
                        if section_id not in existing['sections']:
                            existing['sections'][section_id] = section_data
                        else:
                            existing_section = existing['sections'][section_id]
                            if section_data['start'] < existing_section['start']:
                                existing_section['start'] = section_data['start']
                            if section_data['end'] > existing_section['end']:
                                existing_section['end'] = section_data['end']
                            if 'title' in section_data and (len(section_data['title']) > len(existing_section.get('title', ''))):
                                existing_section['title'] = section_data['title']
    
    def _adjust_page_ranges(self, chapters):
        """
        Adjust page ranges to ensure chapters and sections don't overlap.
        
        Args:
            chapters (dict): Chapters dictionary to adjust
        """
        # Sort chapters by start page
        sorted_chapters = sorted([(k, v) for k, v in chapters.items()], key=lambda x: x[1]['start'])
        
        # Adjust chapter end pages
        for i in range(len(sorted_chapters) - 1):
            current_ch_id, current_ch = sorted_chapters[i]
            next_ch_id, next_ch = sorted_chapters[i + 1]
            
            if current_ch['end'] < next_ch['start'] - 1:
                current_ch['end'] = next_ch['start'] - 1
                logger.info(f"Adjusted end page of chapter {current_ch_id} to {current_ch['end']}")
            
            # Adjust section end pages within the chapter
            if 'sections' in current_ch and current_ch['sections']:
                sorted_sections = sorted([(k, v) for k, v in current_ch['sections'].items()], key=lambda x: x[1]['start'])
                
                for j in range(len(sorted_sections) - 1):
                    current_sec_id, current_sec = sorted_sections[j]
                    next_sec_id, next_sec = sorted_sections[j + 1]
                    
                    if current_sec['end'] < next_sec['start'] - 1:
                        current_sec['end'] = next_sec['start'] - 1
                        logger.info(f"Adjusted end page of section {current_sec_id} to {current_sec['end']}")
                
                # Ensure last section doesn't exceed chapter bounds
                if sorted_sections:
                    last_sec_id, last_sec = sorted_sections[-1]
                    if last_sec['end'] < current_ch['end']:
                        last_sec['end'] = current_ch['end']
                        logger.info(f"Adjusted end page of last section {last_sec_id} to {last_sec['end']}")
                
                # Update sections in the chapter
                for sec_id, sec_data in sorted_sections:
                    current_ch['sections'][sec_id] = sec_data
        
        # Update chapters with adjusted data
        for ch_id, ch_data in sorted_chapters:
            chapters[ch_id] = ch_data
    
    def _validate_chapters(self, chapters_dict):
        """
        Validate chapters dictionary to ensure data integrity.
        
        Args:
            chapters_dict (dict): Chapters dictionary to validate
            
        Returns:
            dict: Validated chapters dictionary
        """
        validated = {}
        max_page = 0
        
        # Find maximum page number for validation
        for chapter, data in chapters_dict.items():
            if isinstance(data, dict) and 'end' in data and isinstance(data['end'], int) and data['end'] > max_page:
                max_page = data['end']
        
        reasonable_max = max(max_page, 1000)
        
        for chapter, data in chapters_dict.items():
            if not data or not isinstance(data, dict):
                continue
            
            # Validate chapter page numbers
            if ('start' not in data or 'end' not in data or 
                not isinstance(data['start'], int) or not isinstance(data['end'], int) or
                data['start'] < 1 or data['end'] > reasonable_max or data['start'] > data['end']):
                logger.warning(f"Chapter {chapter} has invalid page numbers: {data.get('start', 'missing')}-{data.get('end', 'missing')}")
                continue
            
            # Validate sections
            if 'sections' in data and isinstance(data['sections'], dict):
                valid_sections = {}
                for section_id, section_data in data['sections'].items():
                    if not isinstance(section_data, dict):
                        continue
                    
                    if ('start' not in section_data or 'end' not in section_data or 
                        not isinstance(section_data['start'], int) or not isinstance(section_data['end'], int) or
                        section_data['start'] < 1 or section_data['end'] > reasonable_max or 
                        section_data['start'] > section_data['end']):
                        logger.warning(f"Section {section_id} has invalid page numbers: {section_data.get('start', 'missing')}-{section_data.get('end', 'missing')}")
                        continue
                    
                    valid_sections[section_id] = section_data
                
                data['sections'] = valid_sections
            
            validated[chapter] = data
        
        return validated
    
    def extract_category_pdfs(self, pdf_path, chapter_results, section_results, category_match_dir, 
                             category_file, second_output_dir=None, third_output_dir=None, base_dir=None):
        """
        Extract category-specific PDFs from the main PDF document.
        
        Args:
            pdf_path (str): Path to the source PDF
            chapter_results (dict): Chapter matching results
            section_results (dict): Section matching results  
            category_match_dir (str): Directory with category matching results
            category_file (str): Path to category definitions file
            second_output_dir (str, optional): Secondary output directory
            third_output_dir (str, optional): Tertiary output directory
            base_dir (str, optional): Base output directory
            
        Returns:
            tuple: (category_counts, output_dir)
        """
        logger.info("=" * 50)
        logger.info("STEP 3: Extracting Category-Specific PDFs...")
        logger.info("=" * 50)
        
        # Setup output directory
        output_dir = setup_output_directory("step3_category_pdfs", base_dir)
        logger.info(f"Output directory: {output_dir}")
        
        # Load category definitions
        try:
            import sys
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("categories", category_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module from {category_file}")
            
            categories_module = importlib.util.module_from_spec(spec)
            sys.modules["categories"] = categories_module
            spec.loader.exec_module(categories_module)
            
            df = categories_module.df
            logger.info(f"Loaded {len(df)} categories from {category_file}")
        except Exception as e:
            logger.error(f"Error loading category file: {str(e)}")
            raise
        
        # Load PDF
        try:
            pdf_reader = PdfReader(pdf_path)
            total_pages = len(pdf_reader.pages)
            logger.info(f"Source PDF has {total_pages} pages")
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
        
        # Collect all categorized items
        category_pages = {}
        
        # Process chapters
        for chapter_id, chapter_data in chapter_results.items():
            if 'categories' in chapter_data:
                for category in chapter_data['categories']:
                    if category not in category_pages:
                        category_pages[category] = []
                    category_pages[category].append({
                        'type': 'chapter',
                        'id': chapter_id,
                        'start': chapter_data.get('start_page', 1),
                        'end': chapter_data.get('end_page', 1),
                        'title': chapter_data.get('title', f'Chapter {chapter_id}')
                    })
        
        # Process sections
        for section_id, section_data in section_results.items():
            if 'categories' in section_data:
                for category in section_data['categories']:
                    if category not in category_pages:
                        category_pages[category] = []
                    category_pages[category].append({
                        'type': 'section',
                        'id': section_id,
                        'start': section_data.get('start_page', 1),
                        'end': section_data.get('end_page', 1),
                        'title': section_data.get('title', f'Section {section_id}')
                    })
        
        logger.info(f"Found content for {len(category_pages)} categories")
        
        # Create PDFs for each category
        category_counts = {}
        
        for category, items in category_pages.items():
            try:
                # Sort items by start page
                items.sort(key=lambda x: x['start'])
                
                # Create new PDF writer
                pdf_writer = PdfWriter()
                page_count = 0
                
                # Add pages for each item
                for item in items:
                    start_page = item['start'] - 1  # Convert to 0-based indexing
                    end_page = item['end'] - 1
                    
                    # Ensure page indices are valid
                    start_page = max(0, min(start_page, total_pages - 1))
                    end_page = max(start_page, min(end_page, total_pages - 1))
                    
                    # Add pages to the new PDF
                    for page_num in range(start_page, end_page + 1):
                        if page_num < total_pages:
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                            page_count += 1
                
                if page_count > 0:
                    # Save the category PDF
                    safe_category = sanitize_filename(category)
                    output_filename = f"{safe_category}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    category_counts[category] = {
                        'pages': page_count,
                        'items': len(items),
                        'file': output_filename
                    }
                    
                    logger.info(f"Created {output_filename}: {page_count} pages from {len(items)} items")
                else:
                    logger.warning(f"No pages found for category: {category}")
            
            except Exception as e:
                logger.error(f"Error creating PDF for category {category}: {str(e)}")
                continue
        
        # Save summary
        summary_path = os.path.join(output_dir, "category_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(category_counts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created {len(category_counts)} category PDFs")
        logger.info(f"Summary saved to {summary_path}")
        
        return category_counts, output_dir


# Global instance for backward compatibility
_global_processor = None

def get_global_processor():
    """Get or create the global PDF processor instance."""
    global _global_processor
    if _global_processor is None:
        _global_processor = PDFProcessor()
    return _global_processor

# Backward compatibility functions
def step1_generate_toc(pdf_path, output_base_dir=None, project_id=None):
    """Generate TOC from PDF (backward compatibility function)."""
    processor = get_global_processor()
    return processor.generate_toc(pdf_path, output_base_dir, project_id)

def step3_extract_category_pdfs(pdf_path, chapter_results, section_results, category_match_dir, 
                               category_file, second_output_dir=None, third_output_dir=None, base_dir=None):
    """Extract category PDFs (backward compatibility function)."""
    processor = get_global_processor()
    return processor.extract_category_pdfs(pdf_path, chapter_results, section_results, 
                                         category_match_dir, category_file, 
                                         second_output_dir, third_output_dir, base_dir)