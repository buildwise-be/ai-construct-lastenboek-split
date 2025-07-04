"""
VMSW Pipeline Demo Script

This script demonstrates the VMSW template-based category matching functionality.
It shows how chapter numbers are matched to categories from VMSWcat.json.
"""

import json
import os
from vmsw_pipeline import load_vmsw_categories, match_chapter_to_vmsw_category

def test_vmsw_matching():
    """Test the VMSW matching logic with sample chapter numbers."""
    
    print("=" * 60)
    print("VMSW Template-Based Category Matching Demo")
    print("=" * 60)
    
    # Load VMSW categories
    try:
        vmsw_categories = load_vmsw_categories()
        print(f"✅ Loaded {len(vmsw_categories)} VMSW categories from VMSWcat.json")
    except Exception as e:
        print(f"❌ Error loading VMSW categories: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Category Mapping Examples:")
    print("=" * 60)
    
    # Test various chapter number formats
    test_chapters = [
        "01",      # Should match "01.10" -> PLAATSBESCHRIJVING
        "03",      # Should match "03." -> AFBRAAKWERKEN
        "20",      # Should match "20 + 21 + 22" -> BOUWMATERIALEN and "20." -> KALKZANDSTEEN
        "20.55",   # Should match "20.55" -> GIPSBLOKKEN and "20." -> KALKZANDSTEEN
        "26",      # Should match multiple 26.* categories
        "27",      # Should match "27." -> STAAL
        "40",      # Should match "40 + 41" -> BUITENSCHRIJNWERK
        "60",      # Should match "60 + 61 + 62 + 63 + 67" -> SANITAIR
        "90",      # Should match "90 + 91 + 92 + 93" -> OMGEVINGSAANLEG
    ]
    
    for chapter in test_chapters:
        print(f"\n📍 Chapter {chapter}:")
        matches = match_chapter_to_vmsw_category(chapter, vmsw_categories)
        
        if matches:
            for match in matches:
                print(f"   ✅ {match}")
        else:
            print(f"   ❌ No matches found")
    
    print("\n" + "=" * 60)
    print("All VMSW Categories Available:")
    print("=" * 60)
    
    for i, category in enumerate(vmsw_categories, 1):
        art_nr = category.get('art_nr', '')
        omschrijving = category.get('omschrijving', '')
        print(f"{i:2}. {art_nr:20} → {omschrijving}")
    
    print(f"\nTotal categories: {len(vmsw_categories)}")

def show_matching_logic():
    """Explain the matching logic used in the VMSW pipeline."""
    
    print("\n" + "=" * 60)
    print("VMSW Matching Logic Explanation:")
    print("=" * 60)
    
    print("""
The VMSW pipeline uses deterministic template-based matching instead of AI:

1. DIRECT MATCH:
   Chapter "03" matches art_nr "03." exactly
   → Result: AFBRAAKWERKEN

2. COMPOUND CATEGORIES:
   Chapter "20" matches art_nr "20 + 21 + 22"
   → Result: BOUWMATERIALEN
   
3. HIERARCHICAL MATCHING:
   Chapter "20.55" matches both:
   - art_nr "20.55" (specific) → GIPSBLOKKEN
   - art_nr "20." (general) → KALKZANDSTEEN
   
4. COMPLEX HIERARCHIES:
   Chapter "26" matches:
   - art_nr "26.26.30." → PREDALLEN
   - art_nr "26.30." → PREFAB BETON
   - art_nr "26.30." → ARCHITECTONISCH BETON
   - art_nr "26.36.10." → WELFSELS

This approach ensures:
✅ 100% consistent results
✅ No AI model dependencies
✅ Fast processing
✅ Easy to understand and modify
""")

if __name__ == "__main__":
    test_vmsw_matching()
    show_matching_logic()
    
    print("\n" + "=" * 60)
    print("To run the full VMSW pipeline:")
    print("python vmsw_pipeline.py <pdf_path> [-o output_dir] [-v]")
    print("=" * 60) 