#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Category Matcher

This module provides intelligent category matching that automatically detects
document type (VMSW vs non-VMSW) and uses the appropriate matching strategy:
- VMSW documents: Fast number-based mapping
- Non-VMSW documents: AI semantic analysis
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple, Any

from .vmsw_matcher import VMSWMatcher, detect_document_type, get_global_vmsw_matcher
from .category_matcher import CategoryMatcher, get_global_matcher

logger = logging.getLogger(__name__)

class HybridMatcher:
    """
    Intelligent matcher that automatically chooses between VMSW and AI matching.
    """
    
    def __init__(self):
        """Initialize the hybrid matcher."""
        self.vmsw_matcher = get_global_vmsw_matcher()
        self.ai_matcher = get_global_matcher()
        self.document_type = None
        self.forced_mode = None  # Can be 'vmsw' or 'ai' to override detection
    
    def force_matching_mode(self, mode: str):
        """
        Force a specific matching mode, overriding automatic detection.
        
        Args:
            mode: 'vmsw' for number-based, 'ai' for semantic, or None for auto-detect
        """
        if mode in ['vmsw', 'ai', None]:
            self.forced_mode = mode
            logger.info(f"Matching mode forced to: {mode}")
        else:
            raise ValueError("Mode must be 'vmsw', 'ai', or None")
    
    def detect_and_set_document_type(self, chapters: Dict[str, Any]) -> str:
        """
        Detect document type and store it for future use.
        
        Args:
            chapters: Dictionary of chapters from TOC generation
            
        Returns:
            str: 'vmsw' or 'non_vmsw'
        """
        if self.forced_mode:
            self.document_type = 'vmsw' if self.forced_mode == 'vmsw' else 'non_vmsw'
            logger.info(f"Using forced document type: {self.document_type}")
        else:
            self.document_type = detect_document_type(chapters)
            logger.info(f"Auto-detected document type: {self.document_type}")
        
        return self.document_type
    
    def match_categories(self, chapters=None, toc_output_dir=None, category_file=None, 
                        base_dir=None, model=None, include_explanations=True, 
                        document_type=None):
        """
        Category matching with user-specified document type.
        
        Args:
            chapters: Chapters dictionary from Step 1
            toc_output_dir: Directory containing TOC results  
            category_file: Path to category definitions file
            base_dir: Base output directory
            model: AI model instance (only used for non-VMSW)
            include_explanations: Whether to include explanations
            document_type: User-specified document type ('vmsw' or 'non_vmsw')
            
        Returns:
            tuple: (chapter_results, section_results, output_dir)
        """
        # Use user-specified document type
        if document_type:
            self.document_type = 'vmsw' if document_type == 'vmsw' else 'non_vmsw'
            logger.info(f"Using user-specified document type: {self.document_type}")
        else:
            # Fallback to auto-detection if no type specified
            if not self.document_type:
                if chapters:
                    self.detect_and_set_document_type(chapters)
                else:
                    # Load chapters from TOC output if needed
                    if toc_output_dir:
                        chapters_file = os.path.join(toc_output_dir, "chapters.json")
                        if os.path.exists(chapters_file):
                            with open(chapters_file, 'r', encoding='utf-8') as f:
                                chapters = json.load(f)
                            self.detect_and_set_document_type(chapters)
                        else:
                            logger.warning("No chapters.json found, defaulting to AI matching")
                            self.document_type = 'non_vmsw'
                    else:
                        logger.warning("No chapter data available, defaulting to AI matching")
                        self.document_type = 'non_vmsw'
        
        # Choose matching strategy
        if self.document_type == 'vmsw':
            return self._match_vmsw_document(chapters, toc_output_dir, category_file, 
                                           base_dir, include_explanations)
        else:
            return self._match_ai_document(chapters, toc_output_dir, category_file, 
                                         base_dir, model, include_explanations)
    
    def _match_vmsw_document(self, chapters, toc_output_dir, category_file, 
                           base_dir, include_explanations):
        """
        Match VMSW document using number-based mapping.
        
        Returns:
            tuple: (chapter_results, section_results, output_dir)
        """
        logger.info("=== USING VMSW NUMBER-BASED MATCHING ===")
        
        # Load chapters if needed
        if not chapters and toc_output_dir:
            chapters_file = os.path.join(toc_output_dir, "chapters.json")
            if os.path.exists(chapters_file):
                with open(chapters_file, 'r', encoding='utf-8') as f:
                    chapters = json.load(f)
        
        if not chapters:
            raise ValueError("No chapter data available for VMSW matching")
        
        # Collect all items for processing
        all_items = []
        
        # Process chapters
        for chapter_id, chapter_data in chapters.items():
            if isinstance(chapter_data, dict):
                item = {
                    'id': chapter_id,
                    'title': chapter_data.get('title', ''),
                    'content': chapter_data.get('content', ''),
                    'type': 'chapter',
                    'start': chapter_data.get('start'),  # Use 'start' from original TOC
                    'end': chapter_data.get('end')       # Use 'end' from original TOC
                }
                all_items.append(item)
                
                # Process sections within chapters
                sections = chapter_data.get('sections', {})
                for section_id, section_data in sections.items():
                    if isinstance(section_data, dict):
                        section_item = {
                            'id': section_id,
                            'title': section_data.get('title', ''),
                            'content': section_data.get('content', ''),
                            'type': 'section',
                            'parent_chapter': chapter_id,
                            'start': section_data.get('start'),  # Use 'start' from original TOC
                            'end': section_data.get('end')       # Use 'end' from original TOC
                        }
                        all_items.append(section_item)
        
        logger.info(f"Processing {len(all_items)} items with VMSW number mapping")
        
        # Process all items with VMSW matcher
        all_results = self.vmsw_matcher.match_vmsw_batch(all_items)
        
        # Separate chapter and section results
        chapter_results = {}
        section_results = {}
        
        for item_id, result in all_results.items():
            if result.get('type') == 'chapter':
                chapter_results[item_id] = result
            else:
                section_results[item_id] = result
        
        # Create output directory
        output_dir = self._create_output_directory(base_dir, "vmsw_matching")
        
        # Save results
        self._save_vmsw_results(output_dir, chapter_results, section_results, all_results)
        
        logger.info(f"VMSW matching completed: {len(chapter_results)} chapters, {len(section_results)} sections")
        logger.info(f"Results saved to: {output_dir}")
        
        return chapter_results, section_results, output_dir
    
    def _match_ai_document(self, chapters, toc_output_dir, category_file, 
                          base_dir, model, include_explanations):
        """
        Match non-VMSW document using AI semantic analysis.
        
        Returns:
            tuple: (chapter_results, section_results, output_dir)
        """
        logger.info("=== USING AI SEMANTIC MATCHING ===")
        
        # Delegate to existing AI matcher
        return self.ai_matcher.match_categories(
            chapters=chapters,
            toc_output_dir=toc_output_dir,
            category_file=category_file,
            base_dir=base_dir,
            model=model,
            include_explanations=include_explanations
        )
    
    def _create_output_directory(self, base_dir, suffix=""):
        """Create output directory for results."""
        import datetime
        
        if not base_dir:
            base_dir = "output"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_dir, f"step2_categories_{suffix}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        return output_dir
    
    def _save_vmsw_results(self, output_dir, chapter_results, section_results, all_results):
        """Save VMSW matching results to files."""
        
        # Save chapter results
        chapters_file = os.path.join(output_dir, "chapter_results.json")
        with open(chapters_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_results, f, ensure_ascii=False, indent=2)
        
        # Save section results
        sections_file = os.path.join(output_dir, "section_results.json")
        with open(sections_file, 'w', encoding='utf-8') as f:
            json.dump(section_results, f, ensure_ascii=False, indent=2)
        
        # Save statistics
        stats = self._calculate_vmsw_statistics(chapter_results, section_results, all_results)
        stats_file = os.path.join(output_dir, "category_statistics.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"VMSW results saved to {output_dir}")
    
    def _calculate_vmsw_statistics(self, chapter_results, section_results, all_results):
        """Calculate statistics for VMSW matching results."""
        
        category_counts = {}
        method_counts = {'vmsw_direct_mapping': 0, 'vmsw_fallback': 0}
        confidence_scores = []
        
        for result in all_results.values():
            # Count categories
            for category in result.get('categories', []):
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count methods
            method = result.get('method', 'unknown')
            if method in method_counts:
                method_counts[method] += 1
            
            # Collect confidence scores
            confidence = result.get('confidence', 0)
            confidence_scores.append(confidence)
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Calculate success rate
        total_items = len(all_results)
        direct_matches = method_counts.get('vmsw_direct_mapping', 0)
        success_rate = direct_matches / total_items if total_items > 0 else 0
        
        stats = {
            'total_items': total_items,
            'chapters': len(chapter_results),
            'sections': len(section_results),
            'method_counts': method_counts,
            'success_rate': success_rate,
            'average_confidence': avg_confidence,
            'category_distribution': category_counts,
            'matching_strategy': 'vmsw_number_based'
        }
        
        return stats

# Global instance for easy access
_global_hybrid_matcher = None

def get_global_hybrid_matcher() -> HybridMatcher:
    """Get the global hybrid matcher instance."""
    global _global_hybrid_matcher
    if _global_hybrid_matcher is None:
        _global_hybrid_matcher = HybridMatcher()
    return _global_hybrid_matcher

# Convenience function for backward compatibility and user-controlled matching
def hybrid_match_categories(chapters=None, toc_output_dir=None, category_file=None, 
                          base_dir=None, model=None, include_explanations=True,
                          document_type=None):
    """
    Hybrid category matching function with user-specified document type.
    
    Args:
        document_type: 'vmsw' for direct mapping, 'non_vmsw' for AI analysis, 
                      None for auto-detection (backward compatibility)
    """
    matcher = get_global_hybrid_matcher()
    return matcher.match_categories(
        chapters=chapters,
        toc_output_dir=toc_output_dir,
        category_file=category_file,
        base_dir=base_dir,
        model=model,
        include_explanations=include_explanations,
        document_type=document_type
    ) 