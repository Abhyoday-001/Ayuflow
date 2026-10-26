from typing import List, Dict, Optional, Any

# Base Intake
INTAKE_QUESTIONS = [
    {"id": "chief_complaint", "text": "What is your main health problem today?"},
    {"id": "associated_symptoms", "text": "Which symptoms are you experiencing?"},
    {"id": "duration", "text": "When did the problem start?"},
    {"id": "severity", "text": "How severe is it?"},
    {"id": "previous_occurrence", "text": "Have you had this problem before?"},
    {"id": "medical_history", "text": "Do you have any existing medical conditions?"},
    {"id": "medications", "text": "Are you currently taking any medicines?"}
]

# Adaptive Branches
CHEST_BRANCH = [
    {"id": "chest_pain_location", "text": "Where exactly is the pain?"},
    {"id": "chest_pain_spread", "text": "Does it spread to your arm, jaw or back?"},
    {"id": "chest_pain_exertion", "text": "Does it worsen with exertion?"},
    {"id": "chest_pain_breathless", "text": "Are you experiencing breathlessness?"},
    {"id": "chest_pain_sweating", "text": "Are you sweating or feeling dizzy?"}
]

KNEE_BRANCH = [
    {"id": "knee_which", "text": "Which knee?"},
    {"id": "knee_stiffness", "text": "Is there morning stiffness?"},
    {"id": "knee_swelling", "text": "Is there swelling?"},
    {"id": "knee_walking", "text": "Is walking difficult?"},
    {"id": "knee_injury", "text": "Was there an injury?"}
]

# AYUSH Assessment block
AYUSH_QUESTIONS = [
    {"id": "ayush_prakriti_sleep", "text": "How is your sleep pattern generally? (Heavy, light, or disturbed)"},
    {"id": "ayush_prakriti_digestion", "text": "How is your appetite and digestion? (Ahara Shakti)"},
    {"id": "ayush_prakriti_temperature", "text": "Do you prefer cold or warm weather?"},
    {"id": "ayush_vikriti_bowel", "text": "How are your bowel movements? (Constipation, loose, or normal)"}
]

class QuestionnairePlanner:
    def determine_next_question(self, answered_ids: List[str], responses: List[Any] = None, intake_type: str = "allopathy") -> Optional[Dict]:
        if responses is None:
            responses = []
            
        # 1. Base questions (Both Allopathy and Ayurveda need this)
        for q in INTAKE_QUESTIONS:
            if q["id"] not in answered_ids:
                return {"question_id": q["id"], "text": q["text"]}
                
        # 2. Adaptive Branching
        chief_complaint_ans = ""
        for r in responses:
            if r.question_id == "chief_complaint" and r.answer:
                chief_complaint_ans = r.answer.lower()
                break
                
        branch_questions = []
        if "chest" in chief_complaint_ans or "chhati" in chief_complaint_ans or "heart" in chief_complaint_ans:
            branch_questions.extend(CHEST_BRANCH)
            
        if "knee" in chief_complaint_ans or "ghutn" in chief_complaint_ans or "joint" in chief_complaint_ans:
            branch_questions.extend(KNEE_BRANCH)
            
        for q in branch_questions:
            if q["id"] not in answered_ids:
                return {"question_id": q["id"], "text": q["text"]}
                
        # 3. AYUSH Assessment (ONLY if intake_type == 'ayurveda')
        if intake_type == "ayurveda":
            for q in AYUSH_QUESTIONS:
                if q["id"] not in answered_ids:
                    return {"question_id": q["id"], "text": q["text"]}
                
        # Intake complete
        return None

    async def phrase_question(self, question_id: str, base_text: str, language: str = "en") -> str:
        from app.services.questionnaire.translations import get_translation
        translated = get_translation(question_id, language, base_text)
        if language == "en":
            return base_text
        return translated

planner_service = QuestionnairePlanner()
