# AI Construct PDF Opdeler

<p align="center">
  <img src="docs/images/BWlogo.png" alt="BW Logo" width="100"/> &nbsp;&nbsp;&nbsp;&nbsp; <img src="docs/images/aico.png" alt="AICO Logo" width="100"/>
</p>

<p align="center">
  <em>VMSW & Non-VMSW Support - Deel uw lastenboek op in delen per onderaannemer</em>
</p>

---

## 🚀 What's New: Hybrid Processing System

This application now supports **both VMSW and Non-VMSW construction documents** with intelligent processing:

- **🔢 VMSW Documents**: Uses number-based category matching for high speed and accuracy.
- **🤖 Non-VMSW Documents**: Employs AI-powered semantic analysis with Google Gemini.
- **🎯 Smart Detection**: Automatically detects the document type, with a manual override option.
- **⚡ Performance**: The VMSW categorization step is over 1000x faster than the AI alternative, leading to significantly quicker overall processing for VMSW files.

---

## Overview

The AI Construct PDF Opdeler is a powerful tool for processing construction specification documents (lastenboeken). It intelligently analyzes documents, extracts structure, categorizes content, and splits documents into contractor-specific PDFs.

### 🎯 Key Features

- **Hybrid Intelligence**: Seamlessly combines number-based VMSW matching with AI semantic analysis.
- **Modern GUI**: A user-friendly interface with real-time progress tracking.
- **Document Type Selection**: Easily choose between VMSW and Non-VMSW processing modes.
- **Model Selection**: Choose between Gemini 2.5 Pro and Gemini 2.5 Flash
- **Batch Processing**: Efficient processing with retry logic and error handling
- **Multi-Output**: Generate PDFs in multiple output directories simultaneously
- **Comprehensive Logging**: Detailed logs with debugging utilities

### 📋 Processing Pipeline

1. **📖 TOC Generation**: Extracts chapters and sections from PDF documents. This step's duration is independent of the document type.
2. **🎯 Smart Categorization**: 
   - **VMSW**: Near-instant direct number mapping (e.g., "02.40" → "02. Funderingen en Kelders").
   - **Non-VMSW**: AI semantic matching with predefined categories.
3. **📄 Document Splitting**: Creates separate PDFs for each construction category.

---

## 📦 Installation

### Prerequisites

- **Python**: 3.7 - 3.13 (3.13 recommended)
- **Internet Connection**: Required for AI processing (Non-VMSW documents)
- **Google Cloud Account**: For Non-VMSW AI processing

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup (Non-VMSW Only)

If you plan to process Non-VMSW documents, set up Google Cloud:

1. **Install Google Cloud CLI**: https://cloud.google.com/sdk/docs/install
2. **Authenticate**:
```bash
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```
3. **Set Project ID** (optional):
```bash
   # Create .env file
   echo GOOGLE_CLOUD_PROJECT="your-project-id" > .env
   ```

### Step 3: Launch Application

```bash
python src/main.py
```

---

## 🖥️ Using the Application

### Quick Start

1. **📁 Select PDF**: Choose your construction document
2. **⚙️ Document Type**: Select "VMSW Document" or "Non-VMSW Document"
3. **📂 Output Directory**: Choose where to save results
4. **▶️ Process**: Click "Run Complete Pipeline"

### Document Type Guide

| Document Type | When to Use | Requirements | Speed |
|---------------|-------------|--------------|-------|
| **VMSW Document** | Documents with VMSW numbering (XX.YY format). | None - uses built-in categories. | ⚡ Faster Overall |
| **Non-VMSW Document** | Other construction documents. | Category file + Google Cloud setup. | 🤖 AI-Powered |

### Advanced Options

- **🎛️ Model Selection**: Choose Gemini 2.5 Pro (accuracy) or Flash (speed)
- **📁 Multiple Outputs**: Set up to 3 different output directories
- **🔧 Individual Steps**: Run TOC, Categorization, or PDF splitting separately
- **📊 Logging**: View detailed processing logs and debugging info

---

## 📁 File Structure

