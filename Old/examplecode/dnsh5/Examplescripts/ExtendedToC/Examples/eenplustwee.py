#eenplustwee.py
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
import argparse

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
    abs_pdf_path = os.path.abspath(pdf_path)
    try:
        file_size = os.path.getsize(abs_pdf_path)
    except Exception:
        file_size = 'Unknown (file not found)'
    print(f"[STEP 1] Using PDF file: {abs_pdf_path} (size: {file_size} bytes)")
    logger.info(f"[STEP 1] Using PDF file: {abs_pdf_path} (size: {file_size} bytes)")
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
    page_batch_size = 30
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

# ----------------------------------------------------------------
# Definitions from the second part of the script, moved here to be available for main()
# ----------------------------------------------------------------

# PyPDF2 is imported at the top as 'from PyPDF2 import PdfReader'
# Other necessary imports like json, os, logging, vertexai, SafetySetting, GenerativeModel are also at the top.
# load_dotenv() is also called at the top.

def extract_section_text(pdf_reader: PdfReader, num_pages: int, start_page: int, end_page: int) -> str:
    """Extracts text from the PDF for pages [start_page..end_page].
    Page numbers are 1-based for input, converted to 0-based for PyPDF2.
    """
    text_content = []
    actual_start_idx = max(0, start_page - 1)
    actual_end_idx = min(num_pages - 1, end_page - 1) 

    if actual_start_idx > actual_end_idx :
        logger.warning(f"Invalid page range for extraction: start_page {start_page} (idx {actual_start_idx}) > end_page {end_page} (idx {actual_end_idx}). Returning empty string.")
        return ""

    for p in range(actual_start_idx, actual_end_idx + 1):
        try:
            page = pdf_reader.pages[p]
            page_text = page.extract_text() or ""
            text_content.append(page_text)
        except IndexError:
            logger.warning(f"Page index {p} out of range (Total pages: {num_pages}). Skipping.")
        except Exception as e:
            logger.warning(f"Could not extract text from page {p+1}. Error: {e}. Skipping.")
    return "\n".join(text_content)


def _traverse_toc_for_ranges(node: dict, code: str, page_ranges: dict):
    start = node.get("start")
    end = node.get("end")
    title = node.get("title", "Untitled Section")

    if code and isinstance(start, int) and isinstance(end, int) and start >= 0 and end >= start:
        page_ranges[code] = {
            "title": title,
            "start": start,
            "end": end
        }
    elif code:
        logger.warning(f"Invalid or missing page range for code {code} ('{title}'). Start: {start}, End: {end}. Skipping range storage.")

    sub_sections = node.get("sections", {})
    if isinstance(sub_sections, dict):
        for subcode, subnode in sub_sections.items():
            if isinstance(subnode, dict):
                _traverse_toc_for_ranges(subnode, code=subcode, page_ranges=page_ranges)
            else:
                logger.warning(f"Expected dictionary for subsection {subcode}, but got {type(subnode)}. Skipping subsection.")


