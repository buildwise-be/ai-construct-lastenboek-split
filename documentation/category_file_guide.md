# Creating and Customizing Category Files

This guide explains how to create and customize category files used by the AI Construct PDF Splitter to classify document sections.

## What is a Category File?

A category file defines the construction categories that the AI will use to match chapters and sections from your PDF documents. Each category includes:

- A numbered identifier and category name (e.g., "01. Afbraak en Grondwerken")
- A list of keywords or phrases associated with that category
- Additional metadata used by the application for matching

## Available Formats

You can create category files in three formats:

1. **Python Module** (.py file) - The default and most flexible format
2. **Excel Spreadsheet** (.xlsx file) - Easier to edit for non-programmers
3. **CSV File** (.csv file) - Simple text-based format

## Creating a Python Module Category File

This is the recommended format as it provides the most flexibility and performance.

### Basic Structure

A Python module category file needs the following components:

1. A `raw_data_dict` dictionary containing categories and their keywords
2. Processing code to convert the raw dictionary into the required DataFrame structure
3. Export variables used by the application

### Step-by-Step Instructions

1. **Start by copying the example file**:
   ```bash
   cp example_categories.py my_custom_categories.py
   ```

2. **Edit the raw_data_dict**:
   Open the file in your preferred editor and modify the `raw_data_dict` dictionary:

   ```python
   raw_data_dict = {
       '01. Category Name': "['Keyword1', 'Keyword2', 'Related phrase']",
       '02. Another Category': "['Keyword3', 'Keyword4']",
       # Add more categories as needed
   }
   ```

   Each key is a numbered category, and each value is a string representation of a list containing keywords.

3. **Key formatting considerations**:
   - Category numbers should be padded with zeros (e.g., "01." instead of "1.")
   - Keep consistent spacing between the number, period, and category name
   - Category names should be concise but descriptive

4. **Keyword considerations**:
   - Include both singular and plural forms when relevant
   - Consider variations in capitalization
   - Include synonyms and related terms
   - Include domain-specific terminology

5. **Testing your category file**:
   You can test your file by running it directly:
   ```bash
   python my_custom_categories.py
   ```
   This will print out the contents in various formats to verify correctness.

## Creating an Excel Category File

Excel files may be easier to edit for users who prefer spreadsheet interfaces.

1. **Create a new Excel file** with the following columns:
   - `summary` (e.g., "01. Category Name")
   - `description` (comma-separated keywords)
   - `expanded_description` (optional)

2. **Fill in your categories and keywords**:
   - Each row represents one category
   - In the `description` column, separate keywords with commas
   - Save the file with a .xlsx extension

## Creating a CSV Category File

CSV files are simple text files that can be edited with any text editor or spreadsheet program.

1. **Create a new CSV file** with the header row:
   ```
   summary,description,expanded_description
   ```

2. **Add one row per category**:
   ```
   "01. Category Name","Keyword1, Keyword2, Related phrase",
   "02. Another Category","Keyword3, Keyword4",
   ```

3. **Save with .csv extension**

## Importing Your Custom Category File

To use your custom category file:

1. **Via the User Interface**:
   - Launch the application
   - Click "Browse" next to "Category File"
   - Select your custom category file

2. **Via Command Line**:
   ```bash
   python main_script.py <pdf_path> -c <path_to_your_custom_category_file> [other options]
   ```

## Tips for Effective Categories

1. **Be comprehensive**: Include all possible categories that might appear in your documents.

2. **Be specific**: Use precise keywords that clearly distinguish between categories.

3. **Consider hierarchy**: Your numbering system can reflect hierarchical relationships.

4. **Consistent naming**: Maintain a consistent naming convention for all categories.

5. **Test and refine**: After running the tool, review the category matches and adjust your category file based on the results.

## Example: Creating a Specialized Category File

Let's walk through creating a specialized category file for residential construction:

1. **Identify key categories** specific to residential construction

2. **Create a new Python file** called `residential_categories.py`:
   ```python
   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   import os
   os.environ['PYTHONHASHSEED'] = '1'  # Use a fixed seed value

   """
   Residential Construction Categories
   """

   import pandas as pd
   import ast

   # Raw data dictionary with numbered categories and their keywords
   raw_data_dict = {
       '01. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
       '02. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
       '03. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
       '04. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
       '05. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
       '06. Plumbing': "['Plumbing', 'Pipes', 'Water heater', 'Fixtures', 'Drains']",
       '07. Electrical': "['Electrical', 'Wiring', 'Outlets', 'Switches', 'Panel', 'Lighting']",
       '08. HVAC': "['HVAC', 'Heating', 'Cooling', 'Ventilation', 'Ductwork', 'Thermostat']",
       '09. Insulation': "['Insulation', 'Vapor barrier', 'Sound insulation', 'Thermal barrier']",
       '10. Drywall': "['Drywall', 'Gypsum', 'Sheetrock', 'Taping', 'Mudding', 'Texturing']",
       '11. Interior Finishing': "['Interior trim', 'Baseboards', 'Crown molding', 'Casings']",
       '12. Flooring': "['Flooring', 'Hardwood', 'Tile', 'Carpet', 'Vinyl', 'Laminate']",
       '13. Cabinetry': "['Cabinets', 'Kitchen cabinets', 'Vanities', 'Built-ins']",
       '14. Countertops': "['Countertops', 'Granite', 'Quartz', 'Marble', 'Laminate counters']",
       '15. Painting': "['Painting', 'Primer', 'Paint', 'Stain', 'Finishes']",
       '16. Appliances': "['Appliances', 'Refrigerator', 'Range', 'Dishwasher', 'Microwave']",
       '17. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
       '18. Driveway and Walkways': "['Driveway', 'Walkway', 'Paths', 'Concrete', 'Pavers']",
       '19. Deck and Patio': "['Deck', 'Patio', 'Porch', 'Outdoor living']",
       '20. Final Inspection': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
   }

   # Continue with the standard processing code...
   data = []
   
   for category, keywords_str in raw_data_dict.items():
       try:
           if isinstance(keywords_str, str) and keywords_str.startswith('[') and keywords_str.endswith(']'):
               keywords = ast.literal_eval(keywords_str)
           else:
               keywords = []
       except:
           keywords = []
       
       keywords_filtered = [k for k in keywords if isinstance(k, str) and k.strip()]
       description = ', '.join(keywords_filtered)
       
       if description:
           expanded_description = f"{description}, {category}"
       else:
           expanded_description = category
       
       data.append({
           'summary': category,
           'description': description,
           'expanded_description': expanded_description
       })

   df = pd.DataFrame(data)
   df_indexed = df.set_index('summary')
   nonvmswchapters = dict(zip(df['summary'], df['description']))
   nonvmswchapters_expanded = dict(zip(df['summary'], df['expanded_description']))
   ```

3. **Use your new category file** with the application to test its effectiveness.

## Troubleshooting

### Common Issues

1. **"Invalid category file" error**:
   - Ensure your file follows the exact required structure
   - Check for syntax errors in Python files
   - Verify column names in Excel/CSV files

2. **Poor matching results**:
   - Add more keywords to your categories
   - Make keywords more specific
   - Check for overlapping terms between categories

3. **Cannot import category file**:
   - Verify file permissions
   - Check file path
   - Ensure correct file format (.py, .xlsx, or .csv)

### Getting Help

If you continue to have issues with your category file, you can:
- Compare your file with the example_categories.py file
- Check the application logs for specific error messages
- Consult the full documentation for additional information 