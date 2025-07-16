# AI Construct PDF Opdeler

<div align="center" style="display: flex; align-items: center; justify-content: center; gap: 20px;">
  <img src="Requirements/Logo/BWlogo.png" alt="Buildwise Logo" height="70" width="70" style="vertical-align: middle;"/>
  <img src="Requirements/Logo/aiconew.svg" alt="AI Construct Logo" height="70" width="240" style="vertical-align: middle;"/>
</div>

<p align="center">
  <em>GUI-toepassing voor het opdelen van bouwdocumenten per aannemerscategorie</em>
</p>

---

## 🌐 Taal / Language / Langue

📖 **[English](README.en.md)** | 🇳🇱 **Nederlands** | 🇫🇷 **[Français](README.fr.md)**

---

## Hybride Verwerkingssysteem

Deze applicatie ondersteunt zowel VMSW als Non-VMSW bouwdocumenten:

- **VMSW Documenten**: Gebruikt nummer-gebaseerde categoriematching
- **Non-VMSW Documenten**: Gebruikt AI semantische analyse met Google Gemini
- **Automatische Detectie**: Detecteert documenttype met handmatige overschrijvingsoptie
- **Prestaties**: VMSW categorisatie is sneller dan AI-verwerking

---

## Overzicht

De AI Construct PDF Opdeler is een tool voor het verwerken van bouwspecificatiedocumenten (lastenboeken). Het analyseert documenten, extraheert structuur, categoriseert inhoud en splitst documenten op in aannemer-specifieke PDF's.

### Belangrijkste Functies

- **Hybride Verwerking**: Combineert nummer-gebaseerde VMSW matching met AI semantische analyse
- **Documenttype Selectie**: Kies tussen VMSW en Non-VMSW verwerkingsmodi
- **Model Selectie**: Kies tussen Gemini 2.5 Pro en Gemini 2.5 Flash
- **Multi-Output**: Genereer PDF's in meerdere uitvoermappen tegelijkertijd
- **Logging**: Gedetailleerde logging met tijdstempels

### Verwerkingspijplijn

1. **Inhoudsopgave Extractie**: Extraheert hoofdstukken en secties uit PDF-documenten
2. **Categorisatie**: 
   - **VMSW**: Directe nummermapping (bijv. "02.40" → "02. Funderingen en Kelders")
   - **Non-VMSW**: AI semantische matching met voorgedefinieerde categorieën
3. **Document Splitsing**: Creëert aparte PDF's voor elke bouwcategorie

---

## 📦 Installatie

### Vereisten

- **Python**: 3.7 - 3.13 (3.13 aanbevolen)
- **Internetverbinding**: Vereist voor alle documenten (inhoudsopgave extractie gebruikt AI)
- **Google Cloud Account**: Vereist voor alle documenten (inhoudsopgave extractie + Non-VMSW categorisatie)

> **💡 Kosten**: De applicatie is gratis. Kosten zijn alleen voor AI-model gebruik (Vertex AI/Gemini) bij documentverwerking.

### Snelle Installatie

1. **Voer het installatiescript uit:**
   ```bash
   python setup.py
   ```
   Dit zal:
   - Python versiecompatibiliteit controleren
   - Alle afhankelijkheden installeren
   - Benodigde mappen aanmaken
   - Validatiecontroles uitvoeren

2. **Configureer omgeving (optioneel):**
   ```bash
   cp .env.example .env
   # Bewerk .env met uw Google Cloud Project ID
   ```

### Handmatige Installatie

1. **Installeer afhankelijkheden:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Cloud Installatie:**
   ```bash
   # Installeer Google Cloud CLI: https://cloud.google.com/sdk/docs/install
   pip install --upgrade google-genai
   gcloud auth application-default login
   ```
   
   **🔒 Privacy & GDPR**: De Vertex AI integratie verwerkt documentgegevens GDPR-conform binnen Google Cloud's Europese datacenters.

3. **Valideer installatie:**
   ```bash
   python src/utils/validation.py
   ```

### Start Applicatie

```bash
python src/main.py
```

---

## Gebruik van de Applicatie

### Snelle Start

