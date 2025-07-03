#!/usr/bin/env python3
"""
Example usage of the Document Comparison Tool

This script demonstrates various ways to use the document comparison tool.
"""

from pathlib import Path
from document_compare import DocumentComparisonTool

def example_basic_comparison():
    """Basic document comparison example."""
    print("Example 1: Basic document comparison")
    print("-" * 40)
    
    # Create the comparison tool
    tool = DocumentComparisonTool(log_level='INFO')
    
    # Example file paths (replace with your actual files)
    baseline_path = "template.docx"  # Your baseline template
    comparison_path = "document_to_compare.docx"  # Document to compare
    output_dir = "comparison_reports"
    
    try:
        # Perform comparison
        result = tool.compare_documents(
            baseline_path, 
            comparison_path, 
            output_dir
        )
        
        # Print results
        print(f"Similarity: {result.similarity_ratio:.2%}")
        print(f"Differences found: {len(result.differences)}")
        print(f"Missing content: {len(result.missing_content)} items")
        print(f"Added content: {len(result.added_content)} items")
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        print("Please ensure your template and comparison files exist.")
    except Exception as e:
        print(f"Error: {e}")


def example_batch_comparison():
    """Example of comparing multiple documents against a baseline."""
    print("\nExample 2: Batch comparison")
    print("-" * 40)
    
    tool = DocumentComparisonTool(log_level='INFO')
    baseline_path = "template.docx"
    
    # List of documents to compare
    documents_to_compare = [
        "document1.docx",
        "document2.pdf", 
        "document3.docx"
    ]
    
    results = []
    
    for doc_path in documents_to_compare:
        if Path(doc_path).exists():
            try:
                result = tool.compare_documents(
                    baseline_path,
                    doc_path,
                    f"reports/{Path(doc_path).stem}"
                )
                results.append({
                    'document': doc_path,
                    'similarity': result.similarity_ratio,
                    'differences': len(result.differences)
                })
                print(f"{doc_path}: {result.similarity_ratio:.2%} similarity")
            except Exception as e:
                print(f"Error processing {doc_path}: {e}")
        else:
            print(f"File not found: {doc_path}")
    
    # Summary
    if results:
        avg_similarity = sum(r['similarity'] for r in results) / len(results)
        print(f"\nAverage similarity: {avg_similarity:.2%}")


def example_programmatic_usage():
    """Example of using the tool programmatically with custom analysis."""
    print("\nExample 3: Programmatic usage with custom analysis")
    print("-" * 50)
    
    tool = DocumentComparisonTool(log_level='WARNING')  # Less verbose
    
    baseline_path = "template.docx"
    comparison_path = "document_to_compare.docx"
    
    try:
        # Don't generate reports automatically
        result = tool.compare_documents(baseline_path, comparison_path)
        
        # Custom analysis
        if result.similarity_ratio < 0.7:
            print("⚠️  Low similarity detected - significant differences found")
        elif result.similarity_ratio < 0.9:
            print("⚡ Moderate differences found")
        else:
            print("✅ Documents are very similar")
        
        # Analyze specific types of content
        critical_missing = [
            content for content in result.missing_content 
            if any(keyword in content.lower() for keyword in ['requirement', 'must', 'shall'])
        ]
        
        if critical_missing:
            print(f"🚨 Critical missing content ({len(critical_missing)} items):")
            for item in critical_missing[:3]:  # Show first 3
                print(f"  - {item[:100]}...")
        
        # Check for unexpected additions
        if len(result.added_content) > 10:
            print(f"📝 Significant content additions: {len(result.added_content)} items")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Document Comparison Tool - Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_comparison()
    example_batch_comparison()
    example_programmatic_usage()
    
    print("\n" + "=" * 50)
    print("Note: Make sure to replace the example file paths with your actual files!")
    print("Install requirements with: pip install -r requirements_document_compare.txt") 