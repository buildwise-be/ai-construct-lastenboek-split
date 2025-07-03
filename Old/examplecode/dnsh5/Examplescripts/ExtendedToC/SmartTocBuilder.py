import os
import sys
import json
import logging
import base64
import time
import argparse
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
from vertexai.generative_models import SafetySetting, HarmCategory, HarmBlockThreshold

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Vertex AI Generation Configuration
DEFAULT_GENERATION_CONFIG = {
    "max_output_tokens": 8192,
    "temperature": 0.7, # Slightly lower temp for more deterministic structure parsing
    "top_p": 0.95,
}

# Vertex AI Safety Settings (adjust as needed, OFF for maximum content)
DEFAULT_SAFETY_SETTINGS = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
]

# Vertex AI Model Name
DEFAULT_MODEL_NAME = "gemini-1.5-pro-002" # Ensure this is a multimodal model

# API call delay
DEFAULT_API_DELAY_SECONDS = 2.0 # For rate limiting

# --- Helper Functions ---

def initialize_vertex_model(
    project_id: Optional[str] = None,
    location: Optional[str] = "europe-west1", # Common location, adjust if needed
    model_name: str = DEFAULT_MODEL_NAME,
    generation_config: Optional[Dict[str, Any]] = None,
    safety_settings: Optional[List[SafetySetting]] = None
) -> GenerativeModel:
    """Initializes and returns a Vertex AI GenerativeModel."""
    try:
        resolved_project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not resolved_project_id:
            raise ValueError("Google Cloud Project ID not provided or found in GOOGLE_CLOUD_PROJECT env var.")

        vertexai.init(project=resolved_project_id, location=location)
        logger.info(f"Vertex AI initialized. Project: {resolved_project_id}, Location: {location}")

        model = GenerativeModel(
            model_name,
            generation_config=generation_config or DEFAULT_GENERATION_CONFIG,
            safety_settings=safety_settings or DEFAULT_SAFETY_SETTINGS
        )
        logger.info(f"Successfully initialized Vertex AI Model: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Vertex AI model: {str(e)}")


