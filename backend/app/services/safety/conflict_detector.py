from typing import List, Dict

def detect_conflicts(facts: List[Dict]) -> List[Dict]:
    conflicts = []
    
    # Example conflict: Patient says they take no medications, but later mentions Metformin
    has_no_meds = any(f.get("field") == "medications" and f.get("value") in ["none", "None", "no"] for f in facts)
    has_specific_med = any(f.get("field") == "medication_name" for f in facts)
    
    if has_no_meds and has_specific_med:
        conflicts.append({
            "type": "CONTRADICTION",
            "message": "Patient stated no medications, but a specific medication was identified.",
            "fields": ["medications", "medication_name"]
        })
        
    return conflicts
