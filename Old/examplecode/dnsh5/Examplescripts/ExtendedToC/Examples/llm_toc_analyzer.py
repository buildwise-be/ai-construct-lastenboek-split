import PyPDF2
import json
import os
import logging
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

# Configure logging (optional but good practice)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# ----------------------------------------------------------------
# STEP 1: LOAD TOC (already in JSON format)
# ----------------------------------------------------------------
# This is example data, actual TOC will be passed to functions
toc_json_str = """
{
    "00": {
        "start": 3,
        "end": 7,
        "title": "ALGEMEENHEDEN.",
        "sections": {
            "00.01": {
                "start": 3,
                "end": 3,
                "title": "MONSTERS, STALEN, MODELLEN."
            },
            "00.02": {
                "start": 3,
                "end": 4,
                "title": "UITVOERING EN OPMETEN."
            }
        }
    },
    "09": {
        "start": 7,
        "end": 8,
        "title": "VEILIGHEID",
        "sections": {
            "09.10": {
                "start": 7,
                "end": 7,
                "title": "VEILIGHEIDSPLAN ONTWERP"
            }
        }
    }
}
"""
# toc = json.loads(toc_json_str) # No longer needed globally

# ----------------------------------------------------------------
# STEP 2: LOAD THE PDF (REMOVED FROM TOP LEVEL)
# ----------------------------------------------------------------
# PDF loading will be handled by the calling script.

# ----------------------------------------------------------------
# STEP 3: RECURSIVELY PARSE TOC AND EXTRACT TEXT CHUNKS
# ----------------------------------------------------------------

def extract_section_text(pdf_reader: PyPDF2.PdfReader, num_pages: int, start_page: int, end_page: int) -> str:
    """Extracts text from the PDF for pages [start_page..end_page].
    Page numbers are 1-based for input, converted to 0-based for PyPDF2.
    """
    text_content = []
    # Adjust for 0-based indexing for PdfReader and ensure pages are within bounds
    # User provides 1-based pages, PdfReader uses 0-based.
    # Start page: if user gives 1, it's index 0.
    # End page: if user gives 3, it means pages 1, 2, 3 (indices 0, 1, 2).
    # So, range(start_page - 1, end_page)
    
    actual_start_idx = max(0, start_page - 1)
    actual_end_idx = min(num_pages - 1, end_page - 1) # end_page is inclusive, so index is end_page - 1

    if actual_start_idx > actual_end_idx : # If start page is after end page (e.g. start=5, end=3 or bad input)
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
    """
    Internal recursive helper to extract page ranges from the TOC structure.
    Populates the page_ranges dictionary.
    """
    start = node.get("start")
    end = node.get("end")
    title = node.get("title", "Untitled Section")

    # Store page range if valid and code exists
    if code and isinstance(start, int) and isinstance(end, int) and start >= 0 and end >= start:
        page_ranges[code] = {
            "title": title,
            "start": start,
            "end": end
        }
    elif code:
        logger.warning(f"Invalid or missing page range for code {code} ('{title}'). Start: {start}, End: {end}. Skipping range storage.")

    # Traverse subsections if they exist
    sub_sections = node.get("sections", {})
    if isinstance(sub_sections, dict):
        for subcode, subnode in sub_sections.items():
            if isinstance(subnode, dict):
                _traverse_toc_for_ranges(subnode, code=subcode, page_ranges=page_ranges)
            else:
                logger.warning(f"Expected dictionary for subsection {subcode}, but got {type(subnode)}. Skipping subsection.")


