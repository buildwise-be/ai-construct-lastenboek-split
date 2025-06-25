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

**Python Versie:** Python 3.13 wordt aanbevolen, maar alle versies tussen 3.7 en 3.13 zouden moeten werken.

**Belangrijk Opmerking over Python Omgevingen:** Als u Anaconda of andere Python omgeving managers gebruikt, zorg er dan voor dat u de script uitvoert met de correcte Python interpreter waar de afhankelijkheden zijn geïnstalleerd. U moet mogelijk expliciet de pad naar uw Python interpreter opgeven wanneer u het script uitvoert:

```bash
# Voorbeeld voor Anaconda omgeving
C:\path\to\your\conda\env\python.exe main_script.py [argumenten]
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

## Demo

![Tool Demo](docs/images/Minidemosplit.gif)

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

**Python Version:** Python 3.13 is recommended, but any version between 3.7 and 3.13 should work.

**Important Note on Python Environments:** If you're using Anaconda or other Python environment managers, make sure to run the script with the correct Python interpreter where the dependencies are installed. You may need to explicitly specify the path to your Python interpreter when running the script:

```bash
# Example for Anaconda environment
C:\path\to\your\conda\env\python.exe main_script.py [arguments]
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

2.  **Environment Variables:** Create a `.env` file in the project root if you want to store your `GOOGLE_CLOUD_PROJECT` ID there:
    ```
    GOOGLE_CLOUD_PROJECT="your-project-id"
    ```
3.  **Category File:** The script uses a category definition file. By default, it uses `nonvmswhoofdstukken_pandas.py` (located in the same directory as the script). **Important:** This file *must have the exact same structure* as the example file `example_categories` (also in the project directory). You can modify this example file for your own use, or create a completely new file (as a Python module, Excel, or CSV) provided you respect the required structure. You can select the file to use via the user interface or the command line.

## Usage

### User Interface

Run the script directly from the project's root directory to launch the user interface:

```bash
python main_script.py
```

The user interface allows you to:

*   Select the input PDF file.
*   Select the category definition file.
*   Select the base output directory.
*   Optionally select separate PDF output directories.
*   Enter your Google Cloud Project ID (overrides environment variable).
*   Choose the Gemini model (e.g., 1.5 Pro, 2.0 Flash).
*   Run the complete process.

### Command Line (For Advanced Users)

You can also run the process or individual steps from the command line from the project's root directory. This is more suited for users with technical experience.

**Run complete process:**

```bash
python main_script.py <pdf_path> [-c <category_file>] [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] [--model <model_name>] [--no-explanations] [--no-gui]
```

**Run Step 1 (TOC Generation):**

```bash
python main_script.py <pdf_path> [-o <output_dir>] step1 --no-gui
```

**Run Step 2 (Category Matching):**

```bash
python main_script.py <pdf_path> -c <category_file> -i <toc_dir_from_step1> [-o <output_dir>] [--model <model_name>] step2 --no-gui
```

**Run Step 3 (PDF Extraction):**

```bash
python main_script.py <pdf_path> -c <category_file> -i <category_match_dir_from_step2> [-o <output_dir>] [-s <second_output_dir>] [-t <third_output_dir>] step3 --no-gui
```

Use the `--help` flag for more details on command line options:

```bash
python main_script.py --help
```

## Demo

![Tool Demo](docs/images/Minidemosplit.gif)

## Output

The script creates timestamped directories for each run within the specified output directory (defaulting to an `output` subdirectory within the project folder). Each step generates its own subdirectory (`step1_toc`, `step2_category_matching`, `step3_category_pdfs`) containing working files (JSON, CSV) and the final categorized PDFs.

</details>

<!-- FRENCH -->
<details>
<summary><strong>Français</strong></summary>

## AI Construct PDF Splitter (Français)

Ce projet fournit un script Python (`main_script.py`) pour le traitement des cahiers des charges de construction (lastenboeken), ciblant spécifiquement les documents non-VMSW (Société flamande du logement social).

Le processus effectue les étapes suivantes :

1.  **Génération de la Table des Matières :** Extrait les chapitres et sections du document PDF d'entrée.
2.  **Correspondance des Catégories :** Utilise Google Gemini AI (via Vertex AI) pour faire correspondre les chapitres et sections identifiés à un ensemble prédéfini de catégories.
3.  **Division du Document :** Crée des fichiers PDF séparés pour chaque catégorie, contenant les pages pertinentes du document original.

## Prérequis

Installez les paquets Python requis en utilisant pip :

```bash
pip install -r requirements.txt
```

**Version Python :** Python 3.13 est recommandé, mais toute version entre 3.7 et 3.13 devrait fonctionner.

**Important Note on Python Environments:** If you're using Anaconda or other Python environment managers, make sure to run the script with the correct Python interpreter where the dependencies are installed. You may need to explicitly specify the path to your Python interpreter when running the script:

```bash
# Example for Anaconda environment
C:\path\to\your\conda\env\python.exe main_script.py [arguments]
```

Installez Google Cloud CLI (voir [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)) et exécutez les commandes suivantes avant la configuration :

```bash
pip install --upgrade google-genai
gcloud auth application-default login
```

### Instructions d'installation détaillées pour Google Cloud CLI

#### Pour Windows :
1. Téléchargez l'installateur Google Cloud SDK depuis : https://cloud.google.com/sdk/docs/install
2. Exécutez le fichier GoogleCloudSDKInstaller.exe téléchargé
3. Suivez les instructions d'installation
4. Une fois terminé, l'installateur ouvrira un terminal pour exécuter `gcloud init`
5. Après l'initialisation, exécutez :
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

