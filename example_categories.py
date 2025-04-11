#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Set fixed hash seed to avoid randomization issues
import os
os.environ['PYTHONHASHSEED'] = '1'  # Use a fixed seed value

"""
Construction Categories for Non-VMSW Documents

This module defines the standard construction categories used for
classifying sections in construction documents.
"""

import pandas as pd
import ast

# Raw data dictionary with numbered categories and their keywords
raw_data_dict = {
    '01. Afbraak en Grondwerken': "['Afbraak', 'Afbraak metalen constructies', 'Grondwerken', 'Grondwerken ', 'Grondwerken/sierbestrating', 'grondwerken']",
    '02. Funderingen en Kelders': "['Betonkelders', 'Funderingen', 'betonkelders', 'funderingstechnieken', 'paalfunderingen']",
    '03. Ruwbouw en Betonwerken': "['Beton - prefab', 'Beton - vloeren', 'Betonboringen', 'Betonherstellingen', 'Betonkoppelsysteem?', 'Betontrappen', 'Betonwerken', 'Ruwbouwwerken', 'betontrappen', 'hellingsbeton']",
    '04. Staalconstructies en Metaalwerken': "['Binnendeuren deurkaders staal levering', 'Binnendeuren deurkaders staal plaatsing', 'Buitenschrijnwerk staal', 'Glaswerken', 'Laswerken', 'Staal- en laswerken', 'laswerken', 'metaalconstructies', 'metaalwerken', 'staalbouw']",
    '05. Dakwerken': "['Daken en gevels reinigen', 'Daken en gevels schilderen', 'Dakkoepels plaatsen', 'Daktimer', 'Dakwerken', 'Dakwerken hellend dak', 'Dakwerken plat dak', 'Dakwerken zink', 'Groendak', 'OA Adidak']",
    '06. Buitenschrijnwerk': "['Bediening poorten en nooddeuren', 'Binnendeuren', 'Binnendeuren glazen deuren', 'Binnendeuren levering', 'Binnendeuren zweefdeuren', 'Binnenschrijnwerk deuren glas', 'Buitendeuren schuifdeuren automatisch', 'Buitendeuren schuifdeuren brandwerend', 'Buitenschrijnwerk', 'Buitenschrijnwerk aluminium']",
    '07. Binnenschrijnwerk en Interieur': "['Binnenschrijnwerk', 'Binnenschrijnwerk HPL herstellingen', 'Vast meubilair', 'binnenschrijnwerk', 'vast meubilair']",
    '08. Binnenafwerking - Wanden en Plafonds': "['Gipskartonwerken', 'PU vloeren en wanden - gietvloeren', 'Pleister- en gipskartonwerken', 'Verlaagde plafonds', 'gipskartonwerken', 'glazen wanden', 'mobiele wanden', 'pleister- en gipskartonwerken', 'spanplafond', 'verlaagde plafonds']",
    '09. Pleister- en Bezettingswerken': "['Akoestische spuitpleister', 'Gevelpleister', 'Leem', 'Pleisterwerken', 'pleisterwerken']",
    '10. Vloerbekleding': "['Gietvloeren', 'Houten vloeren schuren', 'Isolatie vloer', 'Parketwerken', 'Sportvloer - belijning', 'Steentapijt', 'Tegelwerken', 'Tegelwerken ', 'Vloeren - PU', 'Vloeren - epoxy']",
    '11. Schilder- en Decoratiewerken': "['Schilderwerken', 'Schilderwerken - anti-graffiti', 'Schilderwerken behangen', 'Schilderwerken brandwerend', 'schilderwerken']",
    '12. Isolatiewerken': "['Isolatie akoestisch', 'Isolatie algemeen', 'Isolatie brandwerend', 'Isolatie leidingen', 'Isolatie thermisch', 'Isolatiematerialen', 'Isolatiewerken leidingen']",
    '13. Sanitair': "['Sanitair', 'Sanitaire cabines', 'sanitair ', 'sanitair & cv']",
    '14. Verwarming': "['Centrale verwarming', 'Warmtepompen']",
    '15. Ventilatie': "['Luchtgommen, zandstralen', 'Ventilatie', 'Ventilatie - air conditioning ', 'luchtdichtheidsmeting', 'ventilatie']",
    '16. HVAC': "['HVAC', 'HVAC controles', 'Hvac', 'Regeling HVAC']",
    '17. Elektriciteit': "['Elektriciteit', 'elektriciteit']",
    '18. Brandbeveiliging': "['Blussystemen', 'Branddetectie', 'Branddetectie ', 'Branddetectie (regio Brussel)', 'Brandhaspels (levering)', 'Brandladders aluminium', 'Brandwerende doorvoeren', 'blusinstallatie', 'brandbeveiliging']",
    '19. Toegangscontrole en Beveiliging': "['Inbraakdetectie', 'Valbeveiliging', 'inbraakbeveiliging', 'inbraakdetectie', 'woningbeveiliging']",
    '20. Liften en Verticale Circulatie': "['Liften', 'liften']",
    '21. Trappen en Leuningen': "['Buitentrappen', 'Stralen trappen, muren, liggers', 'Trappen', 'buitentrappen', 'leuningen, balustrades,poorten', 'stalen trappen']",
    '22. Zonwering en Raamdecoratie': "['Gordijnen', 'Gordijnen, rolgordijnen', 'Rolluiken', 'Rolluiken ', 'Rolluiken hout', 'gordijnen', 'rolluiken']",
    '23. Buitenaanleg en Tuinaanleg': "['Groenaanleg', 'Tuinaanleg', 'buitenaanleg', 'klinkers', 'tuinaanleg', 'tuinaanleg - tuinwerken', 'tuinafsluitingen', 'tuinwerken']",
    '24. Riolering en Waterbeheer': "['Ontstopping riolering', 'Rioleringswerken', 'ontstopping riolering', 'rioleringswerken']",
    '25. Glas en Aluminiumconstructies': "['Folie op glas', 'Gevelconstructie alu', 'Loopbruggen aluminium', 'Maatwerk aluminiuim', 'folie op glas', 'röntgenglas']",
    '26. Reiniging en Oplevering': "['Gevelreiniging', 'Opkuis', 'Reinigingswerken ', 'Zonnepanelen reiniging', 'opkuis, vrijmaken bouwgrond']",
    '27. Keukens': "['Keukens ', 'keukens']",
    '28. Laboinrichting': "['labo inrichting']",
    '30. Verlichting': "['Gevelbekleding', 'Wandbekleding', 'gevelbekleding', 'wandbekleding tava']",
    '31. Corian Toepassingen': "['Corian ']",
    '32. Sportinfrastructuur': "['Sportmateriaal (levering)', 'transport']",
    '33. Signalisatie en Bewegwijzering': "['signalisatie']",
    '35. Waterdichting': "['Waterdichting']",
    '36. Meubilair en Inrichting': "['Straatmeubilair', 'Volkern meubilair', 'schoolmeubilair', 'straatmeubilair']",
    '37. Bliksembeveiliging': "['Bliksemafleiding']",
    '38. Advies en Studies': "['Adviesbureau']",
    '39. Steigerbouw en Schoringen': "['Steiger']",
    '40. Panelen en Beplating': "['Akoestische panelen', 'Sandwichpanelen', 'Zonnepanelen']",
    '42. Asbestverwijdering en Milieuwerken': "['Asbestverwijdering', 'asbestverwijdering']",
    '99. Overige': "['Akoestische proeven', 'Algemene bouwwerken', 'Arduin - marmer - blauwe steen (leveren en plaatsen)', 'Asfalt', 'Binnenplaatafwerking', 'Boomverzorging', 'Bouwdrogers', 'Bouwmaterialen', 'Bouwproducten en geokunststoffen ', 'Chape']"
}