def get_toc_page_ranges_from_json(toc_data: dict) -> dict:
    page_ranges = {}
    is_vision_format = False
    for code, node in toc_data.items():
        if isinstance(node, dict) and ("start_page" in node or "end_page" in node):
            is_vision_format = True
            logger.info(f"Detected potential vision TOC format key in item '{code}': start_page={node.get('start_page')}, end_page={node.get('end_page')}")
            break
            
    if is_vision_format:
        logger.info("Processing using vision TOC format logic (start_page/end_page keys expected)")
        
        def _try_convert_page(page_val, page_name, code):
            if page_val is None: return None
            if isinstance(page_val, int): return page_val
            if isinstance(page_val, str):
                try: return int(page_val)
                except ValueError: 
                    logger.warning(f"Node '{code}': Failed to convert string {page_name} '{page_val}' to int.")
                    return None
            logger.warning(f"Node '{code}': Unexpected type for {page_name}: {type(page_val)}, value: {page_val}. Treating as invalid.")
            return None

        def extract_vision_toc_ranges(code, node, page_ranges_dict, parent_code=None):
            if not isinstance(node, dict):
                logger.warning(f"Skipping non-dict node for code '{code}' (parent: {parent_code})")
                return

            title = node.get("title", "Untitled Section")
            summary = node.get("summary")
            raw_start_page = node.get("start_page")
            raw_end_page = node.get("end_page")
            item_data = {"title": title}
            if summary and isinstance(summary, str) and summary.strip():
                item_data["lastenboek_summary"] = summary.strip()

            processed_start = _try_convert_page(raw_start_page, "start_page", code)
            processed_end = _try_convert_page(raw_end_page, "end_page", code)

            page_range_found_directly = False
            if processed_start is not None and processed_end is not None:
                if processed_end >= processed_start:
                    item_data["start"] = processed_start
                    item_data["end"] = processed_end
                    page_ranges_dict[code] = item_data
                    page_range_found_directly = True
                else:
                    logger.warning(f"⚠️ Invalid range logic for '{code}': end_page ({processed_end}) < start_page ({processed_start}).")
            
            if not page_range_found_directly:
                if parent_code and parent_code in page_ranges_dict:
                    parent_data = page_ranges_dict[parent_code]
                    parent_start, parent_end = parent_data.get("start"), parent_data.get("end")
                    if parent_start is not None and parent_end is not None:
                        item_data["start"] = parent_start
                        item_data["end"] = parent_end
                        page_ranges_dict[code] = item_data
                    else: page_ranges_dict[code] = item_data
                else: page_ranges_dict[code] = item_data 

            sections = node.get("sections", {})
            if isinstance(sections, dict):
                for subcode, subnode in sections.items():
                    extract_vision_toc_ranges(subcode, subnode, page_ranges_dict, parent_code=code)

        for code, node in toc_data.items():
            extract_vision_toc_ranges(code, node, page_ranges, parent_code=None)
    else: 
        logger.info("Processing using standard TOC format logic (start/end keys expected)")
        for top_level_code, top_level_node in toc_data.items():
            if isinstance(top_level_node, dict):
                _traverse_toc_for_ranges(top_level_node, code=top_level_code, page_ranges=page_ranges)
            else:
                logger.warning(f"Standard TOC: Expected dictionary for top-level code {top_level_code}, but got {type(top_level_node)}.")
    return page_ranges

def extract_text_for_sections(toc_data: dict, pdf_reader: PdfReader, num_pages: int) -> list:
    logger.info("Starting text extraction for ToC sections.")
    processed_toc_ranges = get_toc_page_ranges_from_json(toc_data)
    sections_with_text = []
    if not processed_toc_ranges:
        logger.warning("No page ranges could be processed from ToC data. Cannot extract text.")
        return []

    for code, section_info in processed_toc_ranges.items():
        title = section_info.get("title", "Untitled Section")
        start_page = section_info.get("start")
        end_page = section_info.get("end")

        if start_page is None or end_page is None:
            logger.warning(f"Skipping text extraction for section '{code}': '{title}' due to missing page numbers.")
            sections_with_text.append({
                "code": code,
                "title": title,
                "content": "",
                "error": "Missing page numbers"
            })
            continue
        
        logger.info(f"Extracting text for section '{code}': '{title}' (Pages: {start_page}-{end_page})")
        content = extract_section_text(pdf_reader, num_pages, start_page, end_page)
        sections_with_text.append({
            "code": code,
            "title": title,
            "start_page_pdf": start_page, 
            "end_page_pdf": end_page,
            "content": content
        })
    logger.info(f"Finished text extraction for {len(sections_with_text)} sections.")
    return sections_with_text

# Vertex AI configuration constants for the second part (analysis)
PART2_VISION_ANALYSIS_MODEL = "gemini-1.5-pro-002" # Specific model for Part 2 vision task
DEFAULT_LOCATION_PART2 = "europe-west1"

