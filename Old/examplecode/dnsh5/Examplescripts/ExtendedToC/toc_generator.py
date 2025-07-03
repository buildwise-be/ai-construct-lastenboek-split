import os
import sys
import json
import argparse
import logging
import base64
import time
import re
import random
from datetime import datetime

from PyPDF2 import PdfReader
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
# import fitz # fitz is not directly used in step1_generate_toc or its direct dependencies

# Configure logging with pipeline_step support
def setup_logging():
    """Set up logging configuration compatible with pipeline orchestrator"""
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        # Only set pipeline_step if it doesn't already exist to avoid KeyError
        if not hasattr(record, 'pipeline_step'):
            record.pipeline_step = 'TOC_GEN'
        return record
    logging.setLogRecordFactory(record_factory)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(pipeline_step)s - %(message)s'
    )

# Initialize logging
setup_logging()
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

# Initialize Vertex AI
try:
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if not PROJECT_ID:
        logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it before running.")
    
    vertexai.init(
        project=PROJECT_ID,
        location="europe-west1",
        api_endpoint="europe-west1-aiplatform.googleapis.com"
    )
    logger.info(f"Successfully initialized Vertex AI (Project: {PROJECT_ID})")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    raise

# Default PDF path (set to empty string or a sample path)
DEFAULT_PDF_PATH = ""

# Default model configuration
DEFAULT_MODEL_PRO = "gemini-1.5-pro-002"  # High-quality, more expensive
DEFAULT_MODEL_FLASH = "gemini-2.0-flash-001"  # Faster, cheaper

def initialize_vertex_model(system_instruction=None, project_id=None, model_name=None):
    """
    Initialize the Vertex AI Gemini model.
    
    Args:
        system_instruction (str, optional): System instruction for the model
        project_id (str, optional): Google Cloud project ID to use
        model_name (str, optional): Model name to use (default: DEFAULT_MODEL_PRO)
        
    Returns:
        vertexai.GenerativeModel: Initialized model
    """
    try:
        if project_id:
            vertexai.init(
                project=project_id,
                location="europe-west1",
                api_endpoint="europe-west1-aiplatform.googleapis.com"
            )
            logger.info(f"Reinitialized Vertex AI with project ID: {project_id}")
        
        effective_model_name = model_name or DEFAULT_MODEL_PRO
        model = GenerativeModel(
            effective_model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            system_instruction=[system_instruction] if system_instruction else None
        )
        logger.info(f"Successfully initialized Vertex AI Gemini model: {effective_model_name}")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model: {str(e)}")
        raise RuntimeError("Failed to initialize Vertex AI model")

def process_with_vertex_ai(model, prompt, post_process=False, max_retries=5):
    """
    Process a prompt with Vertex AI with advanced retry logic and rate limiting.
    
    Args:
        model: The Vertex AI model instance
        prompt (str): The prompt to process
        post_process (bool): Whether to post-process the response to extract Python code
        max_retries (int): Maximum number of retries on failure
        
    Returns:
        str: The model's response text, or extracted Python code if post_process=True
    """
    global consecutive_failures
    global last_failure_time
    
    if 'consecutive_failures' not in globals():
        consecutive_failures = 0
    
    if 'last_failure_time' not in globals():
        last_failure_time = 0
    
    if consecutive_failures > 3:
        cooldown = min(30, consecutive_failures * 5)
        time_since_last_failure = time.time() - last_failure_time
        if time_since_last_failure < cooldown:
            sleep_time = cooldown - time_since_last_failure
            logger.info(f"Rate limit cooldown: Waiting {sleep_time:.1f} seconds before next request...")
            time.sleep(sleep_time)
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                base_delay = min(30, 2 ** attempt)
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter
                logger.info(f"Retry attempt {attempt+1}/{max_retries}: Waiting {delay:.2f} seconds...")
                time.sleep(delay)
            
            response = model.generate_content(prompt)
            consecutive_failures = 0
            
            if post_process:
                try:
                    code_block_match = re.search(r'```python\s*(.*?)\s*```', response.text, re.DOTALL)
                    if code_block_match:
                        code_block = code_block_match.group(1)
                        local_vars = {}
                        exec(code_block, {}, local_vars)
                        if 'chapters' in local_vars:
                            return local_vars['chapters']
                        elif 'secties' in local_vars: # Though not used in current TOC context
                            return local_vars['secties']
                except Exception as e:
                    logger.warning(f"Failed to post-process response: {str(e)}")
                    return response.text
            
            return response.text
            
        except Exception as e:
            consecutive_failures += 1
            last_failure_time = time.time()
            error_message = str(e)
            if "429" in error_message and "Resource exhausted" in error_message:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed with rate limit (429), applying exponential backoff: {error_message}")
                else:
                    logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                    raise
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying: {error_message}")
                else:
                    logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                    raise

