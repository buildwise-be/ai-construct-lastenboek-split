#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Construct PDF Opdeler - Main Entry Point

This is the main entry point for the refactored PDF processing application.
The application has been restructured from a monolithic script into a clean,
modular architecture with responsive GUI and background processing.

Key improvements:
- Modular architecture for better maintainability
- Responsive GUI with background processing
- Clean separation of concerns
- Better error handling and logging
- Same functionality as the original but more robust

Usage:
    python src/main.py
"""

import sys
import logging
import os
from pathlib import Path
from datetime import datetime

# Add src directory to Python path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    print("Please install the required dependencies with:")
    print("pip install -r src/requirements.txt")
    sys.exit(1)

from gui.main_window import MainWindow
from config.settings import (
    APP_NAME, APP_VERSION, LOGGING_CONFIG, 
    validate_config, ASSETS_CONFIG
)

def setup_logging():
    """Setup application logging with both console and file output."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = logs_dir / f"pdf_processor_{timestamp}.log"
    
    # Setup logging with both console and file handlers
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_filename, encoding='utf-8')
        ]
    )
    
    # Also create a symlink to latest log file for easy access
    latest_log = logs_dir / "latest.log"
    try:
        if latest_log.exists():
            latest_log.unlink()
        # Create symlink (on Windows this requires admin rights, so use copy as fallback)
        try:
            latest_log.symlink_to(log_filename.name)
        except (OSError, NotImplementedError):
            # Fallback to copying the file path to a text file
            with open(latest_log, 'w') as f:
                f.write(str(log_filename))
    except Exception:
        pass  # Don't fail if we can't create the symlink
    
    # Set specific loggers to reduce noise
    logging.getLogger('vertexai').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    # Print log file location
    print(f"📝 Logs are being written to: {log_filename}")
    print(f"📝 Latest log shortcut: {latest_log}")
    
    return log_filename

def check_dependencies():
    """Check if all required dependencies are available."""
    required_imports = [
        ('pandas', 'pandas'),
        ('PyPDF2', 'PyPDF2'), 
        ('python-dotenv', 'dotenv'),
        ('google-cloud-aiplatform', 'google.cloud.aiplatform'),
        ('google-generativeai', 'google.generativeai'),
        ('PySide6', 'PySide6'),
        ('PyMuPDF', 'fitz')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_imports:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        return False, missing_packages
    
    return True, []

def setup_environment():
    """Setup environment variables and paths."""
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Add current directory to path for category file imports
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

def main():
    """Main application entry point."""
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    print("=" * 50)
    
    # Setup logging
    log_filename = setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        error_msg = f"Missing required packages: {', '.join(missing)}\n"
        error_msg += "Please install them with: pip install -r src/requirements.txt"
        print(f"ERROR: {error_msg}")
        
        # Try to show GUI error if possible
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Missing Dependencies", error_msg)
        except:
            pass
        
        sys.exit(1)
    
    # Validate configuration
    config_issues = validate_config()
    if config_issues:
        logger.warning("Configuration issues detected:")
        for issue in config_issues:
            logger.warning(f"  - {issue}")
        print("Warning: Some configuration issues detected (see log)")
    
    # Setup environment
    setup_environment()
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("AI Construct")
    
    # Set application icon if available
    icon_path = ASSETS_CONFIG.get("bw_logo_path")
    if icon_path and icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # High DPI settings (Qt 6.x enables high DPI scaling by default)
    # Note: Qt.AA_EnableHighDpiScaling and Qt.AA_UseHighDpiPixmaps are deprecated in Qt 6
    # and no longer needed as high DPI scaling is automatic
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        logger.info(f"{APP_NAME} started successfully")
        print(f"{APP_NAME} GUI launched successfully!")
        print("Check the application window for the interface.")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"ERROR: {error_msg}")
        
        # Show error dialog
        try:
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())