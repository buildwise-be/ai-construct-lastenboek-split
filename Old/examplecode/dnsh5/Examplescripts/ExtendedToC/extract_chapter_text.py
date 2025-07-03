import os
import sys
import json
import argparse
import logging
from collections import defaultdict

# Configure logging with pipeline_step support
def setup_logging():
    """Set up logging configuration compatible with pipeline orchestrator"""
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        # Only set pipeline_step if it doesn't already exist to avoid KeyError
        if not hasattr(record, 'pipeline_step'):
            record.pipeline_step = 'TEXT_EXTRACT'
        return record
    logging.setLogRecordFactory(record_factory)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(pipeline_step)s - %(message)s'
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Default paths - users should verify or provide these via CLI
DEFAULT_LLAMA_PARSE_JSON = "output.json" 
DEFAULT_CHAPTERS_JSON = os.path.join("output", "pipeline_main_script_run_001", "step1_toc", "chapters.json")
DEFAULT_OUTPUT_JSON = "chapters_with_text.json"

def load_json_file(file_path):
    """Loads a JSON file."""
    logger.info(f"Loading JSON file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading {file_path}: {e}")
        raise

def extract_text_for_range(parsed_pages_data, start_page, end_page):
    """
    Extracts and concatenates text from parsed_pages_data for a given page range.
    
    Args:
        parsed_pages_data (list): List of page objects from LlamaParse output.
                                  Each object is a dict, expected to have 'text' and
                                  'metadata' (with 'page_number', 'page_label', or 'fpath_page_idx').
        start_page (int): The starting page number (inclusive, 1-based).
        end_page (int): The ending page number (inclusive, 1-based).
        
    Returns:
        str: Concatenated text for the specified page range.
    """
    relevant_texts = []
    if not parsed_pages_data or not isinstance(parsed_pages_data, list):
        logger.warning("parsed_pages_data is empty or not a list in extract_text_for_range.")
        return ""

    # Create a quick lookup for page content: {page_num: [text_chunk1, text_chunk2]}
    page_content_map = defaultdict(list)
    for page_item_idx, page_item in enumerate(parsed_pages_data):
        if not isinstance(page_item, dict):
            logger.warning(f"Skipping non-dictionary item at index {page_item_idx} in parsed_pages_data: {type(page_item)}")
            continue
        
        page_meta = page_item.get('metadata', {})
        page_num_str = None
        page_num_int = None

        # Try to get page number from metadata, checking common keys
        if 'page_number' in page_meta: # Direct integer typically
            page_num_int = page_meta['page_number']
        elif 'page_label' in page_meta: # Often a string, e.g., "1", "A-1"
            page_num_str = str(page_meta['page_label'])
        elif 'fpath_page_idx' in page_meta: # Usually 0-indexed
            page_num_int = page_meta['fpath_page_idx'] + 1 
        # NEW: Check for top-level 'page' key
        elif 'page' in page_item:
            try:
                page_num_int = int(page_item['page'])
            except Exception:
                logger.debug(f"Could not convert top-level 'page' value '{page_item['page']}' to int at index {page_item_idx}.")
                continue
        
        if page_num_int is not None:
            pass # Already an int
        elif page_num_str is not None:
            try:
                page_num_int = int(page_num_str)
            except ValueError:
                logger.debug(f"Could not convert page_label '{page_num_str}' to int for item at index {page_item_idx}. Metadata: {page_meta}")
                continue # Skip if page number cannot be determined as int
        else:
            logger.debug(f"Page number not found in metadata or as top-level 'page' for item at index {page_item_idx}. Metadata: {page_meta}")
            continue # Skip if no page number source found

        page_text = page_item.get('text', '')
        page_content_map[page_num_int].append(page_text)

    for page_num_iter in range(start_page, end_page + 1):
        if page_num_iter in page_content_map:
            relevant_texts.extend(page_content_map[page_num_iter])
        # else: # This can be noisy if many pages in the range have no direct LlamaParse output
        #     logger.debug(f"No content found for page {page_num_iter} in LlamaParse output's page_content_map.")
            
    return "\n\n".join(relevant_texts)


