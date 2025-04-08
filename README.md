# AI Construct PDF Opdeler

This project provides a Python script (`split_lastenboek.py`) for processing Non-VMSW (Vlaamse Maatschappij voor Sociaal Wonen) construction specification documents (lastenboeken).

The pipeline performs the following steps:

1.  **Table of Contents (TOC) Generation:** Extracts chapters and sections from the input PDF.
2.  **Category Matching:** Uses Google Gemini AI (via Vertex AI) to match the identified chapters and sections against a predefined set of categories.
3.  **Document Splitting:** Creates separate PDF files for each category, containing the relevant pages from the original document.

## Requirements

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

The script requires the following packages:

-   `pandas`
-   `python-dotenv`
-   `PyPDF2`
-   `google-cloud-aiplatform`
-   `google-generativeai`
-   `PyMuPDF`
-   `PySide6`

## Setup

1.  **Google Cloud:**
    *   You need a Google Cloud project with the Vertex AI API enabled.
    *   Set the `GOOGLE_CLOUD_PROJECT` environment variable to your project ID, or enter it in the GUI.
    *   Ensure you have authenticated your environment (e.g., using `gcloud auth application-default login`).
2.  **Environment Variables:** Create a `.env` file in the project root if you want to store your `GOOGLE_CLOUD_PROJECT` ID there:
    ```
    GOOGLE_CLOUD_PROJECT="your-project-id"
    ```
3.  **Category File:** The script uses a category definition file (`nonvmswhoofdstukken_pandas.py` by default, located in the same directory as the script), but you can specify a different one (Python module, Excel, or CSV) via the GUI or CLI.

## Usage

### Graphical User Interface (GUI)

Run the script directly from the project's root directory (`Cleangit`) to launch the PySide6 GUI:

```bash
python split_lastenboek.py
```

The GUI allows you to:

*   Select the input PDF file.
*   Select the category definition file.
*   Select the base output directory.
*   Optionally select separate PDF output directories.
*   Enter your Google Cloud Project ID (overrides environment variable).
*   Choose the Gemini model (1.5 Pro or 2.0 Flash).
*   Run the complete pipeline or individual steps.

### Command Line Interface (CLI)

You can also run the pipeline or individual steps from the command line from the project's root directory (`Cleangit`).

**Run complete pipeline:**

```bash
python split_lastenboek.py <pdf_path> [-c <category_file>] [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] [--model <model_name>] [--no-explanations] [--no-gui]
```

**Run Step 1 (TOC Generation):**

```bash
python split_lastenboek.py <pdf_path> [-o <output_dir>] step1 --no-gui
```

**Run Step 2 (Category Matching):**

```bash
python split_lastenboek.py <pdf_path> -c <category_file> -i <toc_dir_from_step1> [-o <output_dir>] [--model <model_name>] step2 --no-gui
```

**Run Step 3 (PDF Extraction):**

```bash
python split_lastenboek.py <pdf_path> -c <category_file> -i <category_match_dir_from_step2> [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] step3 --no-gui
```

Use the `--help` flag for more details on arguments:

```bash
python split_lastenboek.py --help
```

## Output

The script creates timestamped directories for each run within the specified output directory (defaulting to an `output` subdirectory within the project folder). Each step generates its own subdirectory (`step1_toc`, `step2_category_matching`, `step3_category_pdfs`) containing intermediate files (JSON, CSV) and the final categorized PDFs. 