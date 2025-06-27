#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Set fixed hash seed to avoid randomization issues
import os
os.environ['PYTHONHASHSEED'] = '1'  # Use a fixed seed value

"""
Updated Construction Categories for Non-VMSW Documents

This module defines an updated set of standard construction categories used for
classifying sections in construction documents, based on user input.
Moved from root directory to models for better organization.
"""

import pandas as pd
import ast
import re

# Function to standardize category numbers to two-digit format with leading zeros
def standardize_category_number(category_key):
    """
    Standardizes category numbers to ensure they use the two-digit format with leading zeros.
    For example: '1. Category' becomes '01. Category', '10. Category' remains unchanged.
    """
    pattern = r'^(\d+)\.\s+(.+)$'
    match = re.match(pattern, category_key)
    if match:
        number, name = match.groups()
        # Add leading zero for single-digit numbers
        number = number.zfill(2)
        return f"{number}. {name}"
    return category_key  # Return unchanged if pattern doesn't match

# Updated raw data dictionary with numbered categories and their keywords
raw_data_dict = {
    '01. Afbraak en Grondwerken': "['sloopwerken', 'afbraakwerken', 'strippen', 'puinruiming', 'grondverzet', 'graafwerken', 'uitgraven', 'bouwput', 'egaliseerwerk', 'nivellering', 'bouwrijp maken', 'ontbossing', 'bemaling', 'grondstabilisatie', 'sleuven graven', 'taludvorming']",
    '02. Funderingen en Kelders': "['fundering', 'kelderbouw', 'betonfundering', 'bekisting', 'wapening', 'paalfundering', 'boorpalen', 'keldermuren', 'keldervloer', 'betonstorten', 'funderingsplaat', 'onderbeton', 'funderingstrook', 'vorstrand', 'drainage rond kelder', 'kelderdichting']",
    '03. Ruwbouw en Betonwerken': "['metselwerk', 'betonwerken', 'ruwbouw', 'bekisting', 'wapeningsstaal', 'dragende muren', 'kolommen', 'balken', 'vloerplaat', 'welfsels', 'prefab elementen', 'lateien', 'cellenbeton', 'snelbouwsteen', 'voegwerk', 'betonkolom', 'breedplaatvloer', 'kalkzandsteen']",
    '04. Dakwerken': "['dakbedekking', 'dakpannen', 'leien', 'roofing', 'EPDM', 'dakisolatie', 'dakstructuur', 'daktimmer', 'spanten', 'gordingen', 'dakvenster', 'dakgoot', 'regenpijp', 'nokpannen', 'dakdoorvoer', 'zinkwerk', 'dakkapel', 'plat dak']",
    '05. Buitenschrijnwerk': "['ramen', 'buitendeuren', 'kozijn', 'profielen', 'dorpels', 'beglazing', 'dubbel glas', 'hang- en sluitwerk', 'schuiframen', 'garagepoort', 'voordeur', 'isolatieglas', 'raamkader', 'deurkozijn', 'spouwlat', 'ventilatierooster', 'slot']",
    '06. Binnenschrijnwerk en Interieur': "['binnendeuren', 'plinten', 'inbouwkasten', 'lambrisering', 'vensterbank', 'deurlijsten', 'scharnieren', 'maatwerkmeubilair', 'wandbekleding (hout)', 'trapbekleding', 'omkastingen', 'architraaf', 'dressing', 'boekenkast', 'binnenraam', 'plafondlijst']",
    '07. Binnenafwerking - Wanden en Plafonds': "['scheidingswanden', 'gipskarton', 'Metal Stud', 'voorzetwanden', 'systeemplafond', 'verlaagd plafond', 'plafondtegels', 'akoestisch plafond', 'wandprofielen', 'plafondprofielen', 'brandwerende wand', 'gipsplaten', 'spouwwand', 'plafondrooster']",
    '08. Pleister- en Bezettingswerken': "['pleisterwerk', 'bezettingswerk', 'gipspleister', 'cementering', 'bepleistering', 'raaplaag', 'gladstrijken', 'sierpleister', 'schuurwerk', 'stuccen', 'pleisterspaan', 'hoekprofielen', 'spuitpleister', 'gevelpleister', 'plamuur']",
    '09. Vloerbekleding': "['vloertegels', 'wandtegels', 'parket', 'laminaat', 'tapijt', 'vinyl', 'linoleum', 'gietvloer', 'epoxyvloer', 'chape', 'dekvloer', 'egaline', 'plinten', 'tegelvoegen', 'natuursteen vloer', 'leefbeton']",
    '10. Schilder- en Decoratiewerken': "['schilderwerk', 'verf', 'behang', 'lakwerk', 'vernissen', 'muurverf', 'grondlaag', 'afplakken', 'spuitwerk', 'borstelen', 'schilderstechniek', 'latex', 'rolleren', 'patine', 'kleuradvies']",
    '11. Isolatiewerken': "['dakisolatie', 'muurisolatie', 'vloerisolatie', 'glaswol', 'rotswol', 'PUR-schuim', 'PIR-platen', 'isolatieplaten', 'spouwisolatie', 'isolatiedeken', 'isolatieschuim', 'dampremmende folie', 'EPS', 'XPS', 'na-isolatie']",
    '12. Sanitair': "['waterleidingen', 'afvoerleidingen', 'kraanwerk', 'toilet', 'badkuip', 'douche', 'wastafel', 'urinoir', 'sifon', 'riolering binnenshuis', 'sanitair toestel', 'koppelingen', 'PVC afvoer', 'koperleiding', 'boiler', 'waterverzachter']",
    '13. Verwarming': "['centrale verwarming', 'CV-ketel', 'radiatoren', 'vloerverwarming', 'thermostaat', 'expansievat', 'circulatiepomp', 'condenserende ketel', 'mazoutketel', 'gasketel', 'warmtepomp', 'zonneboiler', 'leidingen', 'schouw', 'thermostatische kraan']",
    '14. Ventilatie': "['mechanische ventilatie', 'balansventilatie', 'afzuiging', 'toevoerlucht', 'afvoerlucht', 'ventilatiekanalen', 'luchtroosters', 'ventilatie-unit', 'warmteterugwinning', 'filter', 'ventilatieplan', 'CO2-sensor', 'natuurlijke ventilatie', 'kanaalwerk']",
    '15. HVAC': "['airconditioning', 'klimaatregeling', 'koelinstallatie', 'luchtbehandeling', 'warmtepomp', 'koelmachine', 'chiller', 'compressor', 'verdamper', 'condensor', 'koelmiddel', 'VRF-systeem', 'luchtgroep', 'fan-coil unit', 'koelleiding', 'koeltoren']",
    '16. Elektriciteit': "['bekabeling', 'leidingen', 'stopcontacten', 'schakelaars', 'verdeelbord', 'zekeringen', 'aardingslus', 'differentieel', 'verlichting', 'armaturen', 'kabelgoten', 'domotica', 'databekabeling', 'parlofonie', 'meterkast']",
    '17. Brandbeveiliging': "['brandalarm', 'rookmelders', 'sprinklers', 'brandblusser', 'brandhaspel', 'brandmeldcentrale', 'noodverlichting', 'handmelder', 'RWA-systeem', 'branddeur', 'brandklep', 'branddetectie', 'sprinklerpomp', 'blusleiding']",
    '18. Toegangscontrole en Beveiliging': "['toegangscontrole', 'inbraakalarm', 'bewegingsmelder', 'camerabewaking', 'badgesysteem', 'codeklavier', 'elektrisch slot', 'magneetcontact', 'sirene', 'parlofoon', 'videofoon', 'toegangslezer', 'alarmcentrale', 'toegangspas', 'slagboom']",
    '19. Liften en Verticale Circulatie': "['liftinstallatie', 'personenlift', 'goederenlift', 'liftkooi', 'liftschacht', 'liftmachinekamer', 'hydraulische lift', 'tractielift', 'liftdeur', 'liftknop', 'roltrap', 'plateaulift', 'hefvermogen', 'nooddaal systeem', 'liftkeuring']",
    '20. Trappen en Leuningen': "['trapconstructie', 'betontrap', 'houten trap', 'metalen trap', 'trapleuning', 'balustrade', 'treden', 'stootborden', 'spiltrap', 'wenteltrap', 'trapbordes', 'leuningsysteem', 'antislipstrip', 'vide-afscherming', 'borstwering']",
    '21. Zonwering en Raamdecoratie': "['rolluiken', 'zonnescherm', 'jaloezieën', 'lamellen', 'gordijnen', 'rolgordijn', 'plisségordijn', 'screens', 'markies', 'verduistering', 'zonwerende folie', 'vliegenraam', 'paneelgordijn', 'overgordijnen']",
    '22. Buitenaanleg en Tuinaanleg': "['bestrating', 'klinkers', 'terrasaanleg', 'oprit', 'asfalt', 'grindpad', 'boordstenen', 'tuinafwerking', 'gazon', 'beplanting', 'tuinomheining', 'tuinpoort', 'sierbestrating', 'vijveraanleg', 'speeltuigen', 'drainage']",
    '23. Riolering en Waterbeheer': "['rioleringsbuizen', 'inspectieput', 'septische put', 'regenwaterput', 'infiltratiekratten', 'afvoergoot', 'drainage', 'kolken', 'pompput', 'rioolpomp', 'bufferbekken', 'overstort', 'afkoppeling', 'DWA/RWA scheiding', 'waterzuivering']",
    '24. Glas en Aluminiumconstructies': "['vliesgevel', 'aluminium ramen', 'gevelbekleding (alu)', 'gordijngevel', 'dubbel glas', 'gelaagd glas', 'gehard glas', 'profielsysteem', 'thermische onderbreking', 'structurele beglazing', 'siliconevoeg', 'beglazingsrubbers', 'glasgevel', 'lichtstraat', 'paneelvulling']",
    '25. Reiniging en Oplevering': "['bouwschoonmaak', 'opleveringsschoonmaak', 'puinopruiming', 'stofzuigen', 'ramen wassen', 'opleveringsklaar', 'afvalafvoer', 'eindschoonmaak', 'opleveringsinspectie', 'schuurmiddel', 'reinigen', 'kuisen', 'stofvrij maken', 'ontvetten']",
    '26. Keukens': "['keukenplaatsing', 'keukenkasten', 'werkblad', 'spoelbak', 'mengkraan', 'kookplaat', 'oven', 'koelkast', 'vaatwasser', 'dampkap', 'keukeneiland', 'inbouwapparatuur', 'keukenfronten', 'lade', 'scharnieren', 'spatwand']",
    '27. Laboinrichting': "['laboratoriummeubilair', 'zuurkast', 'veiligheidskast', 'labotafel', 'werkblad (chemisch resistent)', 'nooddouche', 'oogdouche', 'gasvoorziening', 'afzuigarm', 'laboratoriumkraan', 'spoelbak (lab)', 'laminaire kast', 'reagentiekast', 'labostoelen', 'labofauteuil']",
    '28. Sportinfrastructuur': "['sportvloer', 'belijning', 'tribune', 'basketbalring', 'voetbaldoelen', 'volleybalnet', 'turntoestellen', 'klimrek', 'kunstgrasveld', 'scorebord', 'kleedkamerbanken', 'gymmatten', 'doelnetten', 'pannaveld', 'hockeyveld']",
    '29. Signalisatie en Bewegwijzering': "['bewegwijzering', 'pictogrammen', 'nooduitgangbord', 'informatiebord', 'verkeersbord', 'parkeerborden', 'richtingaanwijzers', 'naambordjes', 'waarschuwingsbord', 'vloermarkering', 'veiligheidssignalisatie', 'LED-borden', 'straatnaambord', 'signalisatiekegel']",
    '30. Waterdichting': "['kelderdichting', 'waterkering', 'bitumenmembraan', 'EPDM-folie', 'afdichtingsband', 'zwelband', 'vochtisolatie', 'lekwaterinjectie', 'bekuiping', 'dampscherm', 'waterproof coating', 'voegdichting', 'bitumineuze verankering', 'scheuroverbrugging']",
    '31. Meubilair en Inrichting': "['stoelen', 'tafels', 'kasten', 'bedden', 'banken (zitbanken)', 'bureaus', 'fauteuils', 'lampen', 'decoratie', 'planken en rekken', 'salontafel', 'wandkast', 'garderobe', 'nachttafel', 'kastenwand']",
    '32. Bliksembeveiliging': "['bliksemafleider', 'aardingslus', 'aardpen', 'overspanningsbeveiliging', 'dakgeleider', 'aardingsnet', 'Faraday-kooi', 'spanningsafleider', 'aardklem', 'blikseminslag', 'potentiaalvereffening']",
    '33. Advies en Studies': "['stabiliteitsstudie', 'EPB-verslaggeving', 'bodemonderzoek', 'sondering', 'veiligheidscoördinatie', 'akoestische studie', 'energieberekening', 'asbestinventaris', 'meetstaat', 'lastenboek', 'werfcontrole', 'expertise', 'studiebureau', 'constructieberekening', 'ontwerptekeningen']",
    '34. Steigerbouw en Schoringen': "['steiger', 'rolsteiger', 'gevelsteiger', 'steigerplank', 'steigerbuis', 'steigerklem', 'hangsteiger', 'veiligheidsnet', 'valbeveiliging', 'schoring', 'stutwerk', 'stempel', 'onderstempeling', 'schoorbalk', 'steigerconstructie']",
    '35. Panelen en Beplating': "['sandwichpanelen', 'gevelbeplating', 'wandpanelen', 'dakpanelen', 'trespa platen', 'HPL platen', 'golfplaten', 'damwandprofiel', 'sidings', 'aluminium composietpanelen', 'polycarbonaat platen', 'steeldeck', 'zetwerk', 'gevelcassette', 'isolatiepaneel']",
    '36. Asbestverwijdering en Milieuwerken': "['asbestinventaris', 'asbestverwijdering', 'asbestsanering', 'hechtgebonden asbest', 'losgebonden asbest', 'containment', 'negatieve druk', 'bodemsanering', 'verontreinigde grond', 'grondwatersanering', 'milieusanering', 'bodemvervuiling', 'tankreiniging', 'afvalverwerking', 'decontaminatie']",
    '38. Advies en Studies': "['stabiliteitsstudie', 'EPB-verslaggeving', 'bodemonderzoek', 'sondering', 'veiligheidscoördinatie', 'akoestische studie', 'energieberekening', 'asbestinventaris', 'meetstaat', 'lastenboek', 'werfcontrole', 'expertise', 'studiebureau', 'constructieberekening', 'ontwerptekeningen']",
    '39. Steigerbouw en Schoringen': "['steiger', 'rolsteiger', 'gevelsteiger', 'steigerplank', 'steigerbuis', 'steigerklem', 'hangsteiger', 'veiligheidsnet', 'valbeveiliging', 'schoring', 'stutwerk', 'stempel', 'onderstempeling', 'schoorbalk', 'steigerconstructie']",
    '42. Asbestverwijdering en Milieuwerken': "['asbestinventaris', 'asbestverwijdering', 'asbestsanering', 'hechtgebonden asbest', 'losgebonden asbest', 'containment', 'negatieve druk', 'bodemsanering', 'verontreinigde grond', 'grondwatersanering', 'milieusanering', 'bodemvervuiling', 'tankreiniging', 'afvalverwerking', 'decontaminatie']",
    '99. Overige': "['diverse', 'algemeen', 'overige werkzaamheden', 'diversen', 'restposten']"
}

