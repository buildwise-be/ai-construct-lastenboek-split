import json
import re

def parse_heading(heading_text):
    """
    Parses a heading string like "00.10. PROJECTGEGEVENS" or "01. TITLE".
    Returns a tuple: (number_str, title_str, level).
    - number_str: The numeric part (e.g., "00.10", "01").
    - title_str: The textual part of the title.
    - level: The hierarchical level (1 for "XX", 2 for "XX.YY", etc.).
    Returns (None, None, 0) if the heading_text does not match the expected numbered format.
    """
    # Regex to capture "XX", "XX.YY", "XX.YY.ZZ" etc., followed by a title.
    # It allows an optional dot after the number part.
    match = re.match(r"(\d{2,}(?:\.\d{2,})*)\.?\s+(.*)", heading_text.strip())
    if match:
        number_str = match.group(1)
        title_str = match.group(2).strip()
        level = number_str.count('.') + 1
        return number_str, title_str, level
    return None, None, 0

def group_text_by_chapter_section(ocr_data_path):
    """
    Parses OCR JSON data and groups text content by chapters and sections
    based on numbered headings (e.g., "00. Chapter", "00.10. Section").

    Args:
        ocr_data_path (str): Path to the OCR JSON file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              top-level chapter. Chapters contain their content and a list
              of sections, which can also contain subsections, and so on.
              Structure of each item:
              {
                  "number": "XX.YY",
                  "title": "Section Title",
                  "level": 2,
                  "content": "Aggregated text content...",
                  "sections": [ ... nested items ... ]
              }
    """
    try:
        with open(ocr_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {ocr_data_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {ocr_data_path}")
        return []

    structured_document = []
    # path_to_current_item_dicts stores the actual dictionary objects in the current hierarchy
    path_to_current_item_dicts = []

    for page_data in data.get("pages", []):
        # page_num = page_data.get("page") # Available if needed for context
        for item in page_data.get("items", []):
            item_type = item.get("type")
            item_value = item.get("value", "").strip()

            if not item_value: # Skip empty items
                continue

            if item_type == "heading":
                number_str, title_str, level = parse_heading(item_value)

                if number_str:  # It's a structured, numbered heading
                    # Adjust the path to find the correct parent for this new heading
                    # Pop items from the path if their level is >= the current heading's level
                    while path_to_current_item_dicts and path_to_current_item_dicts[-1]['level'] >= level:
                        path_to_current_item_dicts.pop()

                    new_structured_item = {
                        "number": number_str,
                        "title": title_str,
                        "level": level,
                        "content": "",  # Text directly under this heading
                        "sections": []  # For child sections/subsections
                    }

                    if not path_to_current_item_dicts:  # This is a top-level chapter
                        structured_document.append(new_structured_item)
                    else:  # This is a nested section/subsection
                        parent_item_dict = path_to_current_item_dicts[-1]
                        parent_item_dict["sections"].append(new_structured_item)
                    
                    path_to_current_item_dicts.append(new_structured_item)
                
                else:  # Un-numbered heading (e.g., "BOUWPLAATS")
                    # Append its text as a specially marked part of the content
                    # of the current lowest-level structured item.
                    if path_to_current_item_dicts:
                        current_item_dict = path_to_current_item_dicts[-1]
                        # Using a Markdown-like format for these subheadings within content
                        current_item_dict["content"] += f"\n\n### {item_value}\n\n" 
                    # else:
                        # Un-numbered heading appears before any numbered heading.
                        # Could be collected into a preamble or a default top-level item.
                        # For now, such un-anchored headings are not added to the structured_document.
                        # print(f"Warning: Un-numbered heading '{item_value}' found before any structured chapter/section.")
                        pass

            elif item_type == "text":
                if path_to_current_item_dicts:
                    current_item_dict = path_to_current_item_dicts[-1]
                    current_item_dict["content"] += item_value + "\n"
                # else:
                    # Text appears before any structured heading.
                    # Could be collected into a preamble.
                    # print(f"Warning: Text '{item_value[:50]}...' found before any structured chapter/section.")
                    pass
    
    # Clean up leading/trailing whitespace from content fields recursively
    def cleanup_content_whitespace(item_list):
        for item_dict in item_list:
            if "content" in item_dict:
                item_dict["content"] = item_dict["content"].strip()
            if "sections" in item_dict and item_dict["sections"]:
                cleanup_content_whitespace(item_dict["sections"])

    cleanup_content_whitespace(structured_document)
    
    return structured_document

# Example of how to use the function:
# if __name__ == "__main__":
#     # Replace with the actual path to your JSON file
#     # Ensure the Llamaocr directory is in the same directory as this script,
#     # or provide an absolute path.
#     json_file_path = "Llamaocr/amsterdamlb.json" 
#     grouped_data = group_text_by_chapter_section(json_file_path)
    
#     if grouped_data:
#         output_json_path = "Llamaocr/amsterdamlb_structured.json"
#         with open(output_json_path, 'w', encoding='utf-8') as outfile:
#             json.dump(grouped_data, outfile, indent=2, ensure_ascii=False)
#         print(f"Structured data written to {output_json_path}")
#     else:
#         print("No structured data was generated.") 