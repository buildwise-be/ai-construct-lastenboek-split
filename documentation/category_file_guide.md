# Creating and Customizing Category Files (Non-VMSW Documents)

This guide explains how to create and customize category files for **Non-VMSW document processing**. 

## 🔢 VMSW vs 🤖 Non-VMSW: When Do You Need This Guide?

| Document Type | Category Files | This Guide Applies |
|---------------|----------------|-------------------|
| **🔢 VMSW Documents** | ❌ Not needed - uses built-in categories | ❌ Skip this guide |
| **🤖 Non-VMSW Documents** | ✅ Required - custom category files | ✅ Use this guide |

### 🔢 VMSW Documents (No Setup Needed)
If you're processing VMSW documents, you can **skip this entire guide**. VMSW processing uses built-in categories that map directly from chapter numbers:

- `00.` → `00. Algemene Bepalingen`
- `01.` → `01. Afbraak en Grondwerken`
- `02.40` → `02. Funderingen en Kelders`
- And 31 more standard VMSW categories...

Just select "VMSW Document" in the application and you're ready to go!

---

## 🤖 Non-VMSW Documents: Custom Category Files

For Non-VMSW documents (custom construction docs, international formats, non-standard numbering), you need to create or customize category files that define how AI should categorize your document sections.

### What is a Category File?

A category file defines the construction categories that the AI will use to match chapters and sections from your PDF documents. Each category includes:

- A numbered identifier and category name (e.g., "01. Foundations")
- A list of keywords or phrases associated with that category
- Additional metadata used by the application for AI matching

### Available Formats

You can create category files in three formats:

1. **Python Module** (.py file) - Recommended for flexibility and performance
2. **Excel Spreadsheet** (.xlsx file) - Easier to edit for non-programmers
3. **CSV File** (.csv file) - Simple text-based format

---

## 🐍 Creating a Python Module Category File

This is the recommended format as it provides the most flexibility and performance.

### Quick Start: Use the Example File

The fastest way to get started:

1. **Copy the example**:
   ```bash
   cp example_categories.py my_custom_categories.py
   ```

2. **Edit for your domain** (see customization section below)

3. **Use in application**: Browse to `my_custom_categories.py` in the GUI

### Basic Structure

A Python module category file needs:

1. A `raw_data_dict` dictionary containing categories and their keywords
2. Processing code to convert the raw dictionary into the required DataFrame structure
3. Export variables used by the application

### Step-by-Step Customization

1. **Open your category file** in a text editor

2. **Edit the raw_data_dict**:
   ```python
   raw_data_dict = {
       '01. Foundations': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
       '02. Structure': "['Framing', 'Beams', 'Columns', 'Steel', 'Concrete']",
       '03. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing']",
       # Add more categories as needed
   }
   ```

3. **Key formatting considerations**:
   - Category numbers should be padded with zeros (e.g., "01." instead of "1.")
   - Keep consistent spacing between the number, period, and category name
   - Category names should be concise but descriptive

4. **Keyword strategy**:
   - Include both singular and plural forms when relevant
   - Consider variations in capitalization
   - Include synonyms and related terms
   - Include domain-specific terminology

5. **Test your file**:
   ```bash
   python my_custom_categories.py
   ```

---

## 📊 Creating an Excel Category File

Excel files are easier for users who prefer spreadsheet interfaces.

### Structure
Create an Excel file with these columns:
- `summary` (e.g., "01. Foundations")
- `description` (comma-separated keywords)
- `expanded_description` (optional)

### Example:
| summary | description | expanded_description |
|---------|-------------|---------------------|
| 01. Foundations | Foundation, Footings, Slab, Basement | Foundation, Footings, Slab, Basement, 01. Foundations |
| 02. Structure | Framing, Beams, Columns, Steel | Framing, Beams, Columns, Steel, 02. Structure |

---

## 📄 Creating a CSV Category File

CSV files are simple text files that can be edited with any text editor.

### Format:
```csv
summary,description,expanded_description
"01. Foundations","Foundation, Footings, Slab, Basement",
"02. Structure","Framing, Beams, Columns, Steel",
"03. Roofing","Roofing, Shingles, Tiles, Gutters",
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab', 'Basement', 'Crawl space']",
    '03. Framing': "['Framing', 'Studs', 'Joists', 'Rafters', 'Trusses', 'Beams']",
    '04. Roofing': "['Roofing', 'Shingles', 'Tiles', 'Gutters', 'Flashing', 'Eaves']",
    '05. Exterior': "['Siding', 'Stucco', 'Brick', 'Stone', 'Exterior finishes']",
    '06. Windows and Doors': "['Windows', 'Doors', 'Entry', 'Sliding door', 'Garage door']",
    '07. Mechanical': "['Plumbing', 'HVAC', 'Electrical', 'Heating', 'Cooling']",
    '08. Interior': "['Drywall', 'Flooring', 'Cabinets', 'Countertops', 'Painting']",
    '09. Landscaping': "['Landscaping', 'Grading', 'Lawn', 'Plants', 'Irrigation']",
    '10. Final': "['Final inspection', 'Punch list', 'Walk-through', 'Completion']"
}
```

### Commercial Construction
```python
raw_data_dict = {
    '01. Site Work': "['Site preparation', 'Earthwork', 'Utilities', 'Paving']",
    '02. Concrete': "['Concrete', 'Reinforcement', 'Formwork', 'Foundation']",
    '03. Masonry': "['Masonry', 'Brick', 'Block', 'Stone', 'Mortar']",
    '04. Metals': "['Structural steel', 'Metal fabrication', 'Reinforcement']",
    '05. Wood & Plastics': "['Rough carpentry', 'Finish carpentry', 'Millwork']",
    '06. Thermal & Moisture': "['Insulation', 'Roofing', 'Siding', 'Waterproofing']",
    '07. Openings': "['Doors', 'Windows', 'Storefronts', 'Glazing']",
    '08. Finishes': "['Flooring', 'Wall finishes', 'Ceiling', 'Painting']",
    '09. Mechanical': "['HVAC', 'Plumbing', 'Fire protection']",
    '10. Electrical': "['Electrical', 'Lighting', 'Communications', 'Security']"
}
```

---

## 🎯 Example: Specialized Category Files

### Residential Construction
```python
raw_data_dict = {
    '01. Site Preparation': "['Excavation', 'Grading', 'Site clearance', 'Utilities']",
    '02. Foundation': "['Foundation', 'Footings', 'Slab