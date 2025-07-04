# AI Construct PDF Splitter - Quick Start Guide

Get up and running with the AI Construct PDF Splitter in minutes! This guide provides the fastest paths for both VMSW and Non-VMSW document processing.

## 🚀 Choose Your Path

The application supports two types of construction documents with different setup requirements:

| Document Type | Setup Time | Requirements | Best For |
|---------------|------------|--------------|----------|
| **🔢 VMSW Documents** | < 1 minute | Python only | Dutch construction docs with XX.YY numbering |
| **🤖 Non-VMSW Documents** | 5-10 minutes | Python + Google Cloud | Custom/international construction docs |

---

## ⚡ Path A: VMSW Documents (Ultra-Fast Setup)

**Perfect for**: Documents using standard VMSW numbering (00.00, 01.10, 02.40, etc.)

### Step 1: Install (30 seconds)
```bash
pip install -r requirements.txt
```

### Step 2: Launch (Instant)
```bash
python src/main.py
```

### Step 3: Process (2 clicks)
1. **📁 Select PDF**: Click "Browse" and choose your VMSW document
2. **⚙️ Document Type**: Select "VMSW Document" from dropdown
3. **▶️ Run**: Click "Run Complete Pipeline"

**That's it!** Your document will be processed in seconds using built-in VMSW categories.

---

## 🤖 Path B: Non-VMSW Documents (Full AI Setup)

**Perfect for**: Custom construction documents, international formats, non-standard numbering

### Step 1: Python Setup (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup (3-5 minutes)

1. **Install Google Cloud CLI**: https://cloud.google.com/sdk/docs/install
2. **Authenticate**:
   ```bash
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```
3. **Set Project ID** (optional):
   ```bash
   # Create .env file or enter in app
   echo GOOGLE_CLOUD_PROJECT="your-project-id" > .env
   ```

### Step 3: Category File (1-2 minutes)
- **Option A**: Use the included `example_categories.py` as-is
- **Option B**: Customize it for your specific construction domain
- **Option C**: Create your own (see [Category File Guide](category_file_guide.md))

### Step 4: Launch & Configure
```bash
python src/main.py
```

1. **📁 Select PDF**: Choose your construction document
2. **⚙️ Document Type**: Select "Non-VMSW Document"
3. **📝 Category File**: Browse to your category file
4. **☁️ Google Cloud**: Enter your project ID (if not in .env)
5. **🤖 Model**: Choose Gemini 2.5 Flash (faster) or Pro (more accurate)
6. **▶️ Run**: Click "Run Complete Pipeline"

---

## 🎯 Understanding Document Types

### How to Identify VMSW Documents
✅ **Choose VMSW if your document has**:
- Chapter numbers like `01.`, `02.`, `03.`
- Section numbers like `01.10`, `02.40`, `03.50`
- Standard Dutch construction terminology
- VMSW-style table of contents

✅ **Example VMSW sections**:
- `00. Algemene Bepalingen`
- `01. Afbraak en Grondwerken`
- `02.40 Metselwerk`

### How to Identify Non-VMSW Documents
✅ **Choose Non-VMSW if your document has**:
- Custom chapter numbering (A.1, Section 1, etc.)
- Non-Dutch or custom terminology
- Unique construction categories
- International document formats

---

## 📊 What Happens During Processing

### All Documents (3 Steps)
1. **📖 TOC Extraction**: Analyzes PDF structure and extracts chapters/sections
2. **🎯 Categorization**: 
   - **VMSW**: Direct number mapping (instant)
   - **Non-VMSW**: AI semantic analysis (intelligent)
3. **📄 PDF Splitting**: Creates separate PDFs for each category

### Expected Processing Times
- **VMSW**: 5-30 seconds (depending on document size)
- **Non-VMSW**: 2-10 minutes (depending on document size and complexity)

---

## 📁 Finding Your Results

After processing completes:

1. **📂 Open Output**: Click "Open Output Folder" or navigate to your chosen output directory
2. **📁 Find Timestamped Folder**: Look for `pdf_processor_YYYYMMDD_HHMMSS/`
3. **📄 Access PDFs**: Open `step3_category_pdfs/` for your categorized documents

**Example output structure**:
```
output/pdf_processor_20250115_143022/
├── step1_toc/                    # Table of contents data
├── step2_category_matching/      # Categorization results  
└── step3_category_pdfs/          # 📄 Your final PDFs!
    ├── 01_Afbraak_en_Grondwerken.pdf
    ├── 02_Funderingen_en_Kelders.pdf
    └── ...
```

---

## 🛠️ Advanced Options

### Individual Step Processing
Run steps separately for more control:
- **Step 1 Only**: Extract table of contents
- **Step 2 Only**: Categorize existing TOC data  
- **Step 3 Only**: Create PDFs from existing categories

### Multiple Output Directories
Configure up to 3 different output locations for the same processing run.

### Model Selection (Non-VMSW)
- **Gemini 2.5 Flash**: Faster processing, good accuracy
- **Gemini 2.5 Pro**: Slower processing, highest accuracy

---

## 🔧 Troubleshooting Quick Fixes

### VMSW Mode Issues
- **"Not detected as VMSW"**: Manually select "VMSW Document" in dropdown
- **Missing categories**: Check if your document uses true VMSW numbering

### Non-VMSW Mode Issues  
- **Google Cloud errors**: Ensure billing is enabled and Vertex AI API is active
- **Slow processing**: Switch to Gemini 2.5 Flash model
- **Poor categorization**: Customize your category file

### General Issues
- **Application won't start**: Check Python version (3.7-3.13 required)
- **PDF won't load**: Ensure PDF is not password-protected or corrupted

---

## 📖 Next Steps

- **🔍 Explore Features**: Check the [Main Documentation](documentation.md) for all capabilities
- **🛠️ Customize Categories**: See [Category File Guide](category_file_guide.md) for Non-VMSW docs
- **👨‍💻 Technical Details**: Review [Developer Guide](developer_guide.md) for architecture info

**Happy document processing!** 🚀 