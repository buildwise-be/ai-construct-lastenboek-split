"""
Non-VMSW Document Processing Pipeline with Distinct Steps

This script organizes the document processing pipeline into three distinct steps,
each corresponding to a previously separate process:

STEP 1: Table of Contents (TOC) generation from a PDF document
STEP 2: Category matching for chapters and sections using Gemini AI via Vertex AI
STEP 3: Document splitting into category-specific PDFs

Each step can be run independently or as part of the complete pipeline.
"""

import os
import sys
import json
import argparse
import logging
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader, PdfWriter
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import shutil
import time
import re
import csv
import base64
import fitz  # Added import for fitz
import random
from datetime import datetime
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QFileDialog, 
    QProgressBar, QGroupBox, QScrollArea, QFrame, QTextEdit, 
    QCheckBox, QMessageBox, QComboBox
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define colors for the UI
COLORS = {
    "primary": "#0087B7",      # Blue
    "secondary": "#00BFB6",    # Teal
    "accent": "#EC6607",       # Orange
    "dark": "#000000",         # Black
    "alternate": "#3f4f87",    # Purple/Navy
    "light": "#FFFFFF",        # White
    "light_gray": "#F5F5F5",   # Light Gray
    "mid_gray": "#E0E0E0",     # Medium Gray
    "dark_gray": "#808080",    # Dark Gray
}

