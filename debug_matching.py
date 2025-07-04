"""
Debug script to understand VMSW matching issues
"""

from vmsw_pipeline import load_vmsw_categories

def debug_matching():
    vmsw_categories = load_vmsw_categories()
    
    print("Debugging chapter '01' matching:")
    normalized_chapter = "01."
    
    for category in vmsw_categories:
        art_nr = category.get('art_nr', '')
        omschrijving = category.get('omschrijving', '')
        
        if '01' in art_nr:
            print(f"  Found relevant art_nr: '{art_nr}' → {omschrijving}")
            print(f"  Direct match check: '{normalized_chapter}' == '{art_nr}' → {normalized_chapter == art_nr}")
            
            if '.' in art_nr:
                art_base = art_nr.split('.')[0]
                chapter_base = normalized_chapter.rstrip('.')
                print(f"  Base match check: '{chapter_base}' == '{art_base}' → {chapter_base == art_base}")
    
    print("\nDebugging chapter '26' matching:")
    normalized_chapter = "26."
    
    for category in vmsw_categories:
        art_nr = category.get('art_nr', '')
        omschrijving = category.get('omschrijving', '')
        
        if '26' in art_nr:
            print(f"  Found relevant art_nr: '{art_nr}' → {omschrijving}")
            print(f"  Direct match check: '{normalized_chapter}' == '{art_nr}' → {normalized_chapter == art_nr}")
            
            if '.' in art_nr:
                art_base = art_nr.split('.')[0]
                chapter_base = normalized_chapter.rstrip('.')
                print(f"  Base match check: '{chapter_base}' == '{art_base}' → {chapter_base == art_base}")

if __name__ == "__main__":
    debug_matching() 