# Create a list to store the parsed data
data = []

# Create a mapping from single-digit to two-digit category format
# This will help when matching categories from external sources
category_format_map = {}
for key in raw_data_dict.keys():
    # Extract the number part
    match = re.match(r'^(\d+)\.\s+(.+)$', key)
    if match:
        number, name = match.groups()
        # If it's a single digit number (1-9), create a mapping
        if len(number) == 1:
            single_digit_key = f"{int(number)}. {name}"
            category_format_map[single_digit_key] = key

# Process each entry to create summary, description and expanded_description
for category, keywords_str in raw_data_dict.items():
    # Parse the keywords string into a list
    try:
        # Check if keywords_str is a string representation of a list
        if isinstance(keywords_str, str) and keywords_str.startswith('[') and keywords_str.endswith(']'):
            keywords = ast.literal_eval(keywords_str)
        # Handle cases where keywords might already be a list or need cleaning
        elif isinstance(keywords_str, list):
             keywords = keywords_str # Already a list
        else:
            # Attempt to split if it's a comma-separated string (fallback)
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    except Exception as e:
        print(f"Error parsing keywords for {category}: {e}") # Log error
        keywords = [] # Default to empty list on error

    # Ensure keywords is a list of strings and filter empty ones
    keywords_filtered = [str(k).strip() for k in keywords if isinstance(k, (str, int, float)) and str(k).strip()]
    description = ', '.join(keywords_filtered)

    # Create expanded description - Mirroring example_categories.py logic
    if description:
        expanded_description = f"{description}, {category}" # Use the numbered category name
    else:
        expanded_description = category # Use the numbered category name

    # Add to data
    data.append({
        'summary': category,  # Use the numbered category as the summary
        'description': description,
        'expanded_description': expanded_description
    })

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Reconstruct final_categories for compatibility - Mirroring example_categories.py logic
final_categories = []
for index, row in df.iterrows():
    description = row['description']
    summary = row['summary'] # summary is numbered ('01. ...')
    if description:
        final_categories.append(f"{description}, {summary}") # Use numbered summary
    else:
        final_categories.append(summary) # Use numbered summary

