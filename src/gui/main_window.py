"""
Main GUI Window Module

This module contains the main application window with responsive background processing.
Extracted and refactored from the monolithic main script.
"""

import os
import logging
from pathlib import Path
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QTextEdit, QFileDialog, QMessageBox, QApplication, QComboBox
)
from PySide6.QtGui import QTextCursor

from .components.styled_components import (
    StyledButton, StyledFrame, HeaderFrame, ProgressSection
)
from .workers.processing_worker import (
    Step1Worker, Step2Worker, Step3Worker, CompletePipelineWorker
)
from config.settings import (
    APP_NAME, APP_SUBTITLE, ASSETS_CONFIG, COLORS, GUI_CONFIG,
    DEFAULT_CATEGORY_FILE, LOGGING_CONFIG, MODEL_CONFIG
)

# Configure logging
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with responsive background processing."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Window setup
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(GUI_CONFIG["min_width"], GUI_CONFIG["min_height"])
        self.resize(GUI_CONFIG["default_width"], GUI_CONFIG["default_height"])
        
        # Application state
        self.pdf_path = ""
        self.category_file_path = ""  # Empty by default since VMSW (default) doesn't need file
        self.output_dir = ""
        self.pdf_output_dir = ""
        self.project_id = ""
        self.selected_model = MODEL_CONFIG["default_model"]
        self.selected_doc_type = "vmsw"  # Default to VMSW
        self.include_explanations = True
        
        # Processing state
        self.current_worker = None
        self.output_dirs = {
            'base': None, 
            'toc': None, 
            'category_matching': None, 
            'category_pdfs': None
        }
        self.last_toc_dir = None
        self.last_category_match_dir = None
        
        # Log counter for GUI display
        self.log_counter = 0
        
        # Setup UI
        self._setup_ui()
        self._setup_responsive_timer()
        
        # Initial log message
        self.log("Applicatie gestart. Selecteer invoerbestanden en voer de pipeline stappen uit.")
    
    def closeEvent(self, event):
        """Handle application close event with proper cleanup."""
        try:
            # Cancel any running processing
            if self.current_worker and self.current_worker.isRunning():
                self.log("Closing application - canceling current processing...")
                self.cancel_processing()
                
                # Wait for worker to finish
                if self.current_worker:
                    self.current_worker.wait(2000)  # Wait max 2 seconds
            
            # Clean up any remaining worker
            self._cleanup_current_worker()
            
            # Accept the close event
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application close: {str(e)}")
            event.accept()  # Close anyway
    
    def _setup_ui(self):
        """Setup the main user interface."""
        # Central widget with scroll area
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Scroll area for main content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        self.scroll_widget = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Setup sections
        self._setup_header()
        self._setup_input_section()
        self._setup_progress_section()
        self._setup_action_buttons()
        self._setup_log_section()
        self._setup_output_section()
        
        # Set scroll widget and add to central layout
        self.scroll_area.setWidget(self.scroll_widget)
        central_layout.addWidget(self.scroll_area)
        
        # Apply global styling
        self._apply_global_styling()
    
    def _setup_header(self):
        """Setup the header section."""
        header = HeaderFrame(
            APP_NAME, 
            APP_SUBTITLE,
            ASSETS_CONFIG["bw_logo_path"],
            ASSETS_CONFIG["aico_logo_path"]
        )
        self.main_layout.addWidget(header)
    
    def _setup_input_section(self):
        """Setup the input configuration section."""
        input_frame = StyledFrame()
        input_layout = QGridLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(15)
        
        # PDF File Selection
        pdf_label = self._create_bold_label("PDF Bestand:")
        self.pdf_path_edit = self._create_file_display()
        self.browse_pdf_button = StyledButton("Bladeren", "secondary")
        self.browse_pdf_button.clicked.connect(self.browse_pdf)
        
        # Category file selection
        cat_label = self._create_bold_label("Categorie Bestand:")
        self.cat_path_edit = self._create_file_display()
        self.cat_path_edit.setPlainText("Built-in VMSW categories (number-based mapping)")  # Default for VMSW
        self.cat_path_edit.setEnabled(False)  # Disabled by default for VMSW
        self.browse_cat_button = StyledButton("Bladeren", "secondary")
        self.browse_cat_button.setEnabled(False)  # Disabled by default for VMSW
        self.browse_cat_button.clicked.connect(self.browse_category_file)
        
        # Output directory selection
        output_label = self._create_bold_label("Output Directory:")
        self.output_path_edit = self._create_file_display()
        self.browse_output_button = StyledButton("Bladeren", "secondary")
        self.browse_output_button.clicked.connect(self.browse_output_dir)
        
        # Project ID configuration
        project_label = self._create_bold_label("Google Cloud Project ID (Optioneel):")
        self.project_id_edit = self._create_file_display()
        self.project_id_edit.setPlaceholderText("Laat leeg om environment variabele te gebruiken")
        
        # Document type selection
        doc_type_label = self._create_bold_label("Document Type:")
        self.doc_type_selector = QComboBox()
        self._setup_doc_type_selector()
        
        # Model selection
        model_label = self._create_bold_label("AI Model:")
        self.model_selector = QComboBox()
        self._setup_model_selector()
        
        # Add to layout
        input_layout.addWidget(pdf_label, 0, 0)
        input_layout.addWidget(self.pdf_path_edit, 0, 1)
        input_layout.addWidget(self.browse_pdf_button, 0, 2)
        
        input_layout.addWidget(cat_label, 1, 0)
        input_layout.addWidget(self.cat_path_edit, 1, 1)
        input_layout.addWidget(self.browse_cat_button, 1, 2)
        
        input_layout.addWidget(output_label, 2, 0)
        input_layout.addWidget(self.output_path_edit, 2, 1)
        input_layout.addWidget(self.browse_output_button, 2, 2)
        
        input_layout.addWidget(project_label, 3, 0)
        input_layout.addWidget(self.project_id_edit, 3, 1, 1, 2)
        
        input_layout.addWidget(doc_type_label, 4, 0)
        input_layout.addWidget(self.doc_type_selector, 4, 1, 1, 2)
        
        input_layout.addWidget(model_label, 5, 0)
        input_layout.addWidget(self.model_selector, 5, 1, 1, 2)
        
        # Set column stretches
        input_layout.setColumnStretch(1, 1)
        
        self.main_layout.addWidget(input_frame)
    
    def _setup_progress_section(self):
        """Setup the progress display section."""
        self.progress_section = ProgressSection()
        self.main_layout.addWidget(self.progress_section)
    
    def _setup_action_buttons(self):
        """Setup the action buttons section."""
        buttons_frame = StyledFrame()
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setContentsMargins(15, 15, 15, 15)
        buttons_layout.setSpacing(10)
        
        # Step buttons with gradient colors from primary to secondary
        self.step1_button = StyledButton("Stap 1: TOC Generatie", "primary")
        self.step1_button.clicked.connect(self.run_step1)
        self._apply_gradient_style(self.step1_button, "#0087B7", "#0098B7")  # Primary blue gradient
        
        self.step2_button = StyledButton("Stap 2: Categorie Matching", "secondary")
        self.step2_button.clicked.connect(self.run_step2)
        self._apply_gradient_style(self.step2_button, "#0098B7", "#00A9B6")  # Transition gradient
        
        self.step3_button = StyledButton("Stap 3: PDF Extractie", "accent")
        self.step3_button.clicked.connect(self.run_step3)
        self._apply_gradient_style(self.step3_button, "#00A9B6", "#00BAB6")  # Transition gradient
        
        self.complete_button = StyledButton("Volledige Pipeline", "alternate")
        self.complete_button.clicked.connect(self.run_complete_pipeline)
        self._apply_gradient_style(self.complete_button, "#00BAB6", "#00BFB6")  # Secondary teal gradient
        
        # Control buttons
        self.cancel_button = StyledButton("Annuleren", "dark")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        
        # Layout buttons
        buttons_layout.addWidget(self.step1_button, 0, 0)
        buttons_layout.addWidget(self.step2_button, 0, 1)
        buttons_layout.addWidget(self.step3_button, 0, 2)
        buttons_layout.addWidget(self.complete_button, 0, 3)
        
        buttons_layout.addWidget(self.cancel_button, 1, 0)
        
        self.main_layout.addWidget(buttons_frame)
    
    def _setup_log_section(self):
        """Setup the collapsible log display section."""
        log_frame = StyledFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        log_layout.setSpacing(10)
        
        # Header with toggle button
        log_header_layout = QHBoxLayout()
        
        self.log_toggle_button = StyledButton("Toon gedetailleerde logs", "secondary")
        self.log_toggle_button.clicked.connect(self._toggle_log_visibility)
        self.log_toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['light_gray']};
                color: {COLORS['dark']};
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORS['mid_gray']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['dark_gray']};
                color: white;
            }}
        """)
        
        # Status line for collapsed view
        self.log_status_label = self._create_bold_label("Status: Klaar voor gebruik")
        self.log_status_label.setStyleSheet(f"color: {COLORS['dark_gray']}; font-weight: normal; font-size: 11px;")
        
        log_header_layout.addWidget(self.log_toggle_button)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.log_status_label)
        
        # Detailed log area (hidden by default)
        self.log_detail_widget = QWidget()
        log_detail_layout = QVBoxLayout(self.log_detail_widget)
        log_detail_layout.setContentsMargins(0, 10, 0, 0)
        log_detail_layout.setSpacing(5)
        
        # Clear log button
        log_controls_layout = QHBoxLayout()
        self.clear_log_button = StyledButton("Log Wissen", "dark_gray")
        self.clear_log_button.clicked.connect(self.clear_log)
        log_controls_layout.addWidget(self.clear_log_button)
        log_controls_layout.addStretch()
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(200)
        self.log_display.setMaximumHeight(400)
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: {COLORS['dark']};
                color: {COLORS['light']};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 5px;
            }}
        """)
        
        log_detail_layout.addLayout(log_controls_layout)
        log_detail_layout.addWidget(self.log_display)
        
        # Add to main layout
        log_layout.addLayout(log_header_layout)
        log_layout.addWidget(self.log_detail_widget)
        
        # Start with logs hidden
        self.log_detail_widget.setVisible(False)
        self.logs_visible = False
        
        self.main_layout.addWidget(log_frame)
    
    def _setup_output_section(self):
        """Setup the output section."""
        output_frame = StyledFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 15, 15, 15)
        output_layout.setSpacing(10)
        
        output_label = self._create_bold_label("Output:")
        
        self.open_output_button = StyledButton("Open Output Map", "primary")
        self.open_output_button.clicked.connect(self.open_output_folder)
        self.open_output_button.setEnabled(False)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.open_output_button)
        
        self.main_layout.addWidget(output_frame)
    
    def _setup_responsive_timer(self):
        """Setup timer to keep UI responsive."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(QApplication.processEvents)
        self.refresh_timer.start(GUI_CONFIG["refresh_interval"])
    
    def _apply_global_styling(self):
        """Apply global application styling."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS["light"]};
            }}
            QScrollArea {{
                background-color: {COLORS["light"]};
                border: none;
            }}
        """)
    
    def _create_bold_label(self, text):
        """Create a bold label with consistent styling."""
        from PySide6.QtWidgets import QLabel
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold;")
        return label
    
    def _create_file_display(self):
        """Create a file path display widget."""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setMaximumHeight(GUI_CONFIG["content_max_height"])
        text_edit.setMinimumHeight(GUI_CONFIG["content_min_height"])
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['mid_gray']};
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        return text_edit
    
    def _apply_gradient_style(self, button, color1, color2):
        """Apply a gradient style to a button."""
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {color1}, stop: 1 {color2});
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
                min-height: {GUI_CONFIG["button_min_height"]}px;
                min-width: {GUI_CONFIG["button_min_width"]}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {color1}CC, stop: 1 {color2}CC);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {color1}77, stop: 1 {color2}77);
            }}
            QPushButton:disabled {{
                background-color: {COLORS["mid_gray"]};
                color: {COLORS["dark_gray"]};
            }}
        """)
    
    def _setup_model_selector(self):
        """Setup the model selection dropdown."""
        for model_key, model_info in MODEL_CONFIG["available_models"].items():
            display_text = f"{model_info['name']} - {model_info['description']}"
            self.model_selector.addItem(display_text, model_key)
        
        # Set default selection
        default_model = MODEL_CONFIG["default_model"]
        for i in range(self.model_selector.count()):
            if self.model_selector.itemData(i) == default_model:
                self.model_selector.setCurrentIndex(i)
                break
        
        # Connect signal to update selected model
        self.model_selector.currentIndexChanged.connect(self._on_model_changed)
        
        # Style the combo box
        self.model_selector.setStyleSheet(f"""
            QComboBox {{
                padding: 5px 10px;
                border: 1px solid {COLORS["mid_gray"]};
                border-radius: 5px;
                background-color: white;
                font-size: 12px;
                min-height: 25px;
            }}
            QComboBox:hover {{
                border-color: {COLORS["primary"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """)
    
    def _setup_doc_type_selector(self):
        """Setup the document type selection dropdown."""
        doc_types = [
            ("vmsw", "VMSW Document - Snelle nummer-mapping"),
            ("non_vmsw", "Non-VMSW Document - AI semantische analyse")
        ]
        
        for doc_type_key, display_text in doc_types:
            self.doc_type_selector.addItem(display_text, doc_type_key)
        
        # Set default to VMSW
        self.doc_type_selector.setCurrentIndex(0)
        
        # Connect signal
        self.doc_type_selector.currentIndexChanged.connect(self._on_doc_type_changed)
        
        # Style the combo box (same as model selector)
        self.doc_type_selector.setStyleSheet(f"""
            QComboBox {{
                padding: 5px 10px;
                border: 1px solid {COLORS["mid_gray"]};
                border-radius: 5px;
                background-color: white;
                font-size: 12px;
                min-height: 25px;
            }}
            QComboBox:hover {{
                border-color: {COLORS["primary"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """)
    
    def _on_doc_type_changed(self):
        """Handle document type selection change."""
        self.selected_doc_type = self.doc_type_selector.currentData()
        doc_type_text = self.doc_type_selector.currentText()
        self.log(f"Document type changed to: {doc_type_text}")
        
        # Update components based on document type
        is_vmsw = self.selected_doc_type == "vmsw"
        
        # Model selector - only enabled for non-VMSW
        self.model_selector.setEnabled(not is_vmsw)
        
        # Category file - update based on document type
        if is_vmsw:
            # VMSW uses built-in categories, show info message
            self.cat_path_edit.setPlainText("Built-in VMSW categories (number-based mapping)")
            self.cat_path_edit.setEnabled(False)
            self.browse_cat_button.setEnabled(False)
            self.category_file_path = ""  # Not needed for VMSW
            self.log("⚡ VMSW mode: Uses built-in categories, lightning-fast direct mapping")
        else:
            # Non-VMSW uses categories file
            self.cat_path_edit.setPlainText(str(self.category_file_path or "src/models/categories.py"))
            self.cat_path_edit.setEnabled(True)
            self.browse_cat_button.setEnabled(True)
            # Set default if not already set
            if not self.category_file_path:
                self.category_file_path = "src/models/categories.py"
                self.cat_path_edit.setPlainText(self.category_file_path)
            self.log("🤖 Non-VMSW mode: Uses category file for AI semantic analysis")
    
    def _on_model_changed(self):
        """Handle model selection change."""
        self.selected_model = self.model_selector.currentData()
        model_name = MODEL_CONFIG["available_models"][self.selected_model]["name"]
        self.log(f"Model changed to: {model_name}")
    
    def log(self, message):
        """Add a message to the log display and update status."""
        self.log_counter += 1
        log_entry = f"[{self.log_counter:04d}] {message}"
        self.log_display.append(log_entry)
        
        # Update status label with latest message (truncated if too long)
        status_message = message[:70] + "..." if len(message) > 70 else message
        self.log_status_label.setText(f"Status: {status_message}")
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_display.setTextCursor(cursor)
        
        # Limit log size
        if self.log_counter > LOGGING_CONFIG["max_lines"]:
            self.clear_log()
        
        # Process events to keep UI responsive
        QApplication.processEvents()
    
    def clear_log(self):
        """Clear the log display."""
        self.log_display.clear()
        self.log_counter = 0
        self.log_status_label.setText("Status: Log gewist")
        self.log("Log cleared.")
    
    def _toggle_log_visibility(self):
        """Toggle the visibility of the detailed log area."""
        self.logs_visible = not self.logs_visible
        self.log_detail_widget.setVisible(self.logs_visible)
        
        if self.logs_visible:
            self.log_toggle_button.setText("📄 Verberg Details & Logs")
        else:
            self.log_toggle_button.setText("📄 Toon Details & Logs")
    
    def browse_pdf(self):
        """Browse for PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecteer PDF Bestand", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_edit.setPlainText(file_path)
            self.log(f"PDF bestand geselecteerd: {file_path}")
    
    def browse_category_file(self):
        """Browse for category file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecteer Categorie Bestand", "", "Python Files (*.py)"
        )
        if file_path:
            self.category_file_path = file_path
            self.cat_path_edit.setPlainText(file_path)
            self.log(f"Categorie bestand geselecteerd: {file_path}")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Selecteer Output Directory"
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_path_edit.setPlainText(dir_path)
            self.log(f"Output directory geselecteerd: {dir_path}")
    
    def validate_inputs(self, check_pdf=True, check_category_file=True, check_output_dir=False):
        """Validate input fields."""
        issues = []
        
        if check_pdf and not self.pdf_path:
            issues.append("PDF bestand moet geselecteerd zijn")
        elif check_pdf and not os.path.exists(self.pdf_path):
            issues.append("PDF bestand bestaat niet")
        
        # Only check category file for non-VMSW documents
        if check_category_file and self.selected_doc_type != "vmsw":
            if not self.category_file_path:
                issues.append("Categorie bestand moet geselecteerd zijn voor Non-VMSW documenten") 
            elif not os.path.exists(self.category_file_path):
                issues.append("Categorie bestand bestaat niet")
        
        if check_output_dir and not self.output_dir:
            issues.append("Output directory moet geselecteerd zijn")
        
        if issues:
            QMessageBox.warning(self, "Validatie Fout", "\n".join(issues))
            return False
        
        return True
    
    def _set_processing_state(self, is_processing):
        """Enable/disable UI elements during processing."""
        # Disable input controls during processing
        self.browse_pdf_button.setEnabled(not is_processing)
        self.browse_output_button.setEnabled(not is_processing)
        self.doc_type_selector.setEnabled(not is_processing)
        
        # Handle category file and model selector based on document type
        if not is_processing:
            is_vmsw = self.selected_doc_type == "vmsw"
            # Category file controls - only enabled for non-VMSW
            self.browse_cat_button.setEnabled(not is_vmsw)
            self.cat_path_edit.setEnabled(not is_vmsw)
            # Model selector - only enabled for non-VMSW
            self.model_selector.setEnabled(not is_vmsw)
        else:
            # During processing, disable everything
            self.browse_cat_button.setEnabled(False)
            self.cat_path_edit.setEnabled(False)
            self.model_selector.setEnabled(False)
        
        # Disable step buttons during processing
        self.step1_button.setEnabled(not is_processing)
        self.step2_button.setEnabled(not is_processing)
        self.step3_button.setEnabled(not is_processing)
        self.complete_button.setEnabled(not is_processing)
        
        # Enable/disable cancel button
        self.cancel_button.setEnabled(is_processing)
    
    def _connect_worker_signals(self, worker):
        """Connect worker signals to UI handlers with thread safety."""
        # Use Qt.QueuedConnection to ensure signals are handled on the main thread
        from PySide6.QtCore import Qt
        
        worker.started.connect(lambda: self._set_processing_state(True), Qt.QueuedConnection)
        worker.finished.connect(self._on_worker_finished, Qt.QueuedConnection)
        worker.error.connect(self._on_worker_error, Qt.QueuedConnection)
        worker.progress.connect(self._on_worker_progress, Qt.QueuedConnection)
        worker.log_message.connect(self._on_worker_log_message, Qt.QueuedConnection)
        
        # Store worker reference for cleanup
        self.current_worker = worker
    
    def _on_worker_progress(self, percentage, message):
        """Handle worker progress updates."""
        self.progress_section.update_progress(percentage, message)
        
        # Update step indicators based on progress
        if self.current_worker and hasattr(self.current_worker, 'step_name'):
            step_name = self.current_worker.step_name
            if "Step 1" in step_name:
                self.progress_section.update_step_status("step1", "running")
            elif "Step 2" in step_name:
                self.progress_section.update_step_status("step2", "running")
            elif "Step 3" in step_name:
                self.progress_section.update_step_status("step3", "running")
            elif "Complete" in step_name:
                if percentage < 35:
                    self.progress_section.update_step_status("step1", "running")
                elif percentage < 70:
                    self.progress_section.update_step_status("step1", "success")
                    self.progress_section.update_step_status("step2", "running")
                elif percentage < 100:
                    self.progress_section.update_step_status("step2", "success")
                    self.progress_section.update_step_status("step3", "running")
    
    def _on_worker_finished(self, results):
        """Handle worker completion."""
        self._set_processing_state(False)
        
        # Update step indicators
        step = results.get('step', '')
        if step == 'step1':
            self.progress_section.update_step_status("step1", "success")
            self.last_toc_dir = results.get('output_dir', '')
        elif step == 'step2':
            self.progress_section.update_step_status("step2", "success")
            self.last_category_match_dir = results.get('output_dir', '')
        elif step == 'step3':
            self.progress_section.update_step_status("step3", "success")
        elif step == 'complete':
            self.progress_section.update_step_status("step1", "success")
            self.progress_section.update_step_status("step2", "success")
            self.progress_section.update_step_status("step3", "success")
            if 'results' in results:
                final_results = results['results']
                self.last_toc_dir = final_results.get('step1', {}).get('output_dir', '')
                self.last_category_match_dir = final_results.get('step2', {}).get('output_dir', '')
        
        # Enable output folder button
        self.open_output_button.setEnabled(True)
        
        self.log(f"Verwerking voltooid: {step}")
        self._cleanup_current_worker()
    
    def _on_worker_error(self, error_message):
        """Handle worker errors."""
        self._set_processing_state(False)
        
        # Update step indicators to show error
        if self.current_worker and hasattr(self.current_worker, 'step_name'):
            step_name = self.current_worker.step_name
            if "Step 1" in step_name:
                self.progress_section.update_step_status("step1", "error")
            elif "Step 2" in step_name:
                self.progress_section.update_step_status("step2", "error")
            elif "Step 3" in step_name:
                self.progress_section.update_step_status("step3", "error")
        
        self.log(f"FOUT: {error_message}")
        QMessageBox.critical(self, "Verwerkingsfout", error_message)
        self._cleanup_current_worker()
    
    def _on_worker_log_message(self, message):
        """Handle log messages from worker threads with thread safety."""
        try:
            self.log(message)
        except Exception as e:
            logger.error(f"Error logging worker message: {str(e)}")
    
    def _cleanup_current_worker(self):
        """Clean up the current worker thread and free resources."""
        if self.current_worker:
            try:
                # Wait a bit for worker to finish if it's still running
                if self.current_worker.isRunning():
                    self.current_worker.wait(1000)  # Wait max 1 second
                
                # Disconnect all signals to prevent memory leaks
                self.current_worker.started.disconnect()
                self.current_worker.finished.disconnect()
                self.current_worker.error.disconnect()
                self.current_worker.progress.disconnect()
                if hasattr(self.current_worker, 'log_message'):
                    self.current_worker.log_message.disconnect()
                
                # Delete the worker object
                self.current_worker.deleteLater()
                
            except Exception as e:
                logger.error(f"Error cleaning up worker: {str(e)}")
            finally:
                self.current_worker = None
                
                # Force garbage collection
                import gc
                gc.collect()
    
    def run_step1(self):
        """Run Step 1: TOC Generation."""
        if not self.validate_inputs(check_pdf=True, check_category_file=False):
            return
        
        self.log("=== STAP 1: TOC GENERATIE ===")
        self.progress_section.reset_progress()
        
        # Get project ID
        project_id = self.project_id_edit.toPlainText().strip() or None
        
        # Create and start worker
        self.current_worker = Step1Worker(
            self.pdf_path, 
            self.output_dir or None,
            project_id
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def run_step2(self):
        """Run Step 2: Category Matching."""
        # For step 2, category file is only required for non-VMSW documents
        # (VMSW documents will use the default category file)
        if not self.validate_inputs(check_pdf=False, check_category_file=(self.selected_doc_type != "vmsw")):
            return
        
        # Check if we have TOC data
        if not self.last_toc_dir:
            QMessageBox.warning(
                self, "Geen TOC Data", 
                "Voer eerst Stap 1 (TOC Generatie) uit."
            )
            return
        
        self.log("=== STAP 2: CATEGORIE MATCHING ===")
        self.progress_section.reset_progress()
        
        # Determine category file path
        # For VMSW documents, use default category file if user hasn't selected one
        if self.selected_doc_type == "vmsw" and not self.category_file_path:
            category_file_to_use = str(DEFAULT_CATEGORY_FILE)
            self.log(f"Using default category file for VMSW document: {category_file_to_use}")
        else:
            category_file_to_use = self.category_file_path
        
        # Create and start worker
        self.current_worker = Step2Worker(
            None,  # chapters will be loaded from toc_output_dir
            self.last_toc_dir,
            category_file_to_use,
            self.output_dir or None,
            self.selected_model,  # Pass selected model
            self.include_explanations,
            self.selected_doc_type  # Pass selected document type
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def run_step3(self):
        """Run Step 3: PDF Extraction."""
        # For step 3, category file is only required for non-VMSW documents
        # (VMSW documents will use the default category file)
        if not self.validate_inputs(check_pdf=True, check_category_file=(self.selected_doc_type != "vmsw")):
            return
        
        # Check if we have category matching data
        if not self.last_category_match_dir:
            QMessageBox.warning(
                self, "Geen Categorie Data", 
                "Voer eerst Stap 2 (Categorie Matching) uit."
            )
            return
        
        self.log("=== STAP 3: PDF EXTRACTIE ===")
        self.progress_section.reset_progress()
        
        # Determine category file path
        # For VMSW documents, use default category file if user hasn't selected one
        if self.selected_doc_type == "vmsw" and not self.category_file_path:
            category_file_to_use = str(DEFAULT_CATEGORY_FILE)
            self.log(f"Using default category file for VMSW document: {category_file_to_use}")
        else:
            category_file_to_use = self.category_file_path
        
        # Load results from Step 2
        try:
            import json
            
            chapters_file = os.path.join(self.last_category_match_dir, "chapter_results.json")
            sections_file = os.path.join(self.last_category_match_dir, "section_results.json")
            
            with open(chapters_file, 'r', encoding='utf-8') as f:
                chapter_results = json.load(f)
            
            with open(sections_file, 'r', encoding='utf-8') as f:
                section_results = json.load(f)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Fout bij laden data", 
                f"Kan resultaten van Stap 2 niet laden: {str(e)}"
            )
            return
        
        # Create and start worker
        self.current_worker = Step3Worker(
            self.pdf_path,
            chapter_results,
            section_results,
            self.last_category_match_dir,
            category_file_to_use,
            None,  # second_output_dir
            None,  # third_output_dir
            self.output_dir or None
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def run_complete_pipeline(self):
        """Run the complete pipeline."""
        # For complete pipeline, category file is only required for non-VMSW documents
        # (VMSW documents will use the default category file)
        if not self.validate_inputs(check_pdf=True, check_category_file=(self.selected_doc_type != "vmsw")):
            return
        
        self.log("=== VOLLEDIGE PIPELINE ===")
        self.progress_section.reset_progress()
        
        # Get project ID
        project_id = self.project_id_edit.toPlainText().strip() or None
        
        # Determine category file path
        # For VMSW documents, use default category file if user hasn't selected one
        if self.selected_doc_type == "vmsw" and not self.category_file_path:
            category_file_to_use = str(DEFAULT_CATEGORY_FILE)
            self.log(f"Using default category file for VMSW document: {category_file_to_use}")
        else:
            category_file_to_use = self.category_file_path
        
        # Create and start worker
        self.current_worker = CompletePipelineWorker(
            self.pdf_path,
            self.output_dir or None,
            category_file_to_use,
            None,  # second_output_dir
            None,  # third_output_dir
            project_id,
            self.selected_model,  # Pass selected model
            self.selected_doc_type  # Pass selected document type
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def cancel_processing(self):
        """Cancel current processing with proper cleanup."""
        if self.current_worker:
            self.current_worker.cancel()
            self.log("Annulering aangevraagd...")
            self._set_processing_state(False)
            self.progress_section.reset_progress()
            
            # Wait for worker to finish and clean up
            self._cleanup_current_worker()
    
    def open_output_folder(self):
        """Open the output folder in file manager."""
        output_path = self.output_dir
        
        # Try to find the most recent output directory
        if not output_path and self.last_category_match_dir:
            output_path = str(Path(self.last_category_match_dir).parent)
        elif not output_path and self.last_toc_dir:
            output_path = str(Path(self.last_toc_dir).parent)
        
        if output_path and os.path.exists(output_path):
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    os.startfile(output_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", output_path])
                else:  # Linux
                    subprocess.run(["xdg-open", output_path])
                
                self.log(f"Output map geopend: {output_path}")
            except Exception as e:
                self.log(f"Kan output map niet openen: {str(e)}")
                QMessageBox.information(
                    self, "Output Map", 
                    f"Output map locatie:\n{output_path}"
                )
        else:
            QMessageBox.information(
                self, "Geen Output", 
                "Geen output map beschikbaar. Voer eerst een verwerkingsstap uit."
            )