def post_process_results(response_text):
    """
    Extract Python dictionary from Vertex AI model response.
    
    Args:
        response_text (str): The raw response text from the model
        
    Returns:
        dict: Extracted dictionary or None if parsing fails
    """
    try:
        code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
        if code_block_match:
            code_block = code_block_match.group(1)
            local_vars = {}
            exec(code_block, {}, local_vars)
            if 'chapters' in local_vars:
                return local_vars['chapters']
            # 'secties' might be relevant if the model output format changes
            elif 'secties' in local_vars:
                return local_vars['secties'] 
    except Exception as e:
        logger.error(f"Error post-processing results: {str(e)}")
    return None

def setup_output_directory(step_name=None, base_output_dir=None, called_by_orchestrator=False):
    """
    Create an output directory structure.
    If called_by_orchestrator is True, it will use base_output_dir directly.
    Otherwise, it creates a new structure based on script name and a sequential index.
    
    Args:
        step_name (str, optional): Name of the step being executed
        base_output_dir (str, optional): Base directory for outputs
        called_by_orchestrator (bool): If True, uses base_output_dir as the final path.
        
    Returns:
        str: Path to the output directory
    """
    if called_by_orchestrator and base_output_dir:
        # Orchestrator has already prepared the specific directory for this step
        os.makedirs(base_output_dir, exist_ok=True)
        logger.info(f"Using pre-defined output directory from orchestrator: {base_output_dir}")
        return base_output_dir

    # Original logic for standalone execution or different pipeline integration
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    # Use 'output' as default if base_output_dir is not provided or not an orchestrator call
    effective_base_path = base_output_dir if base_output_dir and not called_by_orchestrator else "output"
    
    is_pipeline_dir_logic_needed = not called_by_orchestrator # Only apply old logic if not called by our orchestrator

    if is_pipeline_dir_logic_needed and base_output_dir: # Existing logic for finding pipeline_root if any
        path_parts = base_output_dir.split(os.sep)
        pipeline_root = None
        for i, part in enumerate(path_parts):
            if part.startswith("pipeline_"):
                pipeline_root = os.sep.join(path_parts[:i+1])
                logger.info(f"Found existing pipeline directory in path: {pipeline_root}")
                break
        if pipeline_root and step_name:
            # This part of the logic might still be complex if base_output_dir is deep
            # For orchestrator, this block is skipped.
            # For standalone, if base_output_dir points into an existing pipeline run,
            # it will try to create a step_name subdir or a timestamped one.
            step_specific_dir = os.path.join(pipeline_root, step_name)
            if os.path.exists(step_specific_dir):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"{step_specific_dir}_{timestamp}"
                logger.info(f"Step directory {step_specific_dir} already exists, creating timestamped one: {output_dir}")
            else:
                output_dir = step_specific_dir
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created step directory within existing pipeline: {output_dir}")
            return output_dir
        elif pipeline_root: # base_output_dir is a pipeline root, but no step_name
             # This case means the output_dir will be this pipeline_root.
             # If step_name is expected later, this might not be what's intended for non-orchestrator calls.
            logger.info(f"Using pipeline root as output directory: {pipeline_root}")
            # Ensure it exists if we are to return it.
            os.makedirs(pipeline_root, exist_ok=True)
            return pipeline_root


    # Fallback to creating a new pipeline_script_run_XXX directory structure
    # This will be used for standalone runs, or if orchestrator doesn't provide base_output_dir
    index = 1
    run_prefix = f"pipeline_{script_name}_run_"
    if os.path.exists(effective_base_path):
        existing_dirs = [d for d in os.listdir(effective_base_path) 
                        if os.path.isdir(os.path.join(effective_base_path, d)) 
                        and d.startswith(run_prefix)]
        indices = []
        for dir_name in existing_dirs:
            try:
                idx_str = dir_name[len(run_prefix):]
                indices.append(int(idx_str))
            except ValueError:
                continue
        if indices:
            most_recent_index = max(indices)
            # If it's a new run (no step_name initially) or continuing the most recent.
            # For step-specific calls later, it should use the existing run's index.
            index = most_recent_index if step_name else most_recent_index + 1 
                                                             
    run_id_dir_name = f"{run_prefix}{index:03d}"
    final_output_dir_base = os.path.join(effective_base_path, run_id_dir_name)

    if step_name:
        output_dir = os.path.join(final_output_dir_base, step_name)
    else: # No step_name, creating the root of a new run
        output_dir = final_output_dir_base
            
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory created/ensured: {output_dir}")
    return output_dir