1. **Selecteer PDF**: Kies uw bouwdocument
2. **Documenttype**: Selecteer "VMSW Document" of "Non-VMSW Document"
3. **Uitvoermap**: Kies waar resultaten opgeslagen worden
4. **Verwerken**: Klik op "Volledige Pijplijn Uitvoeren"

### Documenttype Gids

| Documenttype | Wanneer Gebruiken | Vereisten | Categorisatie Snelheid |
|--------------|-------------------|-----------|------------------------|
| **VMSW Document** | Documenten met VMSW-nummering (XX.YY formaat) | Google Cloud + ingebouwde categorieën | Snelle categorisatie |
| **Non-VMSW Document** | Andere bouwdocumenten | Google Cloud + Categoriebestand | AI categorisatie |

### Geavanceerde Opties

- **Model Selectie**: Kies Gemini 2.5 Pro (nauwkeurigheid) of Flash (snelheid)
- **Meerdere Outputs**: Stel tot 3 verschillende uitvoermappen in
- **Individuele Stappen**: Voer inhoudsopgave extractie, categorisatie of PDF-splitsing afzonderlijk uit
- **Logging**: Bekijk gedetailleerde verwerkingslogs

---

## Project Architectuur

```
├── src/                          # Modulaire architectuur
│   ├── main.py                   # Applicatie-ingangspunt
│   ├── config/                   # Configuratiebeheer
│   │   ├── __init__.py
│   │   └── settings.py           # Gecentraliseerde instellingen
│   ├── core/                     # Kernverwerkingslogica
│   │   ├── __init__.py
│   │   ├── ai_client.py          # Vertex AI-integratie
│   │   ├── pdf_processor.py      # Inhoudsopgave extractie & PDF-splitsing
│   │   ├── category_matcher.py   # AI-categoriematching
│   │   ├── hybrid_matcher.py     # Documenttypeafhandeling
│   │   ├── vmsw_matcher.py       # VMSW nummer-gebaseerde matching
│   │   └── file_utils.py         # Bestandsoperaties
│   ├── gui/                      # Gebruikersinterface componenten
│   │   ├── __init__.py
│   │   ├── main_window.py        # Hoofdapplicatievenster
│   │   ├── components/           # Herbruikbare UI-componenten
│   │   │   ├── __init__.py
│   │   │   └── styled_components.py
│   │   └── workers/              # Achtergrondverwerking
│   │       ├── __init__.py
│   │       └── processing_worker.py
│   ├── models/                   # Datamodellen en categorieën
│   │   ├── __init__.py
│   │   └── categories.py         # Categoriedefinities
│   └── utils/                    # Hulpprogramma modules
│       ├── __init__.py
│       ├── validation.py         # Installatie validatie
│       └── migration.py          # Migratie utilities
├── launch.py                     # Eenvoudig startscript
├── setup.py                      # Installatiescript
├── example_categories.py         # Categoriesjabloon
├── VMSWcat.json                  # VMSW categorieën configuratie
├── requirements.txt              # Python afhankelijkheden
├── .env.example                  # Omgevingsconfiguratie sjabloon
└── documentation/                # Uitgebreide documentatie
```

---

## VMSW vs Non-VMSW Verwerking

### VMSW Documenten

**Geschikt voor**: Nederlandse bouwdocumenten met standaard VMSW-nummering

**Hoe het werkt**:
- Wijst hoofdstuknummers direct toe aan categorieën (bijv. "02" → "02. Funderingen en Kelders")
- De categorisatiestap is snel en vereist geen AI
- Ingebouwde sloopdetectie
- Hoge betrouwbaarheid door gestandaardiseerde nummering

**Categorieën omvatten**:
- 00. Algemene Bepalingen
- 01. Afbraak en Grondwerken
- 02. Funderingen en Kelders
- En 31 meer standaard VMSW-categorieën...

### Non-VMSW Documenten

**Geschikt voor**: Aangepaste bouwdocumenten, internationale formaten

**Hoe het werkt**:
- AI analyseert inhoud semantisch
- Matcht tegen aangepaste categoriedefinities
- Biedt betrouwbaarheidsscores en uitleg (resultaten kunnen variëren)
- Retry-logica voor betere resultaten