def get_toc_page_ranges_from_json(toc_data: dict) -> dict:
    """
    Processes a loaded TOC dictionary (from JSON) and extracts a flat dictionary
    mapping specific item codes to their titles and page ranges.
    """
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
                    else: page_ranges_dict[code] = item_data # Store without range if parent has no range
                else: page_ranges_dict[code] = item_data # Store without range if no parent or parent not in dict

            sections = node.get("sections", {})
            if isinstance(sections, dict):
                for subcode, subnode in sections.items():
                    extract_vision_toc_ranges(subcode, subnode, page_ranges_dict, parent_code=code)

        for code, node in toc_data.items():
            extract_vision_toc_ranges(code, node, page_ranges, parent_code=None)
            
    else: # Standard TOC format
        logger.info("Processing using standard TOC format logic (start/end keys expected)")
        for top_level_code, top_level_node in toc_data.items():
            if isinstance(top_level_node, dict):
                _traverse_toc_for_ranges(top_level_node, code=top_level_code, page_ranges=page_ranges)
            else:
                logger.warning(f"Standard TOC: Expected dictionary for top-level code {top_level_code}, but got {type(top_level_node)}.")

    # Final summary log
    # ... (logging logic can remain similar)
    return page_ranges

# New function to extract text for all sections based on ToC
def extract_text_for_sections(toc_data: dict, pdf_reader: PyPDF2.PdfReader, num_pages: int) -> list:
    """
    Extracts text for each section defined in the ToC.
    """
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
                "content": "", # Empty content if pages are missing
                "error": "Missing page numbers"
            })
            continue
        
        logger.info(f"Extracting text for section '{code}': '{title}' (Pages: {start_page}-{end_page})")
        content = extract_section_text(pdf_reader, num_pages, start_page, end_page)
        
        sections_with_text.append({
            "code": code,
            "title": title,
            "start_page_pdf": start_page, # Store original 1-based page numbers
            "end_page_pdf": end_page,
            "content": content
        })
    
    logger.info(f"Finished text extraction for {len(sections_with_text)} sections.")
    return sections_with_text

# Vertex AI configuration constants (can be overridden by parameters)
DEFAULT_MODEL_NAME = "gemini-1.5-flash-001" # Changed from 2.0 to 1.5 as per example
DEFAULT_LOCATION = "europe-west1"

GENERATION_CONFIG = {
    "max_output_tokens": 8192, # Increased as per other script
    "temperature": 0.5, # Adjusted from 1
    "top_p": 0.95,
}
SAFETY_SETTINGS = [
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
]

