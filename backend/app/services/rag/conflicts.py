def detect_conflicts(facts):
    conflicts = []
    # simple heuristic for demo
    # If patient says no diabetes but history says diabetes
    history = [f for f in facts if f.category == 'medical_history']
    for h in history:
        val = str(h.value).lower()
        # Find if patient has contradictory symptoms or statements
        if ("diabetes" in val or "dm" in val) and any("no diabetes" in str(f.value).lower() or "nahi hai diabetes" in str(f.value).lower() for f in facts):
            conflicts.append({
                "type": "contradiction",
                "description": "Patient denies diabetes but historical record indicates diabetes.",
                "sources": [s for s in h.source_reference] if hasattr(h, 'source_reference') else []
            })
    return conflicts
