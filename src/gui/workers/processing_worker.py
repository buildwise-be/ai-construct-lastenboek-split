"""
Processing Worker Module

This module provides background workers for long-running processing tasks.
This keeps the GUI responsive during AI processing operations.
"""

import logging
from PySide6.QtCore import QThread, Signal, QObject
from typing import Optional, Dict, Any, Callable

# Configure logging
logger = logging.getLogger(__name__)


class ProcessingWorker(QThread):
    """
    Background worker thread for processing operations.
    """
    
    # Signals
    started = Signal()
    finished = Signal(dict)  # Emits results dictionary
    error = Signal(str)  # Emits error message
    progress = Signal(int, str)  # Emits (percentage, status_message)
    log_message = Signal(str)  # Emits log messages for GUI display
    
    def __init__(self, task_func: Callable, *args, **kwargs):
        """
        Initialize the processing worker.
        
        Args:
            task_func: The function to execute in the background
            *args: Arguments to pass to the task function
            **kwargs: Keyword arguments to pass to the task function
        """
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.results = None
        self.error_message = None
        self._is_cancelled = False
    
    def run(self):
        """Execute the background task."""
        try:
            logger.info("Starting background processing task")
            self.started.emit()
            
            # Execute the task function
            self.results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                logger.info("Background processing task completed successfully")
                self.finished.emit(self.results or {})
            
        except Exception as e:
            error_msg = f"Error in background processing: {str(e)}"
            logger.error(error_msg)
            self.error_message = error_msg
            self.error.emit(error_msg)
    
    def cancel(self):
        """Cancel the processing task."""
        self._is_cancelled = True
        logger.info("Processing task cancellation requested")
    
    def is_cancelled(self):
        """Check if the task has been cancelled."""
        return self._is_cancelled
    
    def emit_progress(self, percentage: int, message: str = ""):
        """Emit progress update."""
        if not self._is_cancelled:
            self.progress.emit(percentage, message)
    
    def emit_log(self, message: str):
        """Emit log message for GUI display."""
        if not self._is_cancelled:
            self.log_message.emit(message)


class Step1Worker(ProcessingWorker):
    """Worker for Step 1: TOC Generation."""
    
    def __init__(self, pdf_path: str, output_base_dir: Optional[str] = None, 
                 project_id: Optional[str] = None):
        """
        Initialize Step 1 worker.
        
        Args:
            pdf_path: Path to PDF file
            output_base_dir: Base output directory
            project_id: Google Cloud project ID
        """
        # Import here to avoid circular imports
        from ...core.pdf_processor import step1_generate_toc
        
        super().__init__(step1_generate_toc, pdf_path, output_base_dir, project_id)
        self.step_name = "Step 1: TOC Generation"
    
    def run(self):
        """Execute Step 1 with progress reporting."""
        try:
            self.emit_log(f"Starting {self.step_name}")
            self.emit_progress(0, "Initializing TOC generation...")
            self.started.emit()
            
            self.emit_progress(10, "Loading PDF file...")
            self.emit_log("Loading and validating PDF file")
            
            self.emit_progress(20, "Initializing AI model...")
            self.emit_log("Connecting to Vertex AI")
            
            self.emit_progress(30, "Processing PDF in batches...")
            self.emit_log("Starting batch processing of PDF pages")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(90, "Saving results...")
                self.emit_log("Saving TOC results to output directory")
                
                self.emit_progress(100, "TOC generation completed!")
                self.emit_log(f"{self.step_name} completed successfully")
                
                self.finished.emit({
                    'chapters': results[0] if results else {},
                    'output_dir': results[1] if len(results) > 1 else "",
                    'step': 'step1'
                })
            
        except Exception as e:
            error_msg = f"Error in {self.step_name}: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)


