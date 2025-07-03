import json
import os

# --- Configuration ---
OCR_RESULT_FILE_PATH = os.path.join("output", "google_ocr", "CoordinatedArchitectlastenboek_ocr_result.json")
EXTRACTED_TEXT_OUTPUT_DIR = os.path.join("output", "google_ocr")
EXTRACTED_TEXT_FILENAME = "CoordinatedArchitectlastenboek_extracted_text.json"
EXTRACTED_TEXT_FILE_PATH = os.path.join(EXTRACTED_TEXT_OUTPUT_DIR, EXTRACTED_TEXT_FILENAME)

# Helper function to reconstruct text for a given layout from the document's full text.
# This is needed because the .text field in the Document object from Document AI
# often contains the text for the entire batch, and page-specific text needs to be extracted.
def layout_to_text(layout: dict, full_text: str) -> str:
    """
    Extracts text segments for a given layout from the document's full text.
    Assumes layout is a dictionary (from JSON) with a 'textAnchor' and 'textSegments'.
    """
    if not layout or 'textAnchor' not in layout or not layout['textAnchor'].get('textSegments'):
        return ""
    
    text_segments = layout['textAnchor']['textSegments']
    page_text_parts = []
    for segment in text_segments:
        start_index = int(segment.get('startIndex', 0))
        end_index = int(segment.get('endIndex', 0))
        if end_index > start_index:
            page_text_parts.append(full_text[start_index:end_index])
    return "".join(page_text_parts)

def main():
    print(f"Loading OCR results from: {OCR_RESULT_FILE_PATH}")

    if not os.path.exists(OCR_RESULT_FILE_PATH):
        print(f"Error: OCR result file not found at {OCR_RESULT_FILE_PATH}")
        print("Please run the OCR script (e.g., run_ocr.py) first.")
        return

    try:
        with open(OCR_RESULT_FILE_PATH, "r", encoding="utf-8") as f:
            batched_ocr_results = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {OCR_RESULT_FILE_PATH}: {e}")
        return
    except Exception as e:
        print(f"Error reading {OCR_RESULT_FILE_PATH}: {e}")
        return

    if not isinstance(batched_ocr_results, list):
        print(f"Error: Expected a list of OCR batches in {OCR_RESULT_FILE_PATH}, but got {type(batched_ocr_results)}")
        return

    extracted_pages_data = []
    cumulative_page_index = 0

    print(f"Found {len(batched_ocr_results)} batch(es) in the OCR results.")

    for batch_idx, document_batch_dict in enumerate(batched_ocr_results):
        print(f"  Processing Batch {batch_idx + 1}...")
        
        # The full text for this batch
        batch_full_text = document_batch_dict.get('text', '')
        
        if 'pages' not in document_batch_dict or not isinstance(document_batch_dict['pages'], list):
            print(f"    Warning: Batch {batch_idx + 1} has no 'pages' list or it's not a list. Skipping this batch.")
            continue

        for page_dict in document_batch_dict['pages']:
            original_page_number = page_dict.get('pageNumber')
            if original_page_number is None:
                print(f"    Warning: Page in Batch {batch_idx + 1} missing 'pageNumber'. Assigning sequential index {cumulative_page_index + 1}.")
                original_page_number = f"(Sequential Index {cumulative_page_index + 1})"
            
            # The primary source of text for a page should be its blocks/paragraphs/lines layouts.
            # Concatenate text from all paragraphs on the page.
            page_text_parts = []
            if 'paragraphs' in page_dict and isinstance(page_dict['paragraphs'], list):
                for para_layout in page_dict['paragraphs']:
                    if 'layout' in para_layout:
                        page_text_parts.append(layout_to_text(para_layout['layout'], batch_full_text))
            elif 'blocks' in page_dict and isinstance(page_dict['blocks'], list):
                # Fallback to blocks if paragraphs are not present or empty
                for block_layout in page_dict['blocks']:
                    if 'layout' in block_layout:
                        page_text_parts.append(layout_to_text(block_layout['layout'], batch_full_text))
            else:
                 # If no paragraphs or blocks, attempt to get text from the page's own layout (if any)
                 # This might be less common for full page text, but worth a try.
                 if 'layout' in page_dict:
                    page_text_parts.append(layout_to_text(page_dict['layout'], batch_full_text))
                 else:
                    print(f"    Warning: Page {original_page_number} in Batch {batch_idx + 1} has no paragraphs, blocks, or page layout to extract text from.")
            
            full_page_text = "\n".join(page_text_parts).strip()

            extracted_pages_data.append({
                "original_page_number": original_page_number,
                "text": full_page_text
            })
            cumulative_page_index += 1
        
        print(f"  Finished processing Batch {batch_idx + 1}.")

    # Ensure output directory exists
    os.makedirs(EXTRACTED_TEXT_OUTPUT_DIR, exist_ok=True)

    try:
        with open(EXTRACTED_TEXT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(extracted_pages_data, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully extracted text from {cumulative_page_index} page(s).")
        print(f"Cleaned text saved to: {EXTRACTED_TEXT_FILE_PATH}")
    except Exception as e:
        print(f"Error writing extracted text to {EXTRACTED_TEXT_FILE_PATH}: {e}")

if __name__ == "__main__":
    main() 