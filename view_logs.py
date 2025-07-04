#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Log Viewer for AI Construct PDF Opdeler

This script allows you to view application logs in real-time from outside the GUI.
You can use this to monitor processing while using the GUI or command-line tools.

Usage:
    python view_logs.py              # View latest log file
    python view_logs.py --follow     # Follow log file in real-time (like tail -f)
    python view_logs.py --list       # List all available log files
    python view_logs.py --file <filename>  # View specific log file
"""

import os
import sys
import time
import argparse
from pathlib import Path


def find_latest_log():
    """Find the most recent log file."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found. Run the application first to generate logs.")
        return None
    
    # Check for latest.log shortcut first
    latest_log = logs_dir / "latest.log"
    if latest_log.exists():
        try:
            # If it's a symlink, follow it
            if latest_log.is_symlink():
                return latest_log.resolve()
            else:
                # If it's a text file with the path, read it
                with open(latest_log, 'r') as f:
                    log_path = f.read().strip()
                    return Path(log_path)
        except Exception:
            pass
    
    # Fallback: find the most recent log file by timestamp
    log_files = list(logs_dir.glob("pdf_processor_*.log"))
    if not log_files:
        print("❌ No log files found.")
        return None
    
    # Sort by modification time and return the newest
    latest = max(log_files, key=lambda f: f.stat().st_mtime)
    return latest


def list_log_files():
    """List all available log files."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found.")
        return
    
    log_files = list(logs_dir.glob("pdf_processor_*.log"))
    if not log_files:
        print("❌ No log files found.")
        return
    
    print("📝 Available log files:")
    print("=" * 50)
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    for i, log_file in enumerate(log_files):
        size = log_file.stat().st_size
        mtime = time.ctime(log_file.stat().st_mtime)
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
        
        marker = "🟢 (latest)" if i == 0 else "  "
        print(f"{marker} {log_file.name}")
        print(f"     Created: {mtime}")
        print(f"     Size: {size_str}")
        print()


def view_log_file(log_file, follow=False, lines=50):
    """View log file content."""
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        return
    
    print(f"📖 Viewing: {log_file}")
    print(f"📝 Size: {log_file.stat().st_size:,} bytes")
    print("=" * 80)
    
    try:
        if follow:
            # Follow mode (like tail -f)
            print("🔄 Following log file (Ctrl+C to stop)...")
            print("=" * 80)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                # First, show the last N lines
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                f.seek(max(0, file_size - 8192))  # Read last 8KB
                lines_content = f.readlines()
                
                # Show last 'lines' lines
                for line in lines_content[-lines:]:
                    print(line.rstrip())
                
                # Now follow new content
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        time.sleep(0.1)
        else:
            # Normal view mode
            with open(log_file, 'r', encoding='utf-8') as f:
                if lines > 0:
                    # Show last N lines
                    content = f.readlines()
                    for line in content[-lines:]:
                        print(line.rstrip())
                else:
                    # Show entire file
                    print(f.read())
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopped following log file.")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="View AI Construct PDF Opdeler logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python view_logs.py                    # View last 50 lines of latest log
  python view_logs.py -f                 # Follow latest log in real-time
  python view_logs.py --lines 100        # View last 100 lines
  python view_logs.py --file mylog.log   # View specific log file
  python view_logs.py --list             # List all log files
        """
    )
    
    parser.add_argument('--follow', '-f', action='store_true',
                        help='Follow log file in real-time (like tail -f)')
    parser.add_argument('--lines', '-n', type=int, default=50,
                        help='Number of lines to show (default: 50, 0 = all)')
    parser.add_argument('--file', type=str,
                        help='Specific log file to view')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all available log files')
    
    args = parser.parse_args()
    
    if args.list:
        list_log_files()
        return
    
    if args.file:
        log_file = Path("logs") / args.file
    else:
        log_file = find_latest_log()
    
    if not log_file:
        return
    
    view_log_file(log_file, follow=args.follow, lines=args.lines)


if __name__ == "__main__":
    main() 