@echo off
rem ============================================================================
rem Demo Script Runner
rem ============================================================================
rem This script runs the demo, assuming necessary dependencies are installed.

echo Running AI Construct PDF Opdeler Demo...
echo.
echo This will launch the GUI where you can:
echo 1. Select sample_lastenboek.pdf as the input file
echo 2. Select ../example_categories.py as the category file
echo 3. Set step3_input as the input directory
echo 4. Set output as the output directory
echo 5. Run Step 3 (Split)
echo.

rem Use a generic python command, assuming it's in the system PATH
rem This is more portable than a hardcoded absolute path.
python demo_script.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo GUI launched successfully.
) else (
    echo An error occurred while launching the GUI. Please check the output above.
)

pause 