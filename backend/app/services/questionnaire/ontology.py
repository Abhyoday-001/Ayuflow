# A simple deterministic ontology graph mapping chief complaints/symptoms to required and optional questions.

QUESTION_ONTOLOGY = {
    "fever": {
        "required": ["duration", "severity", "pattern"],
        "optional": ["associated_symptoms", "medications_taken"]
    },
    "back_pain": {
        "required": ["duration", "severity", "location", "onset"],
        "optional": ["radiation", "aggravating_factors", "relieving_factors", "associated_symptoms"]
    },
    "general": {
        "required": ["chief_complaint"],
        "optional": ["relevant_history", "medications", "allergies"]
    }
}

QUESTION_PROMPTS = {
    "chief_complaint": "What brings you to the hospital today?",
    "duration": "How long have you been experiencing this?",
    "severity": "On a scale of 1 to 10, how severe is it?",
    "pattern": "Does it get worse at any particular time of the day?",
    "location": "Exactly where is the pain located?",
    "onset": "Did this start suddenly or gradually?",
    "radiation": "Does the pain spread to any other part of your body?",
    "aggravating_factors": "Does anything make it worse?",
    "relieving_factors": "Does anything make it better?",
    "associated_symptoms": "Are you experiencing any other symptoms with this?",
    "medications_taken": "Have you taken any medicines for this so far?",
    "relevant_history": "Do you have any past medical conditions?",
    "medications": "Are you currently taking any daily medications?",
    "allergies": "Do you have any allergies?"
}
