# AI Construct PDF Opdeler

<div align="center">
  <img src="Requirements/Logo/BWlogo.png" alt="Buildwise Logo" height="80"/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Requirements/Logo/aico.png" alt="AI Construct Logo" height="80"/>
</div>

<p align="center">
  <em>Modern GUI application for splitting construction documents by contractor categories</em>
</p>

---

## 🚀 What's New: Hybrid Processing System

This application supports **both VMSW and Non-VMSW construction documents** with intelligent processing:

- **🔢 VMSW Documents**: Uses number-based category matching for high speed and accuracy
- **🤖 Non-VMSW Documents**: Employs AI-powered semantic analysis with Google Gemini
- **🎯 Smart Detection**: Automatically detects document type with manual override option
- **⚡ Performance**: VMSW categorization is 1000x faster than AI processing
- **🖥️ Modern GUI**: Responsive interface with real-time progress tracking

---

## Overview

The AI Construct PDF Opdeler is a powerful tool for processing construction specification documents (lastenboeken). It intelligently analyzes documents, extracts structure, categorizes content, and splits documents into contractor-specific PDFs.

### 🎯 Key Features

- **Hybrid Intelligence**: Combines number-based VMSW matching with AI semantic analysis
- **Responsive GUI**: No more freezing during long operations
- **Real-time Progress**: Live progress bars and status updates  
- **Document Type Selection**: Choose between VMSW and Non-VMSW processing modes
- **Model Selection**: Choose between Gemini 2.5 Pro and Gemini 2.5 Flash
- **Cancellation Support**: Stop operations mid-process
- **Multi-Output**: Generate PDFs in multiple output directories simultaneously
- **Professional Logging**: Auto-scrolling log with timestamps and debugging utilities

### 📋 Processing Pipeline

1. **📖 TOC Generation**: Extracts chapters and sections from PDF documents
2. **🎯 Smart Categorization**: 
   - **VMSW**: Near-instant direct number mapping (e.g., "02.40" → "02. Funderingen en Kelders")
   - **Non-VMSW**: AI semantic matching with predefined categories
3. **📄 Document Splitting**: Creates separate PDFs for each construction category

---

## 📦 Installation

### Prerequisites

- **Python**: 3.7 - 3.13 (3.13 recommended)
- **Internet Connection**: Required for AI processing (Non-VMSW documents)
- **Google Cloud Account**: For Non-VMSW AI processing

### Quick Setup

1. **Run the setup script:**
   ```bash
   python setup.py
   ```
   This will:
   - Check Python version compatibility
   - Install all dependencies
   - Create necessary directories
   - Run validation checks

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud Project ID
   ```

### Manual Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Cloud Setup (Non-VMSW Only):**
   ```bash
   # Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

3. **Validate installation:**
   ```bash
   python src/utils/validation.py
   ```

### Launch Application

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
| **VMSW Document** | Documents with VMSW numbering (XX.YY format) | None - uses built-in categories | ⚡ Ultra Fast |
| **Non-VMSW Document** | Other construction documents | Category file + Google Cloud setup | 🤖 AI-Powered |

### Advanced Options

- **🎛️ Model Selection**: Choose Gemini 2.5 Pro (accuracy) or Flash (speed)
- **📁 Multiple Outputs**: Set up to 3 different output directories
- **🔧 Individual Steps**: Run TOC, Categorization, or PDF splitting separately
- **📊 Real-time Logging**: View detailed processing logs and debugging info
- **⏹️ Cancellation**: Stop processing at any time

---

## 📁 Project Architecture