```
├── src/                    # Modern application architecture
│   ├── config/            # Configuration and settings
│   ├── core/              # Core processing logic
│   │   ├── ai_client.py   # Google Gemini integration
│   │   ├── hybrid_matcher.py  # Smart document type handling
│   │   ├── vmsw_matcher.py    # VMSW number-based matching
│   │   └── category_matcher.py # Non-VMSW AI matching
│   ├── gui/               # User interface components
│   ├── models/            # Data models and categories
│   └── utils/             # Utilities and helpers
├── main_script.py         # Legacy command-line interface
├── vmsw_pipeline.py       # VMSW-specific processing
└── documentation/         # Comprehensive documentation
```

---

## 🎯 VMSW vs Non-VMSW Processing

### VMSW Documents

**Perfect for**: Dutch construction documents using standard VMSW numbering

**How it works**:
- Directly maps chapter numbers to categories (e.g., "02" → "02. Funderingen en Kelders").
- The categorization step is nearly instantaneous and requires no AI.
- Built-in demolition detection.
- 100% confidence scores.

**Categories include**:
- 00. Algemene Bepalingen
- 01. Afbraak en Grondwerken  
- 02. Funderingen en Kelders
- And 31 more standard VMSW categories...

### Non-VMSW Documents

**Perfect for**: Custom construction documents, international formats

**How it works**:
- AI analyzes content semantically
- Matches against custom category definitions
- Provides confidence scores and explanations
- Intelligent retry logic for best results

**Requirements**:
- Custom category file (Python, Excel, or CSV)
- Google Cloud project with Vertex AI enabled

---

## 📊 Output Structure

Each processing run creates a timestamped directory:

```
output/
└── pdf_processor_YYYYMMDD_HHMMSS/
    ├── step1_toc/              # Table of contents extraction
    │   ├── chapters.json
    │   ├── sections.json
    │   └── toc.csv
    ├── step2_category_matching/ # Categorization results
    │   ├── category_matches.json
    │   ├── category_statistics.json
    │   └── matching_details.csv
    └── step3_category_pdfs/     # Final categorized PDFs
        ├── 01_Afbraak_en_Grondwerken.pdf
        ├── 02_Funderingen_en_Kelders.pdf
        └── ...
```

---

## 🛠️ Advanced Usage

### Command Line Interface

```bash
# Complete pipeline
python main_script.py document.pdf --document-type vmsw

# Individual steps
python main_script.py document.pdf step1 --no-gui
python main_script.py document.pdf step2 --document-type non-vmsw -c categories.py
python main_script.py document.pdf step3 --no-gui
```

### Custom Category Files (Non-VMSW)

Create custom categories in Python, Excel, or CSV format:

```python
# example_custom_categories.py
raw_data_dict = {
    '01. Foundations': "['Foundation', 'Footings', 'Slab', 'Basement']",
    '02. Structure': "['Framing', 'Beams', 'Columns', 'Steel']",
    # ... more categories
}
```

See [Category File Guide](documentation/category_file_guide.md) for details.

---

## 🔧 Troubleshooting

### Common Issues

1. **VMSW Detection Problems**: Manually select "VMSW Document" in the dropdown
2. **AI Processing Slow**: Use Gemini 2.5 Flash model for faster processing
3. **Google Cloud Errors**: Ensure billing is enabled and Vertex AI API is active
4. **Category Mismatches**: Review and customize your category file

### Getting Help

- 📖 [Full Documentation](documentation/documentation.md)
- 🚀 [Quick Start Guide](documentation/quick_start_guide.md)
- 👨‍💻 [Developer Guide](documentation/developer_guide.md)
- 📝 [Category File Guide](documentation/category_file_guide.md)

---

## 🎥 Demo

![Tool Demo](docs/images/Minidemosplit.gif)

---

## 📄 License & Support

This tool is designed for construction industry professionals working with specification documents. For support, feature requests, or bug reports, please refer to the documentation or contact the development team.

**Performance Highlights**:
- ⚡ VMSW Categorization: ~0.001 seconds per item.
- 🤖 Non-VMSW Categorization: ~4.7 seconds per item.
- 📊 Typical AI accuracy: 85-95% depending on document quality.
- 🔄 Automatic retry logic ensures high success rates for AI processing.