# Set the summary as the index for easy lookups
df_indexed = df.set_index('summary') # Index uses numbered summary ('01. ...')

# Create dictionaries from the DataFrame for backward compatibility
nonvmswchapters = dict(zip(df['summary'], df['description'])) # Keys are numbered summary ('01. ...')
nonvmswchapters_expanded = dict(zip(df['summary'], df['expanded_description'])) # Keys are numbered summary ('01. ...')

# Create a function to standardize category lookup
def get_category_description(category_key):
    """
    Get category description using two-digit format with leading zeros.
    Handles both single-digit and two-digit formats for lookup.
    """
    # If the key is already in the dictionary, return it
    if category_key in nonvmswchapters:
        return nonvmswchapters[category_key]
    
    # Check if there's a format mapping for this key
    if category_key in category_format_map:
        standardized_key = category_format_map[category_key]
        return nonvmswchapters.get(standardized_key)
    
    # Try standardizing the key
    standardized_key = standardize_category_number(category_key)
    return nonvmswchapters.get(standardized_key)

# Similar function for expanded description
def get_expanded_description(category_key):
    """
    Get expanded category description using two-digit format with leading zeros.
    Handles both single-digit and two-digit formats for lookup.
    """
    # If the key is already in the dictionary, return it
    if category_key in nonvmswchapters_expanded:
        return nonvmswchapters_expanded[category_key]
    
    # Check if there's a format mapping for this key
    if category_key in category_format_map:
        standardized_key = category_format_map[category_key]
        return nonvmswchapters_expanded.get(standardized_key)
    
    # Try standardizing the key
    standardized_key = standardize_category_number(category_key)
    return nonvmswchapters_expanded.get(standardized_key)