#### Pour macOS/Linux :
1. Téléchargez le package approprié depuis : https://cloud.google.com/sdk/docs/install
2. Extrayez l'archive (fichier tar.gz) vers l'emplacement de votre choix
3. Exécutez le script d'installation : `./google-cloud-sdk/install.sh`
4. Initialisez le SDK : `./google-cloud-sdk/bin/gcloud init`
5. Après l'initialisation, exécutez :
   ```
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```

Le script nécessite les paquets suivants :

*   `pandas`
*   `python-dotenv`
*   `PyPDF2`
*   `google-cloud-aiplatform`
*   `google-generativeai`
*   `PyMuPDF`
*   `PySide6`

## Configuration

1.  **Google Cloud :**
    *   Vous avez besoin d'un projet Google Cloud avec l'API Vertex AI activée.
    *   Définissez la variable d'environnement `GOOGLE_CLOUD_PROJECT` avec votre ID de projet, ou saisissez-le dans l'interface utilisateur.
    *   Assurez-vous d'être connecté à Google Cloud (par exemple, en utilisant `gcloud auth application-default login`).
    *   **Conforme au RGPD :** Nous travaillons avec l'initialisation de Google Vertex AI pour garantir que toutes les données sont traitées conformément à la réglementation RGPD.

    **Création d'un projet Vertex AI :**
    *   Accédez à la [Console Google Cloud](https://console.cloud.google.com/)
    *   Créez un nouveau projet ou sélectionnez un projet existant
    *   Activez l'API Vertex AI pour votre projet via la bibliothèque d'API
    *   **Important :** Vous devez associer des informations de facturation à votre projet Google Cloud pour utiliser les services Vertex AI, même dans le cadre de l'utilisation gratuite
    *   Vous avez deux options pour définir les détails de votre projet :
        * Définir cela comme variable d'environnement (voir ci-dessous)
        * OU entrer cela directement via l'interface utilisateur (UI) de l'application

2.  **Variables d'Environnement :** Créez un fichier `.env` à la racine du projet si vous souhaitez y stocker votre ID `GOOGLE_CLOUD_PROJECT` :
    ```
    GOOGLE_CLOUD_PROJECT="votre-id-projet"
    ```
3.  **Fichier de Catégories :** Le script utilise un fichier de définition de catégories. Par défaut, il utilise `nonvmswhoofdstukken_pandas.py` (situé dans le même répertoire que le script). **Important :** Ce fichier *doit avoir exactement la même structure* que le fichier d'exemple `example_categories` (également dans le répertoire du projet). Vous pouvez modifier ce fichier d'exemple pour votre propre usage, ou créer un tout nouveau fichier (en tant que module Python, Excel ou CSV) à condition de respecter la structure requise. Vous pouvez sélectionner le fichier à utiliser via l'interface utilisateur ou la ligne de commande.

## Utilisation

### Interface Utilisateur

Exécutez le script directement depuis le répertoire racine du projet pour lancer l'interface utilisateur :

```bash
python main_script.py
```

L'interface utilisateur vous permet de :

*   Sélectionner le fichier PDF d'entrée.
*   Sélectionner le fichier de définition des catégories.
*   Sélectionner le répertoire de sortie de base.
*   Sélectionner éventuellement des répertoires de sortie PDF distincts.
*   Entrer votre ID de projet Google Cloud (remplace la variable d'environnement).
*   Choisir le modèle Gemini (par ex., 1.5 Pro, 2.0 Flash).
*   Exécuter le processus complet.

### Ligne de Commande (Pour Utilisateurs Avancés)

Vous pouvez également exécuter le processus ou des étapes individuelles depuis la ligne de commande à partir du répertoire racine du projet. Ceci est plus adapté aux utilisateurs ayant une expérience technique.

**Exécuter le processus complet :**

```bash
python main_script.py <chemin_pdf> [-c <fichier_catégorie>] [-o <répertoire_sortie>] [-s <deuxième_répertoire_sortie>] [-t <troisième_répertoire_sortie>] [--model <nom_modèle>] [--no-explanations] [--no-gui]
```

**Exécuter l'Étape 1 (Génération Table des Matières) :**

```bash
python main_script.py <chemin_pdf> [-o <répertoire_sortie>] step1 --no-gui
```

**Exécuter l'Étape 2 (Correspondance Catégories) :**

```bash
python main_script.py <chemin_pdf> -c <fichier_catégorie> -i <répertoire_tdm_étape1> [-o <répertoire_sortie>] [--model <nom_modèle>] step2 --no-gui
```

**Exécuter l'Étape 3 (Extraction PDF) :**

```bash
python main_script.py <chemin_pdf> -c <fichier_catégorie> -i <répertoire_corres_catégorie_étape2> [-o <répertoire_sortie>] [-s <deuxième_répertoire_sortie>] [-t <troisième_répertoire_sortie>] step3 --no-gui
```

Utilisez l'option `--help` pour plus de détails sur les options de la ligne de commande :

```bash
python main_script.py --help
```

## Démo

![Tool Demo](docs/images/Minidemosplit.gif)

## Sortie

Le script crée des répertoires horodatés pour chaque exécution dans le répertoire de sortie spécifié (par défaut, un sous-répertoire `output` dans le dossier du projet). Chaque étape génère son propre sous-répertoire (`step1_toc`, `step2_category_matching`, `step3_category_pdfs`) contenant des fichiers de travail (JSON, CSV) et les PDF finaux classés par catégorie.

</details>