class Step2Worker(ProcessingWorker):
    """Worker for Step 2: Category Matching."""
    
    def __init__(self, chapters: Optional[Dict] = None, toc_output_dir: Optional[str] = None,
                 category_file: Optional[str] = None, base_dir: Optional[str] = None,
                 model = None, include_explanations: bool = True):
        """
        Initialize Step 2 worker.
        
        Args:
            chapters: Chapters dictionary from Step 1
            toc_output_dir: Directory containing TOC results
            category_file: Path to category definitions file
            base_dir: Base output directory
            model: AI model instance
            include_explanations: Whether to include explanations
        """
        # Import here to avoid circular imports
        from ...core.category_matcher import step2_match_categories
        
        super().__init__(step2_match_categories, chapters, toc_output_dir, 
                        category_file, base_dir, model)
        self.step_name = "Step 2: Category Matching"
        self.include_explanations = include_explanations
    
    def run(self):
        """Execute Step 2 with progress reporting."""
        try:
            self.emit_log(f"Starting {self.step_name}")
            self.emit_progress(0, "Initializing category matching...")
            self.started.emit()
            
            self.emit_progress(10, "Loading chapters data...")
            self.emit_log("Loading TOC data from Step 1")
            
            self.emit_progress(20, "Loading category definitions...")
            self.emit_log("Loading construction category definitions")
            
            self.emit_progress(30, "Initializing AI model...")
            self.emit_log("Preparing AI model for categorization")
            
            self.emit_progress(40, "Processing items in batches...")
            self.emit_log("Starting batch processing for category matching")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(85, "Calculating statistics...")
                self.emit_log("Generating category usage statistics")
                
                self.emit_progress(95, "Saving results...")
                self.emit_log("Saving categorization results")
                
                self.emit_progress(100, "Category matching completed!")
                self.emit_log(f"{self.step_name} completed successfully")
                
                self.finished.emit({
                    'chapter_results': results[0] if results else {},
                    'section_results': results[1] if len(results) > 1 else {},
                    'output_dir': results[2] if len(results) > 2 else "",
                    'step': 'step2'
                })
            
        except Exception as e:
            error_msg = f"Error in {self.step_name}: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)


class Step3Worker(ProcessingWorker):
    """Worker for Step 3: PDF Extraction."""
    
    def __init__(self, pdf_path: str, chapter_results: Dict, section_results: Dict,
                 category_match_dir: str, category_file: str, 
                 second_output_dir: Optional[str] = None, 
                 third_output_dir: Optional[str] = None,
                 base_dir: Optional[str] = None):
        """
        Initialize Step 3 worker.
        
        Args:
            pdf_path: Path to source PDF
            chapter_results: Chapter matching results
            section_results: Section matching results
            category_match_dir: Directory with category matching results
            category_file: Path to category definitions file
            second_output_dir: Secondary output directory
            third_output_dir: Tertiary output directory
            base_dir: Base output directory
        """
        # Import here to avoid circular imports
        from ...core.pdf_processor import step3_extract_category_pdfs
        
        super().__init__(step3_extract_category_pdfs, pdf_path, chapter_results,
                        section_results, category_match_dir, category_file,
                        second_output_dir, third_output_dir, base_dir)
        self.step_name = "Step 3: PDF Extraction"
    
    def run(self):
        """Execute Step 3 with progress reporting."""
        try:
            self.emit_log(f"Starting {self.step_name}")
            self.emit_progress(0, "Initializing PDF extraction...")
            self.started.emit()
            
            self.emit_progress(10, "Loading categorization results...")
            self.emit_log("Loading results from Step 2")
            
            self.emit_progress(20, "Loading source PDF...")
            self.emit_log("Opening source PDF for extraction")
            
            self.emit_progress(30, "Organizing content by categories...")
            self.emit_log("Mapping chapters and sections to categories")
            
            self.emit_progress(50, "Creating category-specific PDFs...")
            self.emit_log("Extracting and creating individual category PDFs")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(90, "Generating summary...")
                self.emit_log("Creating extraction summary")
                
                self.emit_progress(100, "PDF extraction completed!")
                self.emit_log(f"{self.step_name} completed successfully")
                
                self.finished.emit({
                    'category_counts': results[0] if results else {},
                    'output_dir': results[1] if len(results) > 1 else "",
                    'step': 'step3'
                })
            
        except Exception as e:
            error_msg = f"Error in {self.step_name}: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)


