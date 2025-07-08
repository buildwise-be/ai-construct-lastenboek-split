"""
Migration Utilities

This module provides utilities to help users migrate from the old monolithic script
to the new modular architecture.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MigrationHelper:
    """Helper class for migrating from old monolithic script to new modular version."""
    
    def __init__(self, old_script_dir: str = ".", new_structure_dir: str = "src"):
        """
        Initialize migration helper.
        
        Args:
            old_script_dir: Directory containing the old monolithic script
            new_structure_dir: Directory containing the new modular structure
        """
        self.old_dir = Path(old_script_dir)
        self.new_dir = Path(new_structure_dir)
    
    def find_old_files(self) -> Dict[str, Path]:
        """Find old script files that need migration."""
        old_files = {}
        
        # Look for main script
        for name in ["main_script.py", "Lastenboekopdeler.py", "pdf_processor.py"]:
            file_path = self.old_dir / name
            if file_path.exists():
                old_files["main_script"] = file_path
                break
        
        # Look for category files
        for name in ["example_categories.py", "categories.py", "nonvmswhoofdstukken_pandas.py"]:
            file_path = self.old_dir / name
            if file_path.exists():
                old_files["categories"] = file_path
                break
        
        # Look for TOC generation
        toc_file = self.old_dir / "toc_generation.py"
        if toc_file.exists():
            old_files["toc_generation"] = toc_file
        
        # Look for requirements
        req_file = self.old_dir / "requirements.txt"
        if req_file.exists():
            old_files["requirements"] = req_file
        
        # Look for output directories
        output_dir = self.old_dir / "output"
        if output_dir.exists():
            old_files["output"] = output_dir
        
        return old_files
    
    def migrate_output_data(self, preserve_old: bool = True) -> Tuple[bool, List[str]]:
        """
        Migrate existing output data to new structure.
        
        Args:
            preserve_old: Whether to keep the old output directory
            
        Returns:
            Tuple of (success, list of migrated files)
        """
        old_files = self.find_old_files()
        migrated = []
        
        if "output" not in old_files:
            logger.info("No old output directory found")
            return True, []
        
        old_output = old_files["output"]
        new_output = Path("output")
        
        try:
            # Create new output directory if it doesn't exist
            new_output.mkdir(exist_ok=True)
            
            # Copy or move output files
            for item in old_output.iterdir():
                if item.is_file():
                    dest = new_output / item.name
                    if preserve_old:
                        shutil.copy2(item, dest)
                        logger.info(f"Copied {item} to {dest}")
                    else:
                        shutil.move(str(item), str(dest))
                        logger.info(f"Moved {item} to {dest}")
                    migrated.append(str(dest))
                elif item.is_dir():
                    dest = new_output / item.name
                    if preserve_old:
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                        logger.info(f"Copied directory {item} to {dest}")
                    else:
                        shutil.move(str(item), str(dest))
                        logger.info(f"Moved directory {item} to {dest}")
                    migrated.append(str(dest))
            
            return True, migrated
            
        except Exception as e:
            logger.error(f"Error migrating output data: {str(e)}")
            return False, []
    
    def backup_old_files(self) -> Tuple[bool, str]:
        """
        Create a backup of old files before migration.
        
        Returns:
            Tuple of (success, backup_directory)
        """
        old_files = self.find_old_files()
        
        if not old_files:
            logger.info("No old files found to backup")
            return True, ""
        
        # Create backup directory with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backup_old_files_{timestamp}")
        
        try:
            backup_dir.mkdir(exist_ok=True)
            
            for file_type, file_path in old_files.items():
                if file_path.is_file():
                    dest = backup_dir / file_path.name
                    shutil.copy2(file_path, dest)
                    logger.info(f"Backed up {file_path} to {dest}")
                elif file_path.is_dir():
                    dest = backup_dir / file_path.name
                    shutil.copytree(file_path, dest, dirs_exist_ok=True)
                    logger.info(f"Backed up directory {file_path} to {dest}")
            
            return True, str(backup_dir)
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return False, ""
    
    def create_migration_report(self) -> Dict:
        """Create a detailed migration report."""
        old_files = self.find_old_files()
        
        report = {
            "migration_date": str(Path.cwd()),
            "old_files_found": {},
            "new_structure_status": {},
            "recommendations": []
        }
        
        # Document old files
        for file_type, file_path in old_files.items():
            report["old_files_found"][file_type] = {
                "path": str(file_path),
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0
            }
        
        # Check new structure
        new_files = [
            "src/main.py",
            "src/config/settings.py", 
            "src/core/ai_client.py",
            "src/core/pdf_processor.py",
            "src/core/category_matcher.py",
            "src/gui/main_window.py",
            "src/models/categories.py"
        ]
        
        for file_path in new_files:
            full_path = Path(file_path)
            report["new_structure_status"][file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0
            }
        
        # Generate recommendations
        if old_files:
            report["recommendations"].append("Consider backing up old files before removing them")
            
        if "output" in old_files:
            report["recommendations"].append("Migrate existing output data to maintain processing history")
            
        if "categories" in old_files:
            report["recommendations"].append("Review custom categories for compatibility with new structure")
        
        report["recommendations"].append("Run validation script to ensure new setup is working")
        report["recommendations"].append("Test with a small PDF file before processing large documents")
        
        return report
    
    def suggest_cleanup(self) -> List[str]:
        """Suggest files that can be safely removed after migration."""
        old_files = self.find_old_files()
        cleanup_suggestions = []
        
        if "main_script" in old_files:
            cleanup_suggestions.append(f"Old main script: {old_files['main_script']}")
        
        if "toc_generation" in old_files:
            cleanup_suggestions.append(f"Old TOC script: {old_files['toc_generation']}")
        
        # Check for other potential old files
        old_patterns = [
            "*.pyc",
            "__pycache__/",
            "*.log",
            "test_*.py"
        ]
        
        for pattern in old_patterns:
            matches = list(self.old_dir.glob(pattern))
            for match in matches:
                cleanup_suggestions.append(f"Temporary file: {match}")
        
        return cleanup_suggestions


def run_migration_check() -> None:
    """Run a complete migration check and provide recommendations."""
    print("🔄 AI Construct PDF Opdeler - Migration Check")
    print("=" * 50)
    
    migration = MigrationHelper()
    
    # Find old files
    print("\n📂 Scanning for old files...")
    old_files = migration.find_old_files()
    
    if not old_files:
        print("  ✅ No old files found - looks like a clean installation!")
        return
    
    print(f"  Found {len(old_files)} old file(s):")
    for file_type, file_path in old_files.items():
        print(f"    📄 {file_type}: {file_path}")
    
    # Generate migration report
    print("\n📋 Generating migration report...")
    report = migration.create_migration_report()
    
    print("\n🎯 Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    # Suggest cleanup
    print("\n🧹 Cleanup suggestions:")
    cleanup_items = migration.suggest_cleanup()
    if cleanup_items:
        for item in cleanup_items:
            print(f"  🗑️  {item}")
    else:
        print("  ✅ No cleanup needed")
    
    print("\n" + "=" * 50)
    print("💡 To perform migration:")
    print("   1. Run backup: migration.backup_old_files()")
    print("   2. Migrate output: migration.migrate_output_data()")
    print("   3. Test new version: python src/main.py")
    print("   4. Clean up old files when satisfied")


if __name__ == "__main__":
    run_migration_check()