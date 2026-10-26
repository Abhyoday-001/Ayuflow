from pydantic import BaseModel
from typing import List, Optional

class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None

from enum import Enum
from typing import Dict, Any

class QualityState(str, Enum):
    GOOD = "GOOD"
    REVIEW = "REVIEW"
    RETRY = "RETRY"

class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    avg_logprob: Optional[float] = None
    no_speech_prob: Optional[float] = None
    compression_ratio: Optional[float] = None

class TranscriptionResult(BaseModel):
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    segments: List[TranscriptSegment] = []
    provider: str
    model: str
    quality: Optional[Dict[str, Any]] = None
    quality_state: Optional[QualityState] = None
