import streamlit as st
import whisper
import torch
import os
from transformers import pipeline
from tempfile import NamedTemporaryFile
import spacy
import dateparser
import re
import pandas as pd
import pyap
import usaddress

# —— CACHING MODEL LOADS ——
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

@st.cache_resource
def load_classifier():
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        hypothesis_template="This text is about {}.",
        device=0 if torch.cuda.is_available() else -1
    )

@st.cache_resource
def load_spacy_trf():
    # Requires: pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.5.0/en_core_web_trf-3.5.0-py3-none-any.whl
    return spacy.load("en_core_web_trf")

# —— CONFIGURATION ——
CATEGORIES = [
    "Robbery", "Assault", "Cybercrime", "Domestic Violence",
    "Vandalism", "Theft", "Kidnapping", "Harassment/Stalking",
    "Drug-Related", "Traffic Violation", "Murder / Homicide",
    "Missing Person", "Extortion / Blackmail", "Sexual Offense",
    "Child Abuse", "Terrorism / Bomb Threat", "Financial Fraud / Scam",
    "Illegal Possession", "Noise Disturbance", "Animal Cruelty"
]

# —— HELPER FUNCTIONS ——
def classify_complaint(text, classifier, labels):
    res = classifier(text, labels)
    return res["labels"][0], res["scores"][0]


def extract_best_address(text):
    # 1) Try spaCy transformer ADDRESS entities
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ADDRESS":
            return ent.text

    # 2) Fallback to pyap (US, CA, UK)
    results = pyap.parse(text, country='US')
    if results:
        return results[0].full_address

    # 3) Fallback to usaddress
    try:
        tagged, label = usaddress.tag(text)
        if label == 'Street Address':
            components = []
            for part in ["AddressNumber","StreetNamePreType","StreetName",
                         "StreetNamePostType","PlaceName","StateName","ZipCode"]:
                if part in tagged:
                    components.append(tagged[part])
            return " ".join(components)
    except usaddress.RepeatedLabelError:
        pass
    return "Not found"


def extract_insights(text):
    # Get address or generic location
    address = extract_best_address(text)
    if address != "Not found":
        location = address
    else:
        doc = nlp(text)
        locs = [ent.text for ent in doc.ents if ent.label_ in ("GPE","LOC","FACILITY")]
        location = locs[0] if locs else "Not found"

    # Date parsing only for explicit dates
    doc = nlp(text)
    times = [ent.text for ent in doc.ents if ent.label_ in ("TIME","DATE")]
    if times:
        parsed = dateparser.parse(
            times[0],
            settings={'REQUIRE_PARTS': ['day','month','year']}
        )
        time_str = parsed.strftime("%Y-%m-%d") if parsed else "Not found"
    else:
        time_str = "Not found"

    urgency_kw = {"emergency":3, "immediate":2, "urgent":2, "asap":2, "now":1}
    score = sum(w for k,w in urgency_kw.items() if k in text.lower())
    urgency = "Critical" if score>=3 else ("High" if score>0 else "Normal")

    weapon_kw = ["gun","knife","rifle","pistol","weapon","shoot","gunfire"]
    found_weapons = [kw for kw in weapon_kw if kw in text.lower()]
    weapon_involved = f"Yes ({', '.join(found_weapons)})" if found_weapons else "No"

    injury_kw = ["injured","hurt","wounded","bleeding"]
    injury_reported = "Yes" if any(kw in text.lower() for kw in injury_kw) else "No"

    return {
        "Location": location,
        "Time": time_str,
        "Urgency": urgency,
        "Weapon Involved": weapon_involved,
        "Injury Reported": injury_reported
    }


def extract_extra_insights(text):
    suspect_desc = "Not found"
    m = re.search(r'suspect (?:described as )?([^.]+)\.', text, re.IGNORECASE)
    if m:
        suspect_desc = m.group(1).strip()
    witness_present = "Yes" if "witness" in text.lower() else "No"
    return {
        "Suspect Description": suspect_desc,
        "Witness Present": witness_present
    }


def generate_actionable_insights(insights, category):
    actions = []
    if insights["Location"] != "Not found":
        actions.append(f"Dispatch nearest unit to {insights['Location']}.")
    if insights["Urgency"] in ("Critical","High"):
        actions.append("Flag as high-priority response.")
    if insights["Weapon Involved"].startswith("Yes"):
        actions.append("Notify armed response team.")
    if insights["Injury Reported"] == "Yes":
        actions.append("Send medical assistance.")
    if category == "Cybercrime":
        actions.append("Preserve digital evidence and system logs.")
    if not actions:
        actions.append("Review details and assign follow-up investigation.")
    return actions


def main():
    st.title("🚨 Police Call – Crime Insight Extractor")

    whisper_model = load_whisper_model()
    classifier     = load_classifier()
    global nlp
    nlp            = load_spacy_trf()

    uploaded_file = st.file_uploader(
        "Upload a police complaint audio file (.wav/.mp3)",
        type=["wav","mp3"]
    )
    if not uploaded_file:
        return

    with NamedTemporaryFile(delete=False,
             suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.audio(audio_path)
    st.info("Transcribing audio…")
    result = whisper_model.transcribe(audio_path)
    text   = result["text"].strip()
    st.success("✅ Transcription complete")
    st.markdown("📝 Transcribed Text:")
    st.write(text)

    # Classification
    st.info("Classifying category…")
    category, conf = classify_complaint(text, classifier, CATEGORIES)
    st.success(f"🚔 Category: {category} (confidence {conf:.0%})")

    # Insights
    insights   = extract_insights(text)
    extra_ins  = extract_extra_insights(text)
    actionable = generate_actionable_insights(insights, category)

    # Build insights table
    insights_data = {
        "Insight": list(insights.keys()) + list(extra_ins.keys()) + ["Complaint Category","Category Confidence"],
        "Value":   list(insights.values()) + list(extra_ins.values()) + [category, f"{conf:.0%}"]
    }
    df_insights = pd.DataFrame(insights_data)
    st.subheader("🔍 Extracted Insights")
    st.table(df_insights)

    # Actionable steps table
    df_actions = pd.DataFrame({"Actionable Next Steps": actionable})
    st.subheader("🛠 Actionable Next Steps")
    st.table(df_actions)

    os.remove(audio_path)

if __name__ == "__main__":
    main()