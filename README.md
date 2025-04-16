<h1 align="center" style="color: #0087B7;">AI Construct PDF Opdeler</h1>

<p align="center">
  <img src="docs/images/BWlogo.png" alt="BW Logo" width="100"/> &nbsp;&nbsp;&nbsp;&nbsp; <img src="docs/images/aico.png" alt="AICO Logo" width="100"/>
</p>

<p align="center">
  <em>Deel uw lastenboek op in delen per onderaannemer</em>
</p>

<!-- DUTCH -->
<details>
<summary><strong>Nederlands</strong></summary>

## AI Construct PDF Opdeler (Nederlands)

Dit project biedt een Python-script (`main_script.py`) voor het verwerken van specificatiedocumenten voor de bouw (lastenboeken), specifiek gericht op niet-VMSW (Vlaamse Maatschappij voor Sociaal Wonen) documenten.

Het proces voert de volgende stappen uit:

1.  **Inhoudsopgave Generatie:** Extraheert hoofdstukken en secties uit het ingevoerde PDF-document.
2.  **Categorie Matching:** Gebruikt Google Gemini AI (via Vertex AI) om de geïdentificeerde hoofdstukken en secties te matchen met een vooraf gedefinieerde set categorieën.
3.  **Document Splitsing:** Creëert afzonderlijke PDF-bestanden voor elke categorie, die de relevante pagina's uit het originele document bevatten.

## Vereisten

Installeer de vereiste Python-pakketten met pip:

```bash
pip install -r requirements.txt
```

Installeer de Google Cloud CLI (zie [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)) en voer de volgende commando's uit voordat u begint:

```bash
pip install --upgrade google-genai
gcloud auth application-default login
```

### Gedetailleerde Google Cloud CLI installatie-instructies

#### Voor Windows:
1. Download de Google Cloud SDK installer van: https://cloud.google.com/sdk/docs/install
2. Voer het gedownloade GoogleCloudSDKInstaller.exe bestand uit
3. Volg de installatie-instructies
4. Na voltooiing zal de installer een terminal openen om `gcloud init` uit te voeren
5. Na initialisatie, voer uit:
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

#### Voor macOS/Linux:
1. Download het juiste pakket van: https://cloud.google.com/sdk/docs/install
2. Pak het archief (tar.gz bestand) uit naar de gewenste locatie
3. Voer het installatiescript uit: `./google-cloud-sdk/install.sh`
4. Initialiseer de SDK: `./google-cloud-sdk/bin/gcloud init`
5. Na initialisatie, voer uit:
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

Het script vereist de volgende pakketten:

*   `pandas`
*   `python-dotenv`
*   `PyPDF2`
*   `google-cloud-aiplatform`
*   `google-generativeai`
*   `PyMuPDF`
*   `PySide6`

## Setup

