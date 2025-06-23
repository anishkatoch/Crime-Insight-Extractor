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
