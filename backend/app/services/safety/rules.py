from typing import List, Dict

# Hardcoded deterministic rules. 
# In production, this would be a rules engine or a verified database.
RED_FLAGS = [
    {
        "id": "RF001",
        "conditions": [{"field": "chest_pain", "operator": "exists"}, {"field": "radiation", "value": "left_arm"}],
        "message": "Potential cardiac event. Requires immediate triage.",
        "severity": "CRITICAL"
    },
    {
        "id": "RF002",
        "conditions": [{"field": "fever", "operator": "exists"}, {"field": "neck_stiffness", "operator": "exists"}],
        "message": "Potential meningitis. Requires immediate evaluation.",
        "severity": "CRITICAL"
    }
]

def evaluate_red_flags(facts: List[Dict]) -> List[Dict]:
    triggered_flags = []
    
    # Simple rule evaluator
    for rule in RED_FLAGS:
        rule_triggered = True
        for cond in rule["conditions"]:
            field = cond["field"]
            fact_match = next((f for f in facts if f.get("field") == field), None)
            
            if not fact_match:
                rule_triggered = False
                break
                
            if cond.get("operator") == "exists":
                continue
                
            if cond.get("value") and fact_match.get("value") != cond["value"]:
                rule_triggered = False
                break
                
        if rule_triggered:
            triggered_flags.append(rule)
            
    return triggered_flags
