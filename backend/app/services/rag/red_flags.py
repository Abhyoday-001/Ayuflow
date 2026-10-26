def detect_red_flags(facts):
    red_flags = []
    # simple heuristic for demo
    for f in facts:
        val = str(f.value).lower()
        if "chest" in val and "pain" in val and any("breathless" in str(x.value).lower() or "sweat" in str(x.value).lower() for x in facts):
            red_flags.append({
                "symptom": "Chest pain with breathlessness/sweating",
                "severity": "CRITICAL",
                "reason": "Potential cardiac event."
            })
    return red_flags
