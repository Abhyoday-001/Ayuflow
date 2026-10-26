import sys
import argparse
from app.core.languages import INDIAN_LANGUAGES

def check_tts(lang_filter=None, test_all=False):
    print("Checking TTS dependencies...")
    try:
        import torch
        from transformers import VitsModel, AutoTokenizer
        print("✅ transformers and torch are installed.\n")
    except ImportError:
        print("❌ Missing dependencies. Please run:")
        print("pip install transformers torch scipy soundfile")
        sys.exit(1)

    langs_to_check = []
    if lang_filter:
        if lang_filter not in INDIAN_LANGUAGES:
            print(f"❌ Language '{lang_filter}' not found in registry.")
            sys.exit(1)
        langs_to_check = [lang_filter]
    elif test_all:
        langs_to_check = [k for k, v in INDIAN_LANGUAGES.items() if v.get("status") == "supported"]
    else:
        # Default behavior is to check hi and en
        langs_to_check = ["hi", "en"]

    for lang_code in langs_to_check:
        info = INDIAN_LANGUAGES[lang_code]
        model_id = info["tts_model"]
        name = info["name"]
        
        print(f"--- Checking {name} ({model_id}) ---")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = VitsModel.from_pretrained(model_id)
            print(f"✅ {name} model loaded successfully.")
            
            # Simple synthesis test
            inputs = tokenizer(info["native_name"], return_tensors="pt")
            with torch.no_grad():
                output = model(**inputs).waveform
            print(f"✅ {name} synthesis successful.\n")
        except Exception as e:
            print(f"❌ {name} model check failed: {e}\n")
            if lang_filter or test_all:
                sys.exit(1)

    print("🎉 Requested TTS Models are ready for local execution!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, help="Language code to check (e.g., hi, ta)")
    parser.add_argument("--all", action="store_true", help="Check all supported languages")
    args = parser.parse_args()
    
    check_tts(lang_filter=args.language, test_all=args.all)
