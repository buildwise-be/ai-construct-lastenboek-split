"""
Configuration Settings Module

This module centralizes all configuration settings and constants.
Extracted from the monolithic main script to improve maintainability.
"""

import os
from pathlib import Path

# Application Information
APP_NAME = "AI Construct PDF Opdeler"
APP_SUBTITLE = "VMSW & Non-VMSW Support - Deel uw lastenboek op in delen per onderaannemer"
APP_VERSION = "2.0.0"
APP_AUTHOR = "AI Construct"

# Default Paths
MODULE_DIR = Path(__file__).parent.parent.parent  # Go up to workspace root
DEFAULT_PDF_PATH = ""  # No default PDF path
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_CATEGORY_FILE = MODULE_DIR / "src" / "models" / "categories.py"

# Color Scheme
COLORS = {
    "primary": "#0087B7",      # Blue
    "secondary": "#00BFB6",    # Teal
    "accent": "#EC6607",       # Orange
    "dark": "#000000",         # Black
    "alternate": "#3f4f87",    # Purple/Navy
    "light": "#FFFFFF",        # White
    "off_white": "#FAFAFA",    # Subtle off-white for header
    "light_gray": "#F5F5F5",   # Light Gray
    "mid_gray": "#E0E0E0",     # Medium Gray
    "dark_gray": "#808080",    # Dark Gray
}

# GUI Configuration
GUI_CONFIG = {
    "min_width": 1000,
    "min_height": 800,
    "default_width": 1200,
    "default_height": 900,
    "button_min_height": 35,
    "button_min_width": 100,
    "bw_logo_size": (70, 70),
    "bw_logo_frame_size": (80, 80),
    "aico_logo_size": (120, 35),
    "aico_logo_frame_size": (130, 40),
    "header_frame_size": (250, 80),
    "content_max_height": 40,
    "content_min_height": 30,
    "refresh_interval": 100,  # milliseconds
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "max_lines": 1000,  # Maximum lines in GUI log
}

# Processing Configuration
PROCESSING_CONFIG = {
    "batch_size": 10,           # Items to process in each batch
    "page_batch_size": 50,      # PDF pages to process in each batch
    "page_overlap": 5,          # Overlap between page batches
    "rate_limit_delay": 2.0,    # Base delay between API calls (seconds)
    "max_retries": 5,           # Maximum retry attempts
    "include_explanations": True,  # Whether to include AI explanations
}

# File Configuration
FILE_CONFIG = {
    "supported_pdf_extensions": [".pdf"],
    "supported_category_extensions": [".py"],
    "max_file_size": 100 * 1024 * 1024,  # 100MB max file size
    "output_formats": ["json", "csv"],
}

# Step Configuration
STEPS_CONFIG = {
    "step1": {
        "name": "Genereer Inhoudstafel",
        "description": "Inhoudstafel uit PDF extraheren",
        "color": "primary"
    },
    "step2": {
        "name": "Match Categorieën", 
        "description": "Hoofdstukken en secties matchen met categorieën via AI",
        "color": "secondary"
    },
    "step3": {
        "name": "Extraheer PDF's",
        "description": "PDF opsplitsen in categorie-specifieke documenten",
        "color": "accent"
    },
    "complete": {
        "name": "Volledige Pipeline",
        "description": "Alle stappen opeenvolgend uitvoeren",
        "color": "alternate"
    }
}

# Environment Variables
def get_env_setting(key: str, default=None, required=False):
    """
    Get environment variable with optional default and required validation.
    
    Args:
        key (str): Environment variable key
        default: Default value if not found
        required (bool): Whether the variable is required
        
    Returns:
        str: Environment variable value
        
    Raises:
        ValueError: If required variable is not found
    """
    value = os.environ.get(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

# Project and Cloud Configuration
CLOUD_CONFIG = {
    "project_id": get_env_setting("GOOGLE_CLOUD_PROJECT", ""),
    "location": "europe-west1",
    "api_endpoint": "europe-west1-aiplatform.googleapis.com",
}

# Model Configuration
MODEL_CONFIG = {
    "default_model": "gemini-2.5-pro",
    "multimodal_model": "gemini-2.5-pro",
    "available_models": {
        "gemini-2.5-pro": {
            "name": "Gemini 2.5 Pro", 
            "description": "High-quality model (slower, more expensive)"
        },
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash", 
            "description": "Fast model (faster, less expensive)"
        }
    },
    "generation_config": {
        "max_output_tokens": 60000,
        "temperature": 1,
        "top_p": 0.95,
    },
    "safety_settings_categories": [
        "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_DANGEROUS_CONTENT", 
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_HARASSMENT",
    ],
    "safety_threshold": "OFF"
}

# Asset Paths
ASSETS_CONFIG = {
    "bw_logo_path": MODULE_DIR / "Requirements" / "Logo" / "BWlogo.png",
    "aico_logo_path": MODULE_DIR / "Requirements" / "aiconew.svg",
    "docs_path": MODULE_DIR / "docs",
    "demo_path": MODULE_DIR / "demo",
}

# Validation Rules
VALIDATION_RULES = {
    "pdf_file": {
        "required": True,
        "extensions": [".pdf"],
        "max_size": 100 * 1024 * 1024,  # 100MB
    },
    "category_file": {
        "required": True,
        "extensions": [".py"],
        "max_size": 10 * 1024 * 1024,  # 10MB
    },
    "output_directory": {
        "required": True,
        "must_be_writable": True,
    },
    "project_id": {
        "required": False,
        "min_length": 3,
        "pattern": r"^[a-z0-9\-]+$",
    }
}

