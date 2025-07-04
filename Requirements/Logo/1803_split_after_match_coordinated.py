"""
PDF Document Extraction Based on 55 Construction Categories

This script extracts portions of a large PDF document into separate PDF files,
with each file containing pages related to a specific construction category.
The categories are loaded from nonvmswhoofdstukken_pandas2.py,
and section-to-category mappings are loaded from a CSV file.
"""

import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import os
import logging
import sys
import datetime  # Add this import for date functionality

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_category_pdfs(original_pdf_path, mappings_file="analysecategorymatch/section_category_matches.csv", output_dir=None):
    """
    Extract pages from a PDF document based on construction categories.
    
    Args:
        original_pdf_path (str): Path to the original PDF file
        mappings_file (str): Path to the CSV file containing section-to-category mappings
        output_dir (str): Directory to save the extracted PDFs
    
    Returns:
        int: Number of category PDFs successfully created
    """
    # Set default output directory if not provided
    if output_dir is None:
        # Get current date and script name for the subdirectory
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        script_name = os.path.basename(__file__).replace('.py', '')
        output_dir = os.path.join("output", f"{current_date}_{script_name}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Load the category mappings
    try:
        category_mappings = pd.read_csv(mappings_file)
        logger.info(f"Loaded category mappings from {mappings_file}")
    except Exception as e:
        logger.error(f"Failed to load category mappings: {e}")
        return 0
    
    # Get the 55 categories from nonvmswhoofdstukken_pandas2.py
    try:
        from nonvmswhoofdstukken_pandas2 import final_categories
        logger.info(f"Loaded {len(final_categories)} categories from nonvmswhoofdstukken_pandas2.py")
    except Exception as e:
        logger.error(f"Failed to load categories: {e}")
        return 0
    
    # Load the PDF
    try:
        reader = PdfReader(original_pdf_path)
        total_pages = len(reader.pages)
        logger.info(f"Loaded PDF with {total_pages} pages")
    except Exception as e:
        logger.error(f"Failed to load PDF: {e}")
        return 0
    
    successful_extractions = 0
    
    # For each category, create a new PDF
    for category_entry in final_categories:
        # Extract the category name (last part after comma)
        parts = category_entry.split(', ')
        category = parts[-1]
        
        # Clean the category name to use as filename
        clean_category = category.replace(' ', '_').replace('&', 'and').replace(',', '')
        
        # Filter the mappings to get relevant sections
        relevant_sections = category_mappings[category_mappings['Matched Category'] == category]
        
        if len(relevant_sections) == 0:
            logger.warning(f"No sections found for category: {category}")
            continue
        
        # Create a new PDF writer
        writer = PdfWriter()
        
        # Track pages already added to avoid duplicates
        added_pages = set()
        
        # Extract page ranges from the 'Pages' column
        for _, row in relevant_sections.iterrows():
            page_range = row['Pages']
            try:
                start_page, end_page = map(int, page_range.split('-'))
                
                # PDF pages are 0-indexed, but our page numbers start at 1
                for page_num in range(start_page - 1, end_page):
                    if page_num >= total_pages:
                        logger.warning(f"Page {page_num+1} out of range for PDF with {total_pages} pages")
                        continue
                        
                    if page_num not in added_pages:
                        writer.add_page(reader.pages[page_num])
                        added_pages.add(page_num)
            except Exception as e:
                logger.error(f"Error processing page range {page_range} for category {category}: {e}")
        
        # Save the new PDF if pages were added
        if added_pages:
            output_path = os.path.join(output_dir, f"{clean_category}.pdf")
            try:
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                logger.info(f"Created {output_path} with {len(added_pages)} pages")
                successful_extractions += 1
            except Exception as e:
                logger.error(f"Failed to write PDF for category {category}: {e}")
        else:
            logger.warning(f"No pages to add for category: {category}")
    
    logger.info(f"Extraction complete. Created {successful_extractions} category PDFs.")
    return successful_extractions

def main():
    """
    Main function to parse arguments and run the extraction.
    """
    # Default path to the PDF file
    default_pdf_path = "example_document.pdf"
    
    # Get current date for finding the most recent output directory
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    
    # Look for the most recent output directory from the match script
    match_script_name = "1703matchcategorieswtoc"
    match_output_dir = os.path.join("output", f"{current_date}_{match_script_name}")
    
    # Default mappings file path (updated to use the match script's output)
    default_mappings_file = os.path.join(match_output_dir, "section_category_matches.csv")
    
    if not os.path.exists(default_mappings_file):
        logger.warning(f"Could not find mappings file at {default_mappings_file}")
        logger.info("Looking for any available mappings file in output directories...")
        
        # Try to find any mappings file in output directories
        output_dir = "output"
        if os.path.exists(output_dir):
            for subdir in sorted(os.listdir(output_dir), reverse=True):
                if match_script_name in subdir:
                    potential_file = os.path.join(output_dir, subdir, "section_category_matches.csv")
                    if os.path.exists(potential_file):
                        default_mappings_file = potential_file
                        logger.info(f"Found mappings file: {default_mappings_file}")
                        break
    
    # If no arguments provided, use the default paths
    if len(sys.argv) == 1:
        logger.info(f"No arguments provided. Using default PDF path: {default_pdf_path}")
        logger.info(f"Using mappings file: {default_mappings_file}")
        extract_category_pdfs(default_pdf_path, default_mappings_file)
    else:
        # Otherwise, use argparse for command-line arguments
        import argparse
        
        parser = argparse.ArgumentParser(description='Extract PDF sections by construction categories')
        parser.add_argument('pdf_path', nargs='?', default=default_pdf_path, 
                            help='Path to the original PDF file')
        parser.add_argument('--output-dir', default=None, 
                            help='Directory to save extracted PDFs (default: output/YYYYMMDD_script_name)')
        parser.add_argument('--mappings-file', default=default_mappings_file, 
                           help='Path to CSV file with section-to-category mappings')
        
        args = parser.parse_args()
        
        extract_category_pdfs(args.pdf_path, args.mappings_file, args.output_dir)

if __name__ == "__main__":
    main()
    
    # Alternatively, uncomment and modify this line to run with hardcoded path:
    # extract_category_pdfs("path/to/your/document.pdf") 