class CompletePipelineWorker(ProcessingWorker):
    """Worker for complete pipeline execution."""
    
    def __init__(self, pdf_path: str, output_base_dir: Optional[str] = None,
                 category_file: Optional[str] = None, 
                 second_output_dir: Optional[str] = None,
                 third_output_dir: Optional[str] = None,
                 project_id: Optional[str] = None):
        """
        Initialize complete pipeline worker.
        
        Args:
            pdf_path: Path to PDF file
            output_base_dir: Base output directory
            category_file: Path to category definitions file
            second_output_dir: Secondary output directory
            third_output_dir: Tertiary output directory
            project_id: Google Cloud project ID
        """
        # Import here to avoid circular imports
        from ...core.pdf_processor import step1_generate_toc, step3_extract_category_pdfs
        from ...core.category_matcher import step2_match_categories
        
        self.step1_func = step1_generate_toc
        self.step2_func = step2_match_categories
        self.step3_func = step3_extract_category_pdfs
        
        super().__init__(self._run_complete_pipeline, pdf_path, output_base_dir,
                        category_file, second_output_dir, third_output_dir, project_id)
        self.step_name = "Complete Pipeline"
    
    def _run_complete_pipeline(self, pdf_path: str, output_base_dir: Optional[str],
                              category_file: Optional[str], second_output_dir: Optional[str],
                              third_output_dir: Optional[str], project_id: Optional[str]):
        """Execute the complete pipeline."""
        
        # Step 1: TOC Generation
        self.emit_progress(5, "Step 1: Starting TOC generation...")
        self.emit_log("=== STEP 1: TOC GENERATION ===")
        
        chapters, step1_output_dir = self.step1_func(pdf_path, output_base_dir, project_id)
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(35, "Step 1 completed. Starting Step 2...")
        self.emit_log("Step 1 completed successfully")
        
        # Step 2: Category Matching
        self.emit_progress(40, "Step 2: Starting category matching...")
        self.emit_log("=== STEP 2: CATEGORY MATCHING ===")
        
        chapter_results, section_results, step2_output_dir = self.step2_func(
            chapters, None, category_file, output_base_dir, None
        )
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(70, "Step 2 completed. Starting Step 3...")
        self.emit_log("Step 2 completed successfully")
        
        # Step 3: PDF Extraction
        self.emit_progress(75, "Step 3: Starting PDF extraction...")
        self.emit_log("=== STEP 3: PDF EXTRACTION ===")
        
        category_counts, step3_output_dir = self.step3_func(
            pdf_path, chapter_results, section_results, step2_output_dir,
            category_file, second_output_dir, third_output_dir, output_base_dir
        )
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(100, "Complete pipeline finished!")
        self.emit_log("=== PIPELINE COMPLETED SUCCESSFULLY ===")
        
        return {
            'step1': {'chapters': chapters, 'output_dir': step1_output_dir},
            'step2': {'chapter_results': chapter_results, 'section_results': section_results, 'output_dir': step2_output_dir},
            'step3': {'category_counts': category_counts, 'output_dir': step3_output_dir},
            'final_output_dir': step3_output_dir
        }
    
    def run(self):
        """Execute complete pipeline with progress reporting."""
        try:
            self.emit_log(f"Starting {self.step_name}")
            self.emit_progress(0, "Initializing complete pipeline...")
            self.started.emit()
            
            # Execute the pipeline
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled and results:
                self.emit_log("Complete pipeline finished successfully")
                self.finished.emit({
                    'results': results,
                    'step': 'complete'
                })
            
        except Exception as e:
            error_msg = f"Error in {self.step_name}: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)