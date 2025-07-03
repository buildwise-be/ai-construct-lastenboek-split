"""
Demo script for AI Construct PDF Opdeler - Modified to run only Step 3
This script is a modified version of main_script.py specifically for the demo.
"""

import sys
import os
import time
import logging
import random
import shutil # Import shutil for file copying

# Append parent directory to sys.path so we can import from main_script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import main script module - we'll import all required modules through it
from main_script import (
    vertexai, setup_output_directory, step3_extract_category_pdfs,
    DEFAULT_CATEGORY_FILE, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QFileDialog, 
    QProgressBar, QGroupBox, QScrollArea, QFrame, QTextEdit, 
    QCheckBox, QMessageBox, QComboBox, StyledButton, StyledFrame,
    Qt, Signal, Slot, QSize, QTimer, QThread, logger, COLORS, QWidget, QPixmap
)

# Set demo defaults
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PDF_PATH = os.path.join(DEMO_DIR, "sample_lastenboek.pdf")
DEFAULT_CATEGORY_FILE = os.path.join(os.path.dirname(DEMO_DIR), "example_categories.py")
DEFAULT_INPUT_DIR = os.path.join(DEMO_DIR, "step3_input")
DEFAULT_OUTPUT_DIR = os.path.join(DEMO_DIR, "output")

# Ensure the required demo files exist
if not os.path.exists(DEFAULT_PDF_PATH):
    logger.error(f"Demo PDF file not found: {DEFAULT_PDF_PATH}")
if not os.path.exists(DEFAULT_CATEGORY_FILE):
    logger.error(f"Category file not found: {DEFAULT_CATEGORY_FILE}")
if not os.path.exists(DEFAULT_INPUT_DIR):
    logger.error(f"Input directory not found: {DEFAULT_INPUT_DIR}")
if not os.path.exists(os.path.join(DEFAULT_INPUT_DIR, "chapters.json")):
    logger.error(f"chapters.json not found in input directory")
if not os.path.exists(os.path.join(DEFAULT_INPUT_DIR, "unified_category_matches.csv")):
    logger.error(f"unified_category_matches.csv not found in input directory")

