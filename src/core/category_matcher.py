"""
Category Matcher Module

This module handles category matching for chapters and sections using AI.
Extracted from the monolithic main script to improve maintainability.
"""

import os
import json
import logging
import time
import pandas as pd
from typing import Dict, Any, Optional, List

from .ai_client import get_global_client
from .file_utils import setup_output_directory

# Configure logging
logger = logging.getLogger(__name__)


class CategoryMatcher:
    """
    Handles category matching for chapters and sections using AI.
    """
    
    def __init__(self):
        """Initialize the category matcher."""
        self.ai_client = get_global_client()
    
    def match_categories(self, chapters=None, toc_output_dir=None, category_file=None, 
                        base_dir=None, model=None, include_explanations=True):
        """
        Match chapters and sections to categories using AI.
        
        Args:
            chapters (dict, optional): Chapters dictionary from TOC generation
            toc_output_dir (str, optional): Directory containing TOC results
            category_file (str): Path to category definitions file
            base_dir (str, optional): Base output directory
            model: AI model instance (optional)
            include_explanations (bool): Whether to include explanations in results
            
        Returns:
            tuple: (chapter_results, section_results, output_dir)
        """
        logger.info("=" * 50)
        logger.info("STEP 2: Matching Categories...")
        logger.info("=" * 50)
        
        # Setup output directory
        output_dir = setup_output_directory("step2_category_matching", base_dir)
        logger.info(f"Output directory: {output_dir}")
        
        # Load chapters data if not provided
        if chapters is None:
            if toc_output_dir:
                chapters_file = os.path.join(toc_output_dir, "chapters.json")
                if os.path.exists(chapters_file):
                    with open(chapters_file, 'r', encoding='utf-8') as f:
                        chapters = json.load(f)
                    logger.info(f"Loaded chapters from {chapters_file}")
                else:
                    raise FileNotFoundError(f"Chapters file not found: {chapters_file}")
            else:
                raise ValueError("Either chapters data or toc_output_dir must be provided")
        
        # Load category definitions
        df = self._load_category_definitions(category_file)
        
        # Initialize model if not provided or if model is a string (model name)
        if model is None:
            model = self.ai_client.create_model()
        elif isinstance(model, str):
            # Model name provided, create model with that name
            model = self.ai_client.create_model(model_name=model)
        
        # Collect all items to process
        all_items = self._collect_items_for_processing(chapters)
        logger.info(f"Found {len(all_items)} items to process")
        
        # Process items in batches
        results = self._process_items_in_batches(model, all_items, df, include_explanations)
        
        # Separate results by type
        chapter_results = {item_id: result for item_id, result in results.items() if result.get('type') == 'chapter'}
        section_results = {item_id: result for item_id, result in results.items() if result.get('type') == 'section'}
        
        # Save results
        self._save_results(output_dir, chapter_results, section_results, df)
        
        logger.info(f"Processed {len(chapter_results)} chapters and {len(section_results)} sections")
        
        return chapter_results, section_results, output_dir
    
    def _load_category_definitions(self, category_file):
        """
        Load category definitions from file.
        
        Args:
            category_file (str): Path to category definitions file
            
        Returns:
            pandas.DataFrame: Category definitions
        """
        try:
            import sys
            import importlib.util
            from pathlib import Path
            
            # Validate category file path
            if not category_file:
                raise ValueError("Category file path is empty or None")
                
            category_path = Path(category_file)
            if not category_path.exists():
                raise FileNotFoundError(f"Category file not found: {category_file}")
            
            if not category_path.is_file():
                raise ValueError(f"Category file path is not a file: {category_file}")
            
            logger.info(f"Loading category definitions from: {category_file}")
            
            spec = importlib.util.spec_from_file_location("categories", str(category_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create module spec from {category_file}")
            
            categories_module = importlib.util.module_from_spec(spec)
            sys.modules["categories"] = categories_module
            spec.loader.exec_module(categories_module)
            
            # Validate that the module has the required df attribute
            if not hasattr(categories_module, 'df'):
                raise AttributeError(f"Category file {category_file} does not contain required 'df' attribute")
            
            df = categories_module.df
            
            # Validate that df is a pandas DataFrame with data
            import pandas as pd
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Category file 'df' is not a pandas DataFrame: {type(df)}")
            
            if df.empty:
                raise ValueError(f"Category file contains empty DataFrame")
            
            logger.info(f"Successfully loaded {len(df)} categories from {category_file}")
            return df
            
        except Exception as e:
            error_msg = f"Error loading category file '{category_file}': {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _collect_items_for_processing(self, chapters):
        """
        Collect all chapters and sections for processing.
        
        Args:
            chapters (dict): Chapters dictionary
            
        Returns:
            list: List of items to process
        """
        all_items = []
        
        # Process chapters
        for chapter_id, chapter_data in chapters.items():
            if isinstance(chapter_data, dict):
                item = {
                    'id': chapter_id,
                    'type': 'chapter',
                    'title': chapter_data.get('title', f'Chapter {chapter_id}'),
                    'start_page': chapter_data.get('start', 1),
                    'end_page': chapter_data.get('end', 1),
                    'content': chapter_data.get('content', ''),
                    'raw_data': chapter_data
                }
                all_items.append(item)
                
                # Process sections within the chapter
                if 'sections' in chapter_data and isinstance(chapter_data['sections'], dict):
                    for section_id, section_data in chapter_data['sections'].items():
                        if isinstance(section_data, dict):
                            section_item = {
                                'id': section_id,
                                'type': 'section',
                                'title': section_data.get('title', f'Section {section_id}'),
                                'start_page': section_data.get('start', 1),
                                'end_page': section_data.get('end', 1),
                                'content': section_data.get('content', ''),
                                'parent_chapter': chapter_id,
                                'raw_data': section_data
                            }
                            all_items.append(section_item)
        
        return all_items
    
    def _process_items_in_batches(self, model, all_items, df, include_explanations):
        """
        Process items in batches for efficiency.
        
        Args:
            model: AI model instance
            all_items (list): List of items to process
            df (pandas.DataFrame): Category definitions
            include_explanations (bool): Whether to include explanations
            
        Returns:
            dict: Processing results
        """
        batch_size = 10  # Process 10 items at a time for optimal performance
        results = {}
        
        for i in range(0, len(all_items), batch_size):
            batch = all_items[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, len(all_items))
            
            logger.info(f"Processing batch {batch_start}-{batch_end} of {len(all_items)}")
            
            try:
                # Add rate limiting between batches
                if i > 0:
                    time.sleep(2)  # 2 second delay between batches
                
                # Process the batch with retry logic
                batch_results = self._batch_match_to_multiple_categories(model, batch, df, include_explanations, max_retries=3)
                
                # Merge results
                for item_id, result in batch_results.items():
                    results[item_id] = result
                
                logger.info(f"Successfully processed batch {batch_start}-{batch_end}")
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_start}-{batch_end}: {str(e)}")
                
                # Fall back to individual processing for this batch
                logger.info("Falling back to individual item processing...")
                for item in batch:
                    try:
                        time.sleep(1)  # Rate limiting for individual requests
                        individual_result = self._match_single_item(model, item, df, include_explanations, max_retries=3)
                        results[item['id']] = individual_result
                        logger.info(f"Successfully processed individual item: {item['id']}")
                    except Exception as individual_error:
                        logger.error(f"Error processing individual item {item['id']}: {str(individual_error)}")
                        # Create a fallback result
                        results[item['id']] = {
                            'categories': ['99. Overige'],
                            'explanation': 'Failed to process automatically',
                            'confidence': 0.0,
                            'type': item['type'],
                            'title': item['title'],
                            'start_page': item['start_page'],
                            'end_page': item['end_page']
                        }
        
        return results
    
    def _batch_match_to_multiple_categories(self, model, items_batch, df, include_explanations=True, max_retries=3):
        """
        Process a batch of items for category matching with retry logic.
        
        Args:
            model: AI model instance
            items_batch (list): Batch of items to process
            df (pandas.DataFrame): Category definitions
            include_explanations (bool): Whether to include explanations
            max_retries (int): Maximum number of retries for invalid responses
            
        Returns:
            dict: Batch processing results
        """
        # Create the prompt for batch processing
        categories_list = []
        for index, row in df.iterrows():
            categories_list.append(f"{row['summary']}: {row['description']}")
        
        categories_text = "\n".join(categories_list)
        
        # Create batch items description
        items_description = []
        for item in items_batch:
            item_desc = f"ID: {item['id']}\nType: {item['type']}\nTitle: {item['title']}"
            if item['content']:
                item_desc += f"\nContent: {item['content'][:500]}..."  # Limit content length
            items_description.append(item_desc)
        
        items_text = "\n\n---\n\n".join(items_description)
        
        # Build the prompt
        explanation_instruction = """
        For each item, also provide a brief explanation (1-2 sentences) of why you assigned these categories.
        """ if include_explanations else "Do not include explanations in your response."
        
        prompt = f"""
        You are a construction categorization expert. I have {len(items_batch)} construction document items that need to be categorized.
        
        DEMOLITION/REMOVAL WORK RULE:
        - For REMOVAL/DEMOLITION work (keywords: "verwijderen", "slopen", "uitbreken", "opbreken", "demonteren", "afbreken"):
          * ALWAYS include "01. Afbraak en Grondwerken" as PRIMARY category
          * ALSO include relevant trade category as SECONDARY (e.g., "12. Sanitair" for plumbing removal)
        
        This ensures both demolition contractors and trade contractors see relevant work.
        
        Available categories:
        {categories_text}
        
        Items to categorize:
        {items_text}
        
        For each item, assign the most relevant categories (you can assign multiple categories if appropriate).
        Focus on the main construction activities, materials, or specialties involved.
        
        {explanation_instruction}
        
        Respond with a Python dictionary where each key is the item ID and the value contains:
        - 'categories': list of assigned category names (exactly as they appear in the available categories)
        - 'explanation': brief explanation (if requested)
        - 'confidence': confidence score from 0.0 to 1.0
        
        ```python
        results = {{
            "item_id_1": {{
                "categories": ["01. Afbraak en Grondwerken", "03. Ruwbouw en Betonwerken"],
                "explanation": "Brief explanation here" if include_explanations else "",
                "confidence": 0.85
            }},
            "item_id_2": {{
                "categories": ["05. Buitenschrijnwerk"],
                "explanation": "Brief explanation here" if include_explanations else "",
                "confidence": 0.92
            }}
        }}
        ```
        """
        
        # Retry logic for batch processing
        for attempt in range(max_retries):
            try:
                # Add format emphasis on retries
                if attempt > 0:
                    logger.info(f"Batch retry attempt {attempt + 1}/{max_retries}")
                    # Add extra emphasis on format for retries
                    retry_emphasis = f"\n\nIMPORTANT: This is retry attempt {attempt + 1}. Please ensure your response is exactly in the specified Python dictionary format."
                    modified_prompt = prompt + retry_emphasis
                else:
                    modified_prompt = prompt
                
                response = self.ai_client.process_with_retry(model, modified_prompt, post_process=True)
                
                if isinstance(response, dict):
                    # Validate that response contains expected item IDs
                    expected_ids = {item['id'] for item in items_batch}
                    response_ids = set(response.keys())
                    
                    if expected_ids.issubset(response_ids):
                        # Add metadata to each result
                        for item in items_batch:
                            if item['id'] in response:
                                response[item['id']]['type'] = item['type']
                                response[item['id']]['title'] = item['title']
                                response[item['id']]['start_page'] = item['start_page']
                                response[item['id']]['end_page'] = item['end_page']
                        
                        if attempt > 0:
                            logger.info(f"Batch processing succeeded on retry attempt {attempt + 1}")
                        return response
                    else:
                        missing_ids = expected_ids - response_ids
                        logger.warning(f"Response missing {len(missing_ids)} expected IDs: {list(missing_ids)[:5]}...")
                        if attempt == max_retries - 1:
                            raise ValueError(f"Response missing expected item IDs after {max_retries} attempts")
                        continue
                else:
                    logger.warning(f"AI response was not a dictionary (attempt {attempt + 1}/{max_retries})")
                    logger.warning(f"Response type: {type(response)}")
                    logger.warning(f"Response content (first 500 chars): {str(response)[:500]}")
                    if attempt == max_retries - 1:
                        raise ValueError("Invalid response format after all retries")
                    continue
                
            except Exception as e:
                logger.error(f"Error in batch processing attempt {attempt + 1}/{max_retries}: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Exception details: {repr(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Batch processing failed after {max_retries} attempts")
                    raise
                else:
                    # Wait a bit before retrying
                    time.sleep(1 * (attempt + 1))  # Progressive delay
    
    def _match_single_item(self, model, item, df, include_explanations=True, max_retries=3):
        """
        Match a single item to categories with retry logic.
        
        Args:
            model: AI model instance
            item (dict): Item to process
            df (pandas.DataFrame): Category definitions
            include_explanations (bool): Whether to include explanations
            max_retries (int): Maximum number of retries for invalid responses
            
        Returns:
            dict: Matching result
        """
        # Create categories list for the prompt
        categories_list = []
        for index, row in df.iterrows():
            categories_list.append(f"{row['summary']}: {row['description']}")
        
        categories_text = "\n".join(categories_list)
        
        # Build content description
        content_desc = f"Title: {item['title']}"
        if item['content']:
            content_desc += f"\nContent: {item['content'][:1000]}"  # Limit content length
        
        # Build the prompt
        explanation_instruction = """
        Also provide a brief explanation (1-2 sentences) of why you assigned these categories.
        """ if include_explanations else "Do not include an explanation in your response."
        
        prompt = f"""
        You are a construction categorization expert. Please categorize this construction document {item['type']}:
        
        DEMOLITION/REMOVAL WORK RULE:
        - For REMOVAL/DEMOLITION work (keywords: "verwijderen", "slopen", "uitbreken", "opbreken", "demonteren", "afbreken"):
          * ALWAYS include "01. Afbraak en Grondwerken" as PRIMARY category
          * ALSO include relevant trade category as SECONDARY (e.g., "12. Sanitair" for plumbing removal)
        
        This ensures both demolition contractors and trade contractors see relevant work.
        
        {content_desc}
        
        Available categories:
        {categories_text}
        
        Assign the most relevant categories (you can assign multiple categories if appropriate).
        Focus on the main construction activities, materials, or specialties involved.
        
        {explanation_instruction}
        
        Respond with a Python dictionary:
        ```python
        result = {{
            "categories": ["category names exactly as they appear above"],
            "explanation": "brief explanation here" if include_explanations else "",
            "confidence": 0.85  # confidence score from 0.0 to 1.0
        }}
        ```
        """
        
        # Retry logic for single item processing
        for attempt in range(max_retries):
            try:
                # Add format emphasis on retries
                if attempt > 0:
                    logger.info(f"Single item retry attempt {attempt + 1}/{max_retries} for item {item['id']}")
                    # Add extra emphasis on format for retries
                    retry_emphasis = f"\n\nIMPORTANT: This is retry attempt {attempt + 1}. Please ensure your response is exactly in the specified Python dictionary format with 'categories' key."
                    modified_prompt = prompt + retry_emphasis
                else:
                    modified_prompt = prompt
                
                response = self.ai_client.process_with_retry(model, modified_prompt, post_process=True)
                
                if isinstance(response, dict) and 'categories' in response:
                    # Validate that categories is a list
                    if isinstance(response.get('categories'), list) and len(response['categories']) > 0:
                        # Add metadata
                        response['type'] = item['type']
                        response['title'] = item['title']
                        response['start_page'] = item['start_page']
                        response['end_page'] = item['end_page']
                        
                        if attempt > 0:
                            logger.info(f"Single item processing succeeded on retry attempt {attempt + 1} for item {item['id']}")
                        return response
                    else:
                        logger.warning(f"Invalid categories format in response for item {item['id']} (attempt {attempt + 1}/{max_retries})")
                        logger.warning(f"Categories value: {response.get('categories')}")
                        if attempt == max_retries - 1:
                            break
                        continue
                else:
                    logger.warning(f"Invalid response for item {item['id']} (attempt {attempt + 1}/{max_retries})")
                    logger.warning(f"Response type: {type(response)}")
                    logger.warning(f"Response is dict: {isinstance(response, dict)}")
                    if isinstance(response, dict):
                        logger.warning(f"Response keys: {list(response.keys())}")
                        logger.warning(f"Has 'categories' key: {'categories' in response}")
                    logger.warning(f"Response content (first 500 chars): {str(response)[:500]}")
                    if attempt == max_retries - 1:
                        break
                    continue
                    
            except Exception as e:
                logger.error(f"Error matching single item {item['id']} attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Single item processing failed after {max_retries} attempts for item {item['id']}")
                    raise
                else:
                    # Wait a bit before retrying
                    time.sleep(1 * (attempt + 1))  # Progressive delay
        
        # If we get here, all retries failed - return fallback
        logger.warning(f"Using fallback for item {item['id']} after {max_retries} failed attempts")
        return {
            'categories': ['99. Overige'],
            'explanation': 'Unable to categorize automatically after retries',
            'confidence': 0.0,
            'type': item['type'],
            'title': item['title'],
            'start_page': item['start_page'],
            'end_page': item['end_page']
        }
    
    def _save_results(self, output_dir, chapter_results, section_results, df):
        """
        Save processing results to files.
        
        Args:
            output_dir (str): Output directory
            chapter_results (dict): Chapter results
            section_results (dict): Section results
            df (pandas.DataFrame): Category definitions
        """
        # Save chapter results
        chapters_file = os.path.join(output_dir, "chapter_results.json")
        with open(chapters_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved chapter results to {chapters_file}")
        
        # Save section results
        sections_file = os.path.join(output_dir, "section_results.json")
        with open(sections_file, 'w', encoding='utf-8') as f:
            json.dump(section_results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved section results to {sections_file}")
        
        # Generate and save statistics
        stats = self._calculate_category_statistics(chapter_results, section_results, df)
        stats_file = os.path.join(output_dir, "category_statistics.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved statistics to {stats_file}")
    
    def _calculate_category_statistics(self, chapter_results, section_results, df):
        """
        Calculate statistics about category assignments.
        
        Args:
            chapter_results (dict): Chapter results
            section_results (dict): Section results
            df (pandas.DataFrame): Category definitions
            
        Returns:
            dict: Statistics dictionary
        """
        category_counts = {}
        total_items = 0
        
        # Count category assignments
        all_results = {**chapter_results, **section_results}
        
        for item_id, result in all_results.items():
            total_items += 1
            categories = result.get('categories', [])
            
            for category in categories:
                if category not in category_counts:
                    category_counts[category] = {
                        'count': 0,
                        'chapters': 0,
                        'sections': 0,
                        'items': []
                    }
                
                category_counts[category]['count'] += 1
                category_counts[category]['items'].append({
                    'id': item_id,
                    'type': result.get('type', 'unknown'),
                    'title': result.get('title', '')
                })
                
                if result.get('type') == 'chapter':
                    category_counts[category]['chapters'] += 1
                elif result.get('type') == 'section':
                    category_counts[category]['sections'] += 1
        
        # Calculate percentages
        for category in category_counts:
            if total_items > 0:
                category_counts[category]['percentage'] = (category_counts[category]['count'] / total_items) * 100
            else:
                category_counts[category]['percentage'] = 0.0
        
        # Overall statistics
        stats = {
            'total_items': total_items,
            'total_chapters': len(chapter_results),
            'total_sections': len(section_results),
            'categories_used': len(category_counts),
            'categories_available': len(df),
            'category_usage': category_counts
        }
        
        return stats


# Global instance for backward compatibility
_global_matcher = None

def get_global_matcher():
    """Get or create the global category matcher instance."""
    global _global_matcher
    if _global_matcher is None:
        _global_matcher = CategoryMatcher()
    return _global_matcher

# Backward compatibility functions
def step2_match_categories(chapters=None, toc_output_dir=None, category_file=None, 
                          base_dir=None, model=None, document_type=None):
    """
    Step 2: Match chapters and sections to categories using user-controlled hybrid analysis.
    
    Uses user-specified document type or auto-detects document type and uses appropriate strategy:
    - VMSW documents: Fast number-based mapping  
    - Non-VMSW documents: AI semantic analysis
    
    Args:
        chapters: Chapters dictionary from Step 1
        toc_output_dir: Directory containing TOC results from Step 1
        category_file: Path to category definitions file
        base_dir: Base output directory
        model: AI model instance (used only for non-VMSW documents)
        document_type: User-specified 'vmsw' or 'non_vmsw', None for auto-detection
        
    Returns:
        tuple: (chapter_results, section_results, output_dir)
    """
    # Import here to avoid circular imports
    from .hybrid_matcher import get_global_hybrid_matcher
    
    hybrid_matcher = get_global_hybrid_matcher()
    return hybrid_matcher.match_categories(chapters, toc_output_dir, category_file, 
                                         base_dir, model, document_type=document_type)

def batch_match_to_multiple_categories(model, items_batch, df):
    """Process batch of items (backward compatibility function)."""
    matcher = get_global_matcher()
    return matcher._batch_match_to_multiple_categories(model, items_batch, df)

def match_to_multiple_categories(model, title, content_dict=None, is_section=False, df=None):
    """Match single item (backward compatibility function)."""
    matcher = get_global_matcher()
    
    # Convert old-style parameters to new format
    item = {
        'id': 'temp_id',
        'type': 'section' if is_section else 'chapter',
        'title': title,
        'start_page': 1,
        'end_page': 1,
        'content': str(content_dict) if content_dict else '',
    }
    
    result = matcher._match_single_item(matcher.ai_client.model, item, df, max_retries=3)
    return result

def calculate_category_statistics(chapter_results, section_results, df):
    """Calculate statistics (backward compatibility function)."""
    matcher = get_global_matcher()
    return matcher._calculate_category_statistics(chapter_results, section_results, df)