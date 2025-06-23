# 🚨 Police Call – Crime Insight Extractor

A Streamlit application that transcribes police complaint audio files, classifies the type of crime, extracts detailed insights (including precise addresses, dates, urgency, weapon involvement, injuries, suspect descriptions, and witness presence), and generates actionable next steps for response teams.

---

## 📋 Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [How It Works](#how-it-works)  
   - [Model Loading](#model-loading)  
   - [Audio Transcription](#audio-transcription)  
   - [Crime Classification](#crime-classification)  
   - [Insight Extraction](#insight-extraction)  
     - [Address Extraction Pipeline](#address-extraction-pipeline)  
     - [Date & Time Extraction](#date--time-extraction)  
     - [Urgency, Weapon & Injury Detection](#urgency-weapon--injury-detection)  
     - [Suspect & Witness Info](#suspect--witness-info)  
   - [Actionable Steps Generation](#actionable-steps-generation)  
4. [Dependencies](#dependencies)  


---

## 🔑 Features

- **Audio Transcription** using OpenAI Whisper  
- **Zero-Shot Crime Classification** with Hugging Face’s `facebook/bart-large-mnli`  
- **Transformer-Based NER** (`en_core_web_trf`) to detect addresses and locations  
- **Specialized Address Parsing** via `pyap` and `usaddress` for street-level accuracy  
- **Date Parsing** that only accepts explicit day-month-year strings  
- **Automated Insight Extraction** for:  
  - Location (precise address or generic)  
  - Date/Time of incident  
  - Urgency level (Normal, High, Critical)  
  - Weapon involvement  
  - Injury reported  
  - Suspect description  
  - Witness presence  
- **Actionable Next Steps** generated based on extracted insights and crime category  
- **Interactive UI** built with Streamlit for easy uploads and visualization  

---

## 📦 Prerequisites

- **Python** 3.8 or higher  
- **FFmpeg** (for audio file handling)  
- Internet connection to download models the first time  

---

## 🧠 How It Works

### Model Loading
- Cached functions load:  
  - **Whisper** (`base` model) for transcription  
  - **Zero-shot classifier** (`facebook/bart-large-mnli`)  
  - **spaCy transformer** (`en_core_web_trf`)  

### Audio Transcription
- User uploads an audio file  
- FFmpeg (via Whisper) decodes it  
- Whisper transcribes speech to **text**  

### Crime Classification
- Zero-shot classification over a curated list of crime types  
- Returns **top label + confidence**  
- Displayed as both a table (optional) and used downstream  

### Insight Extraction

#### Address Extraction Pipeline
1. **spaCy Transformer NER**: Extracts any entity with `ent.label_ == "ADDRESS"`.  
2. **pyap**: Regex-based street address parser (US, CA, UK).  
3. **usaddress**: Grammar-based tagger for U.S. addresses.  

#### Date & Time Extraction
- **Uses spaCy** to find `DATE`/`TIME` entities  
- **Parses only explicit** day-month-year strings via  
  `dateparser.parse(..., settings={'REQUIRE_PARTS':['day','month','year']})`  
- Falls back to **Not found** if no explicit date combination  

#### Urgency, Weapon & Injury Detection
- **Keywords** map to urgency scores (`emergency`, `urgent`, etc.)  
- **Weapon list** checks words like `gun`, `knife`  
- **Injury keywords** (`injured`, `bleeding`, etc.)  

#### Suspect & Witness Info
- **Regex** for “suspect described as …”  
- Checks for the word **witness**  

### Actionable Steps Generation
- Dispatching units to the extracted address  
- Flagging high-priority responses  
- Notifying armed response team  
- Sending medical assistance  
- Preserving digital evidence for cybercrime  

---

### Extracted Insights for Audio 1 : 112

![image](https://github.com/user-attachments/assets/8295d38a-66c5-44b8-9b1d-d360c33b2aaf)

![image](https://github.com/user-attachments/assets/5473e0ce-6e51-448c-b4ae-15a89f959908)

![image](https://github.com/user-attachments/assets/82a3f825-d63f-4fd8-b1ac-3639e8697dee)



---

## 📜 Dependencies
- `streamlit`  
- `whisper`  
- `torch`  
- `transformers`  
- `spacy`  
- `en_core_web_trf`  
- `dateparser`  
- `pyap`  
- `usaddress`  

