import os
import sys
import json
import logging
import base64
import time
import random
from datetime import datetime
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Vertex AI configuration
GENERATION_CONFIG = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

# Load environment variables
load_dotenv()

# Helper: output directory setup (simplified)
def setup_output_directory(step_name=None, base_output_dir=None):
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    base_output_path = base_output_dir if base_output_dir else "output"
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if step_name:
        output_dir = os.path.join(base_output_path, f"{script_name}_{step_name}_{timestamp}")
    else:
        output_dir = os.path.join(base_output_path, f"{script_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

# Vertex AI model initialization
def initialize_vertex_model(system_instruction=None, project_id=None):
    try:
        if project_id:
            vertexai.init(
                project=project_id,
                location="europe-west1",
                api_endpoint="europe-west1-aiplatform.googleapis.com"
            )
            logger.info(f"Reinitialized Vertex AI with project ID: {project_id}")
        model = GenerativeModel(
            "gemini-1.5-pro-002",
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            system_instruction=[system_instruction] if system_instruction else None
        )
        logger.info("Successfully initialized Vertex AI Gemini model")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model: {str(e)}")
        raise RuntimeError("Failed to initialize Vertex AI model")

# Helper: extract Python dict from model response
def post_process_results(response_text):
    try:
        code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
        if code_block_match:
            code_block = code_block_match.group(1)
            local_vars = {}
            exec(code_block, {}, local_vars)
            if 'chapters' in local_vars:
                return local_vars['chapters']
            elif 'secties' in local_vars:
                return local_vars['secties']
    except Exception as e:
        logger.error(f"Error post-processing results: {str(e)}")
    return None

# Main TOC generation function
def step1_generate_toc(pdf_path, output_base_dir=None, project_id=None):
    logger.info("=" * 50)
    logger.info("STEP 1: Generating Table of Contents...")
    logger.info("=" * 50)
    output_dir = setup_output_directory("step1_toc", output_base_dir)
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    logger.info(f"Processing PDF file: {pdf_path}")
    system_instruction = """You are given a technical specifications PDF document in the construction sector (\"Samengevoegdlastenboek\") that can be a concatenation of multiple different documents, each with their own internal page numbering.\n\nThe document contains numbered chapters in two formats:\n1. Main chapters: formatted as \"XX. TITLE\" (e.g., \"00. ALGEMENE BEPALINGEN\")\n2. Sections: formatted as \"XX.YY TITLE\" (e.g., \"01.10 SECTIETITEL\") or formatted as \"XX.YY.ZZ TITLE\" (e.g., \"01.10.01 SECTIETITEL\") and even \"XX.YY.ZZ.AA TITLE\" (e.g., \"01.10.01.01 SECTIETITEL\")\n\nYour task is to identify both main chapters (00-93) and their sections, using the GLOBAL PDF page numbers (not the internal page numbers that appear within each document section).\n\nFor each main chapter and section:\n1. Record the precise numbering (e.g., \"00\" or \"01.10\")\n2. Record the accurate starting page number based on the GLOBAL PDF page count (starting from 1 for the first page)\n3. Record the accurate ending page number (right before the next chapter/section starts)\n4. Summarize the content of the chapter and sections in 10 keywords or less to help with the categorization process\n\nIMPORTANT: \n- Use the actual PDF page numbers (starting from 1 for the first page of the entire PDF)\n- IGNORE any page numbers printed within the document itself\n- The page numbers in any table of contents (inhoudstafel) are UNRELIABLE - do not use them\n- Determine page numbers by finding where each chapter actually begins and ends in the PDF\n- Be EXTREMELY thorough in identifying ALL sections and subsections, including those with patterns like XX.YY.ZZ.AA\n- Don't miss any chapter or section - this is critical for accurate document processing\n\nFinal output should be a nested Python dictionary structure:```\nchapters = {\n    \"00\": {\n        \"start\": start_page,\n        \"end\": end_page,\n        \"title\": \"CHAPTER TITLE\",\n        \"sections\": {\n            'XX.YY': {'start': start_page, 'end': end_page, 'title': 'section title'},\n            'XX.YY.ZZ': {'start': start_page, 'end': end_page, 'title': 'subsection title'},\n            'XX.YY.ZZ.AA': {'start': start_page, 'end': end_page, 'title': 'sub-subsection title'}\n        }\n    }\n}\n```\n"""
    try:
        model = initialize_vertex_model(system_instruction, project_id=project_id)
        logger.info("Initialized Vertex AI model successfully")
    except Exception as e:
        logger.error(f"Error initializing Vertex AI model: {str(e)}")
        raise
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {total_pages} pages")
    except Exception as e:
        logger.error(f"Error reading PDF page count: {str(e)}")
        raise
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        multimodal_model = GenerativeModel(
            "gemini-1.5-pro-002",
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        logger.info("PDF file loaded and encoded for Vertex AI")
    except Exception as e:
        logger.error(f"Error preparing PDF for Vertex AI: {str(e)}")
        raise
    page_batch_size = 50
    overlap = 5
    page_batches = []
    for start_page in range(1, total_pages + 1, page_batch_size - overlap):
        end_page = min(start_page + page_batch_size - 1, total_pages)
        if end_page - start_page < 5 and len(page_batches) > 0:
            page_batches[-1] = (page_batches[-1][0], end_page)
            break
        page_batches.append((start_page, end_page))
    logger.info(f"Processing PDF in {len(page_batches)} page batches with size {page_batch_size} and overlap {overlap}")
    page_batch_results = {}
    try:
        initial_prompt = f"""
        I'll be analyzing a construction-specific PDF document with {total_pages} pages. First, I need you to provide me with a basic structure of this document.
        The PDF file is a technical construction document in Dutch/Flemish called a \"lastenboek\" (specification document).
        It contains chapters numbered like \"XX. TITLE\" (e.g., \"00. ALGEMENE BEPALINGEN\") and sections like \"XX.YY TITLE\".
        Based on the PDF I'm providing, identify the main chapters (like 00, 01, 02, etc.) and their approximate page ranges.
        This will help me analyze the document in more detail with subsequent questions.
        Format the response as a simple outline with page ranges.
        """
        chat = multimodal_model.start_chat()
        response = chat.send_message([
            initial_prompt,
            Part.from_data(data=pdf_bytes, mime_type="application/pdf")
        ])
        logger.info("Received initial document structure")
        rate_limit_delay = 2.0
        error_backoff_multiplier = 1.0
        for batch_idx, (start_page, end_page) in enumerate(page_batches):
            if batch_idx > 0:
                delay = rate_limit_delay * error_backoff_multiplier
                logger.info(f"Rate limiting: Waiting {delay:.2f} seconds before processing next batch...")
                time.sleep(delay)
            logger.info(f"Processing page batch {batch_idx+1}/{len(page_batches)}: pages {start_page}-{end_page}")
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
                page_batch_dict = post_process_results(batch_response.text)
                if page_batch_dict:
                    logger.info(f"Found chapter/section data in pages {start_page}-{end_page}: {len(page_batch_dict)} chapters")
                    for chapter_id, chapter_data in page_batch_dict.items():
                        if chapter_id not in page_batch_results:
                            page_batch_results[chapter_id] = chapter_data
                        else:
                            existing = page_batch_results[chapter_id]
                            if chapter_data['start'] < existing['start']:
                                existing['start'] = chapter_data['start']
                            if chapter_data['end'] > existing['end']:
                                existing['end'] = chapter_data['end']
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
    sorted_chapters = sorted([(k, v) for k, v in page_batch_results.items()], key=lambda x: x[1]['start'])
    for i in range(len(sorted_chapters) - 1):
        current_ch_id, current_ch = sorted_chapters[i]
        next_ch_id, next_ch = sorted_chapters[i + 1]
        if current_ch['end'] < next_ch['start'] - 1:
            current_ch['end'] = next_ch['start'] - 1
            logger.info(f"Adjusted end page of chapter {current_ch_id} to {current_ch['end']}")
        if 'sections' in current_ch and current_ch['sections']:
            sorted_sections = sorted([(k, v) for k, v in current_ch['sections'].items()], key=lambda x: x[1]['start'])
            for j in range(len(sorted_sections) - 1):
                current_sec_id, current_sec = sorted_sections[j]
                next_sec_id, next_sec = sorted_sections[j + 1]
                if current_sec['end'] < next_sec['start'] - 1:
                    current_sec['end'] = next_sec['start'] - 1
                    logger.info(f"Adjusted end page of section {current_sec_id} to {current_sec['end']}")
            if sorted_sections:
                last_sec_id, last_sec = sorted_sections[-1]
                if last_sec['end'] < current_ch['end']:
                    last_sec['end'] = current_ch['end']
                    logger.info(f"Adjusted end page of last section {last_sec_id} to {last_sec['end']}")
            for sec_id, sec_data in sorted_sections:
                current_ch['sections'][sec_id] = sec_data
    for ch_id, ch_data in sorted_chapters:
        page_batch_results[ch_id] = ch_data
    chapters = page_batch_results
    def validate_chapters(chapters_dict):
        validated = {}
        max_page = 0
        for chapter, data in chapters_dict.items():
            if isinstance(data, dict) and 'end' in data and isinstance(data['end'], int) and data['end'] > max_page:
                max_page = data['end']
        reasonable_max = max(max_page, 1000)
        for chapter, data in chapters_dict.items():
            if not data or not isinstance(data, dict):
                continue
            if ('start' not in data or 'end' not in data or 
                not isinstance(data['start'], int) or not isinstance(data['end'], int) or
                data['start'] < 1 or data['end'] > reasonable_max or data['start'] > data['end']):
                logger.warning(f"Chapter {chapter} has invalid page numbers: {data.get('start', 'missing')}-{data.get('end', 'missing')}")
                continue
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
    validated_chapters = validate_chapters(chapters)
    chapters_json_path = os.path.join(output_dir, "chapters.json")
    with open(chapters_json_path, 'w', encoding='utf-8') as f:
        json.dump(validated_chapters, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved chapters data to {chapters_json_path}")
    return validated_chapters, output_dir

def main():
    # Default test values
    DEFAULT_PDF_PATH = "test.pdf"  # Change to a real test file if available
    DEFAULT_OUTPUT_DIR = "output"
    parser = argparse.ArgumentParser(description="Generate TOC from PDF and output as JSON.")
    parser.add_argument("pdf_path", nargs="?", help="Path to the PDF file to process")
    parser.add_argument("-o", "--output-dir", help="Output directory (optional)")
    parser.add_argument("-p", "--project-id", help="Google Cloud Project ID (optional)")
    parser.add_argument("-j", "--json-file", help="Path to save JSON output (optional)")
    args = parser.parse_args()

    # Use defaults if not provided
    pdf_path = args.pdf_path or DEFAULT_PDF_PATH
    output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
    if not args.pdf_path:
        print(f"No PDF path provided, using default: {pdf_path}")
    if not args.output_dir:
        print(f"No output directory provided, using default: {output_dir}")

    # Check if the default PDF exists if no path is provided
    if pdf_path == DEFAULT_PDF_PATH and not os.path.exists(DEFAULT_PDF_PATH):
        logger.warning(f"Default PDF '{DEFAULT_PDF_PATH}' not found. Please provide a PDF path or create the file.")
        # Create a dummy PDF if it doesn't exist and it's the default, to prevent error on run
        # This is for illustrative purposes; in a real scenario, you'd require the PDF.
        try:
            from PyPDF2 import PdfWriter # Import here to keep it local to main
            writer = PdfWriter()
            writer.add_blank_page(width=210, height=297) # A4 size in points
            with open(DEFAULT_PDF_PATH, "wb") as f:
                writer.write(f)
            logger.info(f"Created a dummy '{DEFAULT_PDF_PATH}' for testing purposes.")
        except Exception as e:
            logger.error(f"Could not create dummy PDF: {e}")
            return # Exit if dummy PDF creation fails

    toc, out_dir = step1_generate_toc(pdf_path, output_dir, args.project_id)
    if args.json_file:
        # If a specific json_file path is given, save the main result there too.
        # The function step1_generate_toc already saves a chapters.json in its own output_dir.
        try:
            with open(args.json_file, 'w', encoding='utf-8') as f:
                json.dump(toc, f, ensure_ascii=False, indent=2)
            print(f"TOC JSON also saved to {args.json_file}")
        except IOError as e:
            print(f"Error saving TOC JSON to {args.json_file}: {e}")
    else:
        # If no specific json_file, print to console as before.
        print(json.dumps(toc, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # Import argparse here, only when script is run directly
    import argparse
    main() 