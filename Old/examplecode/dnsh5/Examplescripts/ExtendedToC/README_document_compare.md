# Document Comparison Tool

A comprehensive Python tool for comparing documents against a baseline template. Supports Word (.docx) and PDF formats with detailed difference reporting in multiple output formats.

## Features

- **Multi-format support**: Compare Word (.docx) and PDF documents
- **Comprehensive analysis**: Detects text differences, missing content, and additions
- **Multiple output formats**: HTML reports with highlights, structured JSON data, and CSV for analysis
- **Similarity scoring**: Quantifies overall document similarity
- **Modular design**: Clean, extensible architecture following best practices
- **CLI and programmatic usage**: Use as a command-line tool or import as a Python module
- **Robust error handling**: Graceful handling of parsing errors and edge cases

## Installation

1. **Clone or download the files**:
   ```bash
   # Files needed:
   # - document_compare.py
   # - requirements_document_compare.txt
   # - document_compare_config.json (optional)
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_document_compare.txt
   ```

## Quick Start

### Command Line Usage

```bash
# Basic comparison
python document_compare.py template.docx document.docx

# With output reports
python document_compare.py template.docx document.pdf --output-dir reports/

# With debug logging
python document_compare.py template.docx document.docx --log-level DEBUG
```

### Programmatic Usage

```python
from document_compare import DocumentComparisonTool

# Create comparison tool
tool = DocumentComparisonTool()

# Compare documents
result = tool.compare_documents(
    baseline_path="template.docx",
    comparison_path="document.docx", 
    output_dir="reports"
)

# Access results
print(f"Similarity: {result.similarity_ratio:.2%}")
print(f"Differences: {len(result.differences)}")
```

## Output Formats

### 1. HTML Report
Beautiful, interactive report with:
- Visual highlighting of differences
- Summary statistics
- Detailed breakdown of missing and added content
- Color-coded sections for easy review

### 2. JSON Report
Structured data format containing:
```json
{
  "baseline_file": "template.docx",
  "comparison_file": "document.docx",
  "similarity_ratio": 0.85,
  "differences": [...],
  "missing_content": [...],
  "added_content": [...],
  "timestamp": "2025-01-06T10:30:00"
}
```

### 3. CSV Report
Tabular format for analysis in Excel/pandas:
- Type (Summary, Difference, Missing, Added)
- Category (removed, added, baseline_only, etc.)
- Content text
- Source document

## Advanced Usage

### Batch Processing
```python
from pathlib import Path
from document_compare import DocumentComparisonTool

tool = DocumentComparisonTool()
baseline = "template.docx"

documents = ["doc1.docx", "doc2.pdf", "doc3.docx"]
results = []

for doc in documents:
    result = tool.compare_documents(baseline, doc, f"reports/{Path(doc).stem}")
    results.append({
        'document': doc,
        'similarity': result.similarity_ratio,
        'issues': len(result.missing_content)
    })

# Analyze batch results
avg_similarity = sum(r['similarity'] for r in results) / len(results)
print(f"Average similarity: {avg_similarity:.2%}")
```

### Custom Analysis
```python
# Detect critical missing content
critical_keywords = ['requirement', 'must', 'shall', 'mandatory']
critical_missing = [
    content for content in result.missing_content 
    if any(keyword in content.lower() for keyword in critical_keywords)
]

# Flag documents with low similarity
if result.similarity_ratio < 0.8:
    print("⚠️ Document significantly differs from template")

# Check for unexpected additions
if len(result.added_content) > 20:
    print("📝 Document contains substantial additional content")
```

## Configuration

The tool can be configured via `document_compare_config.json`:

```json
{
  "comparison_settings": {
    "ignore_case": false,
    "ignore_whitespace": false,
    "minimum_paragraph_length": 10,
    "similarity_threshold": 0.8
  },
  "output_settings": {
    "generate_html": true,
    "generate_json": true,
    "generate_csv": true,
    "output_directory": "comparison_reports"
  }
}
```

## Architecture

The tool follows best practices with a modular design:

- **DocumentParser**: Handles Word and PDF parsing
- **DocumentComparator**: Performs similarity analysis and difference detection  
- **ReportGenerator**: Creates output reports in multiple formats
- **DocumentComparisonTool**: Main orchestrator class

### Key Classes

```python
@dataclass
class DocumentContent:
    file_path: str
    file_type: str
    text_content: str
    paragraphs: List[str]
    word_count: int
    extraction_success: bool

@dataclass  
class ComparisonResult:
    baseline_file: str
    comparison_file: str
    similarity_ratio: float
    differences: List[Dict]
    missing_content: List[str]
    added_content: List[str]
```

## Error Handling

The tool provides robust error handling for:
- Missing files
- Unsupported file formats
- Corrupted documents
- Parsing failures
- Invalid configurations

Errors are logged and reported clearly without crashing the application.

## Performance Considerations

- **Large documents**: The tool handles large documents efficiently by processing in chunks
- **Memory usage**: Optimized to avoid loading entire documents into memory unnecessarily
- **PDF processing**: Uses `pdfplumber` for reliable text extraction from complex PDFs

## Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| Word   | .docx     | Full support including tables |
| PDF    | .pdf      | Text extraction, basic formatting |

*Note: Legacy .doc files are not supported. Convert to .docx first.*

## Examples

See `example_usage.py` for comprehensive usage examples including:
- Basic document comparison
- Batch processing multiple documents
- Custom analysis and reporting
- Error handling patterns

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements_document_compare.txt
   ```

2. **PDF parsing issues**: Some PDFs may have text extraction limitations
   - Try converting PDF to Word format first
   - Check if PDF contains text or just images

3. **Large file processing**: For very large documents, consider:
   - Increasing system memory
   - Processing documents in sections
   - Using the streaming options if available

### Logging

Enable debug logging for troubleshooting:
```bash
python document_compare.py template.docx document.docx --log-level DEBUG
```

## Contributing

The tool is designed for extensibility. To add new features:

1. **New file formats**: Extend the `DocumentParser` class
2. **New comparison algorithms**: Modify the `DocumentComparator` class  
3. **New output formats**: Add methods to the `ReportGenerator` class

## Dependencies

- `python-docx`: Word document parsing
- `pdfplumber`: PDF text extraction
- `jinja2`: HTML template rendering
- `pandas`: Structured data handling
- `difflib`: Text comparison algorithms (built-in)

## License

This tool is provided as-is for document comparison and analysis purposes.

---

For more examples and advanced usage, see the included `example_usage.py` file. 