```
├── src/                          # Modern modular architecture
│   ├── main.py                   # Application entry point
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Centralized settings
│   ├── core/                     # Core processing logic
│   │   ├── __init__.py
│   │   ├── ai_client.py          # Vertex AI integration
│   │   ├── pdf_processor.py      # TOC generation & PDF splitting
│   │   ├── category_matcher.py   # AI category matching
│   │   ├── hybrid_matcher.py     # Smart document type handling
│   │   ├── vmsw_matcher.py       # VMSW number-based matching
│   │   └── file_utils.py         # File operations
│   ├── gui/                      # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py        # Main application window
│   │   ├── components/           # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   └── styled_components.py
│   │   └── workers/              # Background processing
│   │       ├── __init__.py
│   │       └── processing_worker.py
│   ├── models/                   # Data models and categories
│   │   ├── __init__.py
│   │   └── categories.py         # Category definitions
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── validation.py         # Setup validation
│       └── migration.py          # Migration utilities
├── launch.py                     # Simple launcher script
├── setup.py                      # Installation script
├── example_categories.py         # Category template
├── VMSWcat.json                  # VMSW categories configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
└── documentation/                # Comprehensive documentation
```

---

## 🎯 VMSW vs Non-VMSW Processing

### VMSW Documents

**Perfect for**: Dutch construction documents using standard VMSW numbering

**How it works**:
- Directly maps chapter numbers to categories (e.g., "02" → "02. Funderingen en Kelders")
- The categorization step is nearly instantaneous and requires no AI
- Built-in demolition detection
- 100% confidence scores

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

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Required for AI processing
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Optional settings
VERTEX_AI_REGION=europe-west1
VERTEX_AI_MODEL=gemini-2.5-flash
DEFAULT_OUTPUT_DIR=output
LOG_LEVEL=INFO
```

### Category Files

Place your category definition files in the project root:
- `example_categories.py` (default template)
- Custom category files can be selected in the GUI

---

## 📊 Output Structure

Each processing run creates a timestamped directory:

```
output/
└── pdf_processor_step3_category_pdfs_YYYYMMDD_HHMMSS/
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
        └── category_summary.json
```

---

## 🔍 Validation & Troubleshooting

### Run Validation Check
```bash
python src/utils/validation.py
```

This checks:
- Python version compatibility
- All dependencies installed
- File structure integrity
- Module imports working
- Configuration validity

### Common Issues

**Import Errors:**
```bash
pip install -r requirements.txt
```

**Missing Files:**
```bash
python setup.py
```

**Configuration Issues:**
- Check your `.env` file
- Verify Google Cloud Project ID
- Ensure category files exist

---

## 🛠️ Advanced Usage

### Starting the Application

**Option 1: Using the launcher**
```bash
python launch.py
```

**Option 2: Direct execution**
```bash
python src/main.py
```

**Option 3: With validation**
```bash
python launch.py --validate
```

### Command Line Interface

```bash
# Complete pipeline
python main_script.py document.pdf --document-type vmsw

# Individual steps
python main_script.py document.pdf step1 --no-gui
python main_script.py document.pdf step2 --document-type non-vmsw -c categories.py
python main_script.py document.pdf step3 --no-gui
```

---

## 📚 Module Overview

### Core Modules

- **`ai_client.py`**: Handles all Vertex AI interactions with retry logic
- **`pdf_processor.py`**: PDF processing, TOC extraction, and splitting
- **`category_matcher.py`**: AI-powered category matching with batch processing
- **`hybrid_matcher.py`**: Smart document type detection and routing
- **`vmsw_matcher.py`**: High-speed VMSW number-based matching
- **`file_utils.py`**: File operations and directory management

### GUI Components

- **`main_window.py`**: Main application window with responsive design
- **`styled_components.py`**: Reusable UI components with consistent styling
- **`processing_worker.py`**: Background QThread workers for non-blocking operations

### Configuration & Models

- **`settings.py`**: Centralized configuration management
- **`categories.py`**: Category definitions and utilities
- **`validation.py`**: Setup validation and health checks

---

## 🤝 Contributing

This project uses a modern, modular architecture designed for maintainability and extensibility. The codebase follows clean architecture principles with clear separation of concerns.

---

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

---

<div align="center">
  <p><strong>Developed by Buildwise with AI Construct</strong></p>
  <p><em>Professional construction document processing for the modern era</em></p>
</div>