def _initialize_vertex_model(project_id: str, location: str, model_name: str):
    """Helper to initialize Vertex AI and the GenerativeModel."""
    try:
        vertexai.init(project=project_id, location=location)
        logger.info(f"Initialized Vertex AI (Project: {project_id}, Location: {location})")
        model = GenerativeModel(
            model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        logger.info(f"Initialized Generative Model: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model (Project: {project_id}, Model: {model_name}): {e}", exc_info=True)
        raise # Re-raise exception to be caught by caller

def call_llm_api(model: GenerativeModel, chunk_text: str, task_description: str = "") -> str:
    """
    Calls the provided Vertex AI Generative Model.
    """
    if not chunk_text or not chunk_text.strip():
        return "Skipped: Section content is empty."

    prompt = f"{task_description}\n\nText:\n{chunk_text}"
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            return f"Blocked due to: {response.prompt_feedback.block_reason}"
        elif not response.candidates or not response.candidates[0].content.parts:
             return "No response generated or content is empty."
        else:
            try:
                return response.candidates[0].content.parts[0].text
            except (AttributeError, IndexError):
                 logger.warning(f"Could not extract text from response structure: {response}")
                 return "Error: Could not parse response text."
    except Exception as e:
        logger.error(f"Error calling Vertex AI API: {e}", exc_info=True)
        return f"Error: Could not get response from LLM. Details: {e}"

def analyze_sections_with_llm(sections: list, 
                              model: GenerativeModel = None, 
                              project_id: str = None, 
                              location: str = None, 
                              model_name: str = None):
    """
    Analyzes sections using an LLM.
    Can use a pre-initialized model or initialize one using project_id.
    """
    results = []
    total_sections = len(sections)
    
    current_model = model
    if current_model is None:
        if not project_id:
            logger.error("LLM analysis requires either a pre-initialized 'model' or a 'project_id'. Neither provided.")
            # Return empty or add error indicators to sections
            for sec in sections:
                 results.append({**sec, "analysis": "Error: LLM not configured.", "error_llm": "LLM not configured"})
            return results # Or raise an error: raise ValueError("LLM model or project_id required.")

        resolved_model_name = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL_NAME)
        resolved_location = location or os.getenv("GOOGLE_CLOUD_LOCATION", DEFAULT_LOCATION)
        logger.info(f"Attempting to initialize LLM (Project: {project_id}, Model: {resolved_model_name}, Location: {resolved_location}) for analysis.")
        try:
            current_model = _initialize_vertex_model(project_id, resolved_location, resolved_model_name)
        except Exception as e:
            logger.error(f"Failed to initialize LLM for analysis: {e}")
            for sec in sections:
                 results.append({**sec, "analysis": f"Error: LLM initialization failed - {e}", "error_llm": f"LLM init failed: {e}"})
            return results

    if current_model is None: # Should not happen if logic above is correct, but as a safeguard
        logger.error("LLM model is still None after initialization attempt.")
        for sec in sections:
            results.append({**sec, "analysis": "Error: LLM model unavailable after init attempt.", "error_llm": "LLM unavailable post-init"})
        return results

    for i, sec in enumerate(sections):
        code = sec.get("code", "N/A")
        title = sec.get("title", "N/A")
        content = sec.get("content", "")

        instruction = f"""Analyze the following section (Code: {code}, Title: {title}).
        Focus on identifying:
        1. Key requirements or specifications mentioned.
        2. Any potential ambiguities, contradictions, or missing information.
        3. References to other codes or standards.
        Present the analysis clearly and concisely as a structured summary or bullet points.
        If the content is very short or seems to be just a title, state that.
        If the content is missing or says 'Skipped', indicate that analysis cannot be performed."""

        logger.info(f"[{i+1}/{total_sections}] Sending code: {code} - {title} to LLM...")

        if content.strip() and content != "Skipped: Section content is empty.":
            llm_output = call_llm_api(current_model, content, task_description=instruction)
        elif not content.strip():
            llm_output = "Skipped: Section content was empty."
            logger.info("Skipping LLM call because section content is empty.")
        else: # Handles "Skipped: Section content is empty." from previous step
            llm_output = "Analysis cannot be performed as section content was marked as skipped or empty previously."
            logger.info("Skipping LLM call because section content indicates it was previously skipped.")
            
        results.append({
            "code": code,
            "title": title,
            "start_page_pdf": sec.get("start_page_pdf"),
            "end_page_pdf": sec.get("end_page_pdf"),
            # "content": content, # Optionally exclude original content from final analysis to save space
            "analysis": llm_output
        })

    return results

