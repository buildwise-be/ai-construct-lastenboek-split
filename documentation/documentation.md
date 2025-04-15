# AI Construct PDF Splitter Documentation

## Overview
The AI Construct PDF Splitter is a specialized tool designed to process construction specification documents (lastenboeken), particularly targeting non-VMSW (Flemish Social Housing Company) documents. The application analyzes PDF documents, extracts their table of contents, categorizes the content using Google's Gemini AI, and splits the document into separate PDFs based on identified categories.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Setup](#setup)
4. [User Interface](#user-interface)
5. [Processing Pipeline](#processing-pipeline)
6. [Command Line Usage](#command-line-usage)
7. [Output Files](#output-files)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: Minimum 4GB recommended
- **Storage**: At least 500MB of free space for the application and its outputs
- **Internet Connection**: Required for Google Vertex AI integration

## Installation

### Step 1: Clone or Download the Repository
Download the repository to your local machine.

### Step 2: Install Required Dependencies
Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

The application requires the following main packages:
- `pandas`: For data manipulation
- `python-dotenv`: For environment variable management
- `PyPDF2`: For PDF processing
- `google-cloud-aiplatform`: For Google Vertex AI integration
- `google-generativeai`: For using Google Generative AI models
- `PyMuPDF`: For advanced PDF processing
- `PySide6`: For the graphical user interface

### Step 3: Install Google Cloud CLI
Install the Google Cloud CLI by following the instructions at [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

#### For Windows:
1. Download the Google Cloud SDK installer
2. Run the downloaded GoogleCloudSDKInstaller.exe file
3. Follow the installation prompts
4. When complete, the installer will open a terminal to run `gcloud init`

#### For macOS/Linux:
1. Download the appropriate package
2. Extract the archive to your preferred location
3. Run the installation script: `./google-cloud-sdk/install.sh`
4. Initialize the SDK: `./google-cloud-sdk/bin/gcloud init`

### Step 4: Set Up Google Cloud Authentication
Run the following commands to set up authentication:

```bash
pip install --upgrade google-genai
gcloud auth application-default login
```

## Setup

### Google Cloud Project
You need a Google Cloud project with the Vertex AI API enabled:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Enable the Vertex AI API for your project via the API library
4. Connect billing information to your Google Cloud project (required even within the free usage tier)

### Setting Project ID
There are two ways to set your Google Cloud Project ID:

1. **Environment Variable**: Create a `.env` file in the project root with:
   ```
   GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

2. **User Interface**: Enter the project ID directly in the application's user interface

### Category Definition File
The script uses a category definition file to match document sections to predefined categories:

- Default file: `nonvmswhoofdstukken_pandas.py` (located in the same directory as the script)
- Required structure: The file must have the same structure as the example file `example_categories.py`
- Custom files: You can modify the example file or create a new file (Python module, Excel, or CSV) following the required structure
- File selection: Select the file through the user interface or command line

## User Interface

### Launching the Application
Run the script from the project's root directory:

```bash
python main_script.py
```

### Main Interface Sections

#### Input Section
- **PDF File**: Select the input PDF construction specification document
- **Category File**: Choose the category definition file
- **Base Output Directory**: Select where to save output files
- **Additional Output Directories**: Optionally select separate directories for PDF outputs
- **Google Cloud Project ID**: Enter your Google Cloud project ID
- **Gemini Model**: Choose the Gemini AI model version (e.g., 1.5 Pro, 2.0 Flash)

#### Process Controls
- **Run Step 1**: Extract the table of contents only
- **Run Step 2**: Perform category matching only (requires Step 1 to be completed)
- **Run Step 3**: Generate category-specific PDFs only (requires Steps 1 and 2 to be completed)
- **Run Complete Pipeline**: Process all steps in sequence

#### Progress Section
- Visual indicators of the current processing status
- Progress bar for ongoing operations

#### Log Section
- Text area displaying processing messages and progress updates

#### Output Section
- View and access generated output files

## Processing Pipeline

### Step 1: Table of Contents (TOC) Generation
This step extracts chapters and sections from the input PDF document:

1. Analyzes the PDF document
2. Identifies chapter headings and section titles
3. Creates a structured representation of the document's table of contents
4. Generates JSON and CSV files containing the extracted structure

### Step 2: Category Matching
Uses Google Gemini AI via Vertex AI to match the identified chapters and sections against predefined categories:

1. Sends each chapter and section title to the Gemini AI model
2. The AI analyzes and matches content to the most appropriate category
3. Results are saved in JSON and CSV formats
4. Provides matching confidence scores and explanations (if enabled)

### Step 3: Document Splitting
Creates separate PDF files for each category, containing the relevant pages from the original document:

1. Uses the category matching results to determine which pages belong to which categories
2. Extracts the appropriate page ranges from the original PDF
3. Creates individual PDF files for each category
4. Generates multiple copies in different output directories if specified

## Command Line Usage
For advanced users, the tool supports command line operation.

### Complete Pipeline
```bash
python main_script.py <pdf_path> [-c <category_file>] [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] [--model <model_name>] [--no-explanations] [--no-gui]
```

### Individual Steps
```bash
# Run Step 1 (TOC Generation)
python main_script.py <pdf_path> [-o <output_dir>] step1 --no-gui

# Run Step 2 (Category Matching)
python main_script.py <pdf_path> -c <category_file> -i <toc_dir_from_step1> [-o <output_dir>] [--model <model_name>] step2 --no-gui

# Run Step 3 (PDF Extraction)
python main_script.py <pdf_path> -c <category_file> -i <category_match_dir_from_step2> [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] step3 --no-gui
```

For help with command line options:
```bash
python main_script.py --help
```

## Output Files
The script creates timestamped output directories for each execution:

### Step 1 Output (TOC Generation)
- `chapters.json`: Extracted chapters and their page ranges
- `sections.json`: Extracted sections and their page ranges
- `toc.csv`: CSV representation of the table of contents

### Step 2 Output (Category Matching)
- `chapter_results.json`: Category matching results for chapters
- `section_results.json`: Category matching results for sections
- `category_matches.csv`: CSV summarizing all category matches
- `category_statistics.json`: Statistics about category distribution

### Step 3 Output (PDF Extraction)
- Individual PDF files named according to their categories
- Multiple copies in different directories if specified

## Troubleshooting

### Google Cloud Authentication Issues
- Ensure you've run `gcloud auth application-default login`
- Verify your Google Cloud project has the Vertex AI API enabled
- Check that your project ID is correctly set in the application or `.env` file

### PDF Processing Issues
- Make sure the PDF is not encrypted or password-protected
- For large PDFs, allow more processing time
- If the TOC extraction fails, try using a PDF with a clearer structure

### AI Categorization Problems
- Check that your category definition file follows the required structure
- Try using a different Gemini model version
- Review the category matches and adjust the category definitions if needed

## FAQ

### Q: How accurate is the AI categorization?
A: The accuracy depends on the quality of the input document and the category definitions. The Gemini AI model provides high accuracy for well-structured documents with clear chapter and section titles that match the predefined categories.

### Q: Can I process documents in languages other than Dutch?
A: Yes, the system can process documents in multiple languages, as the Gemini AI model supports multilingual understanding. However, you may need to adjust the category definitions to match the language of your documents.

### Q: How large of a PDF can the system handle?
A: The system can process PDFs of various sizes, but very large documents (hundreds of pages) may require more processing time. There is no hard limit, but performance may vary based on your system specifications.

### Q: Do I need to pay for using the Google Vertex AI services?
A: Google Cloud provides a free tier for Vertex AI with certain usage limits. Beyond those limits, charges may apply. Check the [Google Cloud pricing page](https://cloud.google.com/vertex-ai/pricing) for current details.

### Q: Can I customize the categories?
A: Yes, you can modify the category definition file to include custom categories that match your specific needs. Follow the structure of the `example_categories.py` file when creating your own categories. 