def process_chapters_recursively(chapters_node, parsed_pages_data, result_node):
    """
    Recursively processes chapters and their sections to extract text.
    Modifies result_node in place.
    """
    for item_id, item_data in chapters_node.items():
        if not isinstance(item_data, dict):
            logger.warning(f"Skipping item '{item_id}' as its data is not a dictionary: {item_data}")
            continue

        logger.info(f"Processing item: {item_id} - {item_data.get('title', 'N/A')}")
        start_page = item_data.get('start')
        end_page = item_data.get('end')
        title = item_data.get('title', 'N/A')

        if start_page is None or end_page is None:
            logger.warning(f"Skipping item '{item_id}' due to missing 'start' or 'end' page. Data: {item_data}")
            continue
        
        try:
            start_page = int(start_page)
            end_page = int(end_page)
        except ValueError:
            logger.warning(f"Skipping item '{item_id}' due to non-integer 'start' ({start_page}) or 'end' ({end_page}) page.")
            continue

        if start_page <= 0 or end_page <= 0:
            logger.warning(f"Skipping item '{item_id}' due to non-positive 'start' ({start_page}) or 'end' ({end_page}) page.")
            continue
        if start_page > end_page:
            logger.warning(f"Skipping item '{item_id}' as start_page ({start_page}) > end_page ({end_page}).")
            continue

        item_text = extract_text_for_range(parsed_pages_data, start_page, end_page)
        
        result_node[item_id] = {
            "title": title,
            "start_page_raw": item_data.get('start'), # Keep original for reference if needed
            "end_page_raw": item_data.get('end'),     # Keep original for reference
            "start_page_used": start_page,
            "end_page_used": end_page,
            "text": item_text
        }
        logger.debug(f"Extracted text for {item_id} (pages {start_page}-{end_page}), length: {len(item_text)}")

        if 'sections' in item_data and isinstance(item_data['sections'], dict) and item_data['sections']:
            result_node[item_id]['sections'] = {}
            process_chapters_recursively(item_data['sections'], parsed_pages_data, result_node[item_id]['sections'])


def main_cli():
    parser = argparse.ArgumentParser(description="Extract text per chapter from LlamaParse JSON output based on a chapters.json file.")
    parser.add_argument(
        "llama_parse_json", 
        nargs="?",
        default=DEFAULT_LLAMA_PARSE_JSON,
        help=f"Path to the JSON file from LlamaParse (default: {DEFAULT_LLAMA_PARSE_JSON})"
    )
    parser.add_argument(
        "chapters_json", 
        nargs="?",
        default=DEFAULT_CHAPTERS_JSON,
        help=f"Path to the chapters.json file from TOC generation (default: {DEFAULT_CHAPTERS_JSON})"
    )
    parser.add_argument(
        "-o", "--output-json", 
        default=DEFAULT_OUTPUT_JSON,
        help=f"Path to save the output JSON file with extracted text (default: {DEFAULT_OUTPUT_JSON})"
    )
    
    args = parser.parse_args()

    logger.info("Starting chapter text extraction process...")
    logger.info(f"LlamaParse JSON input: {args.llama_parse_json}")
    logger.info(f"Chapters JSON input: {args.chapters_json}")
    logger.info(f"Output JSON: {args.output_json}")

    try:
        parsed_json = load_json_file(args.llama_parse_json)
        # Accept both list and dict-with-pages
        if isinstance(parsed_json, list):
            parsed_pages_data = parsed_json
        elif isinstance(parsed_json, dict) and 'pages' in parsed_json and isinstance(parsed_json['pages'], list):
            parsed_pages_data = parsed_json['pages']
            logger.info(f"Detected 'pages' key in LlamaParse JSON; using its value as the page list.")
        else:
            logger.error(f"LlamaParse JSON content at '{args.llama_parse_json}' is not a list or a dict with a 'pages' key. Type: {type(parsed_json)}. Top-level content: {str(parsed_json)[:200]}")
            sys.exit(1)

        chapters_structure = load_json_file(args.chapters_json)
        if not isinstance(chapters_structure, dict):
            logger.error(f"Chapters JSON content at '{args.chapters_json}' is not a dictionary as expected. Type: {type(chapters_structure)}")
            sys.exit(1)

        extracted_data = {}
        process_chapters_recursively(chapters_structure, parsed_pages_data, extracted_data)
        
        output_dir = os.path.dirname(args.output_json)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully extracted text and saved to {args.output_json}")

    except FileNotFoundError:
        logger.error("One or both input files were not found. Please check the paths.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during the process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main_cli() 