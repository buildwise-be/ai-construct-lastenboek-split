# AI Construct PDF Opdeler - Refactored Version

## 🚀 Overview

This is a completely refactored version of the AI Construct PDF Opdeler application. The monolithic script has been restructured into a modular, maintainable, and user-friendly application with a responsive GUI.

### ⭐ Key Improvements

- **Responsive GUI**: No more freezing during long AI operations
- **Real-time Progress**: Live progress bars and status updates
- **Modular Architecture**: Clean separation of concerns
- **Better Error Handling**: User-friendly error messages
- **Cancellation Support**: Stop operations mid-process
- **Professional Logging**: Auto-scrolling log with timestamps
- **Easy Installation**: Simple setup with validation

## 📁 Project Structure

```
lastenboekexperimenten/
├── src/                          # Main application source
│   ├── main.py                   # Application entry point
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Centralized settings
│   ├── core/                     # Business logic modules
│   │   ├── __init__.py
│   │   ├── ai_client.py          # Vertex AI integration
│   │   ├── pdf_processor.py      # TOC generation & PDF splitting
│   │   ├── category_matcher.py   # AI category matching
│   │   └── file_utils.py         # File operations
│   ├── gui/                      # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py        # Main application window
│   │   ├── components/           # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   └── styled_components.py
│   │   └── workers/              # Background processing
│   │       ├── __init__.py
│   │       └── processing_worker.py
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── categories.py         # Category definitions
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── validation.py         # Setup validation
│   │   └── migration.py          # Migration utilities
│   └── requirements.txt          # Python dependencies
├── launch.py                     # Simple launcher script
├── setup.py                      # Installation script
├── .env.example                  # Environment configuration template
└── README_REFACTORED.md          # This documentation
```

## �️ Installation

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
   pip install -r src/requirements.txt
   ```

2. **Validate installation:**
   ```bash
   python src/utils/validation.py
   ```

## 🚀 Usage

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

### Application Workflow

The application maintains the same 3-step workflow as the original:

1. **📄 TOC Generation**: Extract table of contents from PDF
2. **🤖 Category Matching**: AI-powered category assignment
3. **✂️ PDF Splitting**: Split PDF into categorized sections

### New Features

- **Real-time Progress**: See exactly what's happening at each step
- **Cancellation**: Stop processing at any time
- **Better Errors**: Clear error messages with suggestions
- **Auto-scrolling Log**: See detailed processing information
- **Responsive Design**: GUI never freezes during processing

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Required for AI processing
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Optional settings
VERTEX_AI_REGION=europe-west1
VERTEX_AI_MODEL=gemini-1.5-flash-001
DEFAULT_OUTPUT_DIR=output
LOG_LEVEL=INFO
```

### Category Files

Place your category definition files in the project root:
- `example_categories.py` (default)
- Custom category files can be selected in the GUI

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
pip install -r src/requirements.txt
```

**Missing Files:**
```bash
python setup.py
```

**Configuration Issues:**
- Check your `.env` file
- Verify Google Cloud Project ID
- Ensure category files exist

## 📚 Module Overview

### Core Modules

- **`ai_client.py`**: Handles all Vertex AI interactions with retry logic
- **`pdf_processor.py`**: PDF processing, TOC extraction, and splitting
- **`category_matcher.py`**: AI-powered category matching with batch processing
- **`file_utils.py`**: File operations and directory management

### GUI Components

- **`main_window.py`**: Main application window with responsive design
- **`styled_components.py`**: Reusable UI components with consistent styling
- **`processing_worker.py`**: Background QThread workers for non-blocking operations

### Configuration & Models

- **`settings.py`**: Centralized configuration management
- **`categories.py`**: Category definitions and utilities

## 🔄 Migration from Old Version

### Migration Helper

```bash
python src/utils/migration.py
```

This utility:
- Scans for old files
- Suggests migration steps
- Helps backup old data
- Provides cleanup recommendations

### Manual Migration Steps

1. **Backup old files:**
   ```python
   from src.utils.migration import MigrationHelper
   migration = MigrationHelper()
   success, backup_dir = migration.backup_old_files()
   ```

2. **Migrate output data:**
   ```python
   success, migrated = migration.migrate_output_data()
   ```

3. **Test new version:**
   ```bash
   python src/main.py
   ```

## 🎯 Development

### Project Structure

The refactored application follows clean architecture principles:

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Configurable components
- **Event-Driven**: GUI and business logic communicate via signals
- **Testable**: Modular design makes testing easier

### Key Classes

- `AIClient`: Manages Vertex AI connections and requests
- `PDFProcessor`: Handles PDF operations
- `CategoryMatcher`: AI category matching logic
- `ProcessingWorker`: Background task execution
- `MainWindow`: GUI orchestration

## 📊 Performance Improvements

### Before (Monolithic)
- 3,528 lines in single file
- GUI freezes during processing
- No progress indication
- Hard to maintain/extend

### After (Refactored)
- Modular files (~200-400 lines each)
- Responsive GUI with background processing
- Real-time progress and cancellation
- Easy to maintain and extend

## 🚨 Backward Compatibility

The refactored application maintains 100% functional compatibility:
- Same input/output formats
- Identical processing results
- Same category file format
- Same output directory structure

## 📝 Changelog

### v2.0.0 (Refactored)
- ✅ Complete modular restructure
- ✅ Responsive GUI with background processing
- ✅ Real-time progress and cancellation
- ✅ Professional error handling
- ✅ Centralized configuration
- ✅ Comprehensive validation
- ✅ Migration utilities
- ✅ Easy installation

### v1.0.0 (Original)
- 📄 Monolithic main_script.py
- 🤖 Basic AI processing
- ✂️ PDF splitting functionality

## 🤝 Support

### Getting Help

1. **Run validation**: `python src/utils/validation.py`
2. **Check migration**: `python src/utils/migration.py`
3. **Review logs**: Check the application log window
4. **File an issue**: Describe the problem with error messages

### System Requirements

- Python 3.8 or higher
- 8GB+ RAM (for large PDF processing)
- Google Cloud Project (for AI features)
- 1GB+ free disk space

---

## 📄 License

This project maintains the same license as the original application.

---

**🎉 Enjoy the improved AI Construct PDF Opdeler experience!**