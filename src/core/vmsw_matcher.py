#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VMSW Number-Based Category Matcher

This module provides fast, rule-based category matching for VMSW documents
by directly mapping VMSW chapter numbers to construction categories.
"""

import logging
import re
import json
import os
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class VMSWMatcher:
    """
    Fast rule-based matcher for VMSW documents using chapter number mapping.
    """
    
    def __init__(self):
        """Initialize the VMSW matcher with number-to-category mapping."""
        
        # VMSW chapter number to category mapping
        self.vmsw_mapping = {
            "00": "33. Advies en Studies",  # General provisions, studies, admin
            "01": "01. Afbraak en Grondwerken",
            "02": "02. Funderingen en Kelders", 
            "03": "03. Ruwbouw en Betonwerken",
            "04": "04. Dakwerken",
            "05": "05. Buitenschrijnwerk",
            "06": "06. Binnenschrijnwerk en Interieur",
            "07": "07. Binnenafwerking - Wanden en Plafonds",
            "08": "08. Pleister- en Bezettingswerken", 
            "09": "09. Vloerbekleding",
            "10": "10. Schilder- en Decoratiewerken",
            "11": "11. Isolatiewerken",
            "12": "12. Sanitair",
            "13": "13. Verwarming",
            "14": "14. Ventilatie",
            "15": "15. HVAC",
            "16": "16. Elektriciteit",
            "17": "17. Brandbeveiliging",
            "18": "18. Toegangscontrole en Beveiliging",
            "19": "19. Liften en Verticale Circulatie",
            "20": "20. Trappen en Leuningen",
            "21": "21. Zonwering en Raamdecoratie",
            "22": "22. Buitenaanleg en Tuinaanleg",
            "23": "23. Riolering en Waterbeheer",
            "24": "24. Glas en Aluminiumconstructies",
            "25": "25. Reiniging en Oplevering",
            "26": "26. Keukens",
            "27": "27. Laboinrichting",
            "28": "28. Sportinfrastructuur",
            "29": "29. Signalisatie en Bewegwijzering",
            "30": "30. Waterdichting",
            "31": "31. Meubilair en Inrichting",
            "32": "32. Bliksembeveiliging",
            "33": "33. Advies en Studies",
            "34": "34. Steigerbouw en Schoringen",
            "35": "35. Panelen en Beplating",
            "36": "36. Asbestverwijdering en Milieuwerken",
            "38": "38. Advies en Studies",
            "39": "39. Steigerbouw en Schoringen",
            "42": "42. Asbestverwijdering en Milieuwerken",
        }
    
    def is_vmsw_format(self, title: str) -> bool:
        """
        Detect if a title follows VMSW numbering format.
        
        Args:
            title: Chapter or section title
            
        Returns:
            bool: True if VMSW format detected
        """
        # Look for patterns like "02.40", "15.21", "12.10"
        vmsw_pattern = r'^\d{2}\.\d{2,3}'  # Two digits, dot, two or more digits
        return bool(re.match(vmsw_pattern, title.strip()))
    
    def extract_vmsw_chapter(self, item_id: str) -> Optional[str]:
        """
        Extract VMSW chapter number from item ID (JSON key).
        
        Args:
            item_id: Item ID like "02", "02.40", "15.21" etc.
            
        Returns:
            str: Chapter number like "02" or None if not found
        """
        if not item_id:
            return None
            
        # Handle direct chapter IDs like "02", "15"
        if re.match(r'^\d{2}$', item_id.strip()):
            return item_id.strip()
        
        # Handle section IDs like "02.40", "15.21"  
        match = re.match(r'^(\d{2})\.\d{2,3}', item_id.strip())
        if match:
            return match.group(1)
        
        return None
    
    def match_vmsw_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match a single VMSW item to categories using number mapping.
        
        Args:
            item: Item with 'title', 'content', 'type', etc.
            
        Returns:
            dict: Matching result with categories, confidence, etc.
        """
        title = item.get('title', '')
        item_id = item.get('id', '')
        
        # Extract chapter number from item ID (JSON key)
        chapter_num = self.extract_vmsw_chapter(item_id)
        
        if chapter_num and chapter_num in self.vmsw_mapping:
            # Direct mapping found
            category = self.vmsw_mapping[chapter_num]
            
            # Check for removal/demolition keywords
            removal_keywords = ['verwijderen', 'slopen', 'uitbreken', 'opbreken', 'demonteren', 'afbreken']
            title_lower = title.lower()
            content_lower = item.get('content', '').lower()
            
            categories = [category]  # Primary category
            explanation = f"VMSW chapter {chapter_num} mapped to {category}"
            
            # Add demolition category if removal work detected
            if any(keyword in title_lower or keyword in content_lower for keyword in removal_keywords):
                if "01. Afbraak en Grondwerken" not in categories:
                    categories.insert(0, "01. Afbraak en Grondwerken")  # Make it primary
                    explanation = f"Removal work detected: Added demolition category. " + explanation
            
            result = {
                'categories': categories,
                'explanation': explanation,
                'confidence': 1.0,  # Perfect confidence for direct mapping
                'method': 'vmsw_direct_mapping',
                'vmsw_chapter': chapter_num,
                'type': item.get('type'),
                'title': item.get('title'),
                'start_page': item.get('start') or item.get('start_page'),  # Support both formats
                'end_page': item.get('end') or item.get('end_page')  # Support both formats
            }
            
            logger.info(f"VMSW match: '{title}' -> {categories} (chapter {chapter_num})")
            return result
        
        else:
            # No mapping found - return fallback
            logger.warning(f"No VMSW mapping for chapter {chapter_num} in title: {title}")
            return {
                'categories': ['99. Overige'],
                'explanation': f'No VMSW mapping found for chapter {chapter_num}',
                'confidence': 0.5,
                'method': 'vmsw_fallback',
                'vmsw_chapter': chapter_num,
                'type': item.get('type'),
                'title': item.get('title'),
                'start_page': item.get('start') or item.get('start_page'),  # Support both formats
                'end_page': item.get('end') or item.get('end_page')  # Support both formats
            }
    
    def match_vmsw_batch(self, items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Match a batch of VMSW items to categories.
        
        Args:
            items: List of items to process
            
        Returns:
            dict: Results keyed by item ID
        """
        results = {}
        
        logger.info(f"Processing {len(items)} VMSW items with direct number mapping")
        
        for item in items:
            item_id = item.get('id')
            if item_id:
                results[item_id] = self.match_vmsw_item(item)
        
        # Log statistics
        total_items = len(results)
        direct_matches = sum(1 for r in results.values() if r.get('method') == 'vmsw_direct_mapping')
        fallbacks = total_items - direct_matches
        
        logger.info(f"VMSW batch complete: {direct_matches}/{total_items} direct matches, {fallbacks} fallbacks")
        
        return results

def detect_document_type(chapters: Dict[str, Any]) -> str:
    """
    Detect if document is VMSW format based on JSON keys (chapter IDs and section IDs).
    
    Args:
        chapters: Dictionary of chapters from TOC generation
        
    Returns:
        str: 'vmsw' or 'non_vmsw'
    """
    if not chapters:
        return 'non_vmsw'
    
    vmsw_pattern_count = 0
    total_items = 0
    
    for chapter_id, chapter_data in chapters.items():
        if isinstance(chapter_data, dict):
            total_items += 1
            
            # Check chapter ID (should be "00", "01", "02", etc.)
            if re.match(r'^\d{2}$', chapter_id.strip()):
                vmsw_pattern_count += 1
            
            # Check section IDs (should be "01.00", "02.40", etc.)
            sections = chapter_data.get('sections', {})
            for section_id, section_data in sections.items():
                total_items += 1
                
                # Check section ID format
                if re.match(r'^\d{2}\.\d{2,3}', section_id.strip()):
                    vmsw_pattern_count += 1
    
    # If more than 80% of items follow VMSW pattern, consider it VMSW
    if total_items > 0 and (vmsw_pattern_count / total_items) >= 0.8:
        logger.info(f"VMSW document detected: {vmsw_pattern_count}/{total_items} items match VMSW pattern")
        return 'vmsw'
    else:
        logger.info(f"Non-VMSW document detected: {vmsw_pattern_count}/{total_items} items match VMSW pattern")
        return 'non_vmsw'

# Global instance for easy access
_global_vmsw_matcher = None

def get_global_vmsw_matcher() -> VMSWMatcher:
    """Get the global VMSW matcher instance."""
    global _global_vmsw_matcher
    if _global_vmsw_matcher is None:
        _global_vmsw_matcher = VMSWMatcher()
    return _global_vmsw_matcher 