def load_pdf_to_bytes(pdf_path: str) -> bytes:
    """Loads a PDF file and returns its content as bytes."""
    abs_pdf_path = os.path.abspath(pdf_path)
    if not os.path.exists(abs_pdf_path):
        logger.error(f"PDF file not found: {abs_pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {abs_pdf_path}")
    try:
        with open(abs_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        logger.info(f"Successfully loaded PDF: {abs_pdf_path} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error reading PDF file {abs_pdf_path}: {str(e)}", exc_info=True)
        raise


def post_process_llm_response_to_dict(response_text: str, expected_key: Optional[str] = None) -> Optional[Dict[Any, Any]]:
    """
    Extracts a Python dictionary from a markdown code block in the LLM's response.
    If expected_key is provided, it returns the value of that key from the extracted dictionary.
    Otherwise, it returns the entire extracted dictionary.
    For the special expected_key 'main_chapters', it can also return a list if that's what the LLM provides.
    """
    try:
        # Regex to find python code block
        # It looks for ```python ... ``` or ``` ... ```
        match = re.search(r"```(?:python\s*)?(.*?)\s*```", response_text, re.DOTALL | re.IGNORECASE)
        if not match:
            logger.warning("No Python code block found in LLM response.")
            # Try to see if the whole response is a JSON string
            try:
                data = json.loads(response_text)
                if isinstance(data, dict):
                    if expected_key:
                        return data.get(expected_key)
                    return data
                # If expected_key is 'main_chapters' and data is a list, return it
                if expected_key == "main_chapters" and isinstance(data, list):
                    return data
                logger.warning("LLM response is JSON, but not a dictionary (or a list for main_chapters).")
                return None
            except json.JSONDecodeError:
                logger.warning("LLM response is not a valid JSON string either.")
                return None

        code_block = match.group(1).strip()

        # Attempt to parse as JSON first, as it's safer than exec
        try:
            data = json.loads(code_block)
            if isinstance(data, dict):
                if expected_key:
                    return data.get(expected_key)
                return data
            # If expected_key is 'main_chapters' and data is a list, return it (for JSON that is directly a list)
            if expected_key == "main_chapters" and isinstance(data, list):
                return data
            logger.warning(f"Code block parsed as JSON, but was not a dictionary (or list for main_chapters). Type: {type(data)}")
        except json.JSONDecodeError:
            logger.info("Code block is not direct JSON, attempting exec for Python dict.")
            # If JSON parsing fails, try exec (use with caution, ensure LLM is trusted)
            # Create a controlled environment for exec
            local_vars = {}
            exec(code_block, {}, local_vars) # Provide global and local dicts

            if expected_key:
                if expected_key in local_vars:
                    # Handle special case for 'main_chapters' which should be a list
                    if expected_key == "main_chapters" and isinstance(local_vars[expected_key], list):
                        return local_vars[expected_key]
                    elif isinstance(local_vars[expected_key], dict):
                        return local_vars[expected_key]
                    else:
                        logger.warning(f"Expected key '{expected_key}' found but is not a dictionary (or list for main_chapters). Type: {type(local_vars[expected_key])}")
                        return None
                else:
                    logger.warning(f"Expected key '{expected_key}' not found in executed code block variables: {list(local_vars.keys())}")
                    # Fallback: if only one item in local_vars and it's a list (for main_chapters) or a dict
                    if len(local_vars) == 1:
                        single_value = list(local_vars.values())[0]
                        if expected_key == "main_chapters" and isinstance(single_value, list):
                            return single_value
                        elif isinstance(single_value, dict):
                             # If no expected key, or key not found but only one dict is there
                            if not expected_key or expected_key not in local_vars:
                                return single_value
                    return None
            else: # No expected key, return the first dictionary found or all local_vars if it's a dict
                if len(local_vars) == 1 and isinstance(list(local_vars.values())[0], dict):
                    return list(local_vars.values())[0]
                elif local_vars and all(isinstance(v, dict) for v in local_vars.values()): # Check if local_vars itself is a dict of dicts
                    # This case is ambiguous, prefer returning None or the largest dict
                    # For now, let's return the first one if it's the only main one.
                     # Or, if one key is 'chapters' or 'sections', prefer that.
                    if 'chapters' in local_vars and isinstance(local_vars['chapters'], dict): return local_vars['chapters']
                    if 'sections' in local_vars and isinstance(local_vars['sections'], dict): return local_vars['sections']
                    if 'data' in local_vars and isinstance(local_vars['data'], dict): return local_vars['data']

                logger.warning(f"Could not unambiguously determine the dictionary to return from exec results: {list(local_vars.keys())}")
                return None


    except Exception as e:
        logger.error(f"Error post-processing LLM response: {str(e)}\nResponse text:\n{response_text}", exc_info=True)
    return None


def send_llm_request(
    model: GenerativeModel,
    prompt: str,
    pdf_bytes: Optional[bytes] = None,
    attempt: int = 1,
    max_attempts: int = 3
) -> Optional[str]:
    """Sends a request to the LLM and handles retries for certain issues."""
    try:
        logger.info(f"Sending request to LLM (Attempt {attempt}/{max_attempts}). Prompt length: {len(prompt)}")
        parts = [prompt]
        if pdf_bytes:
            parts.append(Part.from_data(data=pdf_bytes, mime_type="application/pdf"))

        response = model.generate_content(parts)

        if response.candidates:
            if response.candidates[0].finish_reason == FinishReason.SAFETY:
                logger.warning(f"LLM response blocked due to safety reasons: {response.candidates[0].safety_ratings}")
                # You could retry here with modified safety settings or prompt if appropriate
                # For now, we just return None for safety blocks.
                return None # Or raise an exception
            if response.candidates[0].finish_reason == FinishReason.RECITATION:
                logger.warning("LLM response blocked due to recitation.")
                return None
            if response.text:
                logger.info(f"LLM response received. Finish Reason: {response.candidates[0].finish_reason}. Text length: {len(response.text)}")
                return response.text
            else:
                logger.warning(f"LLM response has no text. Finish Reason: {response.candidates[0].finish_reason}, Content: {response.candidates[0].content}")
                return None # Or try to parse parts if it's not text
        else:
            logger.warning(f"LLM response has no candidates. Full response: {response}")
            # Log prompt feedback if available
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                 logger.warning(f"Prompt blocked. Reason: {response.prompt_feedback.block_reason}, Message: {response.prompt_feedback.block_reason_message}")

            if attempt < max_attempts:
                logger.info(f"Retrying LLM request in {DEFAULT_API_DELAY_SECONDS * attempt} seconds...")
                time.sleep(DEFAULT_API_DELAY_SECONDS * attempt)
                return send_llm_request(model, prompt, pdf_bytes, attempt + 1, max_attempts)
            else:
                logger.error("Max retries reached for LLM request with no candidates.")
                return None

    except Exception as e:
        logger.error(f"Error during LLM request (Attempt {attempt}/{max_attempts}): {str(e)}", exc_info=True)
        if attempt < max_attempts:
            logger.info(f"Retrying LLM request in {DEFAULT_API_DELAY_SECONDS * attempt} seconds...")
            time.sleep(DEFAULT_API_DELAY_SECONDS * attempt)
            return send_llm_request(model, prompt, pdf_bytes, attempt + 1, max_attempts)
        else:
            logger.error("Max retries reached for LLM request after exception.")
    return None


# --- Phase 1: Main Chapter Identification ---

def extract_main_chapters_phase1(
    model: GenerativeModel,
    pdf_bytes: bytes,
    total_pdf_pages: int # For context, though LLM determines from PDF
) -> List[Dict[str, Any]]:
    """
    Identifies main chapters, their titles, and their global start pages.
    Returns a list of dictionaries: [{'number': 'XX', 'title': 'CHAPTER TITLE', 'start_page': YYY}, ...]
    sorted by start_page.
    """
    logger.info("=" * 50)
    logger.info("PHASE 1: Identifying Main Chapters...")
    logger.info("=" * 50)

    prompt = f"""
Your sole task is to identify the main chapter declarations in the provided PDF document.
This PDF has a total of {total_pdf_pages} pages.
Main chapters are typically formatted as "XX. CHAPTER TITLE" (e.g., "00. ALGEMENE BEPALINGEN", "01. VOORAFGAANDE WERKEN").
These are the highest-level structural divisions of the document.

For each main chapter you find:
1.  Extract the chapter number (e.g., "00", "01", "15"). This is the "XX" part.
2.  Extract the full chapter title exactly as it appears in the document following the number.
3.  Determine the precise global PDF page number (1-indexed) where this main chapter heading *first definitively appears and its content begins*.

IMPORTANT INSTRUCTIONS:
- Do NOT identify sub-chapters or sections (e.g., "XX.YY" or "XX.YY.ZZ") in this phase. Focus only on the primary, top-level chapter divisions like "00", "01", "02", ..., "10", "11", etc.
- The document might be a concatenation of multiple smaller documents. If you see chapter numbers repeat (e.g., a "01." appearing much later after a "15."), treat them as distinct main chapters if they represent new top-level demarcations. However, for this task, assume standard ascending chapter numbers (00, 01, ..., 10, 11, ...) represent the primary structure.
- Ensure page numbers are accurate global PDF page numbers, starting from 1 for the first page.
- IGNORE any page numbers printed within the document itself or in any internal Table of Contents. Base your page numbering on the actual PDF page sequence.

Output the result as a Python list of dictionaries. Each dictionary must have the keys "number", "title", and "start_page".
The list should be sorted by "start_page" in ascending order.

Example Output Format:
```python
main_chapters = [
    {{"number": "00", "title": "ALGEMENE BEPALINGEN", "start_page": 7}},
    {{"number": "01", "title": "VOORAFGAANDE WERKEN", "start_page": 15}},
    {{"number": "02", "title": "GRONDWERKEN", "start_page": 25}}
    # ... and so on for all main chapters
]
```
Be extremely thorough and identify ALL main chapters from the beginning to the end of the document.
If the document structure is unclear or main chapters are hard to distinguish, do your best to follow these instructions.
"""

    response_text = send_llm_request(model, prompt, pdf_bytes)
    if not response_text:
        logger.error("Phase 1: Failed to get response from LLM for main chapter identification.")
        return []

    parsed_data = post_process_llm_response_to_dict(response_text, expected_key="main_chapters")

    if parsed_data and isinstance(parsed_data, list):
        # Validate structure and types
        validated_chapters = []
        for i, item in enumerate(parsed_data):
            if isinstance(item, dict) and \
               'number' in item and isinstance(item['number'], str) and \
               'title' in item and isinstance(item['title'], str) and \
               'start_page' in item and isinstance(item['start_page'], int):
                validated_chapters.append(item)
            else:
                logger.warning(f"Phase 1: Invalid item format in LLM response for main chapters: {item}. Skipping.")

        # Sort by start_page just in case LLM didn't
        validated_chapters.sort(key=lambda x: x['start_page'])
        logger.info(f"Phase 1: Successfully identified {len(validated_chapters)} main chapters.")
        if len(validated_chapters) > 0:
             logger.debug(f"First few identified main chapters: {validated_chapters[:3]}")
        return validated_chapters
    else:
        logger.error(f"Phase 1: Failed to parse main chapters from LLM response or data is not a list. Parsed: {parsed_data}")
        return []

# --- Phase 2: Detailed Section Extraction within Main Chapter Segments ---

def extract_sections_for_chapter_phase2(
    model: GenerativeModel,
    pdf_bytes: bytes,
    main_chapter_info: Dict[str, Any], # e.g., {'number': '01', 'title': 'TITLE', 'start_page': 15}
    segment_start_page: int,
    segment_end_page: int,
    total_pdf_pages: int
) -> Dict[str, Any]: # Returns the 'sections' dictionary for this main chapter
    """
    Identifies all nested sections (XX.YY, XX.YY.ZZ, etc.) within a given main chapter's page segment.
    """
    ch_num = main_chapter_info['number']
    ch_title = main_chapter_info['title']

    logger.info("-" * 40)
    logger.info(f"PHASE 2: Extracting sections for Main Chapter {ch_num} ('{ch_title}')")
    logger.info(f"Analyzing PDF pages {segment_start_page} through {segment_end_page} (global PDF pages).")
    logger.info("-" * 40)

    if segment_start_page > segment_end_page:
        logger.warning(f"Segment start page {segment_start_page} is after end page {segment_end_page} for Ch. {ch_num}. Skipping.")
        return {}

    # Note for LLM about the document size and focus area
    # Even if we give the whole PDF, the prompt is key to focus its attention.
    prompt = f"""
You are analyzing a specific segment of a {total_pdf_pages}-page PDF document.
This segment spans from global PDF page {segment_start_page} to global PDF page {segment_end_page}.
This segment corresponds to:
Main Chapter Number: {ch_num}
Main Chapter Title: "{ch_title}"

Your task is to identify all hierarchical sections and subsections that fall *strictly within this page range* ({segment_start_page}-{segment_end_page}) AND *logically belong to this Main Chapter ({ch_num} - "{ch_title}")*.

These sections and subsections can have formats like:
- "{ch_num}.YY TITLE" (e.g., "{ch_num}.10 SECTION TITLE")
- "{ch_num}.YY.ZZ TITLE" (e.g., "{ch_num}.10.01 SUBSECTION TITLE")
- "{ch_num}.YY.ZZ.AA TITLE" (e.g., "{ch_num}.10.01.01 SUB-SUBSECTION TITLE")
And potentially even deeper levels like "{ch_num}.YY.ZZ.AA.BB TITLE".

For each such identified item (section, subsection, etc.) that belongs to Main Chapter {ch_num}:
1.  Record its precise and full hierarchical numbering (e.g., "{ch_num}.10", "{ch_num}.10.01", "{ch_num}.10.01.01").
2.  Record its full title exactly as it appears in the document.
3.  Record its accurate starting global PDF page number. This must be >= {segment_start_page} and <= {segment_end_page}.
4.  Record its accurate ending global PDF page number. This must be >= its start page and <= {segment_end_page}.
    The end page is the page just before the next peer-level section/subsection begins, or the end of the current item's content if it's the last one in its hierarchy within the segment, or {segment_end_page} if it extends to the end of the segment.

IMPORTANT INSTRUCTIONS:
-   Accuracy is paramount. Double-check page numbers and titles.
-   Ensure all reported page numbers are global PDF page numbers.
-   The 'start' and 'end' pages for any section or subsection must be within the main chapter segment ({segment_start_page}-{segment_end_page}).
-   Pay close attention to the hierarchical numbering. The output must reflect this hierarchy.
-   Do NOT include items that clearly belong to a *different* Main Chapter, even if they appear on these pages due to document layout.
-   If no sections or subsections are found for Main Chapter {ch_num} within this page range, return an empty dictionary.

Output the result as a single Python dictionary. This dictionary will represent the 'sections' key for Main Chapter {ch_num}.
The keys of this dictionary should be the section numbers (e.g., "{ch_num}.10"), and values should be dictionaries containing 'title', 'start', 'end', and a nested 'sections' dictionary for any subsections.

Example Output Format for the sections of Main Chapter {ch_num}:
```python
# This is the structure for the 'sections' attribute of ONE main chapter
sections_data = {{
    "{ch_num}.10": {{
        "title": "FIRST SECTION TITLE OF CHAPTER {ch_num}",
        "start": {segment_start_page}, # Example page
        "end": ...,  # Example page
        "sections": {{ # For {ch_num}.10.ZZ
            "{ch_num}.10.01": {{
                "title": "SUBSECTION TITLE for {ch_num}.10",
                "start": ...,
                "end": ...,
                "sections": {{ # For {ch_num}.10.01.AA
                    "{ch_num}.10.01.01": {{
                        "title": "SUB-SUBSECTION TITLE for {ch_num}.10.01",
                        "start": ...,
                        "end": ...
                        # No 'sections' key here if it's the deepest level for this branch
                    }}
                }}
            }},
            "{ch_num}.10.02": {{
                "title": "ANOTHER SUBSECTION for {ch_num}.10",
                "start": ...,
                "end": ...
            }}
        }}
    }},
    "{ch_num}.20": {{
        "title": "SECOND SECTION TITLE OF CHAPTER {ch_num}",
        "start": ...,
        "end": ...
        # May or may not have subsections
    }}
}}
```
Focus exclusively on the content within pages {segment_start_page} to {segment_end_page}.
"""

    response_text = send_llm_request(model, prompt, pdf_bytes)
    if not response_text:
        logger.error(f"Phase 2: Failed to get LLM response for Ch. {ch_num} sections.")
        return {}

    parsed_sections = post_process_llm_response_to_dict(response_text, expected_key="sections_data")

    if parsed_sections and isinstance(parsed_sections, dict):
        # Further validation of the nested structure can be added here if needed
        # For now, we trust the LLM followed the detailed instructions.
        logger.info(f"Phase 2: Successfully parsed sections for Main Chapter {ch_num}. Found {len(parsed_sections)} top-level sections.")
        return parsed_sections
    elif isinstance(parsed_sections, dict) and not parsed_sections: # Empty dict is valid
        logger.info(f"Phase 2: No sections found or reported by LLM for Main Chapter {ch_num} in segment {segment_start_page}-{segment_end_page}.")
        return {}
    else:
        logger.error(f"Phase 2: Failed to parse sections for Ch. {ch_num} or data is not a dict. Parsed: {parsed_sections}")
        return {}


# --- Main Orchestration ---

def generate_smart_toc(
    pdf_path: str,
    project_id: Optional[str] = None,
    gcp_location: Optional[str] = "europe-west1"
) -> Dict[str, Any]:
    """Orchestrates the two-phase ToC generation process."""
    try:
        model = initialize_vertex_model(project_id=project_id, location=gcp_location)
        pdf_bytes = load_pdf_to_bytes(pdf_path)

        # Use PyPDF2 to get total page count (more reliable than asking LLM for this)
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            total_pdf_pages = len(reader.pages)
            logger.info(f"PDF total page count from PyPDF2: {total_pdf_pages}")
        except Exception as e_pypdf:
            logger.warning(f"Could not get page count using PyPDF2: {e_pypdf}. Analysis might be affected if LLM also struggles.")
            # As a fallback, we could try to ask the LLM, but it's less reliable
            # For now, if PyPDF2 fails, we might have issues defining the last segment.
            # Let's assume it will be provided or is critical.
            # A simple alternative: make it a required input or estimate very high.
            # For now, if total_pdf_pages is not set, Phase 1's prompt needs adjustment or Phase 2's end segment calculation.
            # Let's make it critical for now
            raise RuntimeError(f"Critical: Could not determine total PDF pages using PyPDF2. Error: {e_pypdf}")


        # Phase 1: Identify Main Chapters
        main_chapters_structure = extract_main_chapters_phase1(model, pdf_bytes, total_pdf_pages)
        if not main_chapters_structure:
            logger.error("ToC Generation failed: No main chapters identified in Phase 1.")
            return {}

        # Add 'end_page' to main_chapters_structure and prepare for Phase 2
        # Also add a placeholder for 'sections'
        processed_main_chapters: List[Dict[str, Any]] = []
        for i, chapter_data in enumerate(main_chapters_structure):
            current_ch_data = chapter_data.copy() # Avoid modifying the iterated list item directly
            segment_start = current_ch_data['start_page']
            if i + 1 < len(main_chapters_structure):
                segment_end = main_chapters_structure[i+1]['start_page'] - 1
            else:
                segment_end = total_pdf_pages # Last chapter goes to the end of the PDF

            # Sanity check for segment_end
            if segment_end < segment_start:
                logger.warning(
                    f"Calculated segment end ({segment_end}) is before start ({segment_start}) "
                    f"for main chapter {current_ch_data['number']} ('{current_ch_data['title']}'). "
                    f"This might be due to overlapping main chapter start pages from Phase 1. "
                    f"Setting end page to start page for this segment: {segment_start}."
                )
                segment_end = segment_start
            
            current_ch_data['end_page'] = segment_end # This is the main chapter's end page
            current_ch_data['sections'] = {} # Placeholder for sections from Phase 2
            processed_main_chapters.append(current_ch_data)


        # Phase 2: Extract sections for each main chapter
        for chapter_details in processed_main_chapters:
            time.sleep(DEFAULT_API_DELAY_SECONDS) # Rate limiting between major calls

            sections_data = extract_sections_for_chapter_phase2(
                model,
                pdf_bytes,
                main_chapter_info=chapter_details, # Contains 'number', 'title', 'start_page'
                segment_start_page=chapter_details['start_page'], # True start of this main chapter
                segment_end_page=chapter_details['end_page'],     # True end of this main chapter
                total_pdf_pages=total_pdf_pages
            )
            chapter_details['sections'] = sections_data # Populate the sections

        # Assemble the final ToC in the desired output format
        final_toc: Dict[str, Any] = {}
        for ch_data in processed_main_chapters:
            final_toc[ch_data['number']] = {
                "title": ch_data['title'],
                "start": ch_data['start_page'],
                "end": ch_data['end_page'],
                "sections": ch_data.get('sections', {}) # Use .get for safety
            }

        logger.info("=" * 50)
        logger.info("Smart ToC Generation Complete.")
        logger.info("=" * 50)
        return final_toc

    except FileNotFoundError:
        # Already logged by load_pdf_to_bytes
        return {} # Or re-raise
    except RuntimeError as re_error: # Renamed variable to avoid conflict with import re
        # Already logged by initialize_vertex_model or other critical parts
        logger.error(f"Runtime error during ToC generation: {str(re_error)}", exc_info=True)
        return {} # Or re-raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during ToC generation: {str(e)}", exc_info=True)
        return {}


if __name__ == "__main__":
    DEFAULT_PDF_PATH = r"C:\Users\gr\Documents\GitHub\ExtendedToC\Lastenboeken\CoordinatedArchitectlastenboek.pdf"
    parser = argparse.ArgumentParser(description="Smart Table of Contents (ToC) Generator using Vertex AI Vision.")
    parser.add_argument("pdf_path", nargs="?", default=DEFAULT_PDF_PATH, help=f"Path to the PDF file to process. Defaults to {DEFAULT_PDF_PATH}")
    parser.add_argument(
        "-o", "--output-json",
        default=None,
        help="Path to save the generated ToC JSON file. If not provided, prints to console."
    )
    parser.add_argument(
        "-p", "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT"),
        help="Google Cloud Project ID. Defaults to GOOGLE_CLOUD_PROJECT env var."
    )
    parser.add_argument(
        "-l", "--location",
        default="europe-west1",
        help="Google Cloud location for Vertex AI. Defaults to 'europe-west1'."
    )
    args = parser.parse_args()

    if not args.project_id:
        logger.error("Error: Google Cloud Project ID is required. Set GOOGLE_CLOUD_PROJECT or use --project-id.")
        sys.exit(1)

    # Add PyPDF2 to requirements if not already there
    # pip install PyPDF2 python-dotenv google-cloud-aiplatform

    generated_toc = generate_smart_toc(
        pdf_path=args.pdf_path,
        project_id=args.project_id,
        gcp_location=args.location
    )

    if generated_toc:
        toc_json_str = json.dumps(generated_toc, ensure_ascii=False, indent=2)
        # Determine output path
        if args.output_json:
            output_path = args.output_json
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join("output", "SmartTocBuilder")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"toc_{timestamp}.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(toc_json_str)
            logger.info(f"Successfully saved ToC to: {output_path}")
            print(f"\nToC saved to: {output_path}")
        except IOError as e:
            logger.error(f"Error saving ToC to {output_path}: {str(e)}")
            print("\n--- Generated Table of Contents ---")
            print(toc_json_str)
            print("--- End of Table of Contents ---")
    else:
        logger.error("Failed to generate Table of Contents.")
        print("Failed to generate Table of Contents. Check logs for details.", file=sys.stderr) 