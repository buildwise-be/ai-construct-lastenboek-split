# AI Construct PDF Opdeler - Demo

This is a demonstration setup where steps 1 and 2 of the PDF processing pipeline have already been completed. You only need to run step 3 to generate the categorized PDF files.

## Files in this Demo

- `sample_lastenboek.pdf`: A sample construction specification document
- `step3_input/chapters.json`: The output from step 1 (TOC extraction)
- `step3_input/unified_category_matches.csv`: The output from step 2 (category matching)

## How to Run the Demo

### Using the Provided Scripts

1. On Windows, double-click the `run_demo.bat` file
2. On Unix-like systems, run `./run_demo.sh` in a terminal

These scripts will launch the GUI interface. From there, follow these steps:

1. Select `sample_lastenboek.pdf` as the input file
2. Select `../example_categories.py` as the category file
3. Set `step3_input` as the input directory
4. Set `output` as the output directory
5. Choose to run Step 3 (Split) only

### Alternative: Command Line (Advanced)

For advanced users, step 3 can also be run directly from the command line:

```bash
# For Windows with Anaconda
C:\path\to\your\python.exe main_script.py sample_lastenboek.pdf -c example_categories.py -i step3_input -o output step3 --no-gui

# For Unix systems
python main_script.py sample_lastenboek.pdf -c example_categories.py -i step3_input -o output step3 --no-gui
```

## Expected Result

After running step 3, you should see a new directory `output/step3_category_pdfs` containing multiple PDFs, each corresponding to a different category from the construction specification document.

## How This Works

In a normal workflow, you would:
1. Run step 1 to extract the table of contents from a PDF
2. Run step 2 to match the chapters and sections to categories
3. Run step 3 to split the PDF into separate files by category

This demo allows you to skip steps 1 and 2, which are more computationally intensive and require AI categorization, and directly see the results of the PDF splitting in step 3. 