# Custom styled button with consistent appearance
class StyledButton(QPushButton):
    """Custom styled button with consistent appearance"""
    def __init__(self, text, color_key="primary", icon=None):
        super().__init__(text)
        self.setMinimumHeight(35)  # Reduced height to match example
        self.setMinimumWidth(100)  # Minimum width for buttons
        
        # Apply the stylesheet based on the color key
        color = COLORS[color_key]
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 3px;  /* Smaller radius to match example */
                padding: 6px 14px;   /* Adjusted padding */
                font-weight: bold;
                font-size: 12px;     /* Adjusted font size */
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            QPushButton:pressed {{
                background-color: {color}77;
            }}
            QPushButton:disabled {{
                background-color: {COLORS["mid_gray"]};
                color: {COLORS["dark_gray"]};
            }}
        """)
        
        # Set icon if provided
        if icon:
            self.setIcon(icon)

# Custom styled frame with consistent appearance
class StyledFrame(QFrame):
    """Custom styled frame with consistent appearance"""
    def __init__(self, color_key="light_gray"):
        super().__init__()
        color = COLORS[color_key]
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)

# Set default paths
DEFAULT_PDF_PATH = "" # Removed hardcoded path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.append(MODULE_DIR)
    logger.info(f"Added {MODULE_DIR} to Python path")

# Default category file path
DEFAULT_CATEGORY_FILE = os.path.join(MODULE_DIR, "nonvmswhoofdstukken_pandas.py")

# Vertex AI configuration
GENERATION_CONFIG = {
    "max_output_tokens": 30000,
    "temperature": 1,
    "top_p": 0.95,
}

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

# Initialize Vertex AI using europe-west1 as location (keeping the data in Belgium )
try:
    # Load project ID from environment variables
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    
    if not PROJECT_ID:
        logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it before running in production.")
    
    vertexai.init(
        project=PROJECT_ID,
        location="europe-west1",
        api_endpoint="europe-west1-aiplatform.googleapis.com"
    )
    logger.info(f"Successfully initialized Vertex AI (Project: {PROJECT_ID})")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    raise

# Load environment variables
load_dotenv()

# Add global parameter near the top of the file, after other configuration variables
INCLUDE_EXPLANATIONS = True  # Global flag to control whether to include explanations

def initialize_vertex_model(system_instruction=None, project_id=None):
    """
    Initialize the Vertex AI Gemini model.
    
    Args:
        system_instruction (str, optional): System instruction for the model
        project_id (str, optional): Google Cloud project ID to use
        
    Returns:
        vertexai.GenerativeModel: Initialized model
    """
    try:
        # Reinitialize with project_id if provided
        if project_id:
            vertexai.init(
                project=project_id,
                location="europe-west1",
                api_endpoint="europe-west1-aiplatform.googleapis.com"
            )
            logger.info(f"Reinitialized Vertex AI with project ID: {project_id}")
        
        model = GenerativeModel(
            "gemini-2.5-pro",
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            system_instruction=[system_instruction] if system_instruction else None
        )
        logger.info("Successfully initialized Vertex AI Gemini model")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model: {str(e)}")
        raise RuntimeError("Failed to initialize Vertex AI model")

def process_with_vertex_ai(model, prompt, post_process=False, max_retries=5):
    """
    Process a prompt with Vertex AI with advanced retry logic and rate limiting.
    
    Args:
        model: The Vertex AI model instance
        prompt (str): The prompt to process
        post_process (bool): Whether to post-process the response to extract Python code
        max_retries (int): Maximum number of retries on failure
        
    Returns:
        str: The model's response text, or extracted Python code if post_process=True
    """
    # Keep track of consecutive failures for rate limiting
    global consecutive_failures
    global last_failure_time
    
    # Initialize global variables if not already set
    if 'consecutive_failures' not in globals():
        global consecutive_failures
        consecutive_failures = 0
    
    if 'last_failure_time' not in globals():
        global last_failure_time
        last_failure_time = 0
    
    # Apply dynamic cooldown if we're hitting rate limits
    if consecutive_failures > 3:
        cooldown = min(30, consecutive_failures * 5)  # Max 30 second cooldown
        time_since_last_failure = time.time() - last_failure_time
        if time_since_last_failure < cooldown:
            sleep_time = cooldown - time_since_last_failure
            logger.info(f"Rate limit cooldown: Waiting {sleep_time:.1f} seconds before next request...")
            time.sleep(sleep_time)
    
    for attempt in range(max_retries):
        try:
            # Calculate backoff with jitter to avoid thundering herd problem
            if attempt > 0:
                base_delay = min(30, 2 ** attempt)  # Cap at 30 seconds
                jitter = random.uniform(0, 0.1 * base_delay)  # 10% jitter
                delay = base_delay + jitter
                logger.info(f"Retry attempt {attempt+1}/{max_retries}: Waiting {delay:.2f} seconds...")
                time.sleep(delay)
            
            # Make the API call
            response = model.generate_content(prompt)
            
            # Reset consecutive failures counter on success
            consecutive_failures = 0
            
            if post_process:
                # Try to extract Python code from the response
                try:
                    code_block_match = re.search(r'```python\s*(.*?)\s*```', response.text, re.DOTALL)
                    if code_block_match:
                        code_block = code_block_match.group(1)
                        # Extract the chapters dictionary
                        local_vars = {}
                        exec(code_block, {}, local_vars)
                        if 'chapters' in local_vars:
                            return local_vars['chapters']
                        elif 'secties' in local_vars:
                            return local_vars['secties']
                except Exception as e:
                    logger.warning(f"Failed to post-process response: {str(e)}")
                    # Fall back to returning raw text
                    return response.text
            
            return response.text
            
        except Exception as e:
            # Update failure tracking
            consecutive_failures += 1
            last_failure_time = time.time()
            
            error_message = str(e)
            # Check if it's a rate limit error
            if "429" in error_message and "Resource exhausted" in error_message:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed with rate limit (429), applying exponential backoff: {error_message}")
                else:
                    logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                    raise
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying: {error_message}")
                else:
                    logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                    raise

# GUI Class for the pipeline
class NonVMSWPipelineGUI(QMainWindow):
    """PySide6 implementation of the Non-VMSW Pipeline GUI"""
    
    def __init__(self):
        super().__init__()
        
        # Initial setup
        self.setWindowTitle("AI Construct PDF Opdeler")
        self.setMinimumSize(1000, 800)
        self.resize(1200, 900)
        
        # Variables to store paths and settings
        self.pdf_path = ""
        self.category_file_path = ""
        self.output_dir = ""
        self.pdf_output_dir = ""
        self.second_output_dir = None  # Added for compatibility with step3_extract_category_pdfs
        self.third_output_dir = None   # Added for compatibility with step3_extract_category_pdfs
        self.include_explanations = True
        self.project_id = ""  # Start with empty project ID - environment vars used as fallback
        
        # Initialize output_dirs dictionary
        self.output_dirs = {'base': None, 'toc': None, 'category_matching': None, 'category_pdfs': None}
        
        # Track process information like in the original GUI
        self.last_toc_dir = None
        self.last_category_match_dir = None
        
        # Log counter
        self.log_counter = 0
        
        # Set up the central widget and scroll area
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout for central widget
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a container widget for the scroll area
        self.scroll_widget = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Set the scroll widget as the scroll area's widget
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Add scroll area to central layout
        central_layout.addWidget(self.scroll_area)
        
        # Create UI sections
        self.setup_header()
        self.setup_input_section()
        self.setup_progress_section()
        self.setup_log_section()
        self.setup_output_section()
        
        # Apply the stylesheet to the entire application
        self.apply_stylesheet()
        
        # Add a timer to keep UI responsive
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(QApplication.processEvents)
        self.refresh_timer.start(100)  # Update every 100ms
        
        # Log startup
        self.log("Application started. Please select input files and run the pipeline steps.")
    
    def setup_header(self):
        """Setup the header section with title and description"""
        header_frame = StyledFrame("primary")
        # Use a more flexible grid layout instead
        header_layout = QGridLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(0)
        
        # Left side for BW logo (without the white frame)
        bw_logo_label = QLabel()
        bw_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements", "Logo", "BWlogo.png")
        if os.path.exists(bw_logo_path):
            try:
                bw_logo_pixmap = QPixmap(bw_logo_path)
                bw_logo_pixmap = bw_logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                bw_logo_label.setPixmap(bw_logo_pixmap)
                bw_logo_label.setStyleSheet("background-color: white; border-radius: 5px; padding: 3px;")
                bw_logo_label.setFixedSize(80, 80)
                bw_logo_label.setAlignment(Qt.AlignCenter)
            except Exception as e:
                logger.error(f"Error loading BW logo: {e}")
                bw_logo_label.setText("BW Logo")
        else:
            logger.warning(f"BW logo not found at: {bw_logo_path}")
            bw_logo_label.setText("BW Logo")

        # Right side for AICO logo (without the white frame)
        aico_logo_label = QLabel()
        aico_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Requirements", "aiconew.svg")
        if os.path.exists(aico_logo_path):
            try:
                aico_logo_pixmap = QPixmap(aico_logo_path)
                aico_logo_pixmap = aico_logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                aico_logo_label.setPixmap(aico_logo_pixmap)
                aico_logo_label.setStyleSheet("background-color: white; border-radius: 5px; padding: 3px;")
                aico_logo_label.setFixedSize(80, 80)
                aico_logo_label.setAlignment(Qt.AlignCenter)
            except Exception as e:
                logger.error(f"Error loading AICO logo: {e}")
                aico_logo_label.setText("AICO Logo")
        else:
            logger.warning(f"AICO logo not found at: {aico_logo_path}")
            aico_logo_label.setText("AICO Logo")
        
        # Title and subtitle directly in header layout - using exact same text as in 2703 file
        title_label = QLabel("AI Construct PDF Opdeler")
        title_label.setStyleSheet(f"""
            color: {COLORS["light"]};
            font-size: 22px;
            font-weight: bold;
            padding: 0px;
        """)
        title_label.setAlignment(Qt.AlignHCenter)
        
        subtitle_label = QLabel("Deel uw lastenboek op in delen per onderaannemer")
        subtitle_label.setStyleSheet(f"""
            color: {COLORS["light"]};
            font-size: 14px;
            padding: 0px;
        """)
        subtitle_label.setAlignment(Qt.AlignHCenter)
        
        # Add everything to the grid layout
        header_layout.addWidget(bw_logo_label, 0, 0, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label, 0, 1, Qt.AlignCenter)
        header_layout.addWidget(subtitle_label, 1, 1, Qt.AlignCenter)
        header_layout.addWidget(aico_logo_label, 0, 2, 2, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        # Make the middle column stretch
        header_layout.setColumnStretch(1, 1)
        
        self.main_layout.addWidget(header_frame)
    
    def setup_input_section(self):
        """Setup the input configuration section"""
        input_frame = StyledFrame()
        input_layout = QGridLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(15)
        
        # PDF File Selection
        pdf_label = QLabel("PDF Bestand:")
        pdf_label.setStyleSheet("font-weight: bold;")
        
        self.pdf_path_edit = QTextEdit()
        self.pdf_path_edit.setReadOnly(True)
        self.pdf_path_edit.setMaximumHeight(40)
        self.pdf_path_edit.setMinimumHeight(30)
        self.pdf_path_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_path_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_path_edit.setPlaceholderText("Geen bestand geselecteerd")
        self.pdf_path_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.browse_button = StyledButton("Bladeren", "secondary")
        self.browse_button.clicked.connect(self.browse_pdf)
        
        # Category file selection
        cat_label = QLabel("Categorie Bestand:")
        cat_label.setStyleSheet("font-weight: bold;")
        
        self.cat_path_edit = QTextEdit()
        self.cat_path_edit.setReadOnly(True)
        self.cat_path_edit.setMaximumHeight(40)
        self.cat_path_edit.setMinimumHeight(30)
        self.cat_path_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_path_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_path_edit.setPlaceholderText("Geen bestand geselecteerd")
        self.cat_path_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.cat_browse_button = StyledButton("Bladeren", "secondary")
        self.cat_browse_button.clicked.connect(self.browse_category_file)
        
        # Output directory selection
        out_label = QLabel("Uitvoermap:")
        out_label.setStyleSheet("font-weight: bold;")
        
        self.out_path_edit = QTextEdit()
        self.out_path_edit.setReadOnly(True)
        self.out_path_edit.setMaximumHeight(40)
        self.out_path_edit.setMinimumHeight(30)
        self.out_path_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.out_path_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.out_path_edit.setPlaceholderText("Geen map geselecteerd")
        self.out_path_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.out_browse_button = StyledButton("Bladeren", "secondary")
        self.out_browse_button.clicked.connect(self.browse_output_dir)
        
        # PDF Output directory selection
        pdf_out_label = QLabel("PDF Uitvoermap (Optioneel):")
        pdf_out_label.setStyleSheet("font-weight: bold;")
        
        self.pdf_out_path_edit = QTextEdit()
        self.pdf_out_path_edit.setReadOnly(True)
        self.pdf_out_path_edit.setMaximumHeight(40)
        self.pdf_out_path_edit.setMinimumHeight(30)
        self.pdf_out_path_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_out_path_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_out_path_edit.setPlaceholderText("Geen map geselecteerd")
        self.pdf_out_path_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.pdf_out_browse_button = StyledButton("Bladeren", "secondary")
        self.pdf_out_browse_button.clicked.connect(self.browse_pdf_output_dir)
        
        # Project ID input
        project_label = QLabel("Google Cloud Project ID:")
        project_label.setStyleSheet("font-weight: bold;")
        
        self.project_id_edit = QLineEdit()
        self.project_id_edit.setText("")  # Start empty
        self.project_id_edit.setPlaceholderText("Uses environment variable if empty")
        self.project_id_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 30px;
            }}
        """)
        self.project_id_edit.textChanged.connect(self.update_project_id)
        
        # Explanation checkbox
        self.explanation_checkbox = QCheckBox("Geen uitleg voor matches (sneller proces)")
        self.explanation_checkbox.setChecked(False)
        self.explanation_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['dark']};
                font-weight: bold;
                margin-top: 10px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['secondary']};
                border: 1px solid {COLORS['secondary']};
            }}
        """)
        
        # Gemini model selection
        model_label = QLabel("Gemini Model:")
        model_label.setStyleSheet("font-weight: bold;")
        
        self.model_selector = QComboBox()
        self.model_selector.addItem("Gemini 2.5 Pro", "gemini-2.5-pro")
        self.model_selector.addItem("Gemini 2.5 Flash", "gemini-2.5-flash")
        self.model_selector.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                min-height: 30px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url(dropdown.png);
                width: 14px;
                height: 14px;
            }}
        """)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        self.run_button = StyledButton("Start Pipeline", "primary")
        self.run_button.clicked.connect(self.run_complete_pipeline)
        self.run_button.setMinimumWidth(200)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.run_button)
        
        # Add all elements to the grid layout
        input_layout.addWidget(pdf_label, 0, 0)
        input_layout.addWidget(self.pdf_path_edit, 0, 1)
        input_layout.addWidget(self.browse_button, 0, 2)
        
        input_layout.addWidget(cat_label, 1, 0)
        input_layout.addWidget(self.cat_path_edit, 1, 1)
        input_layout.addWidget(self.cat_browse_button, 1, 2)
        
        input_layout.addWidget(out_label, 2, 0)
        input_layout.addWidget(self.out_path_edit, 2, 1)
        input_layout.addWidget(self.out_browse_button, 2, 2)
        
        input_layout.addWidget(pdf_out_label, 3, 0)
        input_layout.addWidget(self.pdf_out_path_edit, 3, 1)
        input_layout.addWidget(self.pdf_out_browse_button, 3, 2)
        
        input_layout.addWidget(project_label, 4, 0)
        input_layout.addWidget(self.project_id_edit, 4, 1)
        
        input_layout.addWidget(self.explanation_checkbox, 5, 0, 1, 1)
        input_layout.addWidget(model_label, 5, 1, 1, 1, Qt.AlignRight)
        input_layout.addWidget(self.model_selector, 5, 2, 1, 1)
        
        input_layout.addLayout(button_layout, 6, 0, 1, 3)
        
        # Make the middle column expandable
        input_layout.setColumnStretch(1, 1)
        
        # Set row heights
        for i in range(input_layout.rowCount()):
            input_layout.setRowMinimumHeight(i, 45)
        
        self.main_layout.addWidget(input_frame)
    
    def setup_progress_section(self):
        """Setup the progress tracking section"""
        progress_frame = StyledFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        # Progress bar group
        progress_group = QGroupBox("Pipeline Voortgang")
        progress_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS["mid_gray"]};
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {COLORS["primary"]};
            }}
        """)
        
        progress_group_layout = QVBoxLayout(progress_group)
        progress_group_layout.setContentsMargins(10, 20, 10, 10)
        progress_group_layout.setSpacing(15)
        
        # Create step indicators with status
        steps_layout = QGridLayout()
        steps_layout.setColumnStretch(0, 2)  # Give more space to step description
        steps_layout.setColumnStretch(1, 1)  # Less space for status
        steps_layout.setHorizontalSpacing(20)
        steps_layout.setVerticalSpacing(10)
        
        # Step 1
        step1_label = QLabel("Stap 1: Inhoudstafel Genereren")
        step1_label.setStyleSheet("font-weight: bold;")
        self.step1_status = QLabel("Niet gestart")
        self.step1_status.setStyleSheet(f"""
            color: {COLORS['dark_gray']};
            padding: 5px;
            border-radius: 3px;
            background-color: {COLORS['light_gray']};
        """)
        
        # Step 2
        step2_label = QLabel("Stap 2: Categorieën Matchen")
        step2_label.setStyleSheet("font-weight: bold;")
        self.step2_status = QLabel("Niet gestart")
        self.step2_status.setStyleSheet(f"""
            color: {COLORS['dark_gray']};
            padding: 5px;
            border-radius: 3px;
            background-color: {COLORS['light_gray']};
        """)
        
        # Step 3
        step3_label = QLabel("Stap 3: PDF's Extraheren")
        step3_label.setStyleSheet("font-weight: bold;")
        self.step3_status = QLabel("Niet gestart")
        self.step3_status.setStyleSheet(f"""
            color: {COLORS['dark_gray']};
            padding: 5px;
            border-radius: 3px;
            background-color: {COLORS['light_gray']};
        """)
        
        # Store references to step labels in a list for easier access
        self.step_labels = [step1_label, step2_label, step3_label]
        self.step_statuses = [self.step1_status, self.step2_status, self.step3_status]
        
        # Add steps to layout
        steps_layout.addWidget(step1_label, 0, 0)
        steps_layout.addWidget(self.step1_status, 0, 1)
        steps_layout.addWidget(step2_label, 1, 0)
        steps_layout.addWidget(self.step2_status, 1, 1)
        steps_layout.addWidget(step3_label, 2, 0)
        steps_layout.addWidget(self.step3_status, 2, 1)
        
        progress_group_layout.addLayout(steps_layout)
        
        # Overall progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% Voltooid")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                text-align: center;
                background-color: {COLORS['light_gray']};
                color: {COLORS['dark']};
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background-color: {COLORS['secondary']};
                border-radius: 5px;
            }}
        """)
        
        progress_group_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(progress_group)
        
        # Step execution buttons - only keep Step 1 button
        buttons_layout = QHBoxLayout()
        
        self.step1_button = StyledButton("Genereer Inhoudstafel", "secondary")
        self.step1_button.clicked.connect(self.run_step1)
        
        buttons_layout.addWidget(self.step1_button)
        buttons_layout.addStretch(1)  # Add stretch to align button to the left
        
        progress_layout.addLayout(buttons_layout)
        
        self.main_layout.addWidget(progress_frame)
    
    def setup_log_section(self):
        """Setup the log output section"""
        log_frame = StyledFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        # Log window header
        log_label = QLabel("Log Uitvoer")
        log_label.setStyleSheet(f"""
            font-weight: bold;
            color: {COLORS['dark']};
            font-size: 14px;
        """)
        
        # Create the log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)
        
        # Add "Clear Log" button
        clear_log_button = StyledButton("Clear Log", "dark")
        clear_log_button.setMinimumWidth(100)
        clear_log_button.clicked.connect(self.clear_log)
        
        # Add the widgets to the layout
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(clear_log_button)
        log_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(log_frame)
    
    def setup_output_section(self):
        """Setup the output file section"""
        output_frame = StyledFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 15, 15, 15)
        
        # Output files header
        output_label = QLabel("Output Files")
        output_label.setStyleSheet(f"""
            font-weight: bold;
            color: {COLORS['dark']};
            font-size: 14px;
        """)
        
        # Create the output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(100)
        self.output_text.setPlaceholderText("Output files will be displayed here after processing")
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add open output folder button
        self.open_output_button = StyledButton("Open Output Folder", "alternate")
        self.open_output_button.clicked.connect(self.open_output_folder)
        self.open_output_button.setEnabled(False)
        
        # Add button to layout
        button_layout.addStretch(1)
        button_layout.addWidget(self.open_output_button)
        
        # Add the widgets to the layout
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        output_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(output_frame)
    
    def apply_stylesheet(self):
        """Apply global stylesheet to the application"""
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS["light"]};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }}
            
            QLabel {{
                color: {COLORS["dark"]};
                font-size: 12px;
            }}
            
            QGroupBox {{
                font-size: 13px;
            }}
            
            QToolTip {{
                background-color: {COLORS["dark"]};
                color: {COLORS["light"]};
                border: none;
                padding: 5px;
            }}
            
            QTextEdit {{
                font-size: 12px;
            }}
            
            QPushButton {{
                font-size: 13px;
            }}
        """)

    def log(self, message):
        """Add a message to the log with timestamp and counter"""
        try:
            # Use a simple counter instead of datetime
            self.log_counter += 1
            formatted_message = f"[{self.log_counter}] {message}"
            
            self.log_text.append(formatted_message)
            
            # Ensure the logger also gets the message
            logger.info(message)
            
        except Exception as e:
            logger.error(f"Error in log method: {str(e)}")
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.clear()
        self.log("Log cleared")
    
    def browse_pdf(self):
        """Open file dialog to select a PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_edit.setPlainText(file_path)
            self.log(f"Selected PDF file: {file_path}")
    
    def browse_category_file(self):
        """Open file dialog to select a category file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Category File", "", "Python Files (*.py);;All Files (*.*)"
        )
        
        if file_path:
            self.category_file_path = file_path
            self.cat_path_edit.setPlainText(file_path)
            self.log(f"Selected category file: {file_path}")
    
    def browse_output_dir(self):
        """Open directory dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        
        if directory:
            self.output_dir = directory
            self.out_path_edit.setPlainText(directory)
            self.log(f"Selected output directory: {directory}")
    
    def browse_pdf_output_dir(self):
        """Open directory dialog to select PDF output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select PDF Output Directory"
        )
        
        if directory:
            self.pdf_output_dir = directory
            self.second_output_dir = directory  # Also set second_output_dir for compatibility
            self.pdf_out_path_edit.setPlainText(directory)
            self.log(f"Selected PDF output directory: {directory}")
    
    def update_step_status(self, step_index, status, color=None):
        """Update the status of a step in the UI"""
        if step_index < 0 or step_index >= len(self.step_statuses):
            return
            
        status_label = self.step_statuses[step_index]
        status_label.setText(status)
        
        if color:
            status_label.setStyleSheet(f"""
                color: {color};
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
                background-color: {COLORS['light_gray']};
            """)
    
    def update_progress(self, value):
        """Update the progress bar value"""
        self.progress_bar.setValue(value)
    
    def open_output_folder(self):
        """Open the output folder in the file explorer"""
        if not self.output_dir:
            QMessageBox.warning(self, "No Output Directory", "Please select an output directory first.")
            return
            
        import os
        import subprocess
        try:
            if os.path.exists(self.output_dir):
                if sys.platform == 'win32':
                    os.startfile(self.output_dir)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', self.output_dir])
                else:  # Linux
                    subprocess.run(['xdg-open', self.output_dir])
                self.log(f"Opened output directory: {self.output_dir}")
            else:
                QMessageBox.warning(self, "Directory Not Found", f"The directory {self.output_dir} does not exist.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open the directory: {str(e)}")
            self.log(f"Error opening directory: {str(e)}")
    
    # Methods to connect to the pipeline functions
    def run_step1(self):
        """Run step 1: Generate table of contents"""
        if not self.validate_inputs(check_pdf=True, check_output_dir=True):
            return
            
        # Disable UI elements during processing
        self.setEnabled(False)
            
        # Initialize progress bar and status
        self.update_step_status(0, "In uitvoering", "#3399FF")
        self.update_progress(0)
        
        self.start_time = time.time()
        self.log(f"Starting Step 1: TOC Generation...")
        self.log(f"PDF: {self.pdf_path}")
        
        try:
            # Run the TOC generation
            chapters, toc_output_dir = step1_generate_toc(self.pdf_path, self.output_dir)
            
            # Store the results for later steps
            self.chapters = chapters
            self.last_toc_dir = toc_output_dir
            self.output_dirs['toc'] = toc_output_dir
            
            # Update UI with success
            self.update_step_status(0, "Complete", "#33CC33")
            self.update_progress(100)
            
            self.log(f"TOC generation complete! {len(chapters)} chapters found.")
            self.log(f"Output directory: {toc_output_dir}")
            
            # Show success message
            QMessageBox.information(
                self,
                "Step 1 Complete",
                f"TOC generation completed successfully!\n\nExtracted {len(chapters)} chapters from the document."
            )
        except Exception as e:
            self.log(f"Error in Step 1: {str(e)}")
            logger.exception("Detailed error information:")
            self.update_step_status(0, "Mislukt", "#FF3333")
            
            # Show error message
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred during TOC generation: {str(e)}"
            )
        finally:
            # Re-enable UI
            self.setEnabled(True)
    
    def run_step2(self):
        """Run step 2: Category matching"""
        if not self.validate_inputs(check_category_file=True):
            return
        
        # Get the selected Gemini model name
        selected_model = self.model_selector.currentData()
            
        # Disable UI elements during processing
        self.setEnabled(False)
        
        # Initialize progress
        self.update_step_status(1, "In uitvoering", "#3399FF")
        self.update_progress(0)
        
        # Set global PROJECT_ID for the steps that use it internally
        global PROJECT_ID
        original_project_id = PROJECT_ID
        PROJECT_ID = self.project_id
        
        try:
            # Initialize the AI model with the selected model name and project ID
            model, model_name = initialize_gemini_model(selected_model, self.project_id)
            
            self.log("Starting Step 2: Category Matching...")
            self.log(f"Using model: {model_name}")
            
            # Check if we need to load chapters from a previous step, or use cached data
            if not hasattr(self, 'chapters') or not self.chapters:
                if not self.last_toc_dir:
                    # Prompt the user to run step 1 first
                    QMessageBox.warning(self, "Missing Data", "Please run Step 1 (TOC Generation) first.")
                    self.update_step_status(1, "Niet gestart", "#CCCCCC")
                    self.update_progress(0)
                    self.setEnabled(True)
                    return
                
                # Load chapters from the last successful step 1 run
                try:
                    with open(os.path.join(self.last_toc_dir, "chapters.json"), 'r', encoding='utf-8') as f:
                        self.chapters = json.load(f)
                    self.log(f"Loaded {len(self.chapters)} chapters from {self.last_toc_dir}")
                except Exception as e:
                    self.log(f"Error loading chapters from previous step: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Failed to load chapters from previous step: {str(e)}")
                    self.update_step_status(1, "Mislukt", "#FF3333")
                    self.update_progress(0)
                    self.setEnabled(True)
                    return
            
            # Update the explanation flag from the checkbox
            global INCLUDE_EXPLANATIONS
            INCLUDE_EXPLANATIONS = not self.explanation_checkbox.isChecked()
            
            # Determine the correct base directory for consistent directory structure
            if self.last_toc_dir and os.path.basename(self.last_toc_dir).startswith("step1_"):
                # If last_toc_dir is a step directory, use its parent as the base directory
                pipeline_dir = os.path.dirname(self.last_toc_dir)
            else:
                # Otherwise use the output_dir directly
                pipeline_dir = self.output_dir
            
            # Run the category matching
            category_match_dir, chapter_results, section_results = step2_match_categories(
                self.chapters, 
                self.last_toc_dir, 
                self.category_file_path, 
                base_dir=pipeline_dir,
                model=initialize_gemini_model(selected_model, self.project_id)[0]
            )
            self.update_step_status(1, "Complete", "#33CC33")
            self.update_progress(100)
            self.last_category_match_dir = category_match_dir
            self.output_dirs['category_matching'] = category_match_dir
            
            # Count matches
            total_chapter_matches = sum(len(data["matches"]) for data in chapter_results.values())
            total_section_matches = sum(len(data["matches"]) for data in section_results.values())
            
            # Store the results for step 3
            self.chapter_results = chapter_results
            self.section_results = section_results
            
            # Inform the user
            self.log(f"Category matching complete! Found {total_chapter_matches} chapter matches and {total_section_matches} section matches.")
            self.log(f"Results saved to {category_match_dir}")
            
            # Update GUI
            QMessageBox.information(
                self,
                "Step 2 Complete",
                f"Category matching completed successfully!\n\n"
                f"Found {total_chapter_matches} chapter matches and {total_section_matches} section matches."
            )
            
        except Exception as e:
            self.log(f"Error in Step 2: {str(e)}")
            logger.exception("Detailed error information:")
            self.update_step_status(1, "Mislukt", "#FF3333")
            QMessageBox.critical(self, "Error", f"An error occurred during category matching: {str(e)}")
        finally:
            # Re-enable UI
            self.setEnabled(True)
            
            # Restore original project ID
            PROJECT_ID = original_project_id
    
    def run_step3(self):
        """Run step 3: Extract category PDFs"""
        if not self.validate_inputs(check_pdf=True, check_output_dir=True):
            return
            
        # Check if previous steps have been completed
        if not hasattr(self, 'chapter_results') or not hasattr(self, 'section_results') or not self.last_category_match_dir:
            QMessageBox.warning(self, "Missing Data", "Please run Step 2 (Category Matching) first.")
            return
        
        # Disable UI elements during processing
        self.setEnabled(False)
            
        # Initialize progress
        self.update_step_status(2, "In uitvoering", "#3399FF")
        self.update_progress(0)
        
        self.log(f"Starting Step 3: PDF Extraction...")
        self.log(f"PDF: {self.pdf_path}")
        self.log(f"Using output directory: {self.output_dir}")
        if self.pdf_output_dir:
            self.log(f"Using PDF output directory: {self.pdf_output_dir}")
            # Make sure second_output_dir is set for backward compatibility
            self.second_output_dir = self.pdf_output_dir
        
        # Determine the correct pipeline directory to maintain consistent directory structure
        pipeline_dir = None
        if self.last_category_match_dir and os.path.basename(self.last_category_match_dir).startswith("step2_"):
            # If last_category_match_dir is a step directory, get its parent
            pipeline_dir = os.path.dirname(self.last_category_match_dir)
            self.log(f"Using pipeline directory from category matching: {pipeline_dir}")
        elif self.last_toc_dir and os.path.basename(self.last_toc_dir).startswith("step1_"):
            # If we have a TOC directory but no category directory, use TOC's parent
            pipeline_dir = os.path.dirname(self.last_toc_dir)
            self.log(f"Using pipeline directory from TOC generation: {pipeline_dir}")
        else:
            # Otherwise use the output_dir directly
            pipeline_dir = self.output_dir
            self.log(f"Using main output directory as pipeline directory: {pipeline_dir}")
        
        try:
            # Execute step 3 with stored results from step 2
            pdf_count, pdf_output_dir = step3_extract_category_pdfs(
                self.pdf_path,
                self.chapter_results,
                self.section_results,
                self.last_category_match_dir,
                self.category_file_path,
                self.second_output_dir,
                self.third_output_dir,
                base_dir=pipeline_dir
            )
            
            # Store results
            self.output_dirs['category_pdfs'] = pdf_output_dir
            
            # Update UI
            self.update_step_status(2, "Complete", "#33CC33")
            self.update_progress(100)
            
            self.log(f"PDF extraction complete! {pdf_count} PDFs created.")
            self.log(f"Output directory: {pdf_output_dir}")
            
            # Show success message with option to open the folder
            result = QMessageBox.information(
                self,
                "Step 3 Complete",
                f"PDF extraction completed successfully!\n\n{pdf_count} PDFs were created.\n\nWould you like to open the output folder?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if result == QMessageBox.Yes:
                # Open the output folder
                self.open_output_folder()
                
        except Exception as e:
            self.log(f"Error in Step 3: {str(e)}")
            logger.exception("Detailed error information:")
            self.update_step_status(2, "Mislukt", "#FF3333")
            
            # Show error message
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred during PDF extraction: {str(e)}"
            )
        finally:
            # Re-enable UI
            self.setEnabled(True)
    
    def run_complete_pipeline(self):
        """Run the complete pipeline, executing all steps in sequence"""
        # Validate all required inputs
        if not self.validate_inputs(check_pdf=True, check_category_file=True, check_output_dir=True):
            return
            
        # Get the selected Gemini model name
        selected_model = self.model_selector.currentData()
            
        # Disable UI elements during processing
        self.setEnabled(False)
            
        # Reset progress bar and status
        self.progress_bar.setValue(0)
        self.update_step_status(0, "Niet gestart", "default")
        self.update_step_status(1, "Niet gestart", "default")
        self.update_step_status(2, "Niet gestart", "default")
        
        # Update explanation setting based on checkbox
        global INCLUDE_EXPLANATIONS
        INCLUDE_EXPLANATIONS = not self.explanation_checkbox.isChecked()
        
        # Set global PROJECT_ID for the steps that use it internally
        global PROJECT_ID
        original_project_id = PROJECT_ID
        PROJECT_ID = self.project_id
        
        # Initialize output directories dictionary
        self.output_dirs = {'base': self.output_dir, 'toc': None, 'category_matching': None, 'category_pdfs': None}
        
        # Set start time for calculating total duration
        self.start_time = time.time()
        
        # Log start
        self.log(f"Complete pipeline gestart met model {selected_model}")
        self.log(f"PDF: {self.pdf_path}")
        self.log(f"Categoriebestand: {self.category_file_path}")
        self.log(f"Uitvoermap: {self.output_dir}")
        if self.project_id:
            self.log("Using project ID from input field")
        else:
            self.log("Using project ID from environment if available")
        if self.pdf_output_dir:
            self.log(f"PDF Uitvoermap: {self.pdf_output_dir}")
            # Make sure second_output_dir is set for backward compatibility
            self.second_output_dir = self.pdf_output_dir
        
        try:
            # Step 1: Generate Table of Contents
            logger.info("Step 1: Generating Table of Contents")
            step1_attempts = 0
            step1_max_attempts = 3
            step1_success = False
            step1_backoff = 2  # Initial backoff time in seconds
            chapters = None
            toc_output_dir = None
            
            while step1_attempts < step1_max_attempts and not step1_success:
                try:
                    if step1_attempts > 0:
                        wait_time = step1_backoff * (2 ** (step1_attempts - 1)) * (0.5 + 0.5 * random.random())  # Add jitter
                        logger.info(f"Retrying Step 1 after {wait_time:.2f} seconds (attempt {step1_attempts + 1}/{step1_max_attempts})...")
                        time.sleep(wait_time)
                    
                    chapters, toc_output_dir = step1_generate_toc(self.pdf_path, self.output_dir)
                    self.update_step_status(0, "Complete", "#33CC33")
                    self.update_progress(100)
                    self.last_toc_dir = toc_output_dir
                    self.output_dirs['toc'] = toc_output_dir
                    logger.info(f"Step 1 completed successfully with {len(chapters)} chapters identified")
                    step1_success = True
                except Exception as e:
                    step1_attempts += 1
                    logger.error(f"Error in Step 1 (attempt {step1_attempts}/{step1_max_attempts}): {str(e)}")
                    if step1_attempts == step1_max_attempts:
                        raise RuntimeError(f"Step 1 failed after {step1_max_attempts} attempts: {str(e)}")
            
            # Rate limiting cooldown between step 1 and 2
            cooldown_time = 5  # seconds
            logger.info(f"Rate limiting: Cooling down for {cooldown_time} seconds before starting Step 2...")
            time.sleep(cooldown_time)
            
            # Step 2: Match categories to chapters and sections
            logger.info("Step 2: Matching categories to chapters and sections")
            step2_attempts = 0
            step2_max_attempts = 3
            step2_success = False
            step2_backoff = 3  # Initial backoff time in seconds
            chapter_results = None
            section_results = None
            category_match_dir = None
            
            while step2_attempts < step2_max_attempts and not step2_success:
                try:
                    if step2_attempts > 0:
                        wait_time = step2_backoff * (2 ** (step2_attempts - 1)) * (0.5 + 0.5 * random.random())  # Add jitter
                        logger.info(f"Retrying Step 2 after {wait_time:.2f} seconds (attempt {step2_attempts + 1}/{step2_max_attempts})...")
                        time.sleep(wait_time)
                    
                    # Pass the base directory to ensure step2 creates its directory in the same run
                    # Determine the correct base directory (parent of toc_output_dir)
                    pipeline_dir = os.path.dirname(toc_output_dir)
                    category_match_dir, chapter_results, section_results = step2_match_categories(
                        chapters, 
                        toc_output_dir, 
                        self.category_file_path, 
                        base_dir=pipeline_dir,
                        model=initialize_gemini_model(selected_model, self.project_id)[0]
                    )
                    self.update_step_status(1, "Complete", "#33CC33")
                    self.update_progress(100)
                    self.last_category_match_dir = category_match_dir
                    self.output_dirs['category_matching'] = category_match_dir
                    logger.info(f"Step 2 completed successfully with {len(chapter_results)} chapter matches and {len(section_results)} section matches")
                    step2_success = True
                except Exception as e:
                    step2_attempts += 1
                    logger.error(f"Error in Step 2 (attempt {step2_attempts}/{step2_max_attempts}): {str(e)}")
                    if step2_attempts == step2_max_attempts:
                        raise RuntimeError(f"Step 2 failed after {step2_max_attempts} attempts: {str(e)}")
            
            # Rate limiting cooldown between step 2 and 3 (less critical as step 3 doesn't use API)
            cooldown_time = 2  # seconds
            logger.info(f"Rate limiting: Cooling down for {cooldown_time} seconds before starting Step 3...")
            time.sleep(cooldown_time)
            
            # Step 3: Split document into category-specific PDFs
            logger.info("Step 3: Splitting PDF into Category-Specific Documents")
            try:
                # Pass the correct pipeline directory to ensure consistent directory structure
                # We use the same pipeline_dir as in step 2, which is the parent of toc_output_dir
                pipeline_dir = os.path.dirname(toc_output_dir)
                self.log(f"Using pipeline directory for step 3: {pipeline_dir}")
                
                pdf_count, pdf_output_dir = step3_extract_category_pdfs(
                    self.pdf_path, 
                    chapter_results, 
                    section_results, 
                    category_match_dir, 
                    self.category_file_path,
                    self.second_output_dir,
                    self.third_output_dir,
                    base_dir=pipeline_dir
                )
                self.update_step_status(2, "Complete", "#33CC33")
                self.update_progress(100)
                self.output_dirs['category_pdfs'] = pdf_output_dir
                logger.info(f"Step 3 completed successfully with {pdf_count} PDFs created")
            except Exception as e:
                logger.error(f"Error in Step 3: {str(e)}")
                raise RuntimeError(f"Step 3 failed: {str(e)}")
            
            # Calculate total execution time
            total_time = time.time() - self.start_time
            
            logger.info("=" * 50)
            logger.info("COMPLETE PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logger.info(f"Total execution time: {total_time:.2f} seconds")
            logger.info(f"Output directories:")
            for dir_name, dir_path in self.output_dirs.items():
                logger.info(f"- {dir_name}: {dir_path}")
            logger.info("=" * 50)
            
            # Generate report file in the base directory
            try:
                # Calculate category statistics
                try:
                    if self.category_file_path:
                        # Import the module to get the category dataframe
                        category_dir = os.path.dirname(self.category_file_path)
                        category_module = os.path.splitext(os.path.basename(self.category_file_path))[0]
                        
                        if category_dir not in sys.path:
                            sys.path.append(category_dir)
                            
                        module = __import__(category_module)
                        df = getattr(module, 'df', None)
                    else:
                        from nonvmswhoofdstukken_pandas import df
                        
                    stats = calculate_category_statistics(chapter_results, section_results, df)
                except Exception as e:
                    logger.error(f"Error calculating category statistics: {str(e)}")
                    stats = {
                        "avg_matches_per_chapter": 0,
                        "avg_matches_per_section": 0,
                        "most_frequent_categories": [],
                        "categories_with_no_matches": [],
                        "num_categories_with_no_matches": 0
                    }
                    
                # Write report to the base directory, not to any step directory
                report_file = os.path.join(self.output_dirs['base'], "pipeline_execution_report.txt")
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write("Non-VMSW Document Processing Pipeline - Execution Report\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Execution date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Input PDF: {self.pdf_path}\n")
                    f.write(f"Total execution time: {total_time:.2f} seconds\n\n")
                    
                    f.write("Step 1: Table of Contents Generation\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Identified chapters: {len(chapters)}\n")
                    f.write(f"Output directory: {toc_output_dir}\n\n")
                    
                    f.write("Step 2: Category Matching\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Chapter matches: {len(chapter_results)}\n")
                    f.write(f"Section matches: {len(section_results)}\n")
                    f.write(f"Average matches per chapter: {stats['avg_matches_per_chapter']:.1f}\n")
                    f.write(f"Average matches per section: {stats['avg_matches_per_section']:.1f}\n")
                    f.write(f"Most frequently matched categories: {', '.join(stats['most_frequent_categories'])}\n")
                    f.write(f"Categories with no matches ({stats['num_categories_with_no_matches']} categories had no matches)\n")
                    f.write(f"Output directory: {category_match_dir}\n\n")
                    
                    f.write("Step 3: PDF Extraction\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Generated PDFs: {pdf_count}\n")
                    f.write(f"Output directory: {pdf_output_dir}\n")
                    if self.second_output_dir:
                        f.write(f"Second output directory: {self.second_output_dir}\n")
                        f.write(f"Data files directory: {os.path.join(self.second_output_dir, 'data')}\n")
                    
                    # Only write third output directory info if it exists and is not None
                    third_output_dir = locals().get('third_output_dir')
                    if third_output_dir:
                        f.write(f"Third output directory: {third_output_dir}\n")
                        f.write(f"Data files directory: {os.path.join(third_output_dir, 'data')}\n")
                    
                    return True, self.output_dirs
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                logger.exception(e)
                return False, self.output_dirs
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            logger.exception("Detailed error information:")
            return False, self.output_dirs
        
        finally:
            # Restore original PROJECT_ID
            PROJECT_ID = original_project_id
            # Re-enable UI
            self.setEnabled(True)
    
    def validate_inputs(self, check_pdf=False, check_category_file=False, check_output_dir=False):
        """Validate required inputs before running pipeline steps"""
        if check_pdf and not self.pdf_path:
            QMessageBox.warning(self, "Missing Input", "Please select a PDF file.")
            return False
            
        if check_category_file and not self.category_file_path:
            QMessageBox.warning(self, "Missing Input", "Please select a category file.")
            return False
            
        if check_output_dir and not self.output_dir:
            QMessageBox.warning(self, "Missing Input", "Please select an output directory.")
            return False
            
        return True

    def update_project_id(self):
        """Update the project ID when it changes in the UI"""
        new_project_id = self.project_id_edit.text().strip()
        if new_project_id != self.project_id:
            self.project_id = new_project_id
            if self.project_id:
                self.log(f"Project ID updated")
            else:
                self.log("Project ID cleared, will use environment variable if available")
            
            # Try to reinitialize Vertex AI with new project ID
            self.reinitialize_vertex_ai()
    
    def reinitialize_vertex_ai(self):
        """Reinitialize Vertex AI with the current project ID"""
        try:
            effective_project_id = self.project_id
            if not effective_project_id:
                self.log("Using project ID from environment variable")
                # Try to get from environment but don't display it
                effective_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
            
            if effective_project_id:
                vertexai.init(
                    project=effective_project_id,
                    location="europe-west1",
                    api_endpoint="europe-west1-aiplatform.googleapis.com"
                )
                self.log(f"Successfully reinitialized Vertex AI")
            else:
                self.log("Warning: No Project ID specified and none found in environment.")
        except Exception as e:
            self.log(f"Error initializing Vertex AI: {str(e)}")
            QMessageBox.warning(
                self, 
                "Vertex AI Initialization Error", 
                f"Failed to initialize Vertex AI: {str(e)}"
            )

def setup_output_directory(step_name=None, base_output_dir=None):
    """
    Create an output directory structure based on script name and a sequential index.
    
    Args:
        step_name (str, optional): Name of the step being executed
        base_output_dir (str, optional): Base directory for outputs (overrides default)
        
    Returns:
        str: Path to the output directory
    """
    # Get script name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # Determine the base directory
    base_output_path = base_output_dir if base_output_dir else "output" # Changed default to relative "output"
    
    # Check if base_output_dir is already a pipeline directory or contains one
    is_pipeline_dir = False
    pipeline_root = None
    
    if base_output_dir:
        # Check if the path contains a pipeline directory component
        path_parts = base_output_dir.split(os.sep)
        for i, part in enumerate(path_parts):
            if part.startswith("pipeline_"):
                is_pipeline_dir = True
                # Get the path up to and including the pipeline directory
                pipeline_root = os.sep.join(path_parts[:i+1])
                logger.info(f"Found existing pipeline directory in path: {pipeline_root}")
                break
        
        # Fallback to the old method if we didn't find a pipeline directory
        if not is_pipeline_dir:
            dirname = os.path.basename(base_output_dir)
            parent_dirname = os.path.basename(os.path.dirname(base_output_dir))
            if dirname.startswith("pipeline_") or parent_dirname.startswith("pipeline_"):
                is_pipeline_dir = True
                pipeline_root = base_output_dir if dirname.startswith("pipeline_") else os.path.dirname(base_output_dir)
                logger.info(f"Using existing pipeline directory structure: {pipeline_root}")
    
    # If this is already a pipeline directory, we handle it differently
    if is_pipeline_dir:
        # If a step name is provided, create a subdirectory directly in the pipeline directory
        if step_name:
            # Check if the directory already exists
            base_step_dir = os.path.join(pipeline_root, step_name)
            if os.path.exists(base_step_dir):
                # Directory exists, create a new one with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"{base_step_dir}_{timestamp}"
                logger.info(f"Step directory already exists, creating timestamped directory: {output_dir}")
            else:
                # Directory doesn't exist, use the original name
                output_dir = base_step_dir
                
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created step directory within existing pipeline: {output_dir}")
            return output_dir
        else:
            # No step name, just return the pipeline directory
            return pipeline_root
    
    # Standard case - find the next available index or use the most recent run directory
    index = 1
    most_recent_run_dir = None
    
    if os.path.exists(base_output_path):
        # Get all existing directories with our pipeline prefix
        prefix = f"pipeline_{script_name}_run_"
        existing_dirs = [d for d in os.listdir(base_output_path) 
                        if os.path.isdir(os.path.join(base_output_path, d)) 
                        and d.startswith(prefix)]
        
        # Extract indices from directory names
        indices = []
        for dir_name in existing_dirs:
            try:
                # Extract the number after "run_" 
                idx_str = dir_name[len(prefix):]
                indices.append(int(idx_str))
            except ValueError:
                # Skip if the format doesn't match
                continue
        
        # If we have existing indices, use the most recent one if we're in a step
        if indices:
            most_recent_index = max(indices)
            most_recent_run_dir = os.path.join(base_output_path, f"pipeline_{script_name}_run_{most_recent_index:03d}")
            
            # Check if this is part of an ongoing run (step is specified)
            # If this is a new run (step is None), increment the index
            if step_name is None:
                index = most_recent_index + 1
            else:
                # For steps, use the most recent run directory
                index = most_recent_index
    
    # Create the directory name with the index
    run_id = f"run_{index:03d}"  # Format as 001, 002, etc.
    base_dir = os.path.join(base_output_path, f"pipeline_{script_name}_{run_id}")
    
    # If a step name is provided, create a subdirectory for that step
    if step_name:
        base_step_dir = os.path.join(base_dir, step_name)
        # Check if the directory already exists (in case of reruns)
        if os.path.exists(base_step_dir):
            # Add timestamp to make it unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"{base_step_dir}_{timestamp}"
            logger.info(f"Step directory already exists, creating timestamped directory: {output_dir}")
        else:
            output_dir = base_step_dir
    else:
        output_dir = base_dir
    
    # Create the directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Output directory created: {output_dir}")
    return output_dir

# ================== STEP 1: TOC GENERATION ==================

def step1_generate_toc(pdf_path, output_base_dir=None):
    """
    Generate a table of contents (TOC) for the given PDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_base_dir (str, optional): Base directory for outputs
        
    Returns:
        tuple: (chapters, output_dir) with generated chapters and output directory
    """
    logger.info("=" * 50)
    logger.info("STEP 1: Generating Table of Contents...")
    logger.info("=" * 50)
    
    # Create step-specific output directory
    output_dir = setup_output_directory("step1_toc", output_base_dir)
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    logger.info(f"Processing PDF file: {pdf_path}")
    
    # System instruction for TOC generation
    system_instruction = """You are given a technical specifications PDF document in the construction sector ("Samengevoegdlastenboek") that can be a concatenation of multiple different documents, each with their own internal page numbering.

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
    ```
    """
    
    # Initialize Vertex AI model
    try:
        model = initialize_vertex_model(system_instruction)
        logger.info("Initialized Vertex AI model successfully")
    except Exception as e:
        logger.error(f"Error initializing Vertex AI model: {str(e)}")
        raise
    
    # Get page count for batch processing
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {total_pages} pages")
    except Exception as e:
        logger.error(f"Error reading PDF page count: {str(e)}")
        raise
    
    # Load PDF for Vertex AI processing
    try:
        # Read the PDF file as bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Encode as base64
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        
        # Create a multimodal model for direct PDF processing
        multimodal_model = GenerativeModel(
            "gemini-2.5-pro",  # Use Vision-enabled model
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        
        logger.info("PDF file loaded and encoded for Vertex AI")
    except Exception as e:
        logger.error(f"Error preparing PDF for Vertex AI: {str(e)}")
        raise
    
    # Process the PDF in batches due to model limitations
    # Define page batch size - smaller batches for more detailed analysis
    page_batch_size = 50  # Custom batch size (was 20)
    
    # Override adaptive batch sizing for this run
    """
    # Use smaller batches for larger documents
    if total_pages > 300:
        page_batch_size = 15
    elif total_pages > 500:
        page_batch_size = 10
    """
        
    # Create overlapping page range batches for better boundary detection
    page_batches = []
    overlap = 5  # Custom overlap (was 2)
    
    for start_page in range(1, total_pages + 1, page_batch_size - overlap):
        end_page = min(start_page + page_batch_size - 1, total_pages)
        # Avoid creating tiny batches at the end
        if end_page - start_page < 5 and len(page_batches) > 0:
            # Extend the previous batch instead
            page_batches[-1] = (page_batches[-1][0], end_page)
            break
        page_batches.append((start_page, end_page))
    
    logger.info(f"Processing PDF in {len(page_batches)} page batches with size {page_batch_size} and overlap {overlap}")
    
    # Process each page batch to find chapters and sections using a chat session
    page_batch_results = {}
    
    # Start a chat session for the whole document
    try:
        # First, get an initial TOC from the whole document as context
        initial_prompt = f"""
        I'll be analyzing a construction-specific PDF document with {total_pages} pages. First, I need you to provide me with a basic structure of this document.
        
        The PDF file is a technical construction document in Dutch/Flemish called a "lastenboek" (specification document).
        It contains chapters numbered like "XX. TITLE" (e.g., "00. ALGEMENE BEPALINGEN") and sections like "XX.YY TITLE".
        
        Based on the PDF I'm providing, identify the main chapters (like 00, 01, 02, etc.) and their approximate page ranges.
        This will help me analyze the document in more detail with subsequent questions.
        
        Format the response as a simple outline with page ranges.
        """
        
        # Initialize chat
        chat = multimodal_model.start_chat()
        
        # First message with PDF
        logger.info("Requesting initial document structure analysis...")
        response = chat.send_message(
            [
                initial_prompt,
                Part.from_data(data=pdf_bytes, mime_type="application/pdf")
            ]
        )
        logger.info("Received initial document structure")
        
        # Add rate limiting for batch processing
        rate_limit_delay = 2.0  # Base delay between API calls in seconds
        error_backoff_multiplier = 1.0  # Will increase if we encounter errors
        
        # Now process each batch
        for batch_idx, (start_page, end_page) in enumerate(page_batches):
            # Apply rate limiting between batches
            if batch_idx > 0:
                delay = rate_limit_delay * error_backoff_multiplier
                logger.info(f"Rate limiting: Waiting {delay:.2f} seconds before processing next batch...")
                time.sleep(delay)
                
            logger.info(f"Processing page batch {batch_idx+1}/{len(page_batches)}: pages {start_page}-{end_page}")
            
            # For the first few batches, we'll ask for a more comprehensive analysis
            if batch_idx < 3:
                comprehensive_note = "This is one of the first batches, so pay extra attention to identify the document structure and early chapters."
            elif batch_idx >= len(page_batches) - 3:
                comprehensive_note = "This is one of the final batches, so pay extra attention to identify any closing chapters or sections."
            else:
                comprehensive_note = ""
                
            page_prompt = f"""
            Analyze pages {start_page}-{end_page} of this PDF document and identify any chapters or sections 
            that appear within these pages.
            
            {comprehensive_note}
            
            IMPORTANT INSTRUCTIONS:
            - This document uses chapter numbering like "XX. TITLE" (e.g. "00. ALGEMENE BEPALINGEN")
            - Sections are formatted as "XX.YY TITLE" (e.g., "01.10 SECTIETITEL")
            - Subsections may be formatted as "XX.YY.ZZ TITLE" or "XX.YY.ZZ.AA TITLE"
            - Focus ONLY on pages {start_page} through {end_page}
            - Use the GLOBAL PDF page numbers (starting from 1 for the first page of the PDF)
            - IGNORE any page numbers printed within the document itself
            - For each chapter/section, record its exact start page and end page
            - The end page of a chapter/section is the page right before the next chapter/section begins
            - If a chapter/section starts in this range but continues beyond page {end_page}, set the end page as {end_page} for now
            - If a chapter/section ends in this range but started before page {start_page}, set the start page as {start_page} for now
            - Be thorough, even for sections that appear to be brief
            
            Format the output as a Python dictionary like this:
            ```python
            chapters = {{
                "XX": {{'start': X, 'end': Y, 'title': 'CHAPTER TITLE', 'sections': {{
                    'XX.YY': {{'start': X, 'end': Y, 'title': 'section title'}},
                    'XX.YY.ZZ': {{'start': X, 'end': Y, 'title': 'subsection title'}}
                }}}}
            }}
            ```
            
            Include ONLY chapters or sections that appear within pages {start_page}-{end_page}.
            """
            
            # Send the prompt for this batch
            try:
                batch_response = chat.send_message(page_prompt)
                
                # Extract Python dictionary from response
                page_batch_dict = post_process_results(batch_response.text)
                
                if page_batch_dict:
                    logger.info(f"Found chapter/section data in pages {start_page}-{end_page}: {len(page_batch_dict)} chapters")
                    
                    # Merge with existing results
                    for chapter_id, chapter_data in page_batch_dict.items():
                        if chapter_id not in page_batch_results:
                            page_batch_results[chapter_id] = chapter_data
                        else:
                            # Update existing chapter data
                            existing = page_batch_results[chapter_id]
                            # Update start page if this one is earlier
                            if chapter_data['start'] < existing['start']:
                                existing['start'] = chapter_data['start']
                            # Update end page if this one is later
                            if chapter_data['end'] > existing['end']:
                                existing['end'] = chapter_data['end']
                            
                            # Merge sections
                            if 'sections' in chapter_data:
                                if 'sections' not in existing:
                                    existing['sections'] = {}
                                
                                for section_id, section_data in chapter_data['sections'].items():
                                    if section_id not in existing['sections']:
                                        existing['sections'][section_id] = section_data
                                    else:
                                        # Update existing section data
                                        existing_section = existing['sections'][section_id]
                                        # Update start page if this one is earlier
                                        if section_data['start'] < existing_section['start']:
                                            existing_section['start'] = section_data['start']
                                        # Update end page if this one is later
                                        if section_data['end'] > existing_section['end']:
                                            existing_section['end'] = section_data['end']
                                            
                                        # Preserve the title from the most detailed batch
                                        if 'title' in section_data and (len(section_data['title']) > len(existing_section.get('title', ''))):
                                            existing_section['title'] = section_data['title']
                else:
                    logger.info(f"No chapter/section data found in pages {start_page}-{end_page}")
                    
                # Successful request, keep standard delay
                error_backoff_multiplier = max(1.0, error_backoff_multiplier * 0.8)  # Gradually reduce if it was increased
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_idx+1}: {str(e)}")
                # Increase delay for next batch to avoid rate limits
                error_backoff_multiplier *= 2.0
                logger.warning(f"Increasing rate limit delay multiplier to {error_backoff_multiplier} due to error")
                # Continue with next batch
    
    except Exception as e:
        logger.error(f"Error processing with Vertex AI: {str(e)}")
        raise
    
    # After all batches, do a final pass to identify "unclaimed" areas 
    # and adjust boundaries between adjacent chapters/sections
    logger.info("Performing final cleanup and boundary adjustments...")
    
    # Convert to sorted list of chapters for easier boundary adjustment
    sorted_chapters = sorted([(k, v) for k, v in page_batch_results.items()], 
                            key=lambda x: x[1]['start'])
    
    # Adjust chapter boundaries based on adjacent chapters
    for i in range(len(sorted_chapters) - 1):
        current_ch_id, current_ch = sorted_chapters[i]
        next_ch_id, next_ch = sorted_chapters[i + 1]
        
        # If there's a gap between current chapter end and next chapter start, 
        # extend current chapter end to one page before next chapter start
        if current_ch['end'] < next_ch['start'] - 1:
            current_ch['end'] = next_ch['start'] - 1
            logger.info(f"Adjusted end page of chapter {current_ch_id} to {current_ch['end']}")
        
        # Apply the same logic to sections within each chapter
        if 'sections' in current_ch and current_ch['sections']:
            sorted_sections = sorted([(k, v) for k, v in current_ch['sections'].items()], 
                                    key=lambda x: x[1]['start'])
            
            for j in range(len(sorted_sections) - 1):
                current_sec_id, current_sec = sorted_sections[j]
                next_sec_id, next_sec = sorted_sections[j + 1]
                
                if current_sec['end'] < next_sec['start'] - 1:
                    current_sec['end'] = next_sec['start'] - 1
                    logger.info(f"Adjusted end page of section {current_sec_id} to {current_sec['end']}")
            
            # The last section should end at the chapter end
            if sorted_sections:
                last_sec_id, last_sec = sorted_sections[-1]
                if last_sec['end'] < current_ch['end']:
                    last_sec['end'] = current_ch['end']
                    logger.info(f"Adjusted end page of last section {last_sec_id} to {last_sec['end']}")
            
            # Update the sections in the chapter
            for sec_id, sec_data in sorted_sections:
                current_ch['sections'][sec_id] = sec_data
    
    # Update the batch results with the adjusted chapters
    for ch_id, ch_data in sorted_chapters:
        page_batch_results[ch_id] = ch_data
    
    # Use the page batch results as the final chapter data
    chapters = page_batch_results
    
    # Validate the results to ensure they're reasonable
    def validate_chapters(chapters_dict):
        validated = {}
        max_page = 0  # Track the highest page number seen
        
        # First pass to find max page
        for chapter, data in chapters_dict.items():
            if isinstance(data, dict) and 'end' in data and isinstance(data['end'], int) and data['end'] > max_page:
                max_page = data['end']
        
        # Set a reasonable maximum (adjust based on your document)
        reasonable_max = max(max_page, 1000)  # Use either observed max or 1000, whichever is larger
        
        # Second pass to validate
        for chapter, data in chapters_dict.items():
            # Skip empty chapters or non-dictionary entries
            if not data or not isinstance(data, dict):
                continue
                
            # Check if start/end are reasonable
            if ('start' not in data or 'end' not in data or 
                not isinstance(data['start'], int) or not isinstance(data['end'], int) or
                data['start'] < 1 or data['end'] > reasonable_max or data['start'] > data['end']):
                logger.warning(f"Chapter {chapter} has invalid page numbers: {data.get('start', 'missing')}-{data.get('end', 'missing')}")
                continue
                
            # Validate sections if they exist
            if 'sections' in data and isinstance(data['sections'], dict):
                valid_sections = {}
                for section_id, section_data in data['sections'].items():
                    if not isinstance(section_data, dict):
                        continue
                        
                    if ('start' not in section_data or 'end' not in section_data or 
                        not isinstance(section_data['start'], int) or not isinstance(section_data['end'], int) or
                        section_data['start'] < 1 or section_data['end'] > reasonable_max or 
                        section_data['start'] > section_data['end']):
                        logger.warning(f"Section {section_id} has invalid page numbers: {section_data.get('start', 'missing')}-{section_data.get('end', 'missing')}")
                        continue
                        
                    valid_sections[section_id] = section_data
                
                data['sections'] = valid_sections
                
            validated[chapter] = data
        
        return validated
    
    validated_chapters = validate_chapters(chapters)
    
    # Save the chapters data to a JSON file in the output directory
    chapters_json_path = os.path.join(output_dir, "chapters.json")
    
    with open(chapters_json_path, 'w', encoding='utf-8') as f:
        json.dump(validated_chapters, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved chapters data to {chapters_json_path}")
    
    # Create a simple text report of the TOC structure
    report_lines = ["# Table of Contents", ""]
    
    for chapter_num, chapter_data in sorted(validated_chapters.items()):
        # Only process main chapters (2-digit numbers)
        if chapter_num.isdigit() and len(chapter_num) == 2:
            report_lines.append(f"## Chapter {chapter_num}: {chapter_data['title']} (Pages {chapter_data['start']}-{chapter_data['end']})")
            report_lines.append("")
            
            # Add sections
            for section_id, section_data in sorted(chapter_data.get('sections', {}).items()):
                report_lines.append(f"### {section_id}: {section_data['title']} (Pages {section_data['start']}-{section_data['end']})")
            
            report_lines.append("")  # Add a blank line between chapters
    
    # Write the report to a file
    report_file = os.path.join(output_dir, "toc_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    logger.info(f"TOC report saved to {report_file}")
    
    return validated_chapters, output_dir

# ================== STEP 2: CATEGORY MATCHING ==================

def initialize_gemini_model(model_name="gemini-2.5-pro", project_id=None):
    """
    Initialize the Gemini AI model for category matching.
    
    Args:
        model_name (str): Name of the Gemini model to use
        project_id (str, optional): Google Cloud project ID to use
    
    Returns:
        tuple: (model, model_name) - The model instance and the model name used
    """
    try:
        # Reinitialize with project_id if provided
        if project_id:
            vertexai.init(
                project=project_id,
                location="europe-west1",
                api_endpoint="europe-west1-aiplatform.googleapis.com"
            )
            logger.info(f"Reinitialized Vertex AI with project ID: {project_id}")
        
        # Normalize model name in case we get just "gemini-2.5-pro" without version
        if model_name == "gemini-2.5-pro":
            model_name = "gemini-2.5-pro"
        elif model_name == "gemini-pro":
            model_name = "gemini-pro-001"
            
        # Create model instance using Vertex AI
        model = GenerativeModel(
            model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        logger.info(f"Successfully initialized Vertex AI Gemini model: {model_name}")
        return model, model_name
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model {model_name}: {str(e)}")
        # Fall back to default model if specified model fails
        if model_name != "gemini-2.5-pro":
            logger.info("Falling back to default gemini-2.5-pro model")
            return initialize_gemini_model("gemini-2.5-pro", project_id)
        raise RuntimeError(f"Failed to initialize Gemini model: {model_name}")

def batch_match_to_multiple_categories(model, items_batch, df):
    """
    Use Gemini to match multiple items to categories in a single batch request.
    This function processes up to 10 chapters/sections at once to reduce API calls.
    
    Args:
        model: The Gemini model instance
        items_batch (list): List of dictionaries with item info (title, content_dict, is_section)
        df (DataFrame): DataFrame containing category information
    
    Returns:
        list: List of match results for each item in the batch
    """
    # Define a confidence threshold for considering a category relevant
    RELEVANCE_THRESHOLD = 50  # Minimum confidence score
    
    # Create a list of all available categories with their expanded descriptions
    categories_info = []
    for idx, row in df.iterrows():
        categories_info.append(f"Category: {row['summary']}\nDescription: {row['expanded_description']}")
    
    formatted_categories = "\n\n".join(categories_info)
    
    # Format each item in the batch
    formatted_items = []
    for i, item in enumerate(items_batch):
        title = item['title']
        content_dict = item.get('content_dict')
        is_section = item.get('is_section', False)
        
        content_type = "Section" if is_section else "Chapter"
        
        if content_dict and 'start' in content_dict and 'end' in content_dict:
            page_range = f"Pages: {content_dict['start']}-{content_dict['end']}"
        else:
            page_range = "Pages: Unknown"
        
        section_texts = []
        if content_dict and 'sections' in content_dict:
            section_texts = [f"- {section_id}: {section_data['title']}" for section_id, section_data in content_dict['sections'].items()]
        
        formatted_item = f"ITEM {i+1}: {content_type}: {title}\n{page_range}\n" + "\n".join(section_texts)
        formatted_items.append(formatted_item)
    
    batch_content = "\n\n".join(formatted_items)
    
    # Create the format template based on explanation setting
    if INCLUDE_EXPLANATIONS:
        format_template = """
Category: [category name 1]
Confidence: [score between 0-100]
Explanation: [brief explanation of why this category is relevant]

Category: [category name 2]
Confidence: [score between 0-100]
Explanation: [brief explanation of why this category is relevant]
"""
    else:
        format_template = """
Category: [category name 1]
Confidence: [score between 0-100]

Category: [category name 2]
Confidence: [score between 0-100]
"""
    
    # Create the prompt for Gemini
    prompt = f"""
I have multiple chapters/sections from a construction specification document (lastenboek/bestek) and need to match each to ALL relevant categories.

DEMOLITION/REMOVAL WORK RULE:
- For REMOVAL/DEMOLITION work (keywords: "verwijderen", "slopen", "uitbreken", "opbreken", "demonteren", "afbreken"):
  * ALWAYS include "01. Afbraak en Grondwerken" as PRIMARY category
  * ALSO include relevant trade category as SECONDARY (e.g., "12. Sanitair" for plumbing removal)
  
This ensures both demolition contractors and trade contractors see relevant work.

The items to analyze are:
{batch_content}
    
The available categories are:
{formatted_categories}
    
Please analyze EACH item separately and determine ALL categories that are relevant matches for THAT item.
Consider the topics, terminology, and concepts in each item and the categories.
    
Assign a confidence score (0-100) to each relevant category based on how closely it matches.
Only include categories with a relevance score of {RELEVANCE_THRESHOLD} or higher.
    
Return your answer with the following format for each item:
#ITEM 1{format_template}
#ITEM 2
... and so on for each item.

IMPORTANT: 
1. Use the exact #ITEM X format as a separator between items
2. Process each item independently
3. Include ALL relevant categories for each item
4. Only include categories with confidence {RELEVANCE_THRESHOLD} or higher
"""
    
    try:
        # Use the enhanced process_with_vertex_ai function which has better backoff
        response_text = process_with_vertex_ai(model, prompt)
        logger.info(f"Received batch response for {len(items_batch)} items")
        
        # Split the response by item markers
        item_blocks = re.split(r'#ITEM\s+\d+', response_text)
        # Remove any empty blocks and trim whitespace
        item_blocks = [block.strip() for block in item_blocks if block.strip()]
        
        batch_results = []
        
        # Process each item block (should correspond to items in the batch)
        for i, block in enumerate(item_blocks):
            if i >= len(items_batch):
                logger.warning(f"Received more item blocks than expected: {len(item_blocks)} vs {len(items_batch)}")
                break
                
            # Process the current item block to extract category matches
            item_matches = []
            
            # Split the block into category sections
            category_sections = []
            current_section = []
            
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith("Category:") and current_section:
                    category_sections.append('\n'.join(current_section))
                    current_section = [line]
                else:
                    if line:  # Only add non-empty lines
                        current_section.append(line)
            
            # Add the last section
            if current_section:
                category_sections.append('\n'.join(current_section))
            
            # Process each category section
            for section in category_sections:
                # Extract category name
                category_line = [line for line in section.split('\n') if line.startswith('Category:')]
                if not category_line:
                    continue
                category = category_line[0].replace('Category:', '').strip()
                
                # Extract confidence
                confidence_line = [line for line in section.split('\n') if line.startswith('Confidence:')]
                confidence = 0
                if confidence_line:
                    confidence_text = confidence_line[0].replace('Confidence:', '').strip()
                    # Handle possible formats like "80/100" or just "80"
                    if '/' in confidence_text:
                        confidence = int(confidence_text.split('/')[0])
                    else:
                        try:
                            confidence = int(confidence_text)
                        except ValueError:
                            # Try to extract a number from the text
                            match = re.search(r'(\d+)', confidence_text)
                            if match:
                                confidence = int(match.group(1))
                            else:
                                confidence = 0
                
                # Extract explanation if needed
                explanation = ""
                if INCLUDE_EXPLANATIONS:
                    explanation_line = [line for line in section.split('\n') if line.startswith('Explanation:')]
                    explanation = explanation_line[0].replace('Explanation:', '').strip() if explanation_line else ""
                
                # Add to matches if confidence meets threshold
                if confidence >= RELEVANCE_THRESHOLD:
                    match_data = {
                        "category": category,
                        "confidence": confidence
                    }
                    
                    if INCLUDE_EXPLANATIONS:
                        match_data["explanation"] = explanation
                    
                    item_matches.append(match_data)
            
            # Add this item's matches to the batch results
            batch_results.append(item_matches)
        
        # If we have fewer results than items, pad with error entries
        while len(batch_results) < len(items_batch):
            i = len(batch_results)
            logger.warning(f"Missing results for item {i+1}, adding error entry")
            
            error_entry = {
                "category": "Error",
                "confidence": 0
            }
            
            if INCLUDE_EXPLANATIONS:
                error_entry["explanation"] = "Failed to parse response for this item"
                
            batch_results.append([error_entry])
        
        return batch_results
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        # Return error results for all items in the batch
        error_entry = {
            "category": "Error",
            "confidence": 0
        }
        
        if INCLUDE_EXPLANATIONS:
            error_entry["explanation"] = f"API Error: {str(e)}"
            
        return [[error_entry] for _ in items_batch]

def match_to_multiple_categories(model, title, content_dict=None, is_section=False, df=None):
    """
    Use Gemini to match content to multiple relevant categories.
    This is the original single-item processing function.
    
    Args:
        model: The Gemini model instance
        title (str): The title of the chapter or section
        content_dict (dict, optional): Dictionary with additional content information
        is_section (bool): Whether this is a section (True) or chapter (False)
        df (DataFrame): DataFrame containing category information
    
    Returns:
        list: List of dictionaries with matched categories and confidence scores
    """
    # Define a confidence threshold for considering a category relevant
    RELEVANCE_THRESHOLD = 50  # Minimum confidence score
    
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
    
    # Create the format template based on explanation setting
    if INCLUDE_EXPLANATIONS:
        format_template = """
Category: [category name 1]
Confidence: [score between 0-100]
Explanation: [brief explanation of why this category is relevant]

Category: [category name 2]
Confidence: [score between 0-100]
Explanation: [brief explanation of why this category is relevant]
"""
    else:
        format_template = """
Category: [category name 1]
Confidence: [score between 0-100]

Category: [category name 2]
Confidence: [score between 0-100]
"""
    
    # Create the prompt for Gemini
    prompt = f"""
I have a {content_type.lower()} from a construction specification document (lastenboek) and need to match it to ALL relevant categories.

DEMOLITION/REMOVAL WORK RULE:
- For REMOVAL/DEMOLITION work (keywords: "verwijderen", "slopen", "uitbreken", "opbreken", "demonteren", "afbreken"):
  * ALWAYS include "01. Afbraak en Grondwerken" as PRIMARY category
  * ALSO include relevant trade category as SECONDARY (e.g., "12. Sanitair" for plumbing removal)
  
This ensures both demolition contractors and trade contractors see relevant work.

The {content_type.lower()} information is:
{formatted_content}
    
The available categories are:
{formatted_categories}
    
Please analyze the content and determine ALL categories that are relevant matches, not just the single best match.
Consider the topics, terminology, and concepts in both the {content_type.lower()} and categories.
    
Assign a confidence score (0-100) to each relevant category based on how closely it matches.
Only include categories with a relevance score of {RELEVANCE_THRESHOLD} or higher.
    
Return your answer in the following format:{format_template}
...and so on for all relevant categories.
    """
    
    try:
        # Use the enhanced process_with_vertex_ai function which has better backoff
        response_text = process_with_vertex_ai(model, prompt)
        logger.info(f"Received response for item: {title}")

        # Process the response block to extract category matches
        matches = []
        
        # Split into category blocks
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
                    try:
                        confidence = int(confidence_text)
                    except ValueError:
                        # Try to extract a number from the text
                        match = re.search(r'(\d+)', confidence_text)
                        if match:
                            confidence = int(match.group(1))
                        else:
                            confidence = 0
            
            # Only proceed if confidence meets threshold
            if confidence >= RELEVANCE_THRESHOLD:
                match_data = {
                    "category": category,
                    "confidence": confidence
                }
                
                # Extract explanation if needed
                if INCLUDE_EXPLANATIONS:
                    explanation_line = [line for line in block.split('\n') if line.startswith('Explanation:')]
                    explanation = explanation_line[0].replace('Explanation:', '').strip() if explanation_line else ""
                    match_data["explanation"] = explanation
                
                matches.append(match_data)
        
        return matches
        
    except Exception as e:
        logger.error(f"Error processing item: {str(e)}")
        # Return an error entry
        error_entry = {
            "category": "Error",
            "confidence": 0
        }
        
        if INCLUDE_EXPLANATIONS:
            error_entry["explanation"] = f"API Error: {str(e)}"
            
        return [error_entry]

def step2_match_categories(chapters=None, toc_output_dir=None, category_file=None, base_dir=None, model=None):
    """
    Match chapters and sections to categories using Gemini AI.
    
    Args:
        chapters (dict): Dictionary of chapters from step 1
        toc_output_dir (str): Directory containing TOC output from step 1
        category_file (str): Path to the category file (Excel)
        base_dir (str): Base output directory
        model (GenerativeModel, optional): Pre-initialized Gemini model
    
    Returns:
        tuple: (category_match_dir, chapter_results, section_results)
    """
    logger.info("Step 2: Matching categories to chapters and sections")
    
    # Initialize base directory
    if not base_dir:
        if toc_output_dir:
            # Extract the base directory from toc_output_dir
            base_dir = os.path.dirname(toc_output_dir)
        else:
            base_dir = setup_output_directory(step_name="category_matching")
    
    # Determine the correct pipeline directory to ensure consistent directory structure
    pipeline_dir = None
    
    # First check if base_dir itself contains "pipeline_" in the path
    path_parts = base_dir.split(os.sep)
    pipeline_index = -1
    
    # Find the pipeline directory component in the path
    for i, part in enumerate(path_parts):
        if part.startswith("pipeline_"):
            pipeline_index = i
            break
    
    if pipeline_index >= 0:
        # If we found a pipeline directory in the path, use that as the base
        pipeline_dir = os.sep.join(path_parts[:pipeline_index+1])
        logger.info(f"Extracted pipeline directory from path: {pipeline_dir}")
    elif os.path.basename(base_dir).startswith("step1_"):
        # If base_dir is a step1 directory, go up one level to the pipeline directory
        pipeline_dir = os.path.dirname(base_dir)
        logger.info(f"Using pipeline directory from step1: {pipeline_dir}")
    else:
        # Otherwise use the provided base_dir directly
        pipeline_dir = base_dir
        logger.info(f"Using base directory as pipeline directory: {pipeline_dir}")
    
    # Create output directory for category matching within the pipeline directory
    category_match_dir = setup_output_directory("step2_category_matching", pipeline_dir)
    os.makedirs(category_match_dir, exist_ok=True)
    
    # Load category file (Excel)
    if not category_file:
        category_file = DEFAULT_CATEGORY_FILE
    
    # Check if category file exists
    if not category_file or not os.path.exists(category_file):
        raise FileNotFoundError(f"Category file not found: {category_file}")
    
    # Import the category file
    logger.info(f"Loading category file: {category_file}")
    if category_file.endswith('.xlsx') or category_file.endswith('.xls'):
        df = pd.read_excel(category_file)
    elif category_file.endswith('.csv'):
        df = pd.read_csv(category_file)
    elif category_file.endswith('.py'):
        # Handle Python module by dynamically importing it
        logger.info(f"Importing category data from Python module: {category_file}")
        try:
            # Get the directory and module name
            category_dir = os.path.dirname(category_file)
            category_module = os.path.splitext(os.path.basename(category_file))[0]
            
            # Add directory to path if not already there
            if category_dir not in sys.path:
                sys.path.append(category_dir)
                
            # Import the module and get the df variable
            module = __import__(category_module)
            df = getattr(module, 'df', None)
            
            # Check if df was successfully imported
            if df is None:
                raise AttributeError(f"No 'df' variable found in module {category_module}")
            
            logger.info(f"Successfully imported DataFrame from {category_module}")
        except Exception as e:
            raise ValueError(f"Failed to import DataFrame from Python module: {str(e)}")
    else:
        raise ValueError("Category file must be Excel (.xlsx/.xls), CSV (.csv), or Python (.py) module")
    
    if 'summary' not in df.columns:
        raise ValueError("Category file must contain a 'summary' column")
    
    if 'expanded_description' not in df.columns:
        # Use summary as the description if no description column exists
        df['expanded_description'] = df['summary']
    
    # Load chapters from step 1 if not provided
    if not chapters:
        if not toc_output_dir:
            raise ValueError("Either chapters or toc_output_dir must be provided")
        
        chapters_file = os.path.join(toc_output_dir, "chapters.json")
        with open(chapters_file, 'r', encoding='utf-8') as f:
            chapters = json.load(f)
    
    # Initialize Vertex AI model for category matching if not provided
    if model is None:
        model, model_name = initialize_gemini_model()
        logger.info(f"Using model for category matching: {model_name}")
    else:
        # Just log that we're using a pre-initialized model
        logger.info("Using pre-initialized model for category matching")
    
    # Process chapters and sections to match with categories
    chapter_results = {}
    section_results = {}
    
    # Prepare batch items for processing
    batch_items = []
    
    # Add chapters to the batch
    for chapter_num, chapter_data in chapters.items():
        # Skip if missing required data
        if 'title' not in chapter_data:
            continue
            
        batch_items.append({
            'title': chapter_data['title'],
            'content_dict': chapter_data,
            'is_section': False,
            'id': chapter_num
        })
        
        # Process sections for this chapter
        if 'sections' in chapter_data:
            for section_id, section_data in chapter_data['sections'].items():
                # Skip if missing required data
                if 'title' not in section_data:
                    continue
                    
                batch_items.append({
                    'title': section_data['title'],
                    'content_dict': section_data,
                    'is_section': True,
                    'id': section_id,
                    'chapter_id': chapter_num
                })
    
    # Process in batches for efficiency
    batch_size = 10  # Number of items to process in each batch
    
    for i in range(0, len(batch_items), batch_size):
        current_batch = batch_items[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(batch_items)-1)//batch_size + 1} ({len(current_batch)} items)")
        
        # Call batch processing function
        batch_results = batch_match_to_multiple_categories(model, current_batch, df)
        
        # Store results
        for j, item_result in enumerate(batch_results):
            item = current_batch[j]
            
            if not item['is_section']:
                # For chapters
                chapter_num = item['id']
                chapter_data = item.get('content_dict', {})
                chapter_results[chapter_num] = {
                    "title": item['title'],
                    "matches": item_result,
                    "start": chapter_data.get('start', '?'),
                    "end": chapter_data.get('end', '?')
                }
                logger.info(f"Chapter {chapter_num}: '{item['title']}' matched to {len(item_result)} categories")
            else:
                # For sections
                section_id = item['id']
                section_data = item.get('content_dict', {})
                section_results[section_id] = {
                    "title": item['title'],
                    "chapter_id": item.get('chapter_id'),
                    "matches": item_result,
                    "start": section_data.get('start', '?'),
                    "end": section_data.get('end', '?')
                }
                logger.info(f"Section {section_id}: '{item['title']}' matched to {len(item_result)} categories")
    
    # Save results to CSV files
    chapter_rows = []
    for chapter_num, data in chapter_results.items():
        for match in data["matches"]:
            row = {
                "Type": "Chapter",
                "Chapter Number": chapter_num,
                "Section ID": "",
                "Title": data["title"],
                "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                "Matched Category": match["category"],
                "Confidence": match["confidence"]
            }
            if "explanation" in match:
                row["Explanation"] = match["explanation"]
            chapter_rows.append(row)
    
    chapter_df = pd.DataFrame(chapter_rows)
    chapter_csv_path = os.path.join(category_match_dir, "chapter_category_matches.csv")
    chapter_df.to_csv(chapter_csv_path, index=False)
    logger.info(f"Saved chapter matches to {chapter_csv_path}")
    
    # Create CSV for section matches
    section_rows = []
    for section_id, data in section_results.items():
        chapter_id = data.get("chapter_id", "")
        for match in data["matches"]:
            row = {
                "Type": "Section",
                "Chapter Number": chapter_id,
                "Section ID": section_id,
                "Title": data["title"],
                "Pages": f"{data.get('start', '?')}-{data.get('end', '?')}",
                "Matched Category": match["category"],
                "Confidence": match["confidence"]
            }
            if "explanation" in match:
                row["Explanation"] = match["explanation"]
            section_rows.append(row)
    
    section_df = pd.DataFrame(section_rows)
    section_csv_path = os.path.join(category_match_dir, "section_category_matches.csv")
    section_df.to_csv(section_csv_path, index=False)
    logger.info(f"Saved section matches to {section_csv_path}")
    
    # Create a unified CSV with both chapter and section matches
    unified_df = pd.concat([chapter_df, section_df])
    unified_csv_path = os.path.join(category_match_dir, "unified_category_matches.csv")
    unified_df.to_csv(unified_csv_path, index=False)
    logger.info(f"Saved unified matches to {unified_csv_path}")
    
    # Save raw results as JSON for reference
    try:
        with open(os.path.join(category_match_dir, "chapters_raw_matches.json"), 'w', encoding='utf-8') as f:
            json.dump(chapter_results, f, ensure_ascii=False, indent=2)
            
        with open(os.path.join(category_match_dir, "sections_raw_matches.json"), 'w', encoding='utf-8') as f:
            json.dump(section_results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved raw match data to JSON files")
    except Exception as e:
        logger.warning(f"Failed to save raw match data: {e}")
    
    # Log results summary 
    logger.info(f"Category matching completed successfully!")
    logger.info(f"Matched {len(chapter_results)} chapters and {len(section_results)} sections to categories")
    
    return category_match_dir, chapter_results, section_results

# ================== STEP 3: DOCUMENT SPLITTING ==================

def step3_extract_category_pdfs(pdf_path, chapter_results, section_results, category_match_dir, category_file, second_output_dir=None, third_output_dir=None, base_dir=None):
    """
    Extract category-specific PDFs based on the matched chapters and sections.
    
    Args:
        pdf_path: Path to the original PDF file
        chapter_results: Dictionary of chapter matches with category IDs
        section_results: Dictionary of section matches with category IDs
        category_match_dir: Directory with category matching results
        category_file: Path to the category spreadsheet
        second_output_dir: Optional secondary directory to save PDFs and data
        third_output_dir: Optional third directory to save PDFs and data
        base_dir: Base directory to use for output
        
    Returns:
        Tuple of (number of PDFs created, output directory)
    """
    logger.info("=" * 50)
    logger.info("STEP 3: Splitting document into category-specific PDFs...")
    logger.info("=" * 50)
    
    # Determine the appropriate base directory
    if base_dir is None:
        if category_match_dir:
            # If we have the category_match_dir, use its parent as base_dir
            if os.path.basename(category_match_dir).startswith("step2_"):
                # If category_match_dir is a step directory, go up one level
                base_dir = os.path.dirname(category_match_dir)
            else:
                # Otherwise use category_match_dir's directory
                base_dir = category_match_dir
    
    # Create step-specific output directory using the same pattern as step 1 and 2
    output_dir = setup_output_directory("step3_category_pdfs", base_dir)
    
    # If results are not provided, try to load from step 2 output
    if section_results is None:
        if category_match_dir is None:
            # Look for the most recent step2 output directory
            parent_dir = os.path.dirname(output_dir)  # Get to the parent directory
            potential_step2_dirs = [d for d in os.listdir(parent_dir) if d.startswith("step2_")]
            if potential_step2_dirs:
                category_match_dir = os.path.join(parent_dir, sorted(potential_step2_dirs)[-1])
                logger.info(f"Using category matching data from {category_match_dir}")
            else:
                logger.error("No previous step2 output directory found")
                raise FileNotFoundError("Cannot find category matching data from step 2")
    
    # Full path to the mappings file
    mappings_file = os.path.join(category_match_dir, "section_category_matches.csv") if category_match_dir else None
    
    # Load the category mappings
    try:
        category_mappings = pd.read_csv(mappings_file)
        logger.info(f"Loaded category mappings from {mappings_file}")
    except Exception as e:
        logger.error(f"Failed to load category mappings: {e}")
        return 0, output_dir
    
    # Get the categories from the specified file or use default
    try:
        if category_file:
            logger.info(f"Using custom category file: {category_file}")
            # Get the directory and filename without extension
            category_dir = os.path.dirname(category_file)
            category_module = os.path.splitext(os.path.basename(category_file))[0]
            
            # Make sure the category directory is in the path
            if category_dir not in sys.path:
                sys.path.append(category_dir)
                
            # Import the module
            module = __import__(category_module)
            final_categories = getattr(module, 'final_categories', None)
            
            if final_categories is None:
                logger.error(f"Could not find 'final_categories' in the category file: {category_file}")
                raise ImportError(f"Missing 'final_categories' in {category_file}")
                
            logger.info(f"Successfully imported {len(final_categories)} categories from {category_file}")
        else:
            # Changed from nonvmswhoofdstukken_pandas2 to nonvmswhoofdstukken_pandas since they are identical
            from nonvmswhoofdstukken_pandas import final_categories
            logger.info(f"Loaded {len(final_categories)} categories from nonvmswhoofdstukken_pandas")
    except Exception as e:
        logger.error(f"Failed to load categories: {e}")
        return 0, output_dir
    
    # Load the PDF
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        logger.info(f"Loaded PDF with {total_pages} pages")
    except Exception as e:
        logger.error(f"Failed to load PDF: {e}")
        return 0, output_dir
    
    # Initialize counters
    successful_extractions = 0
    second_dir_copies = 0
    third_dir_copies = 0
    
    # For each category, create a new PDF
    for category_entry in final_categories:
        # Extract the category name (last part after comma)
        parts = category_entry.split(', ')
        category = parts[-1]
        
        # Clean the category name to use as filename
        clean_category = category.replace(' ', '_').replace('&', 'and').replace(',', '')
        
        # Filter the mappings to get relevant sections
        relevant_sections = category_mappings[category_mappings['Matched Category'] == category]
        
        if len(relevant_sections) == 0:
            logger.warning(f"No sections found for category: {category}")
            continue
        
        # Create a new PDF writer
        writer = PdfWriter()
        
        # Track pages already added to avoid duplicates
        added_pages = set()
        
        # Extract page ranges from the 'Pages' column
        for _, row in relevant_sections.iterrows():
            page_range = row['Pages']
            try:
                start_page, end_page = map(int, page_range.split('-'))
                
                # PDF pages are 0-indexed, but our page numbers start at 1
                for page_num in range(start_page - 1, end_page):
                    if page_num >= total_pages:
                        logger.warning(f"Page {page_num+1} out of range for PDF with {total_pages} pages")
                        continue
                        
                    if page_num not in added_pages:
                        writer.add_page(reader.pages[page_num])
                        added_pages.add(page_num)
            except Exception as e:
                logger.error(f"Error processing page range {page_range} for category {category}: {e}")
        
        # Save the new PDF if pages were added
        if added_pages:
            # First, save to the primary output directory
            primary_output_path = os.path.join(output_dir, f"{clean_category}.pdf")
            try:
                with open(primary_output_path, 'wb') as output_file:
                    writer.write(output_file)
                logger.info(f"Created PDF in primary location: {primary_output_path} ({len(added_pages)} pages)")
                successful_extractions += 1
                
                # Make a copy to second output directory if enabled
                if second_output_dir and second_output_dir.strip():
                    second_output_path = os.path.join(second_output_dir, f"{clean_category}.pdf")
                    try:
                        shutil.copy2(primary_output_path, second_output_path)
                        logger.info(f"Copied PDF to second location: {second_output_path}")
                        second_dir_copies += 1
                    except Exception as e:
                        logger.error(f"Failed to copy to second output directory: {str(e)}")
                
                # Make a copy to third output directory if enabled
                if third_output_dir and third_output_dir.strip():
                    third_output_path = os.path.join(third_output_dir, f"{clean_category}.pdf")
                    try:
                        shutil.copy2(primary_output_path, third_output_path)
                        logger.info(f"Copied PDF to third location: {third_output_path}")
                        third_dir_copies += 1
                    except Exception as e:
                        logger.error(f"Failed to copy to third output directory: {str(e)}")
                
                # Create a list of items for this category's detail CSV
                added_items = []
                for _, row in relevant_sections.iterrows():
                    item = {
                        'title': row['Title'],
                        'type': row['Type'],
                        'page': row['Pages'],
                        'confidence': row['Confidence']
                    }
                    added_items.append(item)
                
                # Create CSV with detailed category information
                category_details_csv = os.path.join(output_dir, f"{clean_category}_details.csv")
                with open(category_details_csv, 'w', newline='', encoding='utf-8') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(['Title', 'Type', 'Page', 'Confidence'])
                    for item in sorted(added_items, key=lambda x: x['page']):
                        csv_writer.writerow([
                            item['title'], 
                            item['type'], 
                            item['page'], 
                            item.get('confidence', 'N/A')
                        ])
                logger.info(f"Created category details CSV: {category_details_csv}")
                
                # Copy the category details CSV to second output directory if enabled
                if second_output_dir and second_output_dir.strip():
                    second_csv_path = os.path.join(second_output_dir, f"{clean_category}_details.csv")
                    try:
                        shutil.copy2(category_details_csv, second_csv_path)
                        logger.info(f"Copied category details to second location: {second_csv_path}")
                    except Exception as e:
                        logger.error(f"Failed to copy CSV to second directory: {str(e)}")
                
                # Copy the category details CSV to third output directory if enabled
                if third_output_dir and third_output_dir.strip():
                    third_csv_path = os.path.join(third_output_dir, f"{clean_category}_details.csv")
                    try:
                        shutil.copy2(category_details_csv, third_csv_path)
                        logger.info(f"Copied category details to third location: {third_csv_path}")
                    except Exception as e:
                        logger.error(f"Failed to copy CSV to third directory: {str(e)}")
                
            except Exception as e:
                logger.error(f"Failed to write PDF for category {category}: {e}")
        else:
            logger.warning(f"No pages to add for category: {category}")
    
    # Create a summary file with category statistics
    summary_path = os.path.join(output_dir, "extraction_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("CATEGORY EXTRACTION SUMMARY\n")
        f.write("==========================\n\n")
        f.write(f"Original PDF: {pdf_path}\n")
        f.write(f"Category file: {category_file}\n\n")
        f.write(f"Number of categories processed: {len(final_categories)}\n")
        f.write(f"Number of PDFs successfully created: {successful_extractions}\n\n")
        f.write(f"Primary output directory: {output_dir}\n")
        if second_output_dir and second_output_dir.strip():
            f.write(f"Second output directory: {second_output_dir}\n")
            f.write(f"Copies to second directory: {second_dir_copies}\n")
        if third_output_dir and third_output_dir.strip():
            f.write(f"Third output directory: {third_output_dir}\n")
            f.write(f"Copies to third directory: {third_dir_copies}\n")
    
    logger.info(f"Created extraction summary: {summary_path}")
    
    # Copy all important files from step 2 to second and third output directories
    step2_files = [
        "chapter_category_matches.csv",
        "section_category_matches.csv",
        "unified_category_matches.csv",
        "category_matching_report.md"
    ]
    
    if second_output_dir and second_output_dir.strip():
        try:
            for filename in step2_files:
                src = os.path.join(category_match_dir, filename)
                if os.path.exists(src):
                    dst = os.path.join(second_output_dir, filename)
                    shutil.copy2(src, dst)
                    logger.info(f"Copied {filename} to second data directory")
            
            # Copy summary
            shutil.copy2(summary_path, os.path.join(second_output_dir, "extraction_summary.txt"))
            logger.info("Copied extraction summary to second data directory")
        except Exception as e:
            logger.error(f"Failed to copy files to second directory: {str(e)}")
    
    if third_output_dir and third_output_dir.strip():
        try:
            for filename in step2_files:
                src = os.path.join(category_match_dir, filename)
                if os.path.exists(src):
                    dst = os.path.join(third_output_dir, filename)
                    shutil.copy2(src, dst)
                    logger.info(f"Copied {filename} to third data directory")
            
            # Copy summary
            shutil.copy2(summary_path, os.path.join(third_output_dir, "extraction_summary.txt"))
            logger.info("Copied extraction summary to third data directory")
        except Exception as e:
            logger.error(f"Failed to copy files to third directory: {str(e)}")
    
    # Summary message showing all locations
    output_summary = f"Extraction complete. Created {successful_extractions} category PDFs."
    output_summary += f"\n- Primary output: {output_dir}"
    if second_output_dir and second_output_dir.strip():
        output_summary += f"\n- Second output: {second_output_dir} ({second_dir_copies} copies)"
    if third_output_dir and third_output_dir.strip():
        output_summary += f"\n- Third output: {third_output_dir} ({third_dir_copies} copies)"
    logger.info(output_summary)
    
    return successful_extractions, output_dir

# ================== MAIN PIPELINE ==================

def run_complete_pipeline(pdf_path=DEFAULT_PDF_PATH, output_base_dir=None, category_file=None, second_output_dir=None, third_output_dir=None):
    """
    Execute the complete Non-VMSW document processing pipeline.
    
    Args:
        pdf_path (str): Path to the PDF file to process
        output_base_dir (str, optional): Base directory for outputs
        category_file (str, optional): Path to custom category file
        second_output_dir (str, optional): Second directory to copy split PDFs to
        third_output_dir (str, optional): Third directory to copy split PDFs to
        
    Returns:
        tuple: (success, output_dirs) with success status and list of output directories
    """
    output_dirs = {}  # Change from list to dict
    output_dirs['base'] = setup_output_directory(base_output_dir=output_base_dir)
    output_dirs['toc'] = None
    output_dirs['category_matching'] = None
    output_dirs['category_pdfs'] = None
    
    start_time = time.time()
    
    try:
        logger.info("=" * 50)
        logger.info("STARTING COMPLETE NON-VMSW DOCUMENT PROCESSING PIPELINE")
        logger.info("=" * 50)
        
        # Step 1: Generate Table of Contents with retry logic
        logger.info("\nRUNNING STEP 1: Generating Table of Contents")
        step1_attempts = 0
        step1_max_attempts = 3
        step1_success = False
        step1_backoff = 2  # Initial backoff time in seconds
        chapters = None
        toc_output_dir = None
        
        while step1_attempts < step1_max_attempts and not step1_success:
            try:
                if step1_attempts > 0:
                    wait_time = step1_backoff * (2 ** (step1_attempts - 1)) * (0.5 + 0.5 * random.random())  # Add jitter
                    logger.info(f"Retrying Step 1 after {wait_time:.2f} seconds (attempt {step1_attempts + 1}/{step1_max_attempts})...")
                    time.sleep(wait_time)
                
                chapters, toc_output_dir = step1_generate_toc(pdf_path, output_dirs['base'])
                output_dirs['toc'] = toc_output_dir
                step1_success = True
                logger.info(f"Step 1 completed successfully with {len(chapters)} chapters identified")
                
            except Exception as e:
                step1_attempts += 1
                logger.error(f"Error in Step 1 (attempt {step1_attempts}/{step1_max_attempts}): {str(e)}")
                if step1_attempts == step1_max_attempts:
                    raise RuntimeError(f"Step 1 failed after {step1_max_attempts} attempts: {str(e)}")
        
        # Rate limiting cooldown between step 1 and 2
        cooldown_time = 5  # seconds
        logger.info(f"Rate limiting: Cooling down for {cooldown_time} seconds before starting Step 2...")
        time.sleep(cooldown_time)
        
        # Step 2: Match categories to chapters and sections with retry logic
        logger.info("\nRUNNING STEP 2: Matching Categories")
        step2_attempts = 0
        step2_max_attempts = 3
        step2_success = False
        step2_backoff = 3  # Initial backoff time in seconds
        chapter_results = None
        section_results = None
        category_match_dir = None
        
        while step2_attempts < step2_max_attempts and not step2_success:
            try:
                if step2_attempts > 0:
                    wait_time = step2_backoff * (2 ** (step2_attempts - 1)) * (0.5 + 0.5 * random.random())  # Add jitter
                    logger.info(f"Retrying Step 2 after {wait_time:.2f} seconds (attempt {step2_attempts + 1}/{step2_max_attempts})...")
                    time.sleep(wait_time)
                
                # Pass the base directory to ensure step2 creates its directory in the same run
                category_match_dir, chapter_results, section_results = step2_match_categories(
                    chapters, 
                    toc_output_dir, 
                    category_file, 
                    base_dir=output_dirs['base'],
                    model=initialize_gemini_model()[0]
                )
                output_dirs['category_matching'] = category_match_dir
                step2_success = True
                logger.info(f"Step 2 completed successfully with {len(chapter_results)} chapter matches and {len(section_results)} section matches")
                
            except Exception as e:
                step2_attempts += 1
                logger.error(f"Error in Step 2 (attempt {step2_attempts}/{step2_max_attempts}): {str(e)}")
                if step2_attempts == step2_max_attempts:
                    raise RuntimeError(f"Step 2 failed after {step2_max_attempts} attempts: {str(e)}")
        
        # Rate limiting cooldown between step 2 and 3 (less critical as step 3 doesn't use API)
        cooldown_time = 2  # seconds
        logger.info(f"Rate limiting: Cooling down for {cooldown_time} seconds before starting Step 3...")
        time.sleep(cooldown_time)
        
        # Step 3: Split document into category-specific PDFs
        logger.info("\nRUNNING STEP 3: Splitting PDF into Category-Specific Documents")
        try:
            # Pass the base directory to ensure step3 creates its directory in the same run
            pdf_count, pdf_output_dir = step3_extract_category_pdfs(
                pdf_path, 
                chapter_results, 
                section_results, 
                category_match_dir, 
                category_file,
                second_output_dir,
                third_output_dir,
                base_dir=output_dirs['base']
            )
            output_dirs['category_pdfs'] = pdf_output_dir
            logger.info(f"Step 3 completed successfully with {pdf_count} PDFs created")
            
        except Exception as e:
            logger.error(f"Error in Step 3: {str(e)}")
            raise RuntimeError(f"Step 3 failed: {str(e)}")
        
        # Calculate total execution time
        total_time = time.time() - start_time
        
        logger.info("=" * 50)
        logger.info("COMPLETE PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Output directories:")
        for dir_name, dir_path in output_dirs.items():
            logger.info(f"- {dir_name}: {dir_path}")
        logger.info("=" * 50)
        
        # Generate report file in the base directory
        try:
            # Calculate category statistics
            try:
                if category_file:
                    # Import the module to get the category dataframe
                    category_dir = os.path.dirname(category_file)
                    category_module = os.path.splitext(os.path.basename(category_file))[0]
                    
                    if category_dir not in sys.path:
                        sys.path.append(category_dir)
                        
                    module = __import__(category_module)
                    df = getattr(module, 'df', None)
                else:
                    from nonvmswhoofdstukken_pandas import df
                    
                stats = calculate_category_statistics(chapter_results, section_results, df)
            except Exception as e:
                logger.error(f"Error calculating category statistics: {str(e)}")
                stats = {
                    "avg_matches_per_chapter": 0,
                    "avg_matches_per_section": 0,
                    "most_frequent_categories": [],
                    "categories_with_no_matches": [],
                    "num_categories_with_no_matches": 0
                }
                
            # Write report to the base directory, not to any step directory
            report_file = os.path.join(output_dirs['base'], "pipeline_execution_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("Non-VMSW Document Processing Pipeline - Execution Report\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Execution date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input PDF: {pdf_path}\n")
                f.write(f"Total execution time: {total_time:.2f} seconds\n\n")
                
                f.write("Step 1: Table of Contents Generation\n")
                f.write("-" * 40 + "\n")
                f.write(f"Identified chapters: {len(chapters)}\n")
                f.write(f"Output directory: {toc_output_dir}\n\n")
                
                f.write("Step 2: Category Matching\n")
                f.write("-" * 40 + "\n")
                f.write(f"Chapter matches: {len(chapter_results)}\n")
                f.write(f"Section matches: {len(section_results)}\n")
                f.write(f"Average matches per chapter: {stats['avg_matches_per_chapter']:.1f}\n")
                f.write(f"Average matches per section: {stats['avg_matches_per_section']:.1f}\n")
                f.write(f"Most frequently matched categories: {', '.join(stats['most_frequent_categories'])}\n")
                f.write(f"Categories with no matches ({stats['num_categories_with_no_matches']} categories had no matches)\n")
                f.write(f"Output directory: {category_match_dir}\n\n")
                
                f.write("Step 3: PDF Extraction\n")
                f.write("-" * 40 + "\n")
                f.write(f"Generated PDFs: {pdf_count}\n")
                f.write(f"Output directory: {pdf_output_dir}\n")
                if second_output_dir:
                    f.write(f"Second output directory: {second_output_dir}\n")
                    f.write(f"Data files directory: {os.path.join(second_output_dir, 'data')}\n")
                
                # Only write third output directory info if it exists and is not None
                third_output_dir = locals().get('third_output_dir')
                if third_output_dir:
                    f.write(f"Third output directory: {third_output_dir}\n")
                    f.write(f"Data files directory: {os.path.join(third_output_dir, 'data')}\n")
                
                return True, output_dirs
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            logger.exception(e)
            return False, output_dirs
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        logger.exception("Detailed error information:")
        return False, output_dirs

def main():
    """Main entry point for the application"""
    # Determine if we should use GUI or command line
    if len(sys.argv) > 1 and "--no-gui" in sys.argv:
        run_from_command_line()
    else:
        # Launch the GUI
        app = QApplication(sys.argv)
        window = NonVMSWPipelineGUI()
        window.show()
        
        # Set default values if available
        if os.path.exists(DEFAULT_PDF_PATH):
            window.pdf_path = DEFAULT_PDF_PATH
            window.pdf_path_edit.setPlainText(DEFAULT_PDF_PATH)
            
        if os.path.exists(DEFAULT_CATEGORY_FILE):
            window.category_file_path = DEFAULT_CATEGORY_FILE
            window.cat_path_edit.setPlainText(DEFAULT_CATEGORY_FILE)
            
        default_output_dir = os.path.join(os.getcwd(), "output") # Simplified default path
        window.output_dir = default_output_dir
        window.out_path_edit.setPlainText(default_output_dir)
        
        sys.exit(app.exec())

def post_process_results(response_text):
    """
    Extract Python dictionary from Vertex AI model response.
    
    Args:
        response_text (str): The raw response text from the model
        
    Returns:
        dict: Extracted dictionary or None if parsing fails
    """
    try:
        # Find the code block in the response
        code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
        if code_block_match:
            code_block = code_block_match.group(1)
            
            # Extract the chapters dictionary
            local_vars = {}
            exec(code_block, {}, local_vars)
            
            if 'chapters' in local_vars:
                return local_vars['chapters']
            elif 'secties' in local_vars:
                return local_vars['secties']
    except Exception as e:
        logger.error(f"Error post-processing results: {str(e)}")
    
    return None

def calculate_category_statistics(chapter_results, section_results, df):
    """
    Calculate statistics about category matches.
    
    Args:
        chapter_results: Dictionary of chapter matches
        section_results: Dictionary of section matches
        df: DataFrame containing all categories
        
    Returns:
        dict: Dictionary containing statistics about category matches
    """
    # Calculate matches per chapter
    chapter_match_counts = {}
    for chapter_num, data in chapter_results.items():
        chapter_match_counts[chapter_num] = len(data["matches"])
    
    # Calculate matches per section
    section_match_counts = {}
    for section_key, data in section_results.items():
        section_match_counts[section_key] = len(data["matches"])
    
    # Calculate average matches per chapter and section
    avg_matches_per_chapter = sum(chapter_match_counts.values()) / len(chapter_match_counts) if chapter_match_counts else 0
    avg_matches_per_section = sum(section_match_counts.values()) / len(section_match_counts) if section_match_counts else 0
    
    # Get all matched categories
    matched_categories = set()
    for chapter_num, data in chapter_results.items():
        for match in data["matches"]:
            matched_categories.add(match["category"])
    
    for section_key, data in section_results.items():
        for match in data["matches"]:
            matched_categories.add(match["category"])
    
    # Calculate most frequently matched categories
    category_counts = {}
    for chapter_num, data in chapter_results.items():
        for match in data["matches"]:
            category = match["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
    
    for section_key, data in section_results.items():
        for match in data["matches"]:
            category = match["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
    
    # Sort categories by frequency
    most_frequent_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    top_categories = [cat for cat, count in most_frequent_categories[:5]]
    
    # Find categories with no matches
    all_categories = set([row['summary'] for _, row in df.iterrows()])
    categories_with_no_matches = all_categories - matched_categories
    
    return {
        "avg_matches_per_chapter": avg_matches_per_chapter,
        "avg_matches_per_section": avg_matches_per_section,
        "most_frequent_categories": top_categories,
        "categories_with_no_matches": categories_with_no_matches,
        "num_categories_with_no_matches": len(categories_with_no_matches)
    }

def run_from_command_line():
    """
    Run the pipeline from the command line with specified arguments.
    
    Usage:
    python script.py <pdf_path> [category_file] [output_dir] [--no-explanations]
    """
    parser = argparse.ArgumentParser(description="Run the Non-VMSW document processing pipeline")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("-c", "--category-file", help="Path to the category file (optional)")
    parser.add_argument("-o", "--output-dir", help="Output directory (optional)")
    parser.add_argument("-s", "--second-output-dir", help="Second output directory (optional)")
    parser.add_argument("-t", "--third-output-dir", help="Third output directory (optional)")
    parser.add_argument("--no-explanations", action="store_true",
                        help="Run without generating explanations for category matches (higher efficiency)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--model", choices=["gemini-2.5-pro", "gemini-2.5-flash"],
                        default="gemini-2.5-pro",
                        help="Gemini model to use (default: gemini-2.5-pro)")
    
    # Add subcommands for individual steps
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Step 1 command
    parser_step1 = subparsers.add_parser("step1", help="Run only step 1: TOC generation")
    
    # Step 2 command
    parser_step2 = subparsers.add_parser("step2", help="Run only step 2: Category matching")
    parser_step2.add_argument("-i", "--toc-dir", help="Directory with TOC results from step 1")
    
    # Step 3 command
    parser_step3 = subparsers.add_parser("step3", help="Run only step 3: PDF extraction")
    parser_step3.add_argument("-i", "--category-match-dir", help="Directory with category matching results")
    
    args = parser.parse_args()
    
    # Configure global explanation setting
    global INCLUDE_EXPLANATIONS
    INCLUDE_EXPLANATIONS = not args.no_explanations
    
    logger.info(f"Running with explanations: {INCLUDE_EXPLANATIONS}")
    logger.info(f"Using Gemini model: {args.model}")
    
    # Based on the command, run specific steps or the complete pipeline
    if args.command == "step1":
        # Run only step 1: TOC generation
        step1_generate_toc(args.pdf_path, args.output_dir)
    elif args.command == "step2":
        # Run only step 2: Category matching
        if not args.toc_dir:
            logger.error("Error: --toc-dir is required for step2 command")
            return False
        
        # Load chapters from step 1
        chapters_file = os.path.join(args.toc_dir, "chapters.json")
        if not os.path.exists(chapters_file):
            logger.error(f"Error: Chapters file not found at {chapters_file}")
            return False
        
        with open(chapters_file, 'r', encoding='utf-8') as f:
            chapters = json.load(f)
        
        # Initialize the AI model with the specified model name
        model = initialize_gemini_model(args.model)[0]
        
        step2_match_categories(chapters, args.toc_dir, args.category_file, model=model)
    elif args.command == "step3":
        # Run only step 3: PDF extraction
        category_match_dir = args.category_match_dir
        if not category_match_dir:
            # Find the most recent step2 output directory if not explicitly provided
            if not args.output_dir:
                logger.error("Error: Either --category-match-dir or --output-dir must be specified")
                return False
                
            # Look for directories that contain step2_category_matching
            try:
                potential_step2_dirs = [d for d in os.listdir(args.output_dir) 
                                       if os.path.isdir(os.path.join(args.output_dir, d)) and "step2_category_matching" in d]
                
                if potential_step2_dirs:
                    # Sort by name (which includes date) and get the most recent
                    category_match_dir = os.path.join(args.output_dir, sorted(potential_step2_dirs)[-1])
                    logger.info(f"Using category matching data from {category_match_dir}")
                else:
                    logger.error("No previous step2 output directory found.")
                    return False
            except Exception as e:
                logger.error(f"Error finding previous step2 output: {str(e)}")
                return False
        
        # Load chapter and section results
        chapter_matches_file = os.path.join(category_match_dir, "chapter_category_matches.csv")
        section_matches_file = os.path.join(category_match_dir, "section_category_matches.csv")
        
        if not os.path.exists(chapter_matches_file) or not os.path.exists(section_matches_file):
            logger.error(f"Error: Category match files not found in {category_match_dir}")
            return False
        
        chapter_results = pd.read_csv(chapter_matches_file).to_dict('records')
        section_results = pd.read_csv(section_matches_file).to_dict('records')
        
        step3_extract_category_pdfs(
            args.pdf_path, 
            chapter_results,
            section_results,
            category_match_dir, 
            args.category_file,
            args.second_output_dir,
            args.third_output_dir
        )
    else:
        # Run the complete pipeline with all parameters
        run_complete_pipeline(
            args.pdf_path, 
            args.output_dir, 
            args.category_file, 
            args.second_output_dir
        )
    
    return True

# Main entry point
if __name__ == "__main__":
    main()