GENERATION_CONFIG_PART2 = { # This config might be used by the model in Part 2
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.95,
}
SAFETY_SETTINGS_PART2 = [ # Safety settings for Part 2 model
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
]

def _initialize_vertex_model_part2(project_id_to_use: str, location: str, model_name: str):
    """Helper to initialize Vertex AI and the GenerativeModel for part 2 analysis."""
    try:
        if not project_id_to_use:
             logger.error("Project ID for Vertex AI Part 2 is essential for initialization but was not resolved.")
             raise ValueError("Project ID missing for Part 2 Vertex AI initialization after checks.")

        current_vertex_project = None
        try:
            options = vertexai.get_pipeline_options()
            if options:
                current_vertex_project = options.project
        except Exception: 
            logger.info("Vertex AI does not appear to be initialized, or project options are not retrievable.")
            current_vertex_project = None 

        if current_vertex_project != project_id_to_use:
            vertexai.init(project=project_id_to_use, location=location)
            logger.info(f"Vertex AI Initialized/Re-initialized for Part 2. Project: {project_id_to_use}, Location: {location}")
        else:
            logger.info(f"Vertex AI already initialized with the correct project {project_id_to_use}. Using existing init for Part 2.")
            
        model = GenerativeModel(
            model_name, # This will be PART2_VISION_ANALYSIS_MODEL
            generation_config=GENERATION_CONFIG_PART2, 
            safety_settings=SAFETY_SETTINGS_PART2
        )
        logger.info(f"Initialized Generative Model for Part 2: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model for Part 2 (Project: {project_id_to_use}, Model: {model_name}): {e}", exc_info=True)
        raise 

