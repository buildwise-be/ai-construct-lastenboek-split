#llama_parse_script.py Run this was llama_parse_script.py --gui to run with a GUI
import os
import sys
import argparse
import logging
from llama_cloud_services import LlamaParse
# Add tkinter imports for file dialog
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json

# Default PDF path (set to empty string or a sample path)
DEFAULT_PDF_PATH = r"C:\Users\gr\Documents\GitHub\ExtendedToC\Lastenboeken\cathlabarchitectlb.pdf"

# Configure logging with pipeline_step support
def setup_logging():
    """Set up logging configuration compatible with pipeline orchestrator"""
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        # Only set pipeline_step if it doesn't already exist to avoid KeyError
        if not hasattr(record, 'pipeline_step'):
            record.pipeline_step = 'LLAMA_PARSE'
        return record
    logging.setLogRecordFactory(record_factory)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(pipeline_step)s - %(message)s'
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

def get_unique_filename(base_filename):
    """Return a unique filename by appending _1, _2, etc. before the extension if needed."""
    base, ext = os.path.splitext(base_filename)
    candidate = base_filename
    idx = 1
    while os.path.exists(candidate):
        candidate = f"{base}_{idx}{ext}"
        idx += 1
    return candidate

def run_parse(pdf_path, output_file, log_callback=None, called_by_orchestrator=False):
    if log_callback:
        log_callback(f"Script started. PDF: {pdf_path}, Output base: {output_file}")
    else:
        logger.info(f"Script started. PDF: {pdf_path}, Output base: {output_file}")

    if not pdf_path or not os.path.isfile(pdf_path):
        msg = f"Error: PDF file not found at {pdf_path}"
        if log_callback:
            log_callback(msg)
        logger.error(msg)
        return None

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY", "llx-RMVbTZDlwct4eW6U7Mcm7nLolpS2t67rTMpGZNGBjSLOnNJd")
    if not api_key:
        msg = "LLAMA_CLOUD_API_KEY not found or not set."
        if log_callback:
            log_callback(msg)
        logger.error(msg)
        return None
    else:
        if not called_by_orchestrator:
            logger.info("LLAMA_CLOUD_API_KEY found.")
        if log_callback:
            log_callback("LLAMA_CLOUD_API_KEY found.")

    try:
        parser = LlamaParse(
            api_key=api_key,
            verbose=True,
            language="nl",  # Change if needed
        )
        logger.info(f"Parsing {pdf_path} ...")
        if log_callback:
            log_callback(f"Parsing {pdf_path} ...")
        result = parser.parse(pdf_path)
        markdown_documents = result.get_markdown_documents(split_by_page=False)
        markdown_text = "\n\n".join(doc.text for doc in markdown_documents)

        if called_by_orchestrator:
            md_output_path = output_file + ".md"
            json_output_path = output_file + ".json"
        else:
            md_output_path = get_unique_filename(output_file)
            json_output_path = get_unique_filename(os.path.splitext(md_output_path)[0] + ".json")

        with open(md_output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        logger.info(f"Markdown output written to {md_output_path}")

        with open(json_output_path, "w", encoding="utf-8") as f:
            try:
                json_str = result.model_dump_json(indent=2)
                f.write(json_str)
            except AttributeError:
                json.dump(result.json(), f, ensure_ascii=False, indent=2)
        logger.info(f"JSON output written to {json_output_path}")
        if log_callback:
            log_callback(f"Markdown output written to {md_output_path}")
            log_callback(f"JSON output written to {json_output_path}")
        return json_output_path
    except Exception as e:
        msg = f"Exception during parsing: {e}"
        logger.error(msg)
        if log_callback:
            log_callback(msg)
        return None

def launch_gui():
    root = tk.Tk()
    root.title("LlamaParse PDF to Markdown")
    root.geometry("600x400")

    def log_to_gui(msg):
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    def browse_pdf():
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf_entry.delete(0, tk.END)
            pdf_entry.insert(0, file_path)

    def browse_output():
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")])
        if file_path:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, file_path)

    def run():
        pdf_path = pdf_entry.get()
        output_file = output_entry.get()
        log_text.config(state=tk.NORMAL)
        log_text.delete(1.0, tk.END)
        log_text.config(state=tk.DISABLED)
        success = run_parse(pdf_path, output_file, log_callback=log_to_gui)
        if success:
            messagebox.showinfo("Done", f"Markdown output written to {output_file}")
        else:
            messagebox.showerror("Error", "Parsing failed. See log for details.")

    tk.Label(root, text="PDF File:").pack(anchor=tk.W, padx=10, pady=(10,0))
    pdf_frame = tk.Frame(root)
    pdf_frame.pack(fill=tk.X, padx=10)
    pdf_entry = tk.Entry(pdf_frame, width=60)
    pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    pdf_entry.insert(0, DEFAULT_PDF_PATH)
    tk.Button(pdf_frame, text="Browse", command=browse_pdf).pack(side=tk.LEFT, padx=5)

    tk.Label(root, text="Output Markdown File:").pack(anchor=tk.W, padx=10, pady=(10,0))
    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.X, padx=10)
    output_entry = tk.Entry(output_frame, width=60)
    output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    output_entry.insert(0, "output.md")
    tk.Button(output_frame, text="Browse", command=browse_output).pack(side=tk.LEFT, padx=5)

    tk.Button(root, text="Run Parse", command=run).pack(pady=10)

    log_text = scrolledtext.ScrolledText(root, height=12, state=tk.DISABLED)
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Parse a PDF using LlamaParse API and output markdown.")
    parser.add_argument("pdf_path", nargs="?", default=DEFAULT_PDF_PATH, help="Path to the PDF file to parse.")
    parser.add_argument("-o", "--output", default="output.md", help="Output markdown file.")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode.")
    args = parser.parse_args()

    if args.gui:
        launch_gui()
    else:
        logger.info("Starting in CLI mode.")
        json_path = run_parse(args.pdf_path, args.output)
        if json_path:
            logger.info(f"CLI run successful. Markdown at {args.output}, JSON at {json_path}")
        else:
            logger.error(f"CLI run failed for PDF: {args.pdf_path}")

if __name__ == "__main__":
    main()