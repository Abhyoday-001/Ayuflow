from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, health, asr, intake, documents, encounters, review, extraction, tts, languages

app = FastAPI(title="AyuFlow API", version="0.1.0")

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(health.router, tags=["Health"])
app.include_router(languages.router, prefix="/api/v1/languages", tags=["Languages"])
app.include_router(asr.router, prefix="/api/v1/asr", tags=["ASR"])
app.include_router(extraction.router, prefix="/api/v1/extraction", tags=["Extraction"])
app.include_router(intake.router, prefix="/api/v1/intake", tags=["Intake"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(encounters.router, prefix="/api/v1/encounters", tags=["Encounters"])
app.include_router(review.router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["TTS"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AyuFlow API"}