# Error Messages
ERROR_MESSAGES = {
    "file_not_found": "File not found: {path}",
    "invalid_file_type": "Invalid file type. Expected {expected}, got {actual}",
    "file_too_large": "File is too large. Maximum size is {max_size}MB",
    "directory_not_writable": "Directory is not writable: {path}",
    "invalid_project_id": "Invalid project ID format. Use lowercase letters, numbers, and hyphens only",
    "api_error": "API error occurred: {error}",
    "processing_error": "Processing error: {error}",
    "validation_error": "Validation error: {error}",
}

# Success Messages
SUCCESS_MESSAGES = {
    "file_loaded": "Successfully loaded file: {path}",
    "step_completed": "Step {step} completed successfully",
    "processing_started": "Processing started for {item_count} items",
    "processing_completed": "Processing completed successfully",
    "results_saved": "Results saved to: {path}",
}

# Default System Instructions for AI
SYSTEM_INSTRUCTIONS = {
    "toc_generation": """You are given a technical specifications PDF document in the construction sector ("Samengevoegdlastenboek") that can be a concatenation of multiple different documents, each with their own internal page numbering.

The document contains numbered chapters in two formats:
1. Main chapters: formatted as "XX. TITLE" (e.g., "00. ALGEMENE BEPALINGEN")
2. Sections: formatted as "XX.YY TITLE" (e.g., "01.10 SECTIETITEL") or formatted as "XX.YY.ZZ TITLE" (e.g., "01.10.01 SECTIETITEL") and even "XX.YY.ZZ.AA TITLE" (e.g., "01.10.01.01 SECTIETITEL")

Your task is to identify both main chapters (00-93) and their sections, using the GLOBAL PDF page numbers (not the internal page numbers that appear within each document section).

For each main chapter and section:
1. Record the precise numbering (e.g., "00" or "01.10")
2. Record the accurate starting page number based on the GLOBAL PDF page count (starting from 1 for the first page)
3. Record the accurate ending page number (right before the next chapter/section starts)
4. Summarize the content of the chapter and sections in 10 keywords or less to help with the categorization process

IMPORTANT: 
- Use the actual PDF page numbers (starting from 1 for the first page of the entire PDF)
- IGNORE any page numbers printed within the document itself
- The page numbers in any table of contents (inhoudstafel) are UNRELIABLE - do not use them
- Determine page numbers by finding where each chapter actually begins and ends in the PDF
- Be EXTREMELY thorough in identifying ALL sections and subsections, including those with patterns like XX.YY.ZZ.AA
- Don't miss any chapter or section - this is critical for accurate document processing

Final output should be a nested Python dictionary structure:```
chapters = {
    "00": {
        "start": start_page,
        "end": end_page,
        "title": "CHAPTER TITLE",
        "sections": {
            'XX.YY': {'start': start_page, 'end': end_page, 'title': 'section title'},
            'XX.YY.ZZ': {'start': start_page, 'end': end_page, 'title': 'subsection title'},
            'XX.YY.ZZ.AA': {'start': start_page, 'end': end_page, 'title': 'sub-subsection title'}
        }
    }
}
```""",
    
    "category_matching": """You are a construction categorization expert. Your task is to match construction document chapters and sections to appropriate categories based on their content and titles.

DEMOLITION/REMOVAL WORK RULE:
- For REMOVAL/DEMOLITION work (keywords: "verwijderen", "slopen", "uitbreken", "opbreken", "demonteren", "afbreken"):
  * ALWAYS include "01. Afbraak en Grondwerken" as the PRIMARY category
  * ALSO include the relevant trade category (plumbing, electrical, etc.) as SECONDARY category
  * Example: "Verwijderen van leidingen" → "01. Afbraak en Grondwerken" + "12. Sanitair"

This ensures demolition contractors see all removal work, while trade contractors see removal work relevant to their specialty.

Focus on the main construction activities, materials, or specialties involved. You can assign multiple categories if appropriate. Always provide clear reasoning for your categorization decisions and assign confidence scores based on how certain you are about the match."""
}

def validate_config():
    """Validate configuration settings and environment."""
    issues = []
    
    # Check required directories exist
    if not MODULE_DIR.exists():
        issues.append(f"Module directory not found: {MODULE_DIR}")
    
    # Check asset files
    for asset_name, asset_path in ASSETS_CONFIG.items():
        if not asset_path.exists():
            issues.append(f"Asset file not found: {asset_name} at {asset_path}")
    
    # Check project ID format if provided
    project_id = CLOUD_CONFIG["project_id"]
    if project_id:
        import re
        if not re.match(VALIDATION_RULES["project_id"]["pattern"], project_id):
            issues.append(f"Invalid project ID format: {project_id}")
    
    return issues

def get_output_directory(base_dir=None):
    """Get the output directory, creating it if necessary."""
    output_dir = Path(base_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_step_config(step_name):
    """Get configuration for a specific step."""
    return STEPS_CONFIG.get(step_name, {})

def get_color(color_name):
    """Get a color value by name."""
    return COLORS.get(color_name, COLORS["primary"])

def format_error_message(message_key, **kwargs):
    """Format an error message with provided parameters."""
    template = ERROR_MESSAGES.get(message_key, "Unknown error")
    return template.format(**kwargs)

def format_success_message(message_key, **kwargs):
    """Format a success message with provided parameters."""
    template = SUCCESS_MESSAGES.get(message_key, "Success")
    return template.format(**kwargs)