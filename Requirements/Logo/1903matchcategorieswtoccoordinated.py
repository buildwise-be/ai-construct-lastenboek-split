"""
Script to match chapters and sections from construction specification documents to categories.

This script processes chapters and sections from a construction specification document
(lastenboek) and matches them to relevant categories using Google's Gemini API.
It calculates confidence scores for each match and generates various output files 
including CSV reports, JSON data files, and a category-centric Markdown report.

Dependencies:
    - pandas
    - google.generativeai
    - nonvmswhoofdstukken_pandas (custom module)
"""

import pandas as pd
import google.generativeai as genai
import os
import json
import datetime
import sys
from dotenv import load_dotenv
import logging

# Add the directory containing nonvmswhoofdstukken_pandas.py to the Python path
# Adjust this path to the actual location of the nonvmswhoofdstukken_pandas.py file
module_dir = r"C:\Users\gr\localcoding\Local\AICO\Post-Kickoff\Opdeling Lastenboeken\2. Non-VMSW"
if module_dir not in sys.path:
    sys.path.append(module_dir)
    print(f"Added {module_dir} to Python path")

# Now try to import the module
try:
    from nonvmswhoofdstukken_pandas import df_indexed, df
    print("Successfully imported nonvmswhoofdstukken_pandas")
except ImportError as e:
    print(f"Error importing nonvmswhoofdstukken_pandas: {str(e)}")
    print("Current sys.path:", sys.path)
    print("Please check if nonvmswhoofdstukken_pandas.py exists in one of these directories")
    exit(1)

# Load environment variables (for Gemini API key)
load_dotenv()

# Load chapters from JSON file instead of importing from Python module
json_file_path = r"C:\Users\gr\localcoding\Local\AICO\Post-Kickoff\Opdeling Lastenboeken\2. Non-VMSW\output\20250318_1403tocgeneratornotvmws\1403tocgeneratornotvmws_CoordinatedArchitectlastenboek_analysis_20250318_1.json"

# Load the chapters data from JSON file
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)
    print(f"Successfully loaded chapters data from: {json_file_path}")
except Exception as e:
    print(f"Error loading chapters data from JSON file: {str(e)}")
    exit(1)

# Configure the Gemini API using only environment variables
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Please set the GEMINI_API_KEY environment variable with your API key.")
    exit(1)
genai.configure(api_key=api_key)

# Set up output directory
def setup_output_directory():
    """
    Create an output directory structure with the current date and script name.
    Returns the path to the output directory.
    """
    # Get current date in YYYYMMDD format
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    
    # Get script name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # Create output directory path
    output_dir = os.path.join("output", f"{current_date}_{script_name}")
    
    # Create the directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory created: {output_dir}")
    return output_dir