**Vereisten**:
- Aangepast categoriebestand (Python, Excel of CSV)
- Google Cloud project met Vertex AI ingeschakeld
- **🔒 GDPR-conforme gegevensverwerking** via Vertex AI (Europese infrastructuur)

---

## VMSW Categorieën Aanpassen

De applicatie biedt opties voor het aanpassen van hoe VMSW-documenten worden gegroepeerd in aannemerscategorieën.

### Standaard VMSW Groepering

Standaard gebruiken VMSW-documenten een tweeniveaus mappingsysteem:

1. **Directe Hoofdstuk Mapping** (`src/core/vmsw_matcher.py`): Wijst VMSW-hoofdstukken (00-42) toe aan brede bouwcategorieën
2. **Gedetailleerde Artikel Mapping** (`VMSWcat.json`): Wijst specifieke VMSW-artikelen toe aan gespecialiseerde groeperingen

### Aanpassingsopties

#### Optie 1: Wijzig Hoofdstuk Groeperingen (Eenvoudig)

Bewerk het `vmsw_mapping` woordenboek in `src/core/vmsw_matcher.py`:

```python
self.vmsw_mapping = {
    "00": "33. Advies en Studies",
    "01": "01. Afbraak en Grondwerken", 
    "02": "02. Funderingen en Kelders",
    # Voeg uw aangepaste mappings toe:
    "15": "15. HVAC",  # Standaard
    "15": "15. Klimatisering",  # Aangepaste naam
    # Groepeer meerdere hoofdstukken samen:
    "64": "15. HVAC",  # Voeg samen met bestaande HVAC
    "65": "15. HVAC",
    "66": "15. HVAC",
}
```

#### Optie 2: Creëer Aannemer-Specifieke Groeperingen

Wijzig `VMSWcat.json` om aannemer-specifieke categorieën te creëren:

```json
[
  {
    "art_nr": "20 + 21 + 22",
    "omschrijving": "METSELWERKEN - Aannemer A"
  },
  {
    "art_nr": "30 + 31 + 32", 
    "omschrijving": "DAKWERKEN - Aannemer B"
  },
  {
    "art_nr": "64 + 65 + 66 + 67 + 68 + 69",
    "omschrijving": "HVAC - Aannemer C"
  }
]
```

### Gemeenschappelijke Groeperingsstrategieën

#### Op Vak/Specialiteit
```json
{
  "art_nr": "10 + 17 + 90 + 91",
  "omschrijving": "GRONDWERKEN EN RIOLERING"
},
{
  "art_nr": "64 + 65 + 66 + 67 + 68 + 69", 
  "omschrijving": "HVAC TOTAALPAKKET"
}
```

#### Op Projectfase
```json
{
  "art_nr": "03 + 10 + 11 + 13",
  "omschrijving": "FASE 1 - RUWBOUW"
},
{
  "art_nr": "50 + 51 + 52 + 53",
  "omschrijving": "FASE 3 - AFWERKING"
}
```

---

## Configuratie

### Omgevingsvariabelen

Creëer een `.env` bestand van `.env.example`:

```env
# Vereist voor AI-verwerking
GOOGLE_CLOUD_PROJECT_ID=uw-project-id

# Optionele instellingen
VERTEX_AI_REGION=europe-west1
VERTEX_AI_MODEL=gemini-2.5-flash
DEFAULT_OUTPUT_DIR=output
LOG_LEVEL=INFO
```

### Categoriebestanden

Plaats uw categoriedefinitiebestanden in de projectroot:
- `example_categories.py` (standaard sjabloon)
- Aangepaste categoriebestanden kunnen in de GUI geselecteerd worden

---

## Uitvoerstructuur

Elke verwerkingsrun creëert een map met tijdstempel:

```
output/
└── pdf_processor_step3_category_pdfs_YYYYMMDD_HHMMSS/
    ├── step1_toc/              # Inhoudsopgave extractie
│   ├── chapters.json
│   ├── sections.json
│   └── inhoudsopgave.csv
    ├── step2_category_matching/ # Categorisatieresultaten
    │   ├── category_matches.json
    │   ├── category_statistics.json
    │   └── matching_details.csv
    └── step3_category_pdfs/     # Finale gecategoriseerde PDF's
        ├── 01_Afbraak_en_Grondwerken.pdf
        ├── 02_Funderingen_en_Kelders.pdf
        └── category_summary.json
```

