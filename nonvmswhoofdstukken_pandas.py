import pandas as pd

final_categories = [
    'Plaatsbeschrijvingen - algemeen, Plaatsbeschrijving',
    'Afbraakwerken - asbestverwijdering, Asbest',
    'Afbraakwerken - schoring, Schoring',
    'Proeven - luchtdichtheidsmeting, Luchtdichtheidsmeting',
    'Proeven - akoestiek, Proeven akoestiek',
    'Grondwerken, Ondergrondse leidingen, Buitenverhardingen, Buitenconstructies en afsluitingen, Grondwerken, riolering, omgevingsaanleg',
    'Bronbemaling - algemeen, Droogzuiging',
    'Stut- & ondervangingswerken, Beschoeiingen',
    'Speciale funderingen, Paalfundering',
    'Ondergrondse leidingen, Riolering',
    'Metselwerk, Spouwmuurisolatie, Gevelmetselwerk, Bouwmaterialen',
    'Metselwerk, Kalkzandsteen',
    'Niet-dragende binnenmuur - gipsblokken, Gipsblokken',
    'Dorpels',
    'Ter plaatse gestorte elementen - draagvloeren/breedplaatvloeren, Predallen',
    'Prefab elementen - algemeen, Architectonisch beton',
    'Prefab elementen - draagvloeren/welfsels, Welfsels',
    'Structuurelementen staal, Staal',
    'Brandbeveiliging - algemeen, Brandwerend schilderwerk',
    'Houtskeletbouw',
    'Dakopbouw hellend dak, Thermische isolatie hellend dak, Dakbedekking hellend dak, Hellend dak',
    'Hellingsbeton - algemeen, Hellingsbeton',
    'Thermische isolatie plat dak, Afdichting & afwerking plat dak, Daklichtopeningen, Dakranden en kroonlijsten, Dakwaterafvoer, Plat dak',
    'Ballastlaag - grind, Grind',
    'Ballastlaag - tegels, Terrastegels',
    'Groendak - algemeen, Groendak',
    'Toebehoren plat dak - algemeen, Valbeveiliging',
    'Daklichtopeningen',
    'Dakranden en kroonlijsten',
    'Dakwaterafvoer',
    'Buitenschrijnwerk, Poorten & externe zonwering, Buitenschrijnwerk',
    'Poorten & externe zonwering, Zonwering',
    'Gevelbekledingen',
    'Buitenbepleistering',
    'Buitentrappen & borstweringen, Binnentrappen en leuningen, Buitentrappen & borstweringen',
    'Binnenpleisterwerken',
    'Binnenplaatafwerkingen',
    'Dek- en bedrijfsvloeren',
    'Binnenvloerafwerkingen, Tablet- en wandbekledingen',
    'Toebehoren - algemeen, Vloermatten',
    'Binnendeuren en -ramen',
    'Binnentrappen en leuningen, Houten binnentrappen en leuningen',
    'Vast binnenmeubilair',
    'Sanitair leidingnet, Sanitaire toestellen & toebehoren, Sanitaire kranen & kleppen, Sanitair warm water, Brandbestrijding, Sanitair',
    'Gasinstallaties, Verwarming individuele installaties, Bijzondere installaties, Brandbestrijding, Ventilatie, Opbouwkanalen rookgas en ventilatie, HVAC',
    'Brandbestrijding',
    'Ventilatie, Opbouwkanalen rookgas en ventilatie, Ventilatie',
    'Elektriciteit binnennet, Elektriciteit schakelaars & contactdozen, Elektriciteit lichtarmaturen, Elektriciteit bel & parlofoon, Elektriciteit telecom & domotica, Elektriciteit verwarming, Branddetectie & alarmsystemen, Elektriciteit',
    'Elektromechanica liften',
    'Zonnepanelen & laadpalen',
    'Binnenschilderwerken, Behangwerken, Buitenschilderwerken, Binnenschilderwerken',
    'Buitenverhardingen, Buitenconstructies en afsluitingen, Buitenmeubilair en uitrustingselementen, Groenaanleg en -onderhoud, Omgevingsaanleg',
    'Buitenconstructies en afsluitingen',
    'Buitenmeubilair en uitrustingselementen',
    'Groenaanleg en -onderhoud'
]

# Create a list to store the parsed data
data = []

# Process each entry to separate description and summary
for category in final_categories:
    parts = category.split(', ')
    summary = parts[-1]  # The last part is the summary
    description = ', '.join(parts[:-1])  # Everything else is the description
    
    # If description is empty, use the summary as the description
    if not description:
        description = summary
    
    # Check if the summary is already part of the description
    if summary.lower() in description.lower():
        expanded_description = description
    else:
        expanded_description = f"{description}, {summary}"
        
    data.append({
        'summary': summary,
        'description': description,
        'expanded_description': expanded_description
    })

# Create a DataFrame from the data
df = pd.DataFrame(data)

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
    print(f"Description for 'Plaatsbeschrijving': {df_indexed.loc['Plaatsbeschrijving', 'description']}")
    print(f"Expanded description for 'Plaatsbeschrijving': {df_indexed.loc['Plaatsbeschrijving', 'expanded_description']}")
    
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
# 1. Using the dictionaries: nonvmswchapters['Plaatsbeschrijving']
# 2. Using DataFrame lookup: df[df['summary'] == 'Plaatsbeschrijving']['description'].values[0]
# 3. Using indexed DataFrame: df_indexed.loc['Plaatsbeschrijving', 'description'] 