def step1_generate_toc(pdf_path, output_base_dir=None, called_by_orchestrator=False, model_name=None):
    """
    Generate a table of contents (TOC) for the given PDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_base_dir (str, optional): Base directory for outputs. 
                                         If called_by_orchestrator, this is the exact dir.
        called_by_orchestrator (bool): Passed to setup_output_directory.
        model_name (str, optional): Model name to use (default: DEFAULT_MODEL_PRO)
        
    Returns:
        tuple: (chapters_data, output_dir) 
               chapters_data: the dictionary of chapters
               output_dir: the actual directory path where outputs (chapters.json) were saved.
    """
    logger.info("=" * 50)
    logger.info("STEP 1: Generating Table of Contents...")
    logger.info(f"Called by orchestrator: {called_by_orchestrator}, Output base dir: {output_base_dir}")
    effective_model_name = model_name or DEFAULT_MODEL_PRO
    logger.info(f"Using model: {effective_model_name}")
    logger.info("=" * 50)
    
    # If called by orchestrator, output_base_dir is the *exact* directory to use.
    # setup_output_directory will handle this.
    # The step_name "step1_toc" is implicit for this function;
    # if called by orchestrator, output_base_dir IS the step1_toc specific dir.
    # If standalone, setup_output_directory will create a "step1_toc" subfolder.
    toc_output_dir = setup_output_directory(
        step_name="step1_toc", # Used by standalone logic
        base_output_dir=output_base_dir, 
        called_by_orchestrator=called_by_orchestrator
    )
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    logger.info(f"Processing PDF file: {pdf_path}")
    
    system_instruction = """
You are given a technical specifications PDF document in the construction sector ("Samengevoegdlastenboek") that can be a concatenation of multiple different documents, each with their own internal page numbering.

The document contains numbered chapters in two formats:
1. Main chapters: formatted as "XX. TITLE" (e.g., "00. ALGEMENE BEPALINGEN")
2. Sections: formatted as "XX.YY TITLE" (e.g., "01.10 SECTIETITEL") or formatted as "XX.YY.ZZ TITLE" (e.g., "01.10.01 SECTIETITEL") and even "XX.YY.ZZ.AA TITLE" (e.g., "01.10.01.01 SECTIETITEL")

Your task is to identify both main chapters (00-93) and their sections, using the GLOBAL PDF page numbers (not the internal page numbers that appear within each document section).

For each main chapter and section:
1. Record the precise numbering (e.g., "00" or "01.10")
2. Record the accurate starting page number based on the GLOBAL PDF page count (starting from 1 for the first page)
3. Record the accurate ending page number (right before the next chapter/section starts)
4. Summarize the content of the chapter and sections in 10 keywords or less to help with the categorization process

IMPORTANT: 
- Use the actual PDF page numbers (starting from 1 for the first page of the entire PDF)
- IGNORE any page numbers printed within the document itself
- The page numbers in any table of contents (inhoudstafel) are UNRELIABLE - do not use them
- Determine page numbers by finding where each chapter actually begins and ends in the PDF
- Be EXTREMELY thorough in identifying ALL sections and subsections, including those with patterns like XX.YY.ZZ.AA
- Don't miss any chapter or section - this is critical for accurate document processing

Final output should be a nested Python dictionary structure:
```
chapters = {
    "00": {
        "start": start_page,
        "end": end_page,
        "title": "CHAPTER TITLE",
        "sections": {
            'XX.YY': {'start': start_page, 'end': end_page, 'title': 'section title'},
            'XX.YY.ZZ': {'start': start_page, 'end': end_page, 'title': 'subsection title'},
            'XX.YY.ZZ.AA': {'start': start_page, 'end': end_page, 'title': 'sub-subsection title'}
        }
    }
}
```
"""
    
    try:
        model = initialize_vertex_model(system_instruction, model_name=effective_model_name) # model for system instruction
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
        # pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8") # Not used in chat.send_message
        
        multimodal_model = GenerativeModel( # Model for PDF processing
            effective_model_name, 
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        logger.info("PDF file loaded for Vertex AI")
    except Exception as e:
        logger.error(f"Error preparing PDF for Vertex AI: {str(e)}")
        raise
    
    page_batch_size = 50 
    page_batches = []
    overlap = 5 
    
    for start_page_num in range(1, total_pages + 1, page_batch_size - overlap):
        end_page_num = min(start_page_num + page_batch_size - 1, total_pages)
        if end_page_num - start_page_num < 5 and len(page_batches) > 0:
            page_batches[-1] = (page_batches[-1][0], end_page_num)
            break
        page_batches.append((start_page_num, end_page_num))
    
    logger.info(f"Processing PDF in {len(page_batches)} page batches with size {page_batch_size} and overlap {overlap}")
    
    page_batch_results = {}
    
    try:
        initial_prompt = f'''
I'll be analyzing a construction-specific PDF document with {total_pages} pages. First, I need you to provide me with a basic structure of this document.

The PDF file is a technical construction document in Dutch/Flemish called a "lastenboek" (specification document).
It contains chapters numbered like "XX. TITLE" (e.g., "00. ALGEMENE BEPALINGEN") and sections like "XX.YY TITLE".

Based on the PDF I'm providing, identify the main chapters (like 00, 01, 02, etc.) and their approximate page ranges.
This will help me analyze the document in more detail with subsequent questions.

Format the response as a simple outline with page ranges.
'''
        
        chat = multimodal_model.start_chat()
        logger.info("Requesting initial document structure analysis...")
        response = chat.send_message(
            [
                initial_prompt,
                Part.from_data(data=pdf_bytes, mime_type="application/pdf")
            ]
        )
        logger.info(f"Received initial document structure: {response.text[:200]}...") # Log snippet
        
        rate_limit_delay = 2.0
        error_backoff_multiplier = 1.0
        
        for batch_idx, (start_page, end_page) in enumerate(page_batches):
            if batch_idx > 0:
                delay = rate_limit_delay * error_backoff_multiplier
                logger.info(f"Rate limiting: Waiting {delay:.2f} seconds before processing next batch...")
                time.sleep(delay)
                
            logger.info(f"Processing page batch {batch_idx+1}/{len(page_batches)}: pages {start_page}-{end_page}")
            
            comprehensive_note = ""
            if batch_idx < 3:
                comprehensive_note = "This is one of the first batches, so pay extra attention to identify the document structure and early chapters."
            elif batch_idx >= len(page_batches) - 3:
                comprehensive_note = "This is one of the final batches, so pay extra attention to identify any closing chapters or sections."

            page_prompt = f'''
Analyze pages {start_page}-{end_page} of this PDF document and identify any chapters or sections 
that appear within these pages.

{comprehensive_note}

IMPORTANT INSTRUCTIONS:
- This document uses chapter numbering like "XX. TITLE" (e.g. "00. ALGEMENE BEPALINGEN")
- Sections are formatted as "XX.YY TITLE" (e.g., "01.10 SECTIETITEL")
- Subsections may be formatted as "XX.YY.ZZ TITLE" or "XX.YY.ZZ.AA TITLE"
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
    "XX": {{\'start\': X, \'end\': Y, \'title\': \'CHAPTER TITLE\', \'sections\': {{
        \'XX.YY\': {{\'start\': X, \'end\': Y, \'title\': \'section title\'}},
        \'XX.YY.ZZ\': {{\'start\': X, \'end\': Y, \'title\': \'subsection title\'}}
    }}}}
}}
```

Include ONLY chapters or sections that appear within pages {start_page}-{end_page}.
'''
            
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
                            if chapter_data.get('start', float('inf')) < existing.get('start', float('inf')): # handle missing keys
                                existing['start'] = chapter_data['start']
                            if chapter_data.get('end', float('-inf')) > existing.get('end', float('-inf')): # handle missing keys
                                existing['end'] = chapter_data['end']
                            
                            if 'sections' in chapter_data:
                                if 'sections' not in existing:
                                    existing['sections'] = {}
                                for section_id, section_data in chapter_data['sections'].items():
                                    if section_id not in existing['sections']:
                                        existing['sections'][section_id] = section_data
                                    else:
                                        existing_section = existing['sections'][section_id]
                                        if section_data.get('start', float('inf')) < existing_section.get('start', float('inf')):
                                            existing_section['start'] = section_data['start']
                                        if section_data.get('end', float('-inf')) > existing_section.get('end', float('-inf')):
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
    
    logger.info("Performing final cleanup and boundary adjustments...")
    
    # Ensure all chapter_data has 'start' and 'sections' before sorting
    temp_chapters_for_sorting = []
    for k, v_ch in page_batch_results.items():
        if isinstance(v_ch, dict) and 'start' in v_ch:
            if 'sections' not in v_ch: # Ensure sections key exists
                v_ch['sections'] = {}
            temp_chapters_for_sorting.append((k,v_ch))
        else:
            logger.warning(f"Skipping chapter {k} in sorting due to missing 'start' or not being a dict: {v_ch}")

    sorted_chapters = sorted(temp_chapters_for_sorting, key=lambda x: x[1]['start'])
    
    for i in range(len(sorted_chapters) - 1):
        current_ch_id, current_ch = sorted_chapters[i]
        next_ch_id, next_ch = sorted_chapters[i+1]
        
        if current_ch.get('end', float('-inf')) < next_ch.get('start', float('inf')) -1:
            current_ch['end'] = next_ch['start'] - 1
            logger.info(f"Adjusted end page of chapter {current_ch_id} to {current_ch['end']}")
        
        if 'sections' in current_ch and current_ch['sections']:
            # Ensure all section_data has 'start' before sorting
            temp_sections_for_sorting = []
            for sk, sv_sec in current_ch['sections'].items():
                 if isinstance(sv_sec, dict) and 'start' in sv_sec:
                     temp_sections_for_sorting.append((sk, sv_sec))
                 else:
                    logger.warning(f"Skipping section {sk} in sorting due to missing 'start' or not being a dict: {sv_sec}")
            
            sorted_sections = sorted(temp_sections_for_sorting, key=lambda x: x[1]['start'])
            
            for j in range(len(sorted_sections) - 1):
                current_sec_id, current_sec = sorted_sections[j]
                next_sec_id, next_sec = sorted_sections[j+1]
                if current_sec.get('end', float('-inf')) < next_sec.get('start', float('inf')) - 1:
                    current_sec['end'] = next_sec['start'] - 1
                    logger.info(f"Adjusted end page of section {current_sec_id} to {current_sec['end']}")
            
            if sorted_sections:
                last_sec_id, last_sec = sorted_sections[-1]
                if last_sec.get('end', float('-inf')) < current_ch.get('end', float('-inf')):
                    last_sec['end'] = current_ch['end']
                    logger.info(f"Adjusted end page of last section {last_sec_id} to {last_sec['end']}")
            
            for sec_id, sec_data in sorted_sections:
                current_ch['sections'][sec_id] = sec_data

    for ch_id, ch_data in sorted_chapters:
        page_batch_results[ch_id] = ch_data
        
    chapters = page_batch_results
    
    def validate_chapters(chapters_dict):
        validated = {}
        max_page_val = 0
        for chapter_key, data_val in chapters_dict.items():
            if isinstance(data_val, dict) and 'end' in data_val and isinstance(data_val['end'], int) and data_val['end'] > max_page_val:
                max_page_val = data_val['end']
        
        reasonable_max_page = max(max_page_val, total_pages, 1000) 
        
        for chapter_key, data_val in chapters_dict.items():
            if not data_val or not isinstance(data_val, dict): continue
            if ('start' not in data_val or 'end' not in data_val or 
                not isinstance(data_val['start'], int) or not isinstance(data_val['end'], int) or
                data_val['start'] < 1 or data_val['end'] > reasonable_max_page or data_val['start'] > data_val['end']):
                logger.warning(f"Chapter {chapter_key} has invalid page numbers: {data_val.get('start', 'missing')}-{data_val.get('end', 'missing')}")
                continue
            if 'sections' in data_val and isinstance(data_val['sections'], dict):
                valid_sections = {}
                for section_id_key, section_data_val in data_val['sections'].items():
                    if not isinstance(section_data_val, dict): continue
                    if ('start' not in section_data_val or 'end' not in section_data_val or 
                        not isinstance(section_data_val['start'], int) or not isinstance(section_data_val['end'], int) or
                        section_data_val['start'] < 1 or section_data_val['end'] > reasonable_max_page or 
                        section_data_val['start'] > section_data_val['end']):
                        logger.warning(f"Section {section_id_key} has invalid page numbers: {section_data_val.get('start', 'missing')}-{section_data_val.get('end', 'missing')}")
                        continue
                    valid_sections[section_id_key] = section_data_val
                data_val['sections'] = valid_sections
            validated[chapter_key] = data_val
        return validated
        
    validated_chapters = validate_chapters(chapters)
    
    chapters_json_path = os.path.join(toc_output_dir, "chapters.json")
    with open(chapters_json_path, 'w', encoding='utf-8') as f:
        json.dump(validated_chapters, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved chapters data to {chapters_json_path}")
    
    report_lines = ["# Table of Contents", ""]
    # Sort validated_chapters by chapter number (as string, but should be numeric for main chapters)
    # We need to handle cases where chapter_num might not be purely numeric for sorting.
    # A robust sort would involve converting to a sortable key, e.g., tuple of ints.
    def chapter_sort_key(item):
        num_str = item[0]
        parts = num_str.split('.')
        try:
            # Return tuple of integers for numeric sorting, padded to ensure consistent length
            numeric_parts = tuple(int(p) for p in parts)
            # Pad with zeros to ensure consistent comparison (e.g., "1" becomes (1, 0, 0, 0))
            padded_parts = numeric_parts + (0,) * (10 - len(numeric_parts))  # pad to length 10
            return (0, padded_parts)  # (0, tuple) for numeric sorting first
        except ValueError: 
            # If not purely numeric parts, sort as string after numeric ones
            # Ensure consistent comparison by padding string results too
            return (1, num_str.ljust(50))  # (1, padded_string) for string sorting after numeric ones

    sorted_validated_chapters = sorted(validated_chapters.items(), key=chapter_sort_key)

    for chapter_num_key, chapter_data_val in sorted_validated_chapters:
        if chapter_data_val and isinstance(chapter_data_val, dict) and 'title' in chapter_data_val: # Check data integrity
            report_lines.append(f"## Chapter {chapter_num_key}: {chapter_data_val.get('title','N/A')} (Pages {chapter_data_val.get('start','N/A')}-{chapter_data_val.get('end','N/A')})")
            report_lines.append("")
            
            # Sort sections as well
            if 'sections' in chapter_data_val and isinstance(chapter_data_val['sections'], dict):
                sorted_sections_list = sorted(chapter_data_val['sections'].items(), key=chapter_sort_key)
                for section_id_key, section_data_val in sorted_sections_list:
                     if section_data_val and isinstance(section_data_val, dict) and 'title' in section_data_val:
                        report_lines.append(f"### {section_id_key}: {section_data_val.get('title','N/A')} (Pages {section_data_val.get('start','N/A')}-{section_data_val.get('end','N/A')})")
            report_lines.append("")
    
    report_file = os.path.join(toc_output_dir, "toc_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\\n".join(report_lines))
    logger.info(f"TOC report saved to {report_file}")
    
    return validated_chapters, toc_output_dir

def main_cli():
    parser = argparse.ArgumentParser(description="Generate Table of Contents from a PDF file.")
    parser.add_argument("pdf_path", nargs="?", default=r"C:\Users\gr\Documents\GitHub\ExtendedToC\Lastenboeken\cathlabarchitectlb.pdf", help="Path to the PDF file to process.")
    parser.add_argument("-o", "--output-dir", help="Base directory for output files (optional, defaults to 'output').")
    parser.add_argument("--model", choices=['pro', 'flash'], default='pro', 
                        help="Model to use: 'pro' for gemini-1.5-pro-002 (default), 'flash' for gemini-2.0-flash-001 (cheaper/faster)")
    
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    output_base_dir = args.output_dir if args.output_dir else "output" # Default output to "output" subdirectory
    
    # Map model argument to actual model name
    model_name = DEFAULT_MODEL_PRO if args.model == 'pro' else DEFAULT_MODEL_FLASH
    logger.info(f"Selected model: {model_name}")

    if not pdf_path or not os.path.isfile(pdf_path):
        logger.error(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)

    try:
        # When called from CLI, it's a standalone run, so called_by_orchestrator is False.
        chapters, toc_output_dir_result = step1_generate_toc(pdf_path, output_base_dir, called_by_orchestrator=False, model_name=model_name)
        logger.info(f"TOC generation complete. Output in: {toc_output_dir_result}")
        logger.info(f"Found {len(chapters)} main chapters.")
    except Exception as e:
        logger.error(f"An error occurred during TOC generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_cli() 