---

## Validatie & Probleemoplossing

### Voer Validatiecontrole Uit
```bash
python src/utils/validation.py
```

Dit controleert:
- Python versiecompatibiliteit
- Alle afhankelijkheden geïnstalleerd
- Bestandsstructuur integriteit
- Module imports werkend
- Configuratie geldigheid

### Veelvoorkomende Problemen

**Import Fouten:**
```bash
pip install -r requirements.txt
```

**Ontbrekende Bestanden:**
```bash
python setup.py
```

**Configuratieproblemen:**
- Controleer uw `.env` bestand
- Verifieer Google Cloud Project ID
- Zorg ervoor dat categoriebestanden bestaan

---

## 🛠️ Geavanceerd Gebruik

### Applicatie Starten

**Optie 1: Gebruik de launcher**
```bash
python launch.py
```

**Optie 2: Directe uitvoering**
```bash
python src/main.py
```

**Optie 3: Met validatie**
```bash
python launch.py --validate
```

### Commandoregel Interface

```bash
# Volledige pijplijn
python main_script.py document.pdf --document-type vmsw

# Individuele stappen
python main_script.py document.pdf step1 --no-gui
python main_script.py document.pdf step2 --document-type non-vmsw -c categories.py
python main_script.py document.pdf step3 --no-gui
```

---

## 📚 Module Overzicht

### Kernmodules

- **`ai_client.py`**: Behandelt alle Vertex AI-interacties met retry-logica
- **`pdf_processor.py`**: PDF-verwerking, inhoudsopgave extractie en splitsing
- **`category_matcher.py`**: AI-aangedreven categoriematching met batch-verwerking
- **`hybrid_matcher.py`**: Documenttypedetectie en routing
- **`vmsw_matcher.py`**: Hoge snelheid VMSW nummer-gebaseerde matching
- **`file_utils.py`**: Bestandsoperaties en mapbeheer

### GUI Componenten

- **`main_window.py`**: Hoofdapplicatievenster met responsief ontwerp
- **`styled_components.py`**: Herbruikbare UI-componenten met consistente styling
- **`processing_worker.py`**: Achtergrond QThread workers voor niet-blokkerende operaties

### Configuratie & Modellen

- **`settings.py`**: Gecentraliseerd configuratiebeheer
- **`categories.py`**: Categoriedefinities en utilities
- **`validation.py`**: Installatie validatie en gezondheidscontroles

---

## Snelle Startgids

### Stap 1: Installeer Python Dependencies
```bash
pip install -r requirements.txt
```

### Stap 2: Installeer Google Cloud CLI
1. **Download en installeer** Google Cloud CLI van: https://cloud.google.com/sdk/docs/install
2. **Authenticeer** met uw Google account:
   ```bash
   gcloud auth application-default login
   ```
3. **Stel uw project ID in** (maak een Google Cloud project aan indien nodig):
   ```bash
   gcloud config set project UW-PROJECT-ID
   ```

### Stap 3: Schakel Vereiste APIs In
```bash
gcloud services enable aiplatform.googleapis.com
```

### Stap 4: Start de Applicatie
```bash
python src/main.py
```

### Stap 5: Verwerk Uw Document
1. **Selecteer PDF**: Kies uw bouwdocument
2. **Kies Documenttype**: Selecteer "VMSW Document" of "Non-VMSW Document"
3. **Configureer Instellingen**: Stel uitvoermap in en (voor Non-VMSW) categoriebestand
4. **Voer Pipeline Uit**: Klik op "Run Complete Pipeline"

---

## 📄 Licentie

Dit project is gelicentieerd onder de voorwaarden gespecificeerd in het LICENSE bestand.

---

<div align="center">
  <p><strong>Ontwikkeld in het AI Construct COOCK+ project</strong></p>
  <p><em>Met de steun van VLAIO</em></p>
  <p><em>Bouwdocumentverwerking voor de praktijk</em></p>
</div> 