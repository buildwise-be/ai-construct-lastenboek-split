# AI Construct PDF Splitter - Developer Guide

This guide provides technical information for developers who want to understand, modify, or extend the AI Construct PDF Splitter application.

## Code Structure

### Main Components

1. **Main Script** (`main_script.py`): The central script containing the entire application logic and UI.

2. **Category Definitions** (`example_categories.py` and similar files): Define the categories used for document classification.

### Key Classes and Functions

#### UI Components
- `NonVMSWPipelineGUI`: Main application window class
- `StyledButton`: Custom styled button component
- `StyledFrame`: Custom styled frame component

#### PDF Processing
- `step1_generate_toc`: Extracts table of contents from PDFs
- `validate_chapters`: Validates extracted chapter structure
- `step3_extract_category_pdfs`: Splits PDF into category-specific documents

#### AI Integration
- `initialize_vertex_model`: Sets up connection to Google Vertex AI
- `initialize_gemini_model`: Configures the Gemini AI model
- `process_with_vertex_ai`: Handles communication with the AI model
- `match_to_multiple_categories`: Matches content to predefined categories
- `batch_match_to_multiple_categories`: Processes multiple items in batches for efficiency

#### Pipeline Coordination
- `run_complete_pipeline`: Orchestrates the entire processing sequence
- `setup_output_directory`: Creates and manages output directory structure

## Technical Architecture

### Design Patterns

The application is built using a combination of:
- **Model-View-Controller (MVC)** pattern: Separating data, UI, and control logic
- **Pipeline** pattern: Sequential processing of data through distinct stages
- **Command** pattern: For executing different pipeline stages independently

### Data Flow

1. **Input Phase**: 
   - PDF document is loaded
   - Category definitions are imported
   - Configuration parameters are set

2. **Processing Phase**:
   - Table of Contents extraction
   - Data transformation and structure validation
   - AI-based category matching
   - PDF splitting based on matched categories

3. **Output Phase**:
   - Creation of categorized PDF files
   - Generation of report files (JSON, CSV)

## Integration Points

### Google Cloud / Vertex AI

The application integrates with Google Cloud Vertex AI through:
- `vertexai` Python library for main AI operations
- `google.generativeai` module for additional AI capabilities

Key integration points:
```python
# Initialization
vertexai.init(
    project=PROJECT_ID,
    location="europe-west1",
    api_endpoint="europe-west1-aiplatform.googleapis.com"
)

# Model creation
model = GenerativeModel(
    "gemini-1.5-pro-002",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS,
    system_instruction=[system_instruction] if system_instruction else None
)

# Content processing
response = model.generate_content(prompt_parts)
```

### PDF Processing

PDF manipulation uses a combination of libraries:
- `PyPDF2` for basic operations and page extraction
- `fitz` (PyMuPDF) for advanced content analysis

## Extending the Application

### Adding New Features

1. **New processing step**: Create a new function following the pattern of existing step functions:
   ```python
   def step4_new_functionality(input_data, output_dir, ...):
       # Implementation
       return results
   ```

2. **UI integration**: Add corresponding UI elements to the `NonVMSWPipelineGUI` class:
   ```python
   # Add button
   self.new_feature_button = StyledButton("New Feature")
   self.new_feature_button.clicked.connect(self.run_new_feature)
   
   # Add handler
   def run_new_feature(self):
       # Implementation
   ```

### Modifying Category Matching

To adjust how the AI matches content to categories:

1. **Modify prompt templates**: Update the prompt used for AI matching in the `match_to_multiple_categories` function.

2. **Adjust category definitions**: Create a custom category file following the structure in `example_categories.py`.

3. **Fine-tune AI parameters**: Modify the `GENERATION_CONFIG` dictionary to adjust temperature, top_p, and other parameters.

### Custom Output Formats

To add new output formats:

1. Create a new export function:
   ```python
   def export_to_custom_format(results, output_path):
       # Convert results to desired format
       # Write to output_path
   ```

2. Integrate with the existing pipeline by adding calls to this function in the appropriate step function.

## Performance Optimization

### Processing Large Documents

For large documents, consider:

1. **Chunking**: Process the document in smaller chunks
   ```python
   # Example of processing in batches
   batch_size = 10
   for i in range(0, len(items), batch_size):
       batch = items[i:i+batch_size]
       process_batch(batch)
   ```

2. **Parallel processing**: Use Python's `concurrent.futures` or `multiprocessing` for certain operations
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = list(executor.map(process_item, items))
   ```

### Memory Management

For memory-intensive operations:
- Use `gc.collect()` to force garbage collection after large operations
- Consider using file-based intermediate storage rather than keeping everything in memory

## Troubleshooting Development Issues

### Debugging AI Responses

To debug AI model responses:
1. Enable verbose logging:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Add specific handlers for AI responses:
   ```python
   def debug_ai_response(response):
       logging.debug(f"Raw AI response: {response}")
       # Additional analysis
   ```

### Error Handling

The application includes robust error handling:
- Try-except blocks around critical operations
- Specific error handling for API communication issues
- UI feedback for user-facing errors

Add additional error handling for custom components:
```python
try:
    # Your code
except SpecificException as e:
    logging.error(f"Error in custom component: {str(e)}")
    # Recovery or user notification
```

## Testing

### Test Strategy

For testing new components, consider:

1. **Unit tests** for individual functions
2. **Integration tests** for interactions between components
3. **End-to-end tests** for complete pipeline operation

Example test approach for a new feature:
```python
import unittest

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        
    def test_feature_basic_operation(self):
        # Test basic functionality
        
    def test_feature_edge_cases(self):
        # Test edge cases
        
    def tearDown(self):
        # Clean up
```

## Deployment Considerations

When deploying modifications:

1. **Dependency management**: Update requirements.txt with any new dependencies
2. **Configuration**: Consider extracting more configuration parameters to environment variables
3. **Performance testing**: Test with realistic document sizes before production 