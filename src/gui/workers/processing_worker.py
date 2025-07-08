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
        """Execute the background task with comprehensive error handling."""
        try:
            logger.info("Starting background processing task")
            self.started.emit()
            
            # Validate inputs before processing
            if not self.task_func:
                raise ValueError("No task function provided")
            
            # Execute the task function with enhanced error handling
            try:
                self.results = self.task_func(*self.args, **self.kwargs)
            except KeyboardInterrupt:
                logger.info("Task interrupted by user")
                self._is_cancelled = True
                return
            except MemoryError as e:
                error_msg = f"Out of memory during processing: {str(e)}"
                logger.error(error_msg)
                self.error_message = error_msg
                self.error.emit(error_msg)
                return
            except FileNotFoundError as e:
                error_msg = f"Required file not found: {str(e)}"
                logger.error(error_msg)
                self.error_message = error_msg
                self.error.emit(error_msg)
                return
            except PermissionError as e:
                error_msg = f"Permission denied: {str(e)}"
                logger.error(error_msg)
                self.error_message = error_msg
                self.error.emit(error_msg)
                return
            except TimeoutError as e:
                error_msg = f"Processing timeout: {str(e)}"
                logger.error(error_msg)
                self.error_message = error_msg
                self.error.emit(error_msg)
                return
            except Exception as e:
                # Log the full exception details
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Task function failed with exception: {error_details}")
                raise  # Re-raise to be caught by outer handler
            
            if not self._is_cancelled:
                logger.info("Background processing task completed successfully")
                # Ensure we always emit a dictionary, even if results is None
                results_dict = self.results if isinstance(self.results, dict) else {}
                self.finished.emit(results_dict)
            
        except Exception as e:
            # Final catch-all error handler
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Critical error in background processing: {str(e)}"
            
            logger.error(f"{error_msg}\nFull traceback:\n{error_details}")
            
            self.error_message = error_msg
            
            # Ensure the error signal is emitted safely
            try:
                self.error.emit(error_msg)
            except Exception as emit_error:
                logger.error(f"Failed to emit error signal: {str(emit_error)}")
        
        finally:
            # Cleanup resources if needed
            try:
                self._cleanup_resources()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {str(cleanup_error)}")
    
    def _cleanup_resources(self):
        """Clean up any resources used by the worker."""
        # Clear large objects to free memory
        self.results = None
        self.args = None
        self.kwargs = None
        
        # Force garbage collection
        import gc
        gc.collect()
    
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
        from core.pdf_processor import step1_generate_toc
        
        super().__init__(step1_generate_toc, pdf_path, output_base_dir, project_id)
        self.step_name = "Stap 1: Inhoudstafel Generatie"
    
    def run(self):
        """Execute Step 1 with progress reporting."""
        try:
            self.emit_log(f"Starten {self.step_name}")
            self.emit_progress(0, "Inhoudstafel generatie initialiseren...")
            self.started.emit()
            
            self.emit_progress(10, "PDF bestand laden...")
            self.emit_log("PDF bestand laden en valideren")
            
            self.emit_progress(20, "AI model initialiseren...")
            self.emit_log("Verbinding maken met Vertex AI")
            
            self.emit_progress(30, "PDF verwerken in batches...")
            self.emit_log("Batch verwerking van PDF pagina's starten")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(90, "Resultaten opslaan...")
                self.emit_log("Inhoudstafel resultaten opslaan naar output directory")
                
                self.emit_progress(100, "Inhoudstafel generatie voltooid!")
                self.emit_log(f"{self.step_name} succesvol voltooid")
                
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
                 model = None, include_explanations: bool = True, 
                 document_type: Optional[str] = None):
        """
        Initialize Step 2 worker.
        
        Args:
            chapters: Chapters dictionary from Step 1
            toc_output_dir: Directory containing TOC results
            category_file: Path to category definitions file
            base_dir: Base output directory
            model: AI model instance
            include_explanations: Whether to include explanations
            document_type: User-specified document type ('vmsw' or 'non_vmsw')
        """
        # Import here to avoid circular imports
        from core.category_matcher import step2_match_categories
        
        super().__init__(step2_match_categories, chapters, toc_output_dir, 
                        category_file, base_dir, model, document_type=document_type)
        self.step_name = "Stap 2: Categorie Matching"
        self.include_explanations = include_explanations
        self.document_type = document_type
    
    def run(self):
        """Execute Step 2 with progress reporting."""
        try:
            self.emit_log(f"Starten {self.step_name}")
            self.emit_progress(0, "Categorie matching initialiseren...")
            self.started.emit()
            
            self.emit_progress(10, "Hoofdstuk data laden...")
            self.emit_log("Inhoudstafel data laden van Stap 1")
            
            self.emit_progress(20, "Categorie definities laden...")
            self.emit_log("Bouw categorie definities laden")
            
            self.emit_progress(30, "AI model initialiseren...")
            self.emit_log("AI model voorbereiden voor categorisering")
            
            self.emit_progress(40, "Items verwerken in batches...")
            self.emit_log("Batch verwerking starten voor categorie matching")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(85, "Statistieken berekenen...")
                self.emit_log("Categorie gebruik statistieken genereren")
                
                self.emit_progress(95, "Resultaten opslaan...")
                self.emit_log("Categorisering resultaten opslaan")
                
                self.emit_progress(100, "Categorie matching voltooid!")
                self.emit_log(f"{self.step_name} succesvol voltooid")
                
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
        from core.pdf_processor import step3_extract_category_pdfs
        
        super().__init__(step3_extract_category_pdfs, pdf_path, chapter_results,
                        section_results, category_match_dir, category_file,
                        second_output_dir, third_output_dir, base_dir)
        self.step_name = "Stap 3: PDF Extractie"
    
    def run(self):
        """Execute Step 3 with progress reporting."""
        try:
            self.emit_log(f"Starten {self.step_name}")
            self.emit_progress(0, "PDF extractie initialiseren...")
            self.started.emit()
            
            self.emit_progress(10, "Categorisering resultaten laden...")
            self.emit_log("Resultaten laden van Stap 2")
            
            self.emit_progress(20, "Bron PDF laden...")
            self.emit_log("Bron PDF openen voor extractie")
            
            self.emit_progress(30, "Inhoud organiseren per categorie...")
            self.emit_log("Hoofdstukken en secties toewijzen aan categorieën")
            
            self.emit_progress(50, "Categorie-specifieke PDF's aanmaken...")
            self.emit_log("Individuele categorie PDF's extraheren en aanmaken")
            
            # Execute the actual task
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.emit_progress(90, "Samenvatting genereren...")
                self.emit_log("Extractie samenvatting aanmaken")
                
                self.emit_progress(100, "PDF extractie voltooid!")
                self.emit_log(f"{self.step_name} succesvol voltooid")
                
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
                 project_id: Optional[str] = None,
                 model: Optional[str] = None,
                 document_type: Optional[str] = None):
        """
        Initialize complete pipeline worker.
        
        Args:
            pdf_path: Path to PDF file
            output_base_dir: Base output directory
            category_file: Path to category definitions file
            second_output_dir: Secondary output directory
            third_output_dir: Tertiary output directory
            project_id: Google Cloud project ID
            model: AI model name to use
            document_type: User-specified document type ('vmsw' or 'non_vmsw')
        """
        # Import here to avoid circular imports
        from core.pdf_processor import step1_generate_toc, step3_extract_category_pdfs
        from core.category_matcher import step2_match_categories
        
        self.step1_func = step1_generate_toc
        self.step2_func = step2_match_categories
        self.step3_func = step3_extract_category_pdfs
        
        super().__init__(self._run_complete_pipeline, pdf_path, output_base_dir,
                        category_file, second_output_dir, third_output_dir, project_id, 
                        model, document_type)
        self.step_name = "Volledige Pipeline"
    
    def _run_complete_pipeline(self, pdf_path: str, output_base_dir: Optional[str],
                              category_file: Optional[str], second_output_dir: Optional[str],
                              third_output_dir: Optional[str], project_id: Optional[str],
                              model: Optional[str] = None, document_type: Optional[str] = None):
        """Execute the complete pipeline."""
        
        # Step 1: TOC Generation
        self.emit_progress(5, "Stap 1: Inhoudstafel genereren...")
        self.emit_log("=== STAP 1: INHOUDSTAFEL GENEREREN ===")
        
        chapters, step1_output_dir = self.step1_func(pdf_path, output_base_dir, project_id)
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(35, "Stap 1 voltooid. Stap 2 starten...")
        self.emit_log("Stap 1 succesvol voltooid")
        
        # Step 2: Category Matching
        self.emit_progress(40, "Stap 2: Categorieën matchen...")
        self.emit_log("=== STAP 2: CATEGORIEËN MATCHEN ===")
        
        chapter_results, section_results, step2_output_dir = self.step2_func(
            chapters, None, category_file, output_base_dir, model, document_type=document_type
        )
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(70, "Stap 2 voltooid. Stap 3 starten...")
        self.emit_log("Stap 2 succesvol voltooid")
        
        # Step 3: PDF Extraction
        self.emit_progress(75, "Stap 3: PDF's extraheren...")
        self.emit_log("=== STAP 3: PDF'S EXTRAHEREN ===")
        
        category_counts, step3_output_dir = self.step3_func(
            pdf_path, chapter_results, section_results, step2_output_dir,
            category_file, second_output_dir, third_output_dir, output_base_dir
        )
        
        if self._is_cancelled:
            return None
        
        self.emit_progress(100, "Volledige pipeline voltooid!")
        self.emit_log("=== PIPELINE SUCCESVOL VOLTOOID ===")
        
        return {
            'step1': {'chapters': chapters, 'output_dir': step1_output_dir},
            'step2': {'chapter_results': chapter_results, 'section_results': section_results, 'output_dir': step2_output_dir},
            'step3': {'category_counts': category_counts, 'output_dir': step3_output_dir},
            'final_output_dir': step3_output_dir
        }
    
    def run(self):
        """Execute complete pipeline with progress reporting."""
        try:
            self.emit_log(f"Starten {self.step_name}")
            self.emit_progress(0, "Volledige pipeline initialiseren...")
            self.started.emit()
            
            # Execute the pipeline
            results = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled and results:
                self.emit_log("Volledige pipeline succesvol afgerond")
                self.finished.emit({
                    'results': results,
                    'step': 'complete'
                })
            
        except Exception as e:
            error_msg = f"Error in {self.step_name}: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)