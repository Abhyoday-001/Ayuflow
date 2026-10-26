AYURVEDA_SCHEMA = [
    {
        "id": "chief_complaint",
        "label": "Chief Complaint",
        "type": "textarea",
        "voice_enabled": True
    },
    {
        "id": "prakriti",
        "label": "Prakriti (Body Constitution)",
        "type": "radio",
        "options": ["Vata", "Pitta", "Kapha", "Vata-Pitta", "Pitta-Kapha", "Vata-Kapha", "Tridosha"]
    },
    {
        "id": "vikriti",
        "label": "Vikriti (Morbidity)",
        "type": "multi-select",
        "options": ["Vata Vriddhi", "Pitta Vriddhi", "Kapha Vriddhi", "Vata Kshaya", "Pitta Kshaya", "Kapha Kshaya"]
    },
    {
        "id": "sara",
        "label": "Sara (Tissue Excellence)",
        "type": "radio",
        "options": ["Pravara (Superior)", "Madhyama (Moderate)", "Avara (Inferior)"]
    },
    {
        "id": "samhanana",
        "label": "Samhanana (Compactness)",
        "type": "radio",
        "options": ["Pravara (Well-built)", "Madhyama (Medium-built)", "Avara (Poorly-built)"]
    },
    {
        "id": "pramana",
        "label": "Pramana (Proportion)",
        "type": "radio",
        "options": ["Sama (Proportionate)", "Vishama (Disproportionate)"]
    },
    {
        "id": "satmya",
        "label": "Satmya (Suitability)",
        "type": "radio",
        "options": ["Pravara (All habits suit)", "Madhyama (Mixed habits suit)", "Avara (Only specific habits suit)"]
    },
    {
        "id": "sattva",
        "label": "Sattva (Mental Constitution)",
        "type": "radio",
        "options": ["Pravara (Strong)", "Madhyama (Moderate)", "Avara (Weak)"]
    },
    {
        "id": "ahara_shakti",
        "label": "Ahara Shakti (Digestive Power)",
        "type": "radio",
        "options": ["Pravara (Strong)", "Madhyama (Moderate)", "Avara (Weak)"]
    },
    {
        "id": "vyayama",
        "label": "Vyayama Shakti (Physical Strength)",
        "type": "radio",
        "options": ["Pravara (High)", "Madhyama (Moderate)", "Avara (Low)"]
    },
    {
        "id": "vaya",
        "label": "Vaya (Age Phase)",
        "type": "radio",
        "options": ["Bala (Childhood)", "Madhya (Middle age)", "Jeerna (Old age)"]
    },
    {
        "id": "nidana",
        "label": "Nidana (Etiological Factors)",
        "type": "textarea",
        "voice_enabled": True
    }
]

ALLOPATHY_SCHEMA = [
    {
        "id": "chief_complaint",
        "label": "Chief Complaint",
        "type": "textarea",
        "voice_enabled": True
    },
    {
        "id": "associated_symptoms",
        "label": "Associated Symptoms",
        "type": "textarea",
        "voice_enabled": True
    },
    {
        "id": "duration",
        "label": "Duration (How long?)",
        "type": "text",
        "voice_enabled": False
    },
    {
        "id": "severity",
        "label": "Severity",
        "type": "radio",
        "options": ["Mild", "Moderate", "Severe"]
    },
    {
        "id": "previous_occurrence",
        "label": "Previous Occurrence",
        "type": "radio",
        "options": ["Yes", "No", "Not Sure"]
    },
    {
        "id": "medical_history",
        "label": "Past Medical History",
        "type": "multi-select",
        "options": ["Hypertension", "Diabetes", "Asthma", "Thyroid", "None"]
    },
    {
        "id": "medications",
        "label": "Current Medications",
        "type": "textarea",
        "voice_enabled": True
    }
]

def get_schema(pathway: str):
    if pathway.lower() == 'ayurvedic' or pathway.lower() == 'ayurveda':
        return AYURVEDA_SCHEMA
    return ALLOPATHY_SCHEMA