# Create a list to store the parsed data
data = []

# Process each entry to create summary, description and expanded_description
for category, keywords_str in raw_data_dict.items():
    # Parse the keywords string into a list
    try:
        if isinstance(keywords_str, str) and keywords_str.startswith('[') and keywords_str.endswith(']'):
            keywords = ast.literal_eval(keywords_str)
        else:
            keywords = []
    except:
        keywords = []
    
    # Filter and join keywords for description
    keywords_filtered = [k for k in keywords if isinstance(k, str) and k.strip()]
    description = ', '.join(keywords_filtered)
    
    # Create expanded description
    if description:
        expanded_description = f"{description}, {category}"
    else:
        expanded_description = category
    
    # Add to data
    data.append({
        'summary': category,  # Use the numbered category as the summary
        'description': description,
        'expanded_description': expanded_description
    })

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Reconstruct final_categories for compatibility
final_categories = []
for index, row in df.iterrows():
    description = row['description']
    summary = row['summary']
    if description:
        final_categories.append(f"{description}, {summary}")
    else:
        final_categories.append(summary) # If no description, just use summary

# Set the summary as the index for easy lookups
df_indexed = df.set_index('summary')

# For backward compatibility, create dictionaries from the DataFrame
nonvmswchapters = dict(zip(df['summary'], df['description']))
nonvmswchapters_expanded = dict(zip(df['summary'], df['expanded_description']))

# Only print when this file is run directly, not when imported
if __name__ == "__main__":
    # Print the DataFrame
    print("DataFrame contents:")
    print(df)
    
    print("\n\nAccessing data by summary:")
    first_summary = df['summary'].iloc[0] if not df.empty else "No summaries available"
    print(f"Description for '{first_summary}': {df_indexed.loc[first_summary, 'description'] if not df.empty else 'N/A'}")
    print(f"Expanded description for '{first_summary}': {df_indexed.loc[first_summary, 'expanded_description'] if not df.empty else 'N/A'}")
    
    # Print the original dictionary format for comparison
    print("\n\nOriginal Dictionary contents:")
    for summary, description in nonvmswchapters.items():
        print(f"Summary: '{summary}'")
        print(f"Description: '{description}'")
        print("-" * 50)
        
    print("\n\nExpanded Dictionary contents:")
    for summary, expanded_description in nonvmswchapters_expanded.items():
        print(f"Summary: '{summary}'")
        print(f"Expanded Description: '{expanded_description}'")
        print("-" * 50)

# Access methods:
# 1. Using the dictionaries: nonvmswchapters['01. Afbraak en Grondwerken']
# 2. Using DataFrame lookup: df[df['summary'] == '01. Afbraak en Grondwerken']['description'].values[0]
# 3. Using indexed DataFrame: df_indexed.loc['01. Afbraak en Grondwerken', 'description'] 