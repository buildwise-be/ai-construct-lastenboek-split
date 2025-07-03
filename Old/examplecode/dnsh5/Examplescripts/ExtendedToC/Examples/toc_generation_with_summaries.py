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
            "gemini-1.5-pro-002", # Consider if this model is best for summary, or if the multimodal one should be used here too
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
        # Enhanced regex to handle potential newlines within the code block more gracefully
        code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL | re.MULTILINE)
        if code_block_match:
            code_block = code_block_match.group(1).strip()
            # Ensure the code block is not empty
            if not code_block:
                logger.warning("Extracted empty code block.")
                return None
            local_vars = {}
            exec(code_block, {}, local_vars) # Be cautious with exec on untrusted input
            if 'chapters' in local_vars:
                return local_vars['chapters']
            elif 'secties' in local_vars: # 'secties' might be a typo, consistently use 'chapters'
                logger.warning("Found 'secties' in response, processing as 'chapters'.")
                return local_vars['secties']
            else:
                logger.warning("Neither 'chapters' nor 'secties' found in the extracted code block.")
                return None

    except Exception as e:
        logger.error(f"Error post-processing results: {str(e)}, Response text was: {response_text[:500]}...") # Log part of response
    return None

# Main TOC generation function
def step1_generate_toc_with_summaries(pdf_path, output_base_dir=None, project_id=None):
    logger.info("=" * 50)
    logger.info("STEP 1: Generating Table of Contents with Summaries...")
    logger.info("=" * 50)
    output_dir = setup_output_directory("step1_toc_summaries", output_base_dir)
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    logger.info(f"Processing PDF file: {pdf_path}")

    system_instruction = """You are given a technical specifications PDF document in the construction sector (\"Samengevoegdlastenboek\") that can be a concatenation of multiple different documents, each with their own internal page numbering.

The document contains numbered chapters in two formats:
1. Main chapters: formatted as \"XX. TITLE\" (e.g., \"00. ALGEMENE BEPALINGEN\")
2. Sections: formatted as \"XX.YY TITLE\" (e.g., \"01.10 SECTIETITEL\") or formatted as \"XX.YY.ZZ TITLE\" (e.g., \"01.10.01 SECTIETITEL\") and even \"XX.YY.ZZ.AA TITLE\" (e.g., \"01.10.01.01 SECTIETITEL\")

Your task is to identify both main chapters (00-93) and their sections, using the GLOBAL PDF page numbers (not the internal page numbers that appear within each document section).

For each main chapter and section:
1. Record the precise numbering (e.g., \"00\" or \"01.10\")
2. Record the accurate starting page number based on the GLOBAL PDF page count (starting from 1 for the first page)
3. Record the accurate ending page number (right before the next chapter/section starts)
4. Record the full title as it appears in the document.
5. Provide a concise summary of the chapter or section's content. This summary should be 1-2 sentences or a list of up to 10 keywords.

IMPORTANT:
- Use the actual PDF page numbers (starting from 1 for the first page of the entire PDF)
- IGNORE any page numbers printed within the document itself
- The page numbers in any table of contents (inhoudstafel) are UNRELIABLE - do not use them
- Determine page numbers by finding where each chapter actually begins and ends in the PDF
- Be EXTREMELY thorough in identifying ALL sections and subsections, including those with patterns like XX.YY.ZZ.AA
- Don't miss any chapter or section - this is critical for accurate document processing

Final output should be a nested Python dictionary structure:
```python
chapters = {
    "00": {
        "start": start_page,
        "end": end_page,
        "title": "CHAPTER TITLE",
        "summary": "Concise summary or keywords for the chapter.",
        "sections": {
            'XX.YY': {'start': start_page, 'end': end_page, 'title': 'section title', 'summary': 'Summary for section XX.YY'},
            'XX.YY.ZZ': {'start': start_page, 'end': end_page, 'title': 'subsection title', 'summary': 'Summary for subsection XX.YY.ZZ'},
            'XX.YY.ZZ.AA': {'start': start_page, 'end': end_page, 'title': 'sub-subsection title', 'summary': 'Summary for sub-subsection XX.YY.ZZ.AA'}
        }
    }
}
```
"""
    # Initialize the model that will be used for chat; system instruction is not directly used by multimodal model's start_chat
    # Instead, the instructions are part of each prompt.
    try:
        # The multimodal model is used for PDF interaction, so we initialize it here.
        # The text-only model 'gemini-1.5-pro-002' was previously initialized but system_instruction is better handled with multimodal directly.
        multimodal_model = GenerativeModel(
            "gemini-1.5-pro-002", # Explicitly use the multimodal model version
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
            # System instructions are part of the prompt for send_message with multimodal
        )
        logger.info("Successfully initialized multimodal Vertex AI Gemini model")
    except Exception as e:
        logger.error(f"Error initializing multimodal Vertex AI model: {str(e)}")
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
        # pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8") # Not strictly needed if passing bytes directly
        logger.info("PDF file loaded for Vertex AI")
    except Exception as e:
        logger.error(f"Error preparing PDF for Vertex AI: {str(e)}")
        raise

    page_batch_size = 30 # Reduced batch size for potentially more detailed summary generation per batch
    overlap = 3 # Reduced overlap slightly
    page_batches = []
    for start_page in range(1, total_pages + 1, page_batch_size - overlap):
        end_page = min(start_page + page_batch_size - 1, total_pages)
        if end_page - start_page < 5 and len(page_batches) > 0: # Avoid tiny trailing batches
            page_batches[-1] = (page_batches[-1][0], end_page) # Extend the last batch
            break
        page_batches.append((start_page, end_page))
    logger.info(f"Processing PDF in {len(page_batches)} page batches with size {page_batch_size} and overlap {overlap}")

    page_batch_results = {}
    chat = multimodal_model.start_chat() # Start chat once

    try:
        # Send the system instruction as the first part of the conversation context.
        # Forcing the first message to contain the overall system instruction and the PDF.
        initial_prompt_for_context = f"""{system_instruction}

I am providing a PDF document. Please analyze it according to the instructions above.
I will then ask you to process specific page batches.
This initial message is to set the context and provide the document.
The document has {total_pages} pages.
Acknowledge that you have received the document and instructions.
"""
        # Send initial message with PDF to establish context.
        initial_response = chat.send_message([
            initial_prompt_for_context,
            Part.from_data(data=pdf_bytes, mime_type="application/pdf")
        ])
        logger.info(f"Initial context-setting response: {initial_response.text[:200]}...") # Log part of the response

        rate_limit_delay = 3.0 # Slightly increased base delay
        error_backoff_multiplier = 1.0

        for batch_idx, (start_page, end_page) in enumerate(page_batches):
            if batch_idx > 0:
                delay = rate_limit_delay * error_backoff_multiplier
                logger.info(f"Rate limiting: Waiting {delay:.2f} seconds before processing next batch...")
                time.sleep(delay)

            logger.info(f"Processing page batch {batch_idx+1}/{len(page_batches)}: pages {start_page}-{end_page}")

            if batch_idx < 3:
                comprehensive_note = "This is one of the first batches, so pay extra attention to identify the document structure and early chapters/sections, including their summaries."
            elif batch_idx >= len(page_batches) - 3:
                comprehensive_note = "This is one of the final batches, so pay extra attention to identify any closing chapters or sections and their summaries."
            else:
                comprehensive_note = ""

            page_prompt = f"""
            Now, analyze pages {start_page}-{end_page} of the PDF document I provided earlier.
            Identify any chapters or sections that appear primarily within these pages.
            {comprehensive_note}

            REMEMBER THE IMPORTANT INSTRUCTIONS (from the initial prompt):
            - Chapter numbering: \"XX. TITLE\"
            - Section numbering: \"XX.YY TITLE\", \"XX.YY.ZZ TITLE\", \"XX.YY.ZZ.AA TITLE\"
            - Focus ONLY on pages {start_page} through {end_page} for identifying where entities START or END.
            - Use GLOBAL PDF page numbers (1-indexed).
            - IGNORE printed page numbers within the document.
            - For each chapter/section: record exact start page, end page, full title, and a concise summary (1-2 sentences or up to 10 keywords).
            - End page: page right before the next chapter/section begins.
            - If an item starts in this range but continues beyond page {end_page}, set its end page as {end_page} for now.
            - If an item ends in this range but started before page {start_page}, set its start page as {start_page} for now.
            - Be thorough.

            Format the output ONLY as a Python dictionary like this (ensure the dictionary is complete and valid Python code):
            ```python
            chapters = {{
                # Example for a chapter starting in this page range
                "XX": {{
                    'start': {start_page}, # or actual start if later in batch
                    'end': {end_page},   # or actual end if earlier in batch, or {end_page} if it continues
                    'title': 'FULL CHAPTER TITLE HERE',
                    'summary': 'Concise summary or keywords for chapter XX.',
                    'sections': {{
                        # Example for a section
                        'XX.YY': {{
                            'start': ..., 'end': ..., 'title': 'Full section title XX.YY',
                            'summary': 'Summary for section XX.YY'
                        }},
                        # Example for a subsection
                        'XX.YY.ZZ': {{
                            'start': ..., 'end': ..., 'title': 'Full subsection title XX.YY.ZZ',
                            'summary': 'Summary for subsection XX.YY.ZZ'
                        }}
                        # Add other sections/subsections found in this page range
                    }}
                }}
                # Add other main chapters found in this page range
            }}
            ```
            Include ONLY chapters or sections whose content significantly appears or starts/ends within pages {start_page}-{end_page}.
            If no new chapters or sections are identified in this specific page range, return an empty dictionary: `chapters = {{}}`.
            """
            try:
                batch_response = chat.send_message(page_prompt) # No need to resend PDF
                page_batch_dict = post_process_results(batch_response.text)

                if page_batch_dict:
                    logger.info(f"Found data in pages {start_page}-{end_page}: {len(page_batch_dict)} root items.")
                    for chapter_id, chapter_data in page_batch_dict.items():
                        if not isinstance(chapter_data, dict):
                            logger.warning(f"Skipping invalid chapter data for {chapter_id}: {chapter_data}")
                            continue

                        if chapter_id not in page_batch_results:
                            page_batch_results[chapter_id] = chapter_data
                        else:
                            existing = page_batch_results[chapter_id]
                            existing['start'] = min(existing.get('start', float('inf')), chapter_data.get('start', float('inf')))
                            existing['end'] = max(existing.get('end', float('-inf')), chapter_data.get('end', float('-inf')))
                            if chapter_data.get('title') and (not existing.get('title') or len(chapter_data['title']) > len(existing['title'])):
                                existing['title'] = chapter_data['title']
                            if chapter_data.get('summary') and (not existing.get('summary') or len(chapter_data['summary']) > len(existing.get('summary',''))):
                                existing['summary'] = chapter_data['summary']

                            if 'sections' in chapter_data and isinstance(chapter_data['sections'], dict):
                                if 'sections' not in existing or not isinstance(existing.get('sections'), dict):
                                    existing['sections'] = {}
                                for section_id, section_data in chapter_data['sections'].items():
                                    if not isinstance(section_data, dict):
                                        logger.warning(f"Skipping invalid section data for {section_id} in {chapter_id}")
                                        continue
                                    if section_id not in existing['sections']:
                                        existing['sections'][section_id] = section_data
                                    else:
                                        existing_section = existing['sections'][section_id]
                                        existing_section['start'] = min(existing_section.get('start', float('inf')), section_data.get('start', float('inf')))
                                        existing_section['end'] = max(existing_section.get('end', float('-inf')), section_data.get('end', float('-inf')))
                                        if section_data.get('title') and \
                                           (not existing_section.get('title') or len(section_data['title']) > len(existing_section['title'])):
                                            existing_section['title'] = section_data['title']
                                        if section_data.get('summary') and \
                                           (not existing_section.get('summary') or len(section_data['summary']) > len(existing_section.get('summary',''))):
                                            existing_section['summary'] = section_data['summary']
                else:
                    logger.info(f"No structured data (or empty dict) returned for pages {start_page}-{end_page}. Response: {batch_response.text[:200]}...")
                error_backoff_multiplier = max(1.0, error_backoff_multiplier * 0.9) # Decrease slightly on success
            except Exception as e:
                logger.error(f"Error processing batch {batch_idx+1} (pages {start_page}-{end_page}): {str(e)}. Response text: {batch_response.text[:500] if 'batch_response' in locals() else 'N/A'}")
                error_backoff_multiplier = min(error_backoff_multiplier * 2.0, 16.0) # Increase, with a cap
                logger.warning(f"Increasing rate limit delay multiplier to {error_backoff_multiplier:.2f} due to error.")
    except Exception as e:
        logger.error(f"Error processing with Vertex AI: {str(e)}")
        raise

    # Sort and adjust page numbers
    # Ensure 'start' key exists and is int before sorting, default to high number if missing
    def get_start_page(item):
        if isinstance(item[1], dict) and isinstance(item[1].get('start'), int):
            return item[1]['start']
        return float('inf') # Push items with no/invalid start page to the end

    sorted_chapters = sorted([(k, v) for k, v in page_batch_results.items() if isinstance(v,dict)], key=get_start_page)

    for i in range(len(sorted_chapters) - 1):
        current_ch_id, current_ch = sorted_chapters[i]
        next_ch_id, next_ch = sorted_chapters[i+1]
        # Ensure 'end' and 'start' are valid before comparison
        if isinstance(current_ch.get('end'), int) and isinstance(next_ch.get('start'), int):
            if current_ch['end'] >= next_ch['start']: # Overlap or touch
                 # Option 1: Adjust current_ch end to be before next_ch start
                current_ch['end'] = next_ch['start'] - 1
                logger.info(f"Adjusted end page of chapter {current_ch_id} to {current_ch['end']} to prevent overlap with {next_ch_id}")
            # No explicit adjustment if there's a gap current_ch['end'] < next_ch['start'] -1, assuming model is mostly correct

        if 'sections' in current_ch and isinstance(current_ch['sections'], dict) and current_ch['sections']:
            sorted_sections = sorted([(k, v) for k, v in current_ch['sections'].items() if isinstance(v, dict)], key=get_start_page)
            for j in range(len(sorted_sections) - 1):
                current_sec_id, current_sec = sorted_sections[j]
                next_sec_id, next_sec = sorted_sections[j+1]
                if isinstance(current_sec.get('end'), int) and isinstance(next_sec.get('start'), int):
                    if current_sec['end'] >= next_sec['start']:
                        current_sec['end'] = next_sec['start'] - 1
                        logger.info(f"Adjusted end page of section {current_sec_id} to {current_sec['end']} to prevent overlap with {next_sec_id}")

            if sorted_sections: # Adjust last section's end page to chapter's end page
                last_sec_id, last_sec = sorted_sections[-1]
                if isinstance(last_sec.get('end'), int) and isinstance(current_ch.get('end'), int):
                    if last_sec['end'] < current_ch['end']:
                        last_sec['end'] = current_ch['end']
                        logger.info(f"Adjusted end page of last section {last_sec_id} in {current_ch_id} to chapter end {current_ch['end']}")
                    elif last_sec['end'] > current_ch['end']: # Section should not exceed chapter
                        last_sec['end'] = current_ch['end']
                        logger.warning(f"Trimmed end page of last section {last_sec_id} in {current_ch_id} to chapter end {current_ch['end']}")


            # Update the main dictionary with sorted/adjusted sections
            current_ch['sections'] = {k:v for k,v in sorted_sections}


    # Update the main results dictionary with potentially modified chapter data
    final_chapters = {k:v for k,v in sorted_chapters}

    def validate_and_clean_structure(item_id, item_data, parent_max_page, parent_min_page=1):
        if not isinstance(item_data, dict):
            logger.warning(f"Invalid data for {item_id}, expected dict, got {type(item_data)}. Skipping.")
            return None

        # Validate/default title and summary
        item_data['title'] = item_data.get('title', 'TITLE MISSING')
        item_data['summary'] = item_data.get('summary', 'Summary missing.')

        # Validate page numbers
        start = item_data.get('start')
        end = item_data.get('end')
        valid_pages = True
        if not (isinstance(start, int) and isinstance(end, int) and parent_min_page <= start <= end <= parent_max_page):
            logger.warning(f"Item {item_id} has invalid/out-of-bounds page numbers: start='{start}', end='{end}'. Parent range: {parent_min_page}-{parent_max_page}. Removing item.")
            valid_pages = False
            return None # Remove item if pages are fundamentally flawed

        if 'sections' in item_data and isinstance(item_data['sections'], dict):
            valid_sections = {}
            for section_id, section_data in item_data['sections'].items():
                cleaned_section = validate_and_clean_structure(section_id, section_data, item_data['end'], item_data['start'])
                if cleaned_section:
                    valid_sections[section_id] = cleaned_section
            item_data['sections'] = valid_sections
        elif 'sections' in item_data: # if 'sections' exists but is not a dict
            logger.warning(f"Sections for {item_id} is not a dictionary, removing. Type: {type(item_data['sections'])}")
            del item_data['sections']


        return item_data

    # Overall validation pass
    validated_chapters_final = {}
    for ch_id, ch_data in final_chapters.items():
        cleaned_chapter = validate_and_clean_structure(ch_id, ch_data, total_pages)
        if cleaned_chapter:
            validated_chapters_final[ch_id] = cleaned_chapter
    
    # Re-sort after potential removals from validation
    validated_chapters_final_sorted = dict(sorted(validated_chapters_final.items(), key=lambda item: get_start_page(item)))


    chapters_json_path = os.path.join(output_dir, "chapters_with_summaries.json")
    with open(chapters_json_path, 'w', encoding='utf-8') as f:
        json.dump(validated_chapters_final_sorted, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved chapters with summaries to {chapters_json_path}")
    return validated_chapters_final_sorted, output_dir

def main():
    DEFAULT_PDF_PATH = r"C:\Users\gr\Documents\GitHub\ExtendedToC\Lastenboeken\cathlabarchitectlb.pdf"
    DEFAULT_OUTPUT_DIR = "output_summaries" # Changed default output dir
    import argparse # Import here as it's specific to main execution
    parser = argparse.ArgumentParser(description="Generate TOC with summaries from PDF and output as JSON.")
    parser.add_argument("pdf_path", nargs="?", help="Path to the PDF file to process")
    parser.add_argument("-o", "--output-dir", help="Output directory (optional)")
    parser.add_argument("-p", "--project-id", help="Google Cloud Project ID (optional)")
    parser.add_argument("-j", "--json-file", help="Path to save JSON output (optional, overrides default in output_dir)")
    args = parser.parse_args()

    pdf_path = args.pdf_path or DEFAULT_PDF_PATH
    output_dir_base = args.output_dir # This is the base for setup_output_directory
    
    if not args.pdf_path:
        logger.info(f"No PDF path provided, using default: {pdf_path}")
    # The setup_output_directory will use DEFAULT_OUTPUT_DIR if output_dir_base is None

    if pdf_path == DEFAULT_PDF_PATH and not os.path.exists(DEFAULT_PDF_PATH):
        logger.warning(f"Default PDF '{DEFAULT_PDF_PATH}' not found. Please provide a PDF path or create the file.")
        try:
            from PyPDF2 import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=210, height=297)
            with open(DEFAULT_PDF_PATH, "wb") as f:
                writer.write(f)
            logger.info(f"Created a dummy '{DEFAULT_PDF_PATH}' for testing purposes.")
        except Exception as e:
            logger.error(f"Could not create dummy PDF: {e}")
            return

    # Call the updated function
    toc, generated_output_dir = step1_generate_toc_with_summaries(pdf_path, output_dir_base, args.project_id)

    if args.json_file:
        # If a specific json_file path is given, save the main result there.
        # The function already saves 'chapters_with_summaries.json' in its own time-stamped output_dir.
        try:
            # Ensure the directory for args.json_file exists
            json_output_path_dir = os.path.dirname(args.json_file)
            if json_output_path_dir and not os.path.exists(json_output_path_dir):
                os.makedirs(json_output_path_dir, exist_ok=True)
                logger.info(f"Created directory for custom JSON output: {json_output_path_dir}")

            with open(args.json_file, 'w', encoding='utf-8') as f:
                json.dump(toc, f, ensure_ascii=False, indent=2)
            logger.info(f"TOC with summaries JSON also saved to {args.json_file}")
        except IOError as e:
            logger.error(f"Error saving TOC with summaries JSON to {args.json_file}: {e}")
    else:
        # If no specific json_file, print to console.
        # The primary file is already saved in generated_output_dir.
        print(json.dumps(toc, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 