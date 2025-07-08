"""
File Utilities Module

This module handles file operations, directory setup, and path management.
Extracted from the monolithic main script to improve maintainability.
"""

import os
import shutil
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def setup_output_directory(step_name=None, base_output_dir=None):
    """
    Create a timestamped output directory for processing steps.
    
    Args:
        step_name (str, optional): Name of the processing step
        base_output_dir (str, optional): Base directory for output
        
    Returns:
        str: Path to the created output directory
    """
    # Use a generic script name since we're now modular
    script_name = "pdf_processor"
    base_output_path = base_output_dir if base_output_dir else "output"
    
    # Create base output directory if it doesn't exist
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path, exist_ok=True)
        logger.info(f"Created base output directory: {base_output_path}")
    
    # Create timestamped directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if step_name:
        output_dir = os.path.join(base_output_path, f"{script_name}_{step_name}_{timestamp}")
    else:
        output_dir = os.path.join(base_output_path, f"{script_name}_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    
    return output_dir


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        str: The directory path
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
    
    return directory_path


def copy_file(source_path, destination_path):
    """
    Copy a file from source to destination.
    
    Args:
        source_path (str): Source file path
        destination_path (str): Destination file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        shutil.copy2(source_path, destination_path)
        logger.info(f"Copied file from {source_path} to {destination_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy file from {source_path} to {destination_path}: {str(e)}")
        return False


def move_file(source_path, destination_path):
    """
    Move a file from source to destination.
    
    Args:
        source_path (str): Source file path
        destination_path (str): Destination file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        shutil.move(source_path, destination_path)
        logger.info(f"Moved file from {source_path} to {destination_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to move file from {source_path} to {destination_path}: {str(e)}")
        return False


def delete_file(file_path):
    """
    Delete a file if it exists.
    
    Args:
        file_path (str): Path to the file to delete
        
    Returns:
        bool: True if successful or file doesn't exist, False on error
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {str(e)}")
        return False


def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception as e:
        logger.error(f"Failed to get size of file {file_path}: {str(e)}")
        return 0


def is_valid_pdf(file_path):
    """
    Check if a file is a valid PDF by checking its extension and existence.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file exists and has .pdf extension
    """
    if not file_path:
        return False
    
    if not os.path.exists(file_path):
        logger.warning(f"PDF file does not exist: {file_path}")
        return False
    
    if not file_path.lower().endswith('.pdf'):
        logger.warning(f"File is not a PDF: {file_path}")
        return False
    
    return True


def find_files_with_extension(directory, extension):
    """
    Find all files with a specific extension in a directory.
    
    Args:
        directory (str): Directory to search in
        extension (str): File extension to search for (e.g., '.pdf', '.json')
        
    Returns:
        list: List of file paths with the specified extension
    """
    files = []
    try:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.lower().endswith(extension.lower()):
                    files.append(os.path.join(directory, filename))
        else:
            logger.warning(f"Directory does not exist: {directory}")
    except Exception as e:
        logger.error(f"Failed to list files in {directory}: {str(e)}")
    
    return files


def get_relative_path(file_path, base_path):
    """
    Get the relative path of a file with respect to a base path.
    
    Args:
        file_path (str): The file path
        base_path (str): The base path
        
    Returns:
        str: Relative path
    """
    try:
        return os.path.relpath(file_path, base_path)
    except Exception as e:
        logger.error(f"Failed to get relative path: {str(e)}")
        return file_path


def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace characters that are invalid in filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename