import os
import json
from typing import Optional, Sequence

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import PyPDF2 # Added for PDF page counting

# Configuration
PROJECT_ID = "47863365217"
LOCATION = "eu"  # Must be 'us' or 'eu'
PROCESSOR_ID = "db6cc31835f6518d"
PROCESSOR_VERSION = "stable"  # Use "stable", "rc", or a specific version
FILE_PATH = "C:\\Users\\gr\\Documents\\GitHub\\ExtendedToC\\Lastenboeken\\CoordinatedArchitectlastenboek.pdf"
MIME_TYPE = "application/pdf"
OUTPUT_DIR = "output/google_ocr"
BASE_FILENAME = os.path.basename(FILE_PATH)
OUTPUT_FILENAME = f"{os.path.splitext(BASE_FILENAME)[0]}_ocr_result.json"
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
PAGE_BATCH_SIZE = 15


def get_pdf_page_count(file_path: str) -> int:
    """Counts the number of pages in a PDF file."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)
    except Exception as e:
        print(f"Error reading PDF for page count: {e}")
        raise


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )


def print_page_dimensions(dimension: documentai.Document.Page.Dimension) -> None:
    print(f"    Width: {dimension.width}")
    print(f"    Height: {dimension.height}")


def print_detected_languages(
    detected_languages: Sequence[documentai.Document.Page.DetectedLanguage],
) -> None:
    print("    Detected languages:")
    for lang in detected_languages:
        print(f"        {lang.language_code} ({lang.confidence:.1%})")


def print_blocks(blocks: Sequence[documentai.Document.Page.Block], text: str) -> None:
    print(f"    {len(blocks)} blocks detected:")
    if not blocks:
        return
    first_block_text = layout_to_text(blocks[0].layout, text)
    print(f"        First block text: {repr(first_block_text)}")
    last_block_text = layout_to_text(blocks[-1].layout, text)
    print(f"        Last block text: {repr(last_block_text)}")


def print_paragraphs(
    paragraphs: Sequence[documentai.Document.Page.Paragraph], text: str
) -> None:
    print(f"    {len(paragraphs)} paragraphs detected:")
    if not paragraphs:
        return
    first_paragraph_text = layout_to_text(paragraphs[0].layout, text)
    print(f"        First paragraph text: {repr(first_paragraph_text)}")
    last_paragraph_text = layout_to_text(paragraphs[-1].layout, text)
    print(f"        Last paragraph text: {repr(last_paragraph_text)}")


def print_lines(lines: Sequence[documentai.Document.Page.Line], text: str) -> None:
    print(f"    {len(lines)} lines detected:")
    if not lines:
        return
    first_line_text = layout_to_text(lines[0].layout, text)
    print(f"        First line text: {repr(first_line_text)}")
    last_line_text = layout_to_text(lines[-1].layout, text)
    print(f"        Last line text: {repr(last_line_text)}")


def print_tokens(tokens: Sequence[documentai.Document.Page.Token], text: str) -> None:
    print(f"    {len(tokens)} tokens detected:")
    if not tokens:
        return
    first_token_text = layout_to_text(tokens[0].layout, text)
    first_token_break_type = tokens[0].detected_break.type_.name
    print(f"        First token text: {repr(first_token_text)}")
    print(f"        First token break type: {repr(first_token_break_type)}")
    if tokens[0].style_info:
        print_style_info(tokens[0].style_info)

    last_token_text = layout_to_text(tokens[-1].layout, text)
    last_token_break_type = tokens[-1].detected_break.type_.name
    print(f"        Last token text: {repr(last_token_text)}")
    print(f"        Last token break type: {repr(last_token_break_type)}")
    if tokens[-1].style_info:
        print_style_info(tokens[-1].style_info)


def print_symbols(
    symbols: Sequence[documentai.Document.Page.Symbol], text: str
) -> None:
    print(f"    {len(symbols)} symbols detected:")
    if not symbols:
        return
    first_symbol_text = layout_to_text(symbols[0].layout, text)
    print(f"        First symbol text: {repr(first_symbol_text)}")
    last_symbol_text = layout_to_text(symbols[-1].layout, text)
    print(f"        Last symbol text: {repr(last_symbol_text)}")


def print_image_quality_scores(
    image_quality_scores: documentai.Document.Page.ImageQualityScores,
) -> None:
    print(f"    Quality score: {image_quality_scores.quality_score:.1%}")
    print("    Detected defects:")

    for detected_defect in image_quality_scores.detected_defects:
        print(f"        {detected_defect.type_}: {detected_defect.confidence:.1%}")


def print_style_info(style_info: documentai.Document.Page.Token.StyleInfo) -> None:
    """
    Only supported in version `pretrained-ocr-v2.0-2023-06-02` or later.
    """
    print(f"           Font Size: {style_info.font_size}pt")
    print(f"           Font Type: {style_info.font_type}")
    print(f"           Bold: {style_info.bold}")
    print(f"           Italic: {style_info.italic}")
    print(f"           Underlined: {style_info.underlined}")
    print(f"           Handwritten: {style_info.handwritten}")
    print(
        f"           Text Color (RGBa): {style_info.text_color.red}, {style_info.text_color.green}, {style_info.text_color.blue}, {style_info.text_color.alpha}"
    )


def print_visual_elements(
    visual_elements: Sequence[documentai.Document.Page.VisualElement], text: str
) -> None:
    """
    Only supported in version `pretrained-ocr-v2.0-2023-06-02` or later.
    """
    checkboxes = [x for x in visual_elements if "checkbox" in x.type]
    math_symbols = [x for x in visual_elements if x.type == "math_formula"]

    if checkboxes:
        print(f"    {len(checkboxes)} checkboxes detected:")
        if checkboxes[0].detected_checkbox.checkbox_type == documentai.Document.Page.VisualElement.DetectedCheckbox.CheckboxType.CHECKBOX_TYPE_UNSPECIFIED:
            print("        (Checkbox type unspecified)")
        else:
            print(f"        First checkbox type: {checkboxes[0].detected_checkbox.checkbox_type.name}")
            print(f"        First checkbox checked: {checkboxes[0].detected_checkbox.checked}")


    if math_symbols:
        print(f"    {len(math_symbols)} math symbols detected:")
        first_math_symbol_text = layout_to_text(math_symbols[0].layout, text)
        print(f"        First math symbol: {repr(first_math_symbol_text)}")


def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    file_path: str,
    mime_type: str,
    process_options: Optional[documentai.ProcessOptions] = None,
) -> documentai.Document:
    # You must set the `api_endpoint` if you use a location other than "us".
    client_options = {}
    if location != "us":
      client_options = ClientOptions(
          api_endpoint=f"{location}-documentai.googleapis.com"
      )

    client = documentai.DocumentProcessorServiceClient(
        client_options=client_options
    )

    name = client.processor_version_path(
        project_id, location, processor_id, processor_version
    )

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
        process_options=process_options,
    )

    result = client.process_document(request=request)
    return result.document


def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Processing document: {FILE_PATH}")
    print(f"Output will be saved to: {OUTPUT_FILE_PATH}")

    try:
        total_pages = get_pdf_page_count(FILE_PATH)
        print(f"Total pages in PDF: {total_pages}")
    except Exception as e:
        print(f"Could not determine page count. Aborting. Error: {e}")
        return

    all_processed_document_batches = []
    all_text_parts = []

    try:
        for start_page in range(1, total_pages + 1, PAGE_BATCH_SIZE):
            end_page = min(start_page + PAGE_BATCH_SIZE - 1, total_pages)
            current_batch_pages = list(range(start_page, end_page + 1))
            
            print(f"\nProcessing batch: Pages {start_page} to {end_page}")

            process_options = documentai.ProcessOptions(
                individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
                    pages=current_batch_pages
                )
            )

            document_batch = process_document(
                project_id=PROJECT_ID,
                location=LOCATION,
                processor_id=PROCESSOR_ID,
                processor_version=PROCESSOR_VERSION,
                file_path=FILE_PATH,
                mime_type=MIME_TYPE,
                process_options=process_options,
            )
            
            all_processed_document_batches.append(document_batch)
            if document_batch.text:
                all_text_parts.append(document_batch.text)
            
            print(f"Batch (Pages {start_page}-{end_page}) processing complete. Text found: {len(document_batch.text)} characters.")

        if not all_processed_document_batches:
            print("No document batches were processed.")
            return

        print(f"\nAll {len(all_processed_document_batches)} batches processed.")
        
        # Save the list of Document objects (converted to dicts) as JSON
        from google.protobuf.json_format import MessageToDict
        
        documents_data_to_save = [MessageToDict(doc._pb) for doc in all_processed_document_batches]

        with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(documents_data_to_save, f, ensure_ascii=False, indent=4)
        print(f"Full OCR result (all batches) saved to {OUTPUT_FILE_PATH}")

        # Print a summary of all processed document batches
        print("\n--- Combined Document Summary (Aggregated from Batches) ---")
        
        total_pages_processed_api = sum(len(doc_batch.pages) for doc_batch in all_processed_document_batches)
        print(f"Total pages processed according to API responses: {total_pages_processed_api}")
        
        combined_text_sample = (" ... ".join(all_text_parts))[:1000]
        print(f"Sample of combined text from all batches: {repr(combined_text_sample)}...")


        for batch_idx, document_batch_content in enumerate(all_processed_document_batches):
            print(f"\n--- Summary for Batch {batch_idx + 1} (Original Pages {document_batch_content.pages[0].page_number if document_batch_content.pages else 'N/A'} - {document_batch_content.pages[-1].page_number if document_batch_content.pages else 'N/A'}) ---")
            if document_batch_content.uri: # URI might not be set for batches
                print(f"Document URI (for batch): {document_batch_content.uri}")
            if document_batch_content.mime_type:
                print(f"MIME type (for batch): {document_batch_content.mime_type}")

            print(f"Number of pages in this batch: {len(document_batch_content.pages)}")

            for i, page in enumerate(document_batch_content.pages):
                # Page numbers printed here are as reported by the API for this batch
                print(f"\n--- Page (Original Page Number: {page.page_number}, Index in Batch: {i + 1}) ---")
                if page.dimension:
                    print_page_dimensions(page.dimension)
                if page.detected_languages:
                    print_detected_languages(page.detected_languages)
                if hasattr(page, 'image_quality_scores') and page.image_quality_scores: # Check attribute existence
                    print_image_quality_scores(page.image_quality_scores)

                print_blocks(page.blocks, document_batch_content.text)
                print_paragraphs(page.paragraphs, document_batch_content.text)
                print_lines(page.lines, document_batch_content.text)
                print_tokens(page.tokens, document_batch_content.text)
                if hasattr(page, 'visual_elements') and page.visual_elements: # Check attribute existence
                    print_visual_elements(page.visual_elements, document_batch_content.text)
        
        print("\n--- End of Combined Summary ---")

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 