class DemoPipelineGUI(QMainWindow):
    """Modified GUI that only runs step 3 when the full process button is clicked"""
    def __init__(self):
        super().__init__()
        
        # Set window properties (Matching main_script.py)
        self.setWindowTitle("AI Construct PDF Opdeler") # Remove Demo tag
        self.setMinimumSize(1000, 800) # Match original min size
        self.resize(1200, 900) # Match original default size
        
        # Initialize instance variables (Keep demo defaults for paths)
        self.pdf_path = DEFAULT_PDF_PATH
        self.category_file_path = DEFAULT_CATEGORY_FILE
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.pdf_output_dir = None
        self.second_output_dir = None
        self.third_output_dir = None
        self.include_explanations = True # Match original default
        self.project_id = "" # Match original default

        # Initialize output_dirs dictionary (Matching original)
        self.output_dirs = {'base': None, 'toc': None, 'category_matching': None, 'category_pdfs': None}

        # Track process information like in the original GUI (Can be dummies)
        self.last_toc_dir = None
        self.last_category_match_dir = None

        # Log counter (Matching original)
        self.log_counter = 0

        # Dummy variable for signal handling (Matching original)
        self.project_id_needs_update = False 
        
        # Set up the central widget and scroll area (Matching main_script.py)
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
        # **This is the crucial change**: main_layout is now on scroll_widget
        self.main_layout = QVBoxLayout(self.scroll_widget) 
        # Set margins/spacing for the content layout inside the scroll area
        self.main_layout.setContentsMargins(20, 20, 20, 20) # Original uses margins here
        self.main_layout.setSpacing(20) # Original uses spacing here

        # Set the scroll widget as the scroll area's widget
        self.scroll_area.setWidget(self.scroll_widget)

        # Add scroll area to central layout
        central_layout.addWidget(self.scroll_area)

        # Setup UI sections (Now added to self.main_layout inside scroll_widget)
        self.setup_header()
        self.setup_input_section()
        self.setup_progress_section()
        self.setup_log_section()
        self.setup_output_section()
        
        # Apply overall stylesheet
        self.apply_stylesheet()
        
        # Add a timer to keep UI responsive (Matching original)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(QApplication.processEvents)
        self.refresh_timer.start(100)  # Update every 100ms
        
        # Log initial message (Matching original)
        self.log("Application started. Please select input files and run the pipeline steps.")
        
        # Pre-fill input fields (Using demo defaults where applicable)
        self.pdf_path_edit.setText(self.pdf_path) # Use demo default
        self.cat_path_edit.setText(self.category_file_path) # Use demo default
        self.out_path_edit.setText(self.output_dir) # Use demo default
        # pdf_out_path_edit starts empty
        self.project_id_edit.setText(self.project_id) # Starts empty
        self.explanations_checkbox.setChecked(self.include_explanations) # Starts checked
    
    def setup_header(self):
        """Setup the header section with title and description to match the original GUI"""
        header_frame = StyledFrame("primary")
        # Use a more flexible grid layout instead
        header_layout = QGridLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(0)
        
        # Left side for BW logo
        bw_logo_label = QLabel()
        bw_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Requirements", "Logo", "BWlogo.png")
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

        # Right side for AICO logo
        aico_logo_label = QLabel()
        aico_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Requirements", "Logo", "aico.png")
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
        
        # Title and subtitle
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
        """Setup the input configuration section to exactly match main_script.py"""
        input_frame = StyledFrame()
        input_layout = QGridLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(15)

        # PDF File Selection (Using QTextEdit like original)
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

        # Category file selection (Using QTextEdit like original)
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

        # Output directory selection (Using QTextEdit like original)
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

        # PDF Output directory selection (Using QTextEdit like original)
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

        # Project ID (Optional) - Matching original
        project_id_label = QLabel("Project ID (Optioneel):")
        project_id_label.setStyleSheet("font-weight: bold;")
        
        self.project_id_edit = QLineEdit() # Original uses QLineEdit here
        self.project_id_edit.setPlaceholderText("Laat leeg om GOOGLE_CLOUD_PROJECT var te gebruiken") # Match original placeholder
        self.project_id_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        self.project_id_edit.textChanged.connect(self.update_project_id) # Add connection like original

        # Include Explanations Checkbox - Matching original
        self.explanations_checkbox = QCheckBox("Voeg extra uitleg toe aan output bestanden")
        self.explanations_checkbox.setChecked(self.include_explanations) # Use instance var
        self.explanations_checkbox.stateChanged.connect(self.toggle_explanations) # Add connection like original

        # Action buttons - Replicating original layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 15, 0, 0) # Match original margins

        self.run_step1_button = StyledButton("Start Stap 1", "secondary")
        self.run_step1_button.setEnabled(False) # Disable for demo
        # self.run_step1_button.clicked.connect(self.run_step1)

        self.run_step2_button = StyledButton("Start Stap 2", "secondary")
        self.run_step2_button.setEnabled(False) # Disable for demo
        # self.run_step2_button.clicked.connect(self.run_step2)

        self.run_step3_button = StyledButton("Start Stap 3", "secondary")
        self.run_step3_button.setEnabled(False) # Disable for demo
        # self.run_step3_button.clicked.connect(self.run_step3)

        self.run_pipeline_button = StyledButton("Start Volledige Pipeline", "primary") # Match original text
        self.run_pipeline_button.clicked.connect(self.run_step3_only) # Connect to demo logic
        self.run_pipeline_button.setMinimumWidth(200)

        button_layout.addWidget(self.run_step1_button)
        button_layout.addWidget(self.run_step2_button)
        button_layout.addWidget(self.run_step3_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.run_pipeline_button)

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

        input_layout.addWidget(project_id_label, 4, 0)
        input_layout.addWidget(self.project_id_edit, 4, 1)

        input_layout.addWidget(self.explanations_checkbox, 5, 0, 1, 2)

        input_layout.addLayout(button_layout, 6, 0, 1, 3)

        # Set column stretch for the middle column (input fields)
        input_layout.setColumnStretch(1, 1)

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
        
        # Create step indicators with status - showing all 3 steps but only Step 3 active
        steps_layout = QGridLayout()
        steps_layout.setColumnStretch(0, 2)  # Give more space to step description
        steps_layout.setColumnStretch(1, 1)  # Less space for status
        steps_layout.setHorizontalSpacing(20)
        steps_layout.setVerticalSpacing(10)
        
        # Step 1 - Set to default "Niet gestart" for visual consistency
        step1_label = QLabel("Stap 1: Inhoudstafel Genereren")
        step1_label.setStyleSheet("font-weight: bold;") # Reset style
        self.step1_status = QLabel("Niet gestart") # Reset text
        self.step1_status.setStyleSheet(f"""
            color: {COLORS['dark_gray']};
            padding: 5px;
            border-radius: 3px;
            background-color: {COLORS['light_gray']};
        """) # Reset style
        
        # Step 2 - Set to default "Niet gestart" for visual consistency
        step2_label = QLabel("Stap 2: Categorieën Matchen")
        step2_label.setStyleSheet("font-weight: bold;") # Reset style
        self.step2_status = QLabel("Niet gestart") # Reset text
        self.step2_status.setStyleSheet(f"""
            color: {COLORS['dark_gray']};
            padding: 5px;
            border-radius: 3px;
            background-color: {COLORS['light_gray']};
        """) # Reset style
        
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
        open_output_button = StyledButton("Open Output Folder", "secondary")
        open_output_button.clicked.connect(self.open_output_folder)
        
        button_layout.addStretch(1)
        button_layout.addWidget(open_output_button)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        output_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(output_frame)
    
    def apply_stylesheet(self):
        """Apply common stylesheet to the entire application"""
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['light']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: {COLORS['dark']};
            }}
            QGroupBox {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 3px;
            }}
        """)
    
    def log(self, message):
        """Add a message to the log window"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.append(f"[{timestamp}] {message}")
        # Ensure scrolling to the bottom
        scroll_bar = self.log_text.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        # Also send to logger
        logger.info(message)
    
    def clear_log(self):
        """Clear the log window"""
        self.log_text.clear()
    
    def browse_pdf(self):
        """Browse for PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecteer PDF bestand", "", "PDF bestanden (*.pdf)")
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_edit.setText(file_path)
            self.log(f"PDF bestand geselecteerd: {file_path}")
    
    def browse_category_file(self):
        """Browse for category file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecteer Categorie Bestand", "", "Python bestanden (*.py);;Excel bestanden (*.xlsx);;CSV bestanden (*.csv)")
        if file_path:
            self.category_file_path = file_path
            self.cat_path_edit.setText(file_path)
            self.log(f"Categorie bestand geselecteerd: {file_path}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Selecteer Uitvoermap")
        if dir_path:
            self.output_dir = dir_path
            self.out_path_edit.setText(dir_path)
            self.log(f"Uitvoermap geselecteerd: {dir_path}")
    
    def browse_pdf_output_dir(self):
        """Browse for PDF output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Selecteer PDF Uitvoermap")
        if dir_path:
            self.pdf_output_dir = dir_path
            self.pdf_out_path_edit.setText(dir_path)
            self.second_output_dir = dir_path  # For backward compatibility
            self.log(f"PDF uitvoermap geselecteerd: {dir_path}")
    
    def update_step_status(self, step_index, status, color=None):
        """Update the status display for a pipeline step"""
        if step_index < len(self.step_statuses):
            # Update the status text
            self.step_statuses[step_index].setText(status)
            
            # Update the status color if provided
            if color:
                if color == "default":
                    # Reset to default style
                    self.step_statuses[step_index].setStyleSheet(f"""
                        color: {COLORS['dark_gray']};
                        padding: 5px;
                        border-radius: 3px;
                        background-color: {COLORS['light_gray']};
                    """)
                else:
                    # Apply custom color
                    text_color = COLORS['light'] if color != COLORS['light'] else COLORS['dark']
                    self.step_statuses[step_index].setStyleSheet(f"""
                        color: {text_color};
                        padding: 5px;
                        border-radius: 3px;
                        background-color: {color};
                    """)
            
            # Update the corresponding step label if this is step 3 (the only active one)
            if step_index == 2:  # Step 3
                if status == "Bezig...":
                    self.step_labels[step_index].setStyleSheet("font-weight: bold;")
                elif status == "Voltooid":
                    self.step_labels[step_index].setStyleSheet("font-weight: bold;")
                elif status == "Fout":
                    self.step_labels[step_index].setStyleSheet("font-weight: bold; color: #FF3333;")
                else:
                    self.step_labels[step_index].setStyleSheet("font-weight: bold;")
    
    def update_progress(self, value):
        """Update the progress bar value"""
        self.progress_bar.setValue(value)
    
    def open_output_folder(self):
        """Open the output folder in the file explorer"""
        output_path = self.output_dir
        
        if not output_path or not os.path.exists(output_path):
            QMessageBox.warning(self, "Uitvoermap niet gevonden", "De geselecteerde uitvoermap bestaat niet.")
            return
        
        # Open the folder based on the platform
        if sys.platform == 'win32':
            os.startfile(output_path)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.Popen(['open', output_path])
        else:  # Linux and other Unix-like
            import subprocess
            subprocess.Popen(['xdg-open', output_path])
    
    def validate_inputs(self):
        """Validate the required inputs for the demo"""
        # Check PDF file
        if not self.pdf_path or not os.path.isfile(self.pdf_path):
            QMessageBox.warning(self, "PDF niet gevonden", "Selecteer een geldig PDF bestand.")
            return False
        
        # Check category file
        if not self.category_file_path or not os.path.isfile(self.category_file_path):
            QMessageBox.warning(self, "Categorie bestand niet gevonden", "Selecteer een geldig categorie bestand.")
            return False
        
        # Check output directory
        if not self.output_dir:
            QMessageBox.warning(self, "Uitvoermap niet geselecteerd", "Selecteer een uitvoermap.")
            return False
            
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                self.log(f"Uitvoermap aangemaakt: {self.output_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Fout bij aanmaken map", f"Kon uitvoermap niet aanmaken: {str(e)}")
                return False
        
        return True
    
    def run_step3_only(self):
        """Run only step 3 (PDF extraction) using pre-processed data"""
        # Validate inputs
        if not self.validate_inputs():
            return

        # Disable UI during processing
        self.setEnabled(False)

        # Reset progress
        self.progress_bar.setValue(0)
        # Update step status for step 3 specifically
        self.update_step_status(2, "Bezig...", COLORS["secondary"])
        # Reset steps 1 and 2 visually if needed (though they aren't run)
        self.update_step_status(0, "Niet gestart", "default")
        self.update_step_status(1, "Niet gestart", "default")

        # Set start time
        self.start_time = time.time()

        # Log start
        self.log("Demo gestart - Stap 3 (PDF Extractie)")
        self.log(f"PDF: {self.pdf_path}")
        self.log(f"Categorie bestand: {self.category_file_path}")
        self.log(f"Input map: {DEFAULT_INPUT_DIR}")
        self.log(f"Uitvoermap: {self.output_dir}")

        try:
            # Step 3: Extract category PDFs
            self.log("Stap 3: Extraheren van PDF's per categorie")

            # Set up the step3 output directory
            # Note: setup_output_directory handles timestamping if needed
            step3_dir = setup_output_directory("step3_category_pdfs", self.output_dir)

            # Run step 3 - It will now find section_category_matches.csv in DEFAULT_INPUT_DIR
            # Pass None for chapter_results and section_results as they are unused by the current main_script logic
            pdf_count, pdf_output_dir = step3_extract_category_pdfs(
                self.pdf_path,
                None, # chapter_results - unused by main_script step3
                None, # section_results - unused by main_script step3
                DEFAULT_INPUT_DIR,  # category_match_dir - where it looks for the csv
                self.category_file_path,
                second_output_dir=self.second_output_dir,
                third_output_dir=self.third_output_dir,
                base_dir=self.output_dir
            )

            # Update status and progress
            self.update_step_status(2, "Voltooid", "#33CC33") # Step 3 finished
            self.update_progress(100)

            # Calculate total execution time
            total_time = time.time() - self.start_time

            # Log completion
            self.log(f"Demo voltooid in {total_time:.2f} seconden")
            self.log(f"{pdf_count} PDF's aangemaakt in {pdf_output_dir}")

            # Update output files display
            self.output_text.clear()
            if os.path.exists(pdf_output_dir):
                pdf_files = [f for f in os.listdir(pdf_output_dir) if f.endswith('.pdf')]
                if pdf_files:
                    self.output_text.append(f"Categorie PDF's in {pdf_output_dir}:")
                    for pdf_file in pdf_files:
                        self.output_text.append(f"  - {pdf_file}")
                else:
                    self.output_text.append("Geen PDF bestanden gevonden in de uitvoermap.")
            else:
                self.output_text.append("Uitvoermap bestaat niet.")

            # Show success message
            QMessageBox.information(self, "Demo voltooid", 
                f"De demo is succesvol voltooid!\n\n{pdf_count} PDF's zijn aangemaakt in {pdf_output_dir}")

        except Exception as e:
            # Log error and show error message
            error_message = f"Fout tijdens uitvoeren van stap 3: {str(e)}"
            self.log(error_message)
            self.update_step_status(2, "Fout", "#FF3333")

            logger.exception("Error in demo execution")
            QMessageBox.critical(self, "Fout tijdens uitvoeren", error_message)

        finally:
            # Re-enable UI
            self.setEnabled(True)

    # Dummy method to handle project ID changes (for UI consistency)
    def update_project_id(self):
        new_id = self.project_id_edit.text().strip()
        if new_id != self.project_id:
            self.project_id = new_id
            self.project_id_needs_update = True # Flag that it changed
            self.log(f"Project ID bijgewerkt naar: '{self.project_id}' (wordt niet gebruikt in demo)")
        else:
             self.project_id_needs_update = False

    # Dummy method to handle explanations toggle (for UI consistency)
    def toggle_explanations(self, state):
        self.include_explanations = bool(state == Qt.Checked)
        self.log(f"Extra uitleg {'ingeschakeld' if self.include_explanations else 'uitgeschakeld'} (wordt niet gebruikt in demo)")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    window = DemoPipelineGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 