# AI Construct PDF Splitter Documentation

Welcome to the comprehensive documentation for the AI Construct PDF Splitter tool. This documentation covers the modern hybrid system supporting both VMSW and Non-VMSW construction documents.

## 🚀 What's New

Our application now features a **hybrid processing system** that intelligently handles both document types:

- **⚡ VMSW Documents**: Ultra-fast number-based processing (0.001s per item)
- **🤖 Non-VMSW Documents**: AI-powered semantic analysis with Google Gemini
- **🎯 Smart Detection**: Automatic document type recognition with manual override
- **🔧 Modern GUI**: Beautiful interface with real-time progress tracking

## Available Documentation

| Document | Description | Best For |
|----------|-------------|----------|
| [📋 Main Documentation](documentation.md) | Complete feature guide and technical details | Understanding all capabilities |
| [🚀 Quick Start Guide](quick_start_guide.md) | Get running in 5 minutes | First-time users |
| [👨‍💻 Developer Guide](developer_guide.md) | Code architecture and extension guides | Developers and integrators |
| [📝 Category File Guide](category_file_guide.md) | Creating custom categories for Non-VMSW docs | Advanced Non-VMSW users |

## About AI Construct PDF Splitter

The AI Construct PDF Splitter is a specialized tool designed to process construction specification documents (lastenboeken). It features a **hybrid intelligence system** that automatically detects document types and applies the optimal processing approach:

### 🔢 VMSW Processing
- **When**: Documents using standard VMSW numbering (XX.YY format)
- **Method**: Direct number-to-category mapping
- **Speed**: Lightning fast (1000x faster than AI processing)
- **Requirements**: None - uses built-in VMSW categories
- **Accuracy**: 100% for proper VMSW documents

### 🤖 Non-VMSW Processing  
- **When**: Custom construction documents, international formats
- **Method**: AI semantic analysis with Google Gemini
- **Speed**: Intelligent (4-5 seconds per item)
- **Requirements**: Custom category file + Google Cloud setup
- **Accuracy**: 85-95% depending on document quality

## Key Features

- **🎯 Document Type Selection**: Choose VMSW or Non-VMSW processing modes
- **🤖 Model Selection**: Choose between Gemini 2.5 Pro (accuracy) or Flash (speed)
- **📊 Batch Processing**: Efficient processing with intelligent retry logic
- **📁 Multi-Output**: Generate PDFs in up to 3 different directories
- **🔍 Comprehensive Logging**: Detailed logs with debugging utilities
- **⚡ Performance Optimized**: Smart batch sizing and error handling
- **🎨 Modern Interface**: Beautiful, intuitive GUI with progress tracking

## Getting Started

### For VMSW Documents (Fastest Path)
1. Install dependencies: `pip install -r requirements.txt`
2. Launch application: `python src/main.py`
3. Select your PDF and choose "VMSW Document"
4. Click "Run Complete Pipeline"

### For Non-VMSW Documents
1. Follow the [Quick Start Guide](quick_start_guide.md) for Google Cloud setup
2. Prepare or customize a category file using the [Category File Guide](category_file_guide.md)
3. Launch and configure for Non-VMSW processing

## Quick Feature Comparison

| Feature | VMSW Mode | Non-VMSW Mode |
|---------|-----------|---------------|
| **Setup Time** | < 1 minute | 5-10 minutes |
| **Processing Speed** | ⚡ Ultra-fast | 🤖 Intelligent |
| **Category File** | ❌ Not needed | ✅ Required |
| **Google Cloud** | ❌ Not needed | ✅ Required |
| **Accuracy** | 🎯 100% | 📊 85-95% |
| **Cost** | 🆓 Free | 💰 Pay-per-use |

## For Developers

The application features a modern, modular architecture:

```
src/
├── core/                  # Processing logic
│   ├── hybrid_matcher.py  # Smart document type handling
│   ├── vmsw_matcher.py    # VMSW number-based matching  
│   └── category_matcher.py # Non-VMSW AI matching
├── gui/                   # User interface
├── models/                # Data models and built-in categories
└── utils/                 # Utilities and helpers
```

Refer to the [Developer Guide](developer_guide.md) for architecture details, extension points, and API documentation.

## Support & Community

- 📖 **Full Documentation**: Start with [documentation.md](documentation.md)
- 🚀 **Quick Setup**: See [quick_start_guide.md](quick_start_guide.md)  
- 🔧 **Troubleshooting**: Check the main documentation troubleshooting section
- 💡 **Feature Requests**: Contact the development team

---

**Performance Highlights**:
- ⚡ VMSW: 0.001 seconds per item (1000x faster)
- 🤖 Non-VMSW: ~4.7 seconds per item with 93% avg confidence
- 🎯 Automatic retry logic ensures maximum success rates
- 📊 Supports documents with 80+ items efficiently 