def analyze_sections_with_llm(generated_toc_data: dict,
                              pdf_path: str,
                              project_id: str = None, 
                              location: str = None):
    """
    Analyzes sections using a multimodal LLM by looking at PDF pages directly.
    """
    results = []
    
    actual_project_id_for_init = project_id
    if not actual_project_id_for_init:
        actual_project_id_for_init = os.getenv("GOOGLE_CLOUD_PROJECT")
        if actual_project_id_for_init:
            logger.info(f"LLM analysis (Part 2 Vision) using project_id from GOOGLE_CLOUD_PROJECT env var: {actual_project_id_for_init}")
        else:
            logger.error("LLM analysis (Part 2 Vision) requires a project_id (either via --project-id arg or GOOGLE_CLOUD_PROJECT env var). Neither provided.")
            processed_toc_ranges_for_error = get_toc_page_ranges_from_json(generated_toc_data) if generated_toc_data else {}
            for code, section_info in processed_toc_ranges_for_error.items():
                results.append({
                    "code": code, "title": section_info.get("title", "N/A"),
                    "start_page_pdf": section_info.get("start"), "end_page_pdf": section_info.get("end"),
                    "analysis": "Error: LLM project_id not configured for Part 2 Vision analysis.",
                    "error_llm": "LLM project_id not configured"
                })
            if not processed_toc_ranges_for_error and not generated_toc_data : # if ToC itself is empty or None
                 results.append({"code": "N/A", "title": "N/A", "analysis": "Error: LLM project_id not configured and no ToC data to process."})
            return results
        
    resolved_location = location or os.getenv("GOOGLE_CLOUD_LOCATION_PART2", DEFAULT_LOCATION_PART2)
    
    try:
        analysis_model = _initialize_vertex_model_part2(
            actual_project_id_for_init, 
            resolved_location, 
            PART2_VISION_ANALYSIS_MODEL 
        )
    except Exception as e:
        logger.error(f"Critical error: Failed to initialize LLM for Part 2 Vision analysis: {e}")
        processed_toc_ranges_for_error = get_toc_page_ranges_from_json(generated_toc_data) if generated_toc_data else {}
        for code, section_info in processed_toc_ranges_for_error.items():
            results.append({
                "code": code, "title": section_info.get("title", "N/A"),
                "start_page_pdf": section_info.get("start"), "end_page_pdf": section_info.get("end"),
                "analysis": f"Error: LLM initialization failed for Part 2 Vision analysis - {e}",
                "error_llm": f"LLM init failed: {e}"
            })
        if not processed_toc_ranges_for_error and not generated_toc_data:
            results.append({"code": "N/A", "title": "N/A", "analysis": f"Error: LLM initialization failed ({e}) and no ToC data to process."})
        return results

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_part = Part.from_data(data=pdf_bytes, mime_type="application/pdf")
        logger.info(f"PDF file {pdf_path} loaded as bytes for multimodal analysis.")
    except Exception as e:
        logger.error(f"Error loading PDF {pdf_path} for multimodal analysis: {e}")
        processed_toc_ranges_for_error = get_toc_page_ranges_from_json(generated_toc_data) if generated_toc_data else {}
        for code, section_info in processed_toc_ranges_for_error.items():
            results.append({
                "code": code, "title": section_info.get("title", "N/A"),
                "start_page_pdf": section_info.get("start"), "end_page_pdf": section_info.get("end"),
                "analysis": f"Error: Failed to load PDF for vision analysis - {e}",
                "error_llm": "PDF load error"
            })
        if not processed_toc_ranges_for_error and not generated_toc_data:
             results.append({"code": "N/A", "title": "N/A", "analysis": f"Error: Failed to load PDF ({e}) and no ToC data to process."})
        return results

    processed_toc_ranges = get_toc_page_ranges_from_json(generated_toc_data)
    if not processed_toc_ranges:
        logger.warning("No page ranges could be processed from ToC data (e.g. ToC was empty or malformed). Cannot perform vision analysis.")
        # if generated_toc_data is not None but resulted in no ranges, it implies the ToC was empty or unprocessable.
        # if generated_toc_data was None, it would have been caught by earlier checks for project_id error reporting.
        results.append({"code": "N/A", "title": "N/A", "analysis": "No processable sections found in ToC for vision analysis."})
        return results


    total_sections = len(processed_toc_ranges)
    logger.info(f"Starting vision-based analysis for {total_sections} sections.")

    for i, (code, section_info) in enumerate(processed_toc_ranges.items()):
        title = section_info.get("title", "N/A")
        start_page = section_info.get("start")
        end_page = section_info.get("end")
        llm_output = ""

        if start_page is None or end_page is None:
            logger.warning(f"Skipping vision analysis for section '{code}': '{title}' due to missing page numbers.")
            llm_output = "Skipped: Missing page numbers for vision analysis."
        else:
            section_prompt = f"""
Regarding the provided PDF document:
Analyze the content specifically on pages {start_page} through {end_page} (inclusive, 1-based global PDF page numbers).
This section is identified as Code: {code}, Title: "{title}".

Focus your analysis of these pages on:
1. Key requirements or specifications mentioned for this section.
2. Any potential ambiguities, contradictions, or missing information relevant to this section as found on these pages.
3. References to other codes or standards within this section's content on these pages.
Present the analysis clearly and concisely, perhaps as a structured summary or bullet points.
If the specified pages for this section appear to contain no relevant content for this title/code, or if the content is minimal (e.g., just a heading for this section on these pages), please state that.
Avoid analyzing content from other sections that might coincidentally appear on these pages if they are not part of "{code} - {title}".
"""
            
            logger.info(f"[{i+1}/{total_sections}] Sending section Code: {code} - Title: '{title}' (Pages: {start_page}-{end_page}) for multimodal analysis...")
            try:
                response = analysis_model.generate_content(
                    [pdf_part, section_prompt], # Send PDF and prompt together
                )
                if hasattr(response, 'text'):
                    llm_output = response.text
                elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    llm_output = f"Blocked due to: {response.prompt_feedback.block_reason}"
                elif not response.candidates or not response.candidates[0].content.parts:
                    llm_output = "No response generated or content is empty from vision model."
                else:
                    try:
                        llm_output = response.candidates[0].content.parts[0].text
                    except (AttributeError, IndexError):
                        logger.warning(f"Could not extract text from vision model response structure: {response}")
                        llm_output = "Error: Could not parse vision model response text."

            except Exception as e:
                logger.error(f"Error during multimodal analysis for section {code}: {e}", exc_info=True)
                llm_output = f"Error during multimodal analysis for section {code}: {e}"
        
        results.append({
            "code": code,
            "title": title,
            "start_page_pdf": start_page,
            "end_page_pdf": end_page,
            "analysis": llm_output
        })
        
        if i < total_sections - 1: # Avoid sleeping after the last item
            time.sleep(2.0) # Increased sleep to 2s for safety with Pro model & vision.

    logger.info(f"Finished vision-based analysis for {len(results)} sections.")
    return results