1.  **Google Cloud:**
    *   U heeft een Google Cloud-project nodig waarbij de Vertex AI API is ingeschakeld.
    *   Stel de `GOOGLE_CLOUD_PROJECT` omgevingsvariabele in op uw project-ID, of voer deze in via de gebruikersinterface.
    *   Zorg ervoor dat u bent aangemeld bij Google Cloud (bijv. met `gcloud auth application-default login`).
    *   **GDPR-compliant:** We werken met Google Vertex AI initialisatie om ervoor te zorgen dat alle data in overeenstemming met de GDPR-regelgeving wordt verwerkt.

    **Een Vertex AI Project aanmaken:**
    *   Ga naar [Google Cloud Console](https://console.cloud.google.com/)
    *   Maak een nieuw project aan of selecteer een bestaand project
    *   Activeer de Vertex AI API voor uw project via de API-bibliotheek
    *   **Belangrijk:** U moet factureringsgegevens aan uw Google Cloud-project koppelen om de Vertex AI-diensten te kunnen gebruiken, zelfs binnen de gratis gebruikslimiet
    *   U heeft twee opties voor het instellen van uw projectgegevens:
        * Stel deze in als omgevingsvariabele (zie hieronder)
        * OF voer deze rechtstreeks in via de gebruikersinterface (UI) van de applicatie

2.  **Omgevingsvariabelen:** Maak een `.env`-bestand aan in de hoofdmap van het project als u uw `GOOGLE_CLOUD_PROJECT`-ID daar wilt opslaan:
    ```
    GOOGLE_CLOUD_PROJECT="uw-project-id"
    ```
3.  **Categoriebestand:** Het script gebruikt een categorie-definitiebestand. Standaard wordt `nonvmswhoofdstukken_pandas.py` (in dezelfde map als het script) gebruikt. **Belangrijk:** Dit bestand *moet exact dezelfde structuur hebben* als het voorbeeldbestand `example_categories` (ook in de projectmap). U kunt dit voorbeeldbestand aanpassen voor eigen gebruik, of een volledig nieuw bestand aanmaken (als Python-module, Excel, of CSV) mits u de vereiste structuur respecteert. U kunt het te gebruiken bestand selecteren via de gebruikersinterface of de command line.

## Gebruik

### Gebruikersinterface

Voer het script rechtstreeks uit vanuit de hoofdmap van het project om de gebruikersinterface te starten:

```bash
python main_script.py
```

De gebruikersinterface stelt u in staat om:

*   Het invoer PDF-bestand te selecteren.
*   Het categorie-definitiebestand te selecteren.
*   De basis uitvoermap te selecteren.
*   Optioneel afzonderlijke PDF-uitvoermappen te selecteren.
*   Uw Google Cloud Project ID in te voeren (overschrijft omgevingsvariabele).
*   Het Gemini-model te kiezen (bijv. 1.5 Pro, 2.0 Flash).
*   Het volledige proces uit te voeren.

### Command Line (Voor Gevorderde Gebruikers)

U kunt het proces of afzonderlijke stappen ook uitvoeren vanaf de command line (opdrachtprompt) vanuit de hoofdmap van het project. Dit is meer geschikt voor gebruikers met technische ervaring.

**Volledig proces uitvoeren:**

```bash
python main_script.py <pdf_pad> [-c <categorie_bestand>] [-o <uitvoer_map>] [-s <tweede_uitvoer_map>] [-t <derde_uitvoer_map>] [--model <model_naam>] [--no-explanations] [--no-gui]
```

**Stap 1 uitvoeren (Inhoudsopgave Generatie):**

```bash
python main_script.py <pdf_pad> [-o <uitvoer_map>] step1 --no-gui
```

**Stap 2 uitvoeren (Categorie Matching):**

```bash
python main_script.py <pdf_pad> -c <categorie_bestand> -i <toc_map_van_stap1> [-o <uitvoer_map>] [--model <model_naam>] step2 --no-gui
```

**Stap 3 uitvoeren (PDF Extractie):**

```bash
python main_script.py <pdf_pad> -c <categorie_bestand> -i <categorie_match_map_van_stap2> [-o <uitvoer_map>] [-s <tweede_uitvoer_map>] [-t <derde_uitvoer_map>] step3 --no-gui
```

Gebruik de `--help` vlag voor meer details over de command line opties:

```bash
python main_script.py --help
```

## Uitvoer

Het script maakt voor elke uitvoering mappen met een tijdstempel aan binnen de opgegeven uitvoermap (standaard een `output` submap binnen de projectmap). Elke stap genereert zijn eigen submap (`step1_toc`, `step2_category_matching`, `step3_category_pdfs`) met werkbestanden (JSON, CSV) en de uiteindelijke gecategoriseerde PDF's.

</details>

<!-- ENGLISH -->
<details open>
<summary><strong>English</strong></summary>

## AI Construct PDF Splitter (English)

This project provides a Python script (`main_script.py`) for processing construction specification documents (lastenboeken), specifically targeting non-VMSW (Flemish Social Housing Company) documents.

The process performs the following steps:

1.  **Table of Contents Generation:** Extracts chapters and sections from the input PDF document.
2.  **Category Matching:** Uses Google Gemini AI (via Vertex AI) to match the identified chapters and sections against a predefined set of categories.
3.  **Document Splitting:** Creates separate PDF files for each category, containing the relevant pages from the original document.

## Requirements

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

Install the Google Cloud CLI (see [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)) and run the following commands before setup:

```bash
pip install --upgrade google-genai
gcloud auth application-default login
```

### Detailed Google Cloud CLI Installation Instructions

#### For Windows:
1. Download the Google Cloud SDK installer from: https://cloud.google.com/sdk/docs/install
2. Run the downloaded GoogleCloudSDKInstaller.exe file
3. Follow the installation prompts
4. When complete, the installer will open a terminal to run `gcloud init`
5. After initialization, run:
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

#### For macOS/Linux:
1. Download appropriate package from: https://cloud.google.com/sdk/docs/install
2. Extract the archive (tar.gz file) to your preferred location
3. Run the installation script: `./google-cloud-sdk/install.sh`
4. Initialize the SDK: `./google-cloud-sdk/bin/gcloud init`
5. After initialization, run:
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

The script requires the following packages:

*   `pandas`
*   `python-dotenv`
*   `PyPDF2`
*   `google-cloud-aiplatform`
*   `google-generativeai`
*   `PyMuPDF`
*   `PySide6`

## Setup

1.  **Google Cloud:**
    *   You need a Google Cloud project with the Vertex AI API enabled.
    *   Set the `GOOGLE_CLOUD_PROJECT` environment variable to your project ID, or enter it in the user interface.
    *   Ensure you are logged into Google Cloud (e.g., using `gcloud auth application-default login`).
    *   **GDPR compliant:** We work with Google Vertex AI initialization to ensure all data is processed in compliance with GDPR regulations.

    **Creating a Vertex AI Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/)
    *   Create a new project or select an existing project
    *   Enable the Vertex AI API for your project via the API library
    *   **Important:** You must attach billing information to your Google Cloud project to use Vertex AI services, even within the free usage tier
    *   You have two options for setting your project details:
        * Set this as an environment variable (see below)
        * OR enter this directly via the application's user interface (UI)

2.  **Environment Variables:** Create a `.env` file in the project root if you want to store your `GOOGLE_CLOUD_PROJECT`