# Only print when this file is run directly, not when imported
if __name__ == "__main__":
    # Print the DataFrame
    print("DataFrame contents:")
    print(df.to_string()) # Use to_string() for better console output

    if not df_indexed.empty:
        print("\n\nAccessing data by summary:")
        first_summary = df_indexed.index[0]
        try:
            print(f"Description for '{first_summary}': {df_indexed.loc[first_summary, 'description']}")
            print(f"Expanded description for '{first_summary}': {df_indexed.loc[first_summary, 'expanded_description']}")
        except KeyError:
             print(f"Could not access data for summary '{first_summary}' using .loc")
    else:
        print("\n\nNo data available in DataFrame.")

    # Print the 'nonvmswchapters' dictionary format for comparison
    print("\n\n'nonvmswchapters' Dictionary contents:")
    for summary, description in nonvmswchapters.items():
        print(f"Summary: '{summary}'")
        print(f"Description: '{description}'")
        print("-" * 50)

    # Print the 'nonvmswchapters_expanded' dictionary contents
    print("\n\n'nonvmswchapters_expanded' Dictionary contents:")
    for summary, expanded_description in nonvmswchapters_expanded.items():
        print(f"Summary: '{summary}'")
        print(f"Expanded Description: '{expanded_description}'")
        print("-" * 50)

    # Print the 'final_categories' list contents
    print("\n\n'final_categories' List contents:")
    for cat in final_categories:
        print(cat)
    
    # Demonstrate category lookup with both formats
    print("\n\nCategory lookup example:")
    # Two-digit format (already in dictionary)
    print(f"Looking up '01. Afbraak en Grondwerken': {get_category_description('01. Afbraak en Grondwerken')}")
    # Single-digit format (needs standardization)
    print(f"Looking up '1. Afbraak en Grondwerken': {get_category_description('1. Afbraak en Grondwerken')}")

# Example access methods:
# 1. Using the standardized lookup functions: get_category_description('1. Afbraak en Grondwerken')
# 2. Using the dictionaries (requires exact key format): nonvmswchapters.get('01. Afbraak en Grondwerken')
# 3. Using DataFrame lookup (requires exact key format): df[df['summary'] == '01. Afbraak en Grondwerken']['description'].values[0]
# 4. Using indexed DataFrame (requires exact key format): df_indexed.loc['01. Afbraak en Grondwerken', 'description']