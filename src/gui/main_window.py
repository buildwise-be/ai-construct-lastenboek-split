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
    QScrollArea, QFrame, QTextEdit, QFileDialog, QMessageBox, QApplication
)

from .components.styled_components import (
    StyledButton, StyledFrame, HeaderFrame, ProgressSection
)
from .workers.processing_worker import (
    Step1Worker, Step2Worker, Step3Worker, CompletePipelineWorker
)
from ..config.settings import (
    APP_NAME, APP_SUBTITLE, ASSETS_CONFIG, COLORS, GUI_CONFIG,
    DEFAULT_CATEGORY_FILE, LOGGING_CONFIG
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
        self.category_file_path = str(DEFAULT_CATEGORY_FILE)
        self.output_dir = ""
        self.pdf_output_dir = ""
        self.project_id = ""
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
        self.log("Application started. Please select input files and run the pipeline steps.")
    
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
        self.cat_path_edit.setPlainText(str(DEFAULT_CATEGORY_FILE))
        self.browse_cat_button = StyledButton("Bladeren", "secondary")
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
        
        # Step buttons
        self.step1_button = StyledButton("📑 Stap 1: TOC Generatie", "primary")
        self.step1_button.clicked.connect(self.run_step1)
        
        self.step2_button = StyledButton("🤖 Stap 2: Categorie Matching", "secondary")
        self.step2_button.clicked.connect(self.run_step2)
        
        self.step3_button = StyledButton("✂️ Stap 3: PDF Extractie", "accent")
        self.step3_button.clicked.connect(self.run_step3)
        
        self.complete_button = StyledButton("🚀 Volledige Pipeline", "alternate")
        self.complete_button.clicked.connect(self.run_complete_pipeline)
        
        # Control buttons
        self.cancel_button = StyledButton("⏹️ Annuleren", "dark")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        
        self.clear_log_button = StyledButton("🗑️ Log Wissen", "dark_gray")
        self.clear_log_button.clicked.connect(self.clear_log)
        
        # Layout buttons
        buttons_layout.addWidget(self.step1_button, 0, 0)
        buttons_layout.addWidget(self.step2_button, 0, 1)
        buttons_layout.addWidget(self.step3_button, 0, 2)
        buttons_layout.addWidget(self.complete_button, 0, 3)
        
        buttons_layout.addWidget(self.cancel_button, 1, 0)
        buttons_layout.addWidget(self.clear_log_button, 1, 1)
        
        self.main_layout.addWidget(buttons_frame)
    
    def _setup_log_section(self):
        """Setup the log display section."""
        log_frame = StyledFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        log_layout.setSpacing(10)
        
        log_label = self._create_bold_label("Log Output:")
        
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
        
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_display)
        
        self.main_layout.addWidget(log_frame)
    
    def _setup_output_section(self):
        """Setup the output section."""
        output_frame = StyledFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 15, 15, 15)
        output_layout.setSpacing(10)
        
        output_label = self._create_bold_label("Output:")
        
        self.open_output_button = StyledButton("📁 Open Output Map", "primary")
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
    
    def log(self, message):
        """Add a message to the log display."""
        self.log_counter += 1
        log_entry = f"[{self.log_counter:04d}] {message}"
        self.log_display.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.End)
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
        self.log("Log cleared.")
    
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
        
        if check_category_file and not self.category_file_path:
            issues.append("Categorie bestand moet geselecteerd zijn") 
        elif check_category_file and not os.path.exists(self.category_file_path):
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
        self.browse_cat_button.setEnabled(not is_processing)
        self.browse_output_button.setEnabled(not is_processing)
        
        # Disable step buttons during processing
        self.step1_button.setEnabled(not is_processing)
        self.step2_button.setEnabled(not is_processing)
        self.step3_button.setEnabled(not is_processing)
        self.complete_button.setEnabled(not is_processing)
        
        # Enable/disable cancel button
        self.cancel_button.setEnabled(is_processing)
    
    def _connect_worker_signals(self, worker):
        """Connect worker signals to UI handlers."""
        worker.started.connect(lambda: self._set_processing_state(True))
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        worker.progress.connect(self._on_worker_progress)
        worker.log_message.connect(self.log)
    
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
        self.current_worker = None
    
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
        self.current_worker = None
    
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
        if not self.validate_inputs(check_pdf=False, check_category_file=True):
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
        
        # Create and start worker
        self.current_worker = Step2Worker(
            None,  # chapters will be loaded from toc_output_dir
            self.last_toc_dir,
            self.category_file_path,
            self.output_dir or None,
            None,  # model
            self.include_explanations
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def run_step3(self):
        """Run Step 3: PDF Extraction."""
        if not self.validate_inputs(check_pdf=True, check_category_file=True):
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
            self.category_file_path,
            None,  # second_output_dir
            None,  # third_output_dir
            self.output_dir or None
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def run_complete_pipeline(self):
        """Run the complete pipeline."""
        if not self.validate_inputs(check_pdf=True, check_category_file=True):
            return
        
        self.log("=== VOLLEDIGE PIPELINE ===")
        self.progress_section.reset_progress()
        
        # Get project ID
        project_id = self.project_id_edit.toPlainText().strip() or None
        
        # Create and start worker
        self.current_worker = CompletePipelineWorker(
            self.pdf_path,
            self.output_dir or None,
            self.category_file_path,
            None,  # second_output_dir
            None,  # third_output_dir
            project_id
        )
        self._connect_worker_signals(self.current_worker)
        self.current_worker.start()
    
    def cancel_processing(self):
        """Cancel current processing."""
        if self.current_worker:
            self.current_worker.cancel()
            self.log("Annulering aangevraagd...")
            self._set_processing_state(False)
            self.progress_section.reset_progress()
    
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