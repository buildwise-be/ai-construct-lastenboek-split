# AI Construct PDF Splitter - Quick Start Guide

This guide will help you quickly get started with the AI Construct PDF Splitter tool for processing construction specification documents.

## Installation in 5 Minutes

### 1. Requirements Check
- Ensure you have Python installed (Python 3.13 recommended, any version between 3.7 and 3.13 should work)
- Have a PDF document ready for processing 
- Make sure you have an internet connection

### 2. Install Dependencies
Run the following command in your terminal:

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Setup
- Install Google Cloud CLI from: https://cloud.google.com/sdk/docs/install
- Run these commands to authenticate:

```bash
pip install --upgrade google-genai
gcloud auth application-default login
```

- Follow the browser prompts to log in to your Google account

### 4. Set Project ID
Create a `.env` file in the project directory with:

```
GOOGLE_CLOUD_PROJECT="your-project-id"
```

Or be prepared to enter it in the application.

## Running the Application

### 1. Launch the Application
Run:

```bash
python main_script.py
```

### 2. Configure Input and Output Locations
- Click **Browse** next to "PDF File" to select your construction document
- Select or use the default category file 
- Choose an output directory for the results

### 3. Process the Document
- Click **Run Complete Pipeline** to perform all processing steps
- Wait for the processing to complete (this may take several minutes depending on the document size)

### 4. Access the Results
- When processing is complete, click **Open Output Folder**
- Your document has been split into separate PDFs by category in the `step3_category_pdfs` subfolder

## What Happens Behind the Scenes
1. **Step 1**: The system extracts the table of contents from your PDF
2. **Step 2**: AI categorizes each chapter and section based on its content
3. **Step 3**: The document is split into separate PDFs for each category

## Tips for Best Results
- Use PDF documents with clear chapter and section headings
- For large documents, allow extra processing time
- Check the category file to ensure it matches your document's domain

## Next Steps
- Refer to the full documentation for advanced features
- Try processing individual steps for more control
- Customize the category definitions to better match your documents 