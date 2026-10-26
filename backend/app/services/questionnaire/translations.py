import json

# This should be a robust verified JSON in a real production app.
# We include Tier 1 languages based on the MMS-TTS support we found.

TRANSLATIONS = {
    "chief_complaint": {
        "en": "What problem are you facing today?",
        "hi": "आपको आज किस समस्या के लिए सहायता चाहिए?",
        "mr": "आज तुम्हाला कोणत्या समस्येसाठी मदत हवी आहे?",
        "gu": "આજે તમને કઈ સમસ્યા માટે મદદ જોઈએ છે?",
        "ta": "இன்று உங்களுக்கு என்ன பிரச்சனைக்கு உதவி தேவை?",
        "kn": "ಇಂದು ನಿಮಗೆ ಯಾವ ಸಮಸ್ಯೆಗೆ ಸಹಾಯ ಬೇಕು?",
        "te": "ఈరోజు మీకు ఏ సమస్యకు సహాయం కావాలి?",
        "ml": "ഇന്ന് നിങ്ങൾക്ക് ഏത് പ്രശ്നത്തിനാണ് സഹായം വേണ്ടത്?",
        "bn": "আজ আপনার কী সমস্যার জন্য সাহায্য প্রয়োজন?",
        "pa": "ਅੱਜ ਤੁਹਾਨੂੰ ਕਿਸ ਸਮੱਸਿਆ ਲਈ ਮਦਦ ਚਾਹੀਦੀ ਹੈ?",
        "or": "ଆଜି ଆପଣଙ୍କୁ କେଉଁ ସମସ୍ୟା ପାଇଁ ସାହାଯ୍ୟ ଦରକାର?"
    },
    
    "chest_pain_location": {
        "en": "Where exactly is the pain?",
        "hi": "दर्द ठीक कहाँ हो रहा है?"
    },
    "chest_pain_spread": {
        "en": "Does it spread to your arm, jaw or back?",
        "hi": "क्या यह आपके हाथ, जबड़े या पीठ तक फैलता है?"
    },
    "chest_pain_exertion": {
        "en": "Does it worsen with exertion?",
        "hi": "क्या परिश्रम करने से यह बदतर हो जाता है?"
    },
    "chest_pain_breathless": {
        "en": "Are you experiencing breathlessness?",
        "hi": "क्या आपको सांस लेने में तकलीफ हो रही है?"
    },
    "chest_pain_sweating": {
        "en": "Are you sweating or feeling dizzy?",
        "hi": "क्या आपको पसीना आ रहा है या चक्कर आ रहा है?"
    },
    "knee_which": {
        "en": "Which knee?",
        "hi": "कौन सा घुटना?"
    },
    "knee_stiffness": {
        "en": "Is there morning stiffness?",
        "hi": "क्या सुबह घुटने में अकड़न होती है?"
    },
    "knee_swelling": {
        "en": "Is there swelling?",
        "hi": "क्या घुटने में सूजन है?"
    },
    "knee_walking": {
        "en": "Is walking difficult?",
        "hi": "क्या चलने में परेशानी होती है?"
    },
    "knee_injury": {
        "en": "Was there an injury?",
        "hi": "क्या कोई चोट लगी थी?"
    },
    "ayush_prakriti_sleep": {
        "en": "How is your sleep pattern generally? (Heavy, light, or disturbed)",
        "hi": "आम तौर पर आपकी नींद का पैटर्न कैसा है? (भारी, हल्की, या परेशान)"
    },
    "ayush_prakriti_digestion": {
        "en": "How is your appetite and digestion? (Ahara Shakti)",
        "hi": "आपकी भूख और पाचन कैसा है? (आहार शक्ति)"
    },
    "ayush_prakriti_temperature": {
        "en": "Do you prefer cold or warm weather?",
        "hi": "क्या आप ठंडा या गर्म मौसम पसंद करते हैं?"
    },
    "ayush_vikriti_bowel": {
        "en": "How are your bowel movements? (Constipation, loose, or normal)",
        "hi": "आपका मल त्याग कैसा है? (कब्ज, ढीला, या सामान्य)"
    },

    "duration": {
        "en": "When did the problem start?",
        "hi": "यह समस्या कब शुरू हुई?"
    },
    "severity": {
        "en": "How severe is it?",
        "hi": "यह कितना गंभीर है?"
    },
    "character": {
        "en": "Can you describe the pain or discomfort?",
        "hi": "क्या आप दर्द या परेशानी का वर्णन कर सकते हैं?",
        "mr": "तुम्ही वेदना किंवा त्रासाचे वर्णन करू शकता का?",
        "gu": "શું તમે પીડા અથવા અગવડતાનું વર્ણન કરી શકો છો?",
        "ta": "வலி அல்லது அசௌகரியத்தை விவரிக்க முடியுமா?",
        "kn": "ನೀವು ನೋವು ಅಥವಾ ಅಸ್ವಸ್ಥತೆಯನ್ನು ವಿವರಿಸಬಹುದೇ?",
        "te": "మీరు నొప్పి లేదా అసౌకర్యాన్ని వివరించగలరా?",
        "ml": "വേദനയോ അസ്വസ്ഥതയോ നിങ്ങൾക്ക് വിശദീകരിക്കാമോ?",
        "bn": "আপনি কি ব্যথা বা অস্বস্তির বর্ণনা দিতে পারবেন?",
        "pa": "ਕੀ ਤੁਸੀਂ ਦਰਦ ਜਾਂ ਪਰੇਸ਼ਾਨੀ ਦਾ ਵਰਣਨ ਕਰ ਸਕਦੇ ਹੋ?",
        "or": "ଆପଣ ଯନ୍ତ୍ରଣା କିମ୍ବା ଅସୁବିଧା ବିଷୟରେ ବର୍ଣ୍ଣନା କରିପାରିବେ କି?"
    },
    "pattern": {
        "en": "Is the fever continuous or does it come and go?",
        "hi": "क्या बुखार लगातार रहता है या आता-जाता है?",
        "mr": "ताप सतत असतो की येतो-जातो?",
        "gu": "શું તાવ સતત રહે છે કે આવે છે અને જાય છે?",
        "ta": "காய்ச்சல் தொடர்ந்து இருக்கிறதா அல்லது விட்டு விட்டு வருகிறதா?",
        "kn": "ಜ್ವರ ನಿರಂತರವಾಗಿದೆಯೇ ಅಥವಾ ಬಂದು ಹೋಗುತ್ತದೆಯೇ?",
        "te": "జ్వరం నిరంతరంగా ఉందా లేదా వచ్చి పోతుందా?",
        "ml": "പനി തുടർച്ചയായി നിൽക്കുന്നതാണോ അതോ വന്നും പോയുമിരിക്കുന്നതാണോ?",
        "bn": "জ্বর কি একটানা থাকে নাকি আসে আর যায়?",
        "pa": "ਕੀ ਬੁਖਾਰ ਲਗਾਤਾਰ ਰਹਿੰਦਾ ਹੈ ਜਾਂ ਆਉਂਦਾ-ਜਾਂਦਾ ਹੈ?",
        "or": "ଜ୍ୱର ଲଗାତାର ରହୁଛି ନା ଆସୁଛି ଆଉ ଯାଉଛି?"
    },
    "associated_symptoms": {
        "en": "Which symptoms are you experiencing?",
        "hi": "आप किन लक्षणों का अनुभव कर रहे हैं?"
    },
    "previous_occurrence": {
        "en": "Have you had this problem before?",
        "hi": "क्या आपको यह समस्या पहले कभी हुई है?"
    },
    "medical_history": {
        "en": "Do you have any existing medical conditions?",
        "hi": "क्या आपको कोई मौजूदा चिकित्सीय स्थिति या बीमारी है?"
    },
    "medications": {
        "en": "Are you currently taking any medicines?",
        "hi": "क्या आप वर्तमान में कोई दवा ले रहे हैं?"
    },
    "allergies": {
        "en": "Do you have any allergies?",
        "hi": "क्या आपको कोई एलर्जी है?",
        "mr": "तुम्हाला कोणतीही ऍलर्जी आहे का?",
        "gu": "શું તમને કોઈ એલર્જી છે?",
        "ta": "உங்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?",
        "kn": "ನಿಮಗೆ ಯಾವುದೇ ಅಲರ್ಜಿ ಇದೆಯೇ?",
        "te": "మీకు ఏవైనా అలెర్జీలు ఉన్నాయా?",
        "ml": "നിങ്ങൾക്ക് എന്തെങ്കിലും അലർജിയുണ്ടോ?",
        "bn": "আপনার কি কোনো অ্যালার্জি আছে?",
        "pa": "ਕੀ ਤੁਹਾਨੂੰ ਕੋਈ ਐਲਰਜੀ ਹੈ?",
        "or": "ଆପଣଙ୍କୁ କୌଣସି ଆଲର୍ଜି ଅଛି କି?"
    }
}

def get_translation(question_id: str, language: str, base_text: str = None) -> str:
    """
    Returns the translation for a given question_id.
    Falls back to English if the translation doesn't exist.
    """
    if question_id in TRANSLATIONS:
        return TRANSLATIONS[question_id].get(language, TRANSLATIONS[question_id].get("en", base_text))
    
    # If the ID is not exactly mapped, return the base_text
    return base_text