def main():
    # Default test values
    DEFAULT_PDF_PATH = "C:\\Users\\gr\\Documents\\GitHub\\ExtendedToC\\Lastenboeken\\CoordinatedArchitectlastenboek.pdf"
    DEFAULT_OUTPUT_DIR = "output"
    
    parser = argparse.ArgumentParser(description="Generate TOC from PDF, extract text, analyze sections, and output as JSON.")
    parser.add_argument("pdf_path", nargs="?", help="Path to the PDF file to process")
    parser.add_argument("-o", "--output-dir", help="Base output directory (optional)")
    parser.add_argument("-p", "--project-id", help="Google Cloud Project ID (optional)")
    parser.add_argument("-j", "--json-file", help="Path to save main TOC JSON output (optional). Other outputs will be in a timestamped subfolder.")
    args = parser.parse_args()

    # Use defaults if not provided
    pdf_path = args.pdf_path or DEFAULT_PDF_PATH
    base_output_dir = args.output_dir or DEFAULT_OUTPUT_DIR # Renamed for clarity

    if not args.pdf_path:
        print(f"No PDF path provided, using default: {pdf_path}")
    # No need to print for base_output_dir as it's a base for timestamped folders

    # Check if the default PDF exists if no path is provided
    if pdf_path == DEFAULT_PDF_PATH and not os.path.exists(DEFAULT_PDF_PATH):
        logger.warning(f"Default PDF '{DEFAULT_PDF_PATH}' not found. Creating a dummy PDF.")
        # Create a dummy PDF if it doesn't exist and it's the default, to prevent error on run
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

    # --- Step 1: Generate TOC ---
    logger.info("Initiating Step 1: TOC Generation")
    generated_toc_data, step1_out_dir = step1_generate_toc(pdf_path, base_output_dir, args.project_id)

    if not generated_toc_data:
        logger.error("TOC generation failed or returned empty. Aborting further processing.")
        return
    
    logger.info(f"Step 1 (TOC Generation) complete. Main ToC data saved in: {step1_out_dir}/chapters.json")

    # Save or print TOC based on args.json_file
    if args.json_file:
        # If a specific json_file path is given, save the main result there too.
        # The function step1_generate_toc already saves a chapters.json in its own output_dir.
        try:
            with open(args.json_file, 'w', encoding='utf-8') as f:
                json.dump(generated_toc_data, f, ensure_ascii=False, indent=2)
            print(f"Main TOC JSON also saved to specified file: {args.json_file}")
        except IOError as e:
            print(f"Error saving main TOC JSON to {args.json_file}: {e}")
    else:
        # If no specific json_file, print to console as before.
        print("\n--- Generated Table of Contents (Step 1) ---")
        print(json.dumps(generated_toc_data, ensure_ascii=False, indent=2))
        print("--- End of Generated Table of Contents ---")

    # --- Step 2: Extract Text and Analyze Sections ---
    logger.info("\nInitiating Step 2: Text Extraction and LLM Analysis")
    abs_pdf_path2 = os.path.abspath(pdf_path)
    try:
        file_size2 = os.path.getsize(abs_pdf_path2)
    except Exception:
        file_size2 = 'Unknown (file not found)'
    print(f"[STEP 2] Using PDF file: {abs_pdf_path2} (size: {file_size2} bytes)")
    logger.info(f"[STEP 2] Using PDF file: {abs_pdf_path2} (size: {file_size2} bytes)")
    try:
        with open(pdf_path, 'rb') as pdf_file_handle:
            pdf_reader_instance = PdfReader(pdf_file_handle) # PyPDF2.PdfReader is PdfReader due to import
            num_pdf_pages = len(pdf_reader_instance.pages)
        logger.info(f"Successfully loaded PDF '{pdf_path}' for section analysis ({num_pdf_pages} pages).")

        # sections_with_extracted_text = extract_text_for_sections(generated_toc_data, pdf_reader_instance, num_pdf_pages) # Removed: No longer pre-extracting text for Part 2
        # logger.info(f"Text extraction complete. Extracted text for {len(sections_with_extracted_text)} sections.")

        # if sections_with_extracted_text: # Removed
            # extracted_text_output_path = os.path.join(step1_out_dir, "extracted_section_texts.json") # Removed
            # os.makedirs(os.path.dirname(extracted_text_output_path), exist_ok=True) # Removed
            # with open(extracted_text_output_path, "w", encoding="utf-8") as f_ext: # Removed
                # json.dump(sections_with_extracted_text, f_ext, indent=2, ensure_ascii=False) # Removed
            # logger.info(f"Saved extracted section texts to '{extracted_text_output_path}'") # Removed
        # else: # Removed
            # logger.warning("No text was extracted from sections. LLM analysis might be limited or skipped.") # Removed

        # if not sections_with_extracted_text: # Condition changed
        if not generated_toc_data: # Or check if processed_toc_ranges would be empty
             logger.warning("Skipping LLM Vision analysis as ToC data is missing or empty.")
             analyzed_results = []
        else:
            logger.info(f"Starting LLM Vision analysis based on ToC sections using project ID: {args.project_id or '(env or default)'}.")
            analyzed_results = analyze_sections_with_llm(
                generated_toc_data,
                pdf_path, # Pass the pdf_path directly
                project_id=args.project_id,
                location=os.getenv("GOOGLE_CLOUD_LOCATION_PART2", DEFAULT_LOCATION_PART2)
            )
            logger.info(f"LLM Vision analysis complete. Processed {len(analyzed_results)} sections.")

        if analyzed_results:
            analysis_output_path = os.path.join(step1_out_dir, "analyzed_sections_output.json")
            os.makedirs(os.path.dirname(analysis_output_path), exist_ok=True) # Ensure dir exists
            with open(analysis_output_path, "w", encoding="utf-8") as f_an:
                json.dump(analyzed_results, f_an, indent=2, ensure_ascii=False)
            logger.info(f"Saved LLM Vision analysis results to '{analysis_output_path}'")
            
            if not args.json_file: # If main ToC was printed to console, also print analysis
                print("\n--- LLM Vision Analysis Results (Step 2) ---")
                print(json.dumps(analyzed_results, ensure_ascii=False, indent=2))
                print("--- End of LLM Vision Analysis Results ---")
        else:
            logger.warning("LLM Vision analysis produced no storable results.")

    except FileNotFoundError:
        logger.error(f"PDF file '{pdf_path}' not found during Step 2 processing.")
    except Exception as e:
        logger.error(f"Error during Step 2 (Text Extraction/LLM Analysis): {e}", exc_info=True)
    
    logger.info("\nScript execution finished.")

if __name__ == "__main__":
    main() 


    #SECOND PART STARTS HERE
    # All functions and necessary constants from the "second part" have been moved
    # to before the main() function definition to ensure they are defined when main() is called.
    # Redundant imports and the old if __name__ == "__main__" block for testing part 2
    # have been removed or commented out by previous edits.
    # The text-based analysis for Part 2 has been replaced with vision-based analysis.