# Try to initialize the Gemini model
def initialize_gemini_model():
    """
    Initialize the Gemini generative AI model.
    
    This function attempts to initialize a Gemini model by trying different model versions
    in case some are not available. It tests each model with a simple generation request
    to ensure it's working properly.
    
    Returns:
        GenerativeModel: An initialized Gemini model instance if successful, None otherwise
    """
    model = None
    models_to_try = ['gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-pro', 'gemini-1.0-pro', 'text-bison']

    for model_name in models_to_try:
        try:
            print(f"Trying to initialize model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Test if model works
            response = model.generate_content("Test")
            print(f"Successfully initialized model: {model_name}")
            break
        except Exception as e:
            print(f"Failed to initialize model {model_name}: {str(e)}")

    if model is None:
        print("Failed to initialize any Gemini model. Please check your API key or try again later.")
        exit(1)
        
    return model

# Initialize the model
model = initialize_gemini_model()

# Define a confidence threshold for considering a category relevant
RELEVANCE_THRESHOLD = 50  # Minimum confidence score to consider a category relevant

def match_to_multiple_categories(title, content_dict=None, is_section=False):
    """
    Use Gemini to match content to multiple relevant categories from nonvmswhoofdstukken_pandas.
    
    Args:
        title (str): The title of the chapter or section
        content_dict (dict, optional): Dictionary with additional content information
        is_section (bool): Whether this is a section (True) or chapter (False)
    
    Returns:
        list: List of dictionaries with matched categories and confidence scores
    """
    # Create a formatted text with the content information
    content_type = "Section" if is_section else "Chapter"
    
    if content_dict and 'start' in content_dict and 'end' in content_dict:
        page_range = f"Pages: {content_dict['start']}-{content_dict['end']}"
    else:
        page_range = "Pages: Unknown"
    
    section_texts = []
    if content_dict and 'sections' in content_dict:
        section_texts = [f"- {section_id}: {section_data['title']}" for section_id, section_data in content_dict['sections'].items()]
    
    formatted_content = f"{content_type}: {title}\n{page_range}\n" + "\n".join(section_texts)
    
    # Create a list of all available categories with their expanded descriptions
    categories_info = []
    for idx, row in df.iterrows():
        categories_info.append(f"Category: {row['summary']}\nDescription: {row['expanded_description']}")
    
    formatted_categories = "\n\n".join(categories_info)
    
    # Create the prompt for Gemini
    prompt = f"""
    I have a {content_type.lower()} from a construction specification document (lastenboek) and need to match it to ALL relevant categories.

    The {content_type.lower()} information is:
    {formatted_content}
    
    The available categories are:
    {formatted_categories}
    
    Please analyze the content and determine ALL categories that are relevant matches, not just the single best match.
    Consider the topics, terminology, and concepts in both the {content_type.lower()} and categories.
    
    Assign a confidence score (0-100) to each relevant category based on how closely it matches.
    Only include categories with a relevance score of {RELEVANCE_THRESHOLD} or higher.
    
    Return your answer in the following format:
    Category: [category name 1]
    Confidence: [score between 0-100]
    Explanation: [brief explanation of why this category is relevant]
    
    Category: [category name 2]
    Confidence: [score between 0-100]
    Explanation: [brief explanation of why this category is relevant]
    
    ...and so on for all relevant categories.
    """
    
    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text
        print(f"Raw response for {title}: {response_text[:100]}...")
        
        # Split the response into category blocks
        # Each block starts with "Category:" and contains info about one category
        category_blocks = []
        current_block = []
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith("Category:") and current_block:
                category_blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                if line:  # Only add non-empty lines
                    current_block.append(line)
        
        # Add the last block
        if current_block:
            category_blocks.append('\n'.join(current_block))
        
        # Process each category block
        matches = []
        for block in category_blocks:
            # Extract category name
            category_line = [line for line in block.split('\n') if line.startswith('Category:')]
            if not category_line:
                continue
            category = category_line[0].replace('Category:', '').strip()
            
            # Extract confidence
            confidence_line = [line for line in block.split('\n') if line.startswith('Confidence:')]
            confidence = 0
            if confidence_line:
                confidence_text = confidence_line[0].replace('Confidence:', '').strip()
                # Handle possible formats like "80/100" or just "80"
                if '/' in confidence_text:
                    confidence = int(confidence_text.split('/')[0])
                else:
                    confidence = int(confidence_text)
            
            # Extract explanation
            explanation_line = [line for line in block.split('\n') if line.startswith('Explanation:')]
            explanation = explanation_line[0].replace('Explanation:', '').strip() if explanation_line else ""
            
            # Add to matches if confidence meets threshold
            if confidence >= RELEVANCE_THRESHOLD:
                matches.append({
                    "category": category,
                    "confidence": confidence,
                    "explanation": explanation
                })
        
        # Log the number of matches found
        print(f"Found {len(matches)} relevant categories for '{title}'")
        
        return matches
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return [{
            "category": "Error",
            "confidence": 0,
            "explanation": f"API Error: {str(e)}"
        }]

def process_all_chapters_and_sections():
    """
    Process all chapters and their sections, matching them to categories.
    
    Returns:
        tuple: (chapter_results, section_results) with chapter and section matching results
    """
    chapter_results = {}
    section_results = {}
    
    # Process each chapter
    for chapter_num, chapter_data in chapters.items():
        # Skip chapters with only number identifiers (e.g., chapter "22" inside chapter "21")
        if not (chapter_num.isdigit() and len(chapter_num) == 2):
            continue
            
        print(f"Processing chapter {chapter_num}: {chapter_data['title']}...")
        
        # Match the chapter to categories
        matches = match_to_multiple_categories(chapter_data['title'], chapter_data)
        
        # Store the result
        chapter_results[chapter_num] = {
            "title": chapter_data['title'],
            "start": chapter_data['start'],
            "end": chapter_data['end'],
            "matches": matches
        }
        
        # Process sections within the chapter
        for section_id, section_data in chapter_data['sections'].items():
            print(f"  Processing section {section_id}: {section_data['title']}...")
            
            # Match the section to categories
            section_matches = match_to_multiple_categories(section_data['title'], section_data, is_section=True)
            
            # Store the result
            section_results[f"{chapter_num}_{section_id}"] = {
                "chapter_num": chapter_num,
                "section_id": section_id,
                "title": section_data['title'],
                "start": section_data['start'],
                "end": section_data['end'],
                "matches": section_matches
            }
    
    return chapter_results, section_results

def save_results_to_files(chapter_results, section_results, output_dir):
    """
    Save the matching results to CSV and JSON files.
    
    Args:
        chapter_results (dict): Dictionary with chapter matching results
        section_results (dict): Dictionary with section matching results
        output_dir (str): Directory to save the output files
    """
    # Save chapter results (one row per chapter-category match)
    chapter_output_data = []
    
    for chapter_num, data in chapter_results.items():
        for match in data["matches"]:
            row = {
                "Chapter Number": chapter_num,
                "Chapter Title": data["title"],
                "Pages": f"{data['start']}-{data['end']}",
                "Matched Category": match["category"],
                "Confidence": match["confidence"],
                "Explanation": match["explanation"]
            }
            chapter_output_data.append(row)
            print(f"Added chapter-category match to CSV: Chapter {chapter_num} -> {match['category']} (Confidence: {match['confidence']})")
    
    # Create DataFrame and save to CSV
    chapter_df = pd.DataFrame(chapter_output_data)
    chapter_csv_file = os.path.join(output_dir, "chapter_category_matches.csv")
    chapter_df.to_csv(chapter_csv_file, index=False, encoding='utf-8')
    print(f"Chapter results saved to {chapter_csv_file}")
    
    # Save raw chapter results to JSON
    with open(os.path.join(output_dir, "chapters_raw_matches.json"), 'w', encoding='utf-8') as f:
        json.dump(chapter_results, f, ensure_ascii=False, indent=2)
    print(f"Raw chapter results saved to {os.path.join(output_dir, 'chapters_raw_matches.json')}")
    
    # Save section results (one row per section-category match)
    section_output_data = []
    
    for section_key, data in section_results.items():
        for match in data["matches"]:
            row = {
                "Chapter Number": data["chapter_num"],
                "Section ID": data["section_id"],
                "Section Title": data["title"],
                "Pages": f"{data['start']}-{data['end']}",
                "Matched Category": match["category"],
                "Confidence": match["confidence"],
                "Explanation": match["explanation"]
            }
            section_output_data.append(row)
            print(f"Added section-category match to CSV: Section {data['chapter_num']}.{data['section_id']} -> {match['category']} (Confidence: {match['confidence']})")
    
    # Create DataFrame and save to CSV
    section_df = pd.DataFrame(section_output_data)
    section_csv_file = os.path.join(output_dir, "section_category_matches.csv")
    section_df.to_csv(section_csv_file, index=False, encoding='utf-8')
    print(f"Section results saved to {section_csv_file}")
    
    # Save raw section results to JSON
    with open(os.path.join(output_dir, "sections_raw_matches.json"), 'w', encoding='utf-8') as f:
        json.dump(section_results, f, ensure_ascii=False, indent=2)
    print(f"Raw section results saved to {os.path.join(output_dir, 'sections_raw_matches.json')}")
    
    # Create a category-centric view (what sections are in each category)
    category_sections = {}
    for section_key, data in section_results.items():
        for match in data["matches"]:
            category = match["category"]
            if category not in category_sections:
                category_sections[category] = []
            
            category_sections[category].append({
                "chapter_num": data["chapter_num"],
                "section_id": data["section_id"],
                "title": data["title"],
                "pages": f"{data['start']}-{data['end']}",
                "confidence": match["confidence"]
            })
    
    # Save category-centric view to JSON
    with open(os.path.join(output_dir, "category_sections.json"), 'w', encoding='utf-8') as f:
        json.dump(category_sections, f, ensure_ascii=False, indent=2)
    print(f"Category-centric view saved to {os.path.join(output_dir, 'category_sections.json')}")

def generate_category_report(output_dir):
    """
    Generate a textual report showing which sections are in each category.
    Saves the report to a text file in the specified output directory.
    
    Args:
        output_dir (str): Directory to save the output files
    """
    # Load the category-sections mapping
    try:
        with open(os.path.join(output_dir, "category_sections.json"), 'r', encoding='utf-8') as f:
            category_sections = json.load(f)
        
        report_lines = ["# Category to Sections Mapping Report", ""]
        
        # Sort categories by name
        for category in sorted(category_sections.keys()):
            report_lines.append(f"## Category: {category}")
            report_lines.append("")
            
            # Sort sections by chapter and section ID
            sections = sorted(category_sections[category], 
                key=lambda x: (x["chapter_num"], x["section_id"]))
            
            for section in sections:
                report_lines.append(f"- Chapter {section['chapter_num']}, Section {section['section_id']}: " +
                                    f"{section['title']} (Pages {section['pages']}, Confidence: {section['confidence']})")
            
            report_lines.append("")  # Add a blank line between categories
        
        # Write the report to a file
        report_file = os.path.join(output_dir, "category_sections_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        
        print(f"Category report saved to {report_file}")
    except Exception as e:
        print(f"Failed to generate category report: {str(e)}")

# Print alle categorienamen na het importeren
print("Lijst van categorieën:")
for idx, row in df.iterrows():
    print(f"- {row['summary']}")

if __name__ == "__main__":
    """
    Main execution block of the script.
    
    This is the entry point of the script that performs the following steps:
    1. Sets up an output directory based on current date and script name
    2. Processes all chapters and sections, matching them to categories
    3. Saves the matching results to various output files
    4. Generates a category-centric report
    5. Prints summary information about the matches
    """
    print("Starting chapter and section to category matching...")
    
    # Set up output directory
    output_dir = setup_output_directory()
    
    chapter_results, section_results = process_all_chapters_and_sections()
    save_results_to_files(chapter_results, section_results, output_dir)
    generate_category_report(output_dir)
    print("Matching complete!")

    # Print a summary of the chapter matches
    print("\nSummary of chapter matches:")
    for chapter_num, data in chapter_results.items():
        print(f"Chapter {chapter_num}: '{data['title']}' (Pages {data['start']}-{data['end']}):")
        for match in data["matches"]:
            print(f"  - {match['category']} (Confidence: {match['confidence']})")
    
    # Print a brief summary of section matches (limit to first 5 chapters to avoid overwhelming output)
    print(f"\nSummary of section matches (sample):")
    chapter_count = 0
    for chapter_num in sorted(chapters.keys()):
        if not (chapter_num.isdigit() and len(chapter_num) == 2):
            continue
            
        if chapter_count >= 5:
            break
            
        print(f"\nChapter {chapter_num}:")
        chapter_count += 1
        
        section_count = 0
        for section_key, data in section_results.items():
            if data["chapter_num"] == chapter_num:
                if section_count >= 3:  # Limit to 3 sections per chapter
                    continue
                    
                print(f"  Section {data['section_id']}: '{data['title']}' (Pages {data['start']}-{data['end']}):")
                for match in data["matches"]:
                    print(f"    - {match['category']} (Confidence: {match['confidence']})")
                    
                section_count += 1 