# --- Main execution block for standalone testing (optional) ---
if __name__ == "__main__":
    logger.info("Running llm_toc_analyzer.py as a standalone script for testing.")

    # 1. Setup - Define dummy PDF and ToC for testing
    TEST_PDF_PATH = r"C:\Users\gr\Documents\GitHub\ExtendedToC\output\pipeline_main_script_run_001\step1_toc\chapters.json" # Assumes test.pdf exists from toc_generation.py or manually created
    
    # Create a dummy PDF if it doesn't exist (mirroring toc_generation.py's main)
    if not os.path.exists(TEST_PDF_PATH):
        logger.warning(f"Test PDF '{TEST_PDF_PATH}' not found. Creating a dummy PDF for testing.")
        try:
            writer = PyPDF2.PdfWriter()
            # Add a few blank pages with some text to simulate content
            for i in range(5):
                writer.add_blank_page(width=612, height=792) # Standard US Letter
                # This method of adding text to a blank page is non-trivial with PyPDF2 directly.
                # For a simple test, we'll rely on toc_generation to make a test PDF or user to supply one.
                # If we need text here, we'd use reportlab or similar.
                # For now, pages will be blank if created here.
            with open(TEST_PDF_PATH, "wb") as f:
                writer.write(f)
            logger.info(f"Created dummy '{TEST_PDF_PATH}' with 5 blank pages.")
        except Exception as e:
            logger.error(f"Could not create dummy PDF for testing: {e}", exc_info=True)
            # If PDF creation fails, cannot proceed with text extraction testing here.
            # Consider exiting or skipping parts of the test.
            sys.exit(1) # Exit if dummy PDF creation fails

    # Example ToC data (could be loaded from a file generated by toc_generation.py)
    example_toc_data = {
        "01": {"title": "Chapter 1", "start": 1, "end": 2, "sections": {
            "01.01": {"title": "Section 1.1", "start": 1, "end": 1},
            "01.02": {"title": "Section 1.2", "start": 2, "end": 2}
        }},
        "02": {"title": "Chapter 2", "start": 3, "end": 3}
    }
    logger.info(f"Using example ToC data: {json.dumps(example_toc_data, indent=2)}")

    # 2. Test text extraction
    try:
        with open(TEST_PDF_PATH, 'rb') as pdf_file:
            pdf_reader_instance = PyPDF2.PdfReader(pdf_file)
            num_pdf_pages = len(pdf_reader_instance.pages)
            logger.info(f"Successfully loaded test PDF '{TEST_PDF_PATH}' with {num_pdf_pages} pages.")
            
            sections_with_extracted_text = extract_text_for_sections(example_toc_data, pdf_reader_instance, num_pdf_pages)
            logger.info(f"Extracted text for {len(sections_with_extracted_text)} sections.")
            
            # Save extracted text for review
            if sections_with_extracted_text:
                output_extracted_text_path = "output_llm_analyzer_test/extracted_text_test.json"
                os.makedirs(os.path.dirname(output_extracted_text_path), exist_ok=True)
                with open(output_extracted_text_path, "w", encoding="utf-8") as f:
                    json.dump(sections_with_extracted_text, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved extracted text to '{output_extracted_text_path}'")
            else:
                logger.warning("No text was extracted from sections for the test.")

    except FileNotFoundError:
        logger.error(f"Test PDF '{TEST_PDF_PATH}' not found. Cannot run text extraction test.")
        sections_with_extracted_text = [] # Ensure it's defined for the next step
    except Exception as e:
        logger.error(f"Error during text extraction test: {e}", exc_info=True)
        sections_with_extracted_text = []


    # 3. Test LLM analysis (requires GOOGLE_CLOUD_PROJECT env var)
    test_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not test_project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Skipping LLM analysis test.")
    elif not sections_with_extracted_text:
        logger.warning("No sections with text available (due to previous errors or empty extraction). Skipping LLM analysis test.")
    else:
        logger.info(f"Proceeding with LLM analysis test using Project ID: {test_project_id}.")
        try:
            # We can test by either passing a pre-initialized model or letting the function initialize it.
            # Option 1: Pre-initialize (if you want to test that path)
            # test_model_instance = _initialize_vertex_model(test_project_id, DEFAULT_LOCATION, DEFAULT_MODEL_NAME)
            # analyzed_results = analyze_sections_with_llm(sections_with_extracted_text, model=test_model_instance)
            
            # Option 2: Let the function initialize (tests that path)
            analyzed_results = analyze_sections_with_llm(sections_with_extracted_text, project_id=test_project_id)

            logger.info(f"LLM analysis test complete. Number of analyzed sections: {len(analyzed_results)}")
            if analyzed_results:
                output_analysis_path = "output_llm_analyzer_test/analyzed_sections_test.json"
                os.makedirs(os.path.dirname(output_analysis_path), exist_ok=True)
                with open(output_analysis_path, "w", encoding="utf-8") as f:
                    json.dump(analyzed_results, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved LLM analysis results to '{output_analysis_path}'")
            else:
                logger.warning("LLM analysis test produced no results.")
        except Exception as e:
            logger.error(f"Error during LLM analysis test: {e}", exc_info=True)
            
    logger.info("Standalone test run of llm_toc_analyzer.py finished.")