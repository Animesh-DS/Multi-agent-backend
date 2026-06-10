from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime

# Enums
AgentType = Literal["aria", "rex", "nova", "zara"]
WinnerType = Literal["aria", "rex", "nova", "zara", "consensus"]
DebateStatus = Literal["ready", "started", "completed", "error"]

# --- Endpoint A: POST /upload ---
class UploadResponse(BaseModel):
    problem_id: str
    parsed_text: str
    status: DebateStatus = "ready"

# --- Endpoint B: POST /start-debate ---
class StartDebateRequest(BaseModel):
    problem_id: str
    rounds: int = Field(default=3, ge=1, le=5)

class StartDebateResponse(BaseModel):
    debate_id: str
    status: DebateStatus = "started"

# --- SSE Event Data Models ---
class DebateTurnData(BaseModel):
    turn_id: str
    agent: AgentType
    round: int
    message: str
    targets: List[AgentType]
    timestamp: str

class DebateEndData(BaseModel):
    verdict: str
    confidence: int
    summary_by_agent: Dict[AgentType, str]
    winning_argument: WinnerType

class ErrorData(BaseModel):
    message: str

# --- Endpoint D: GET /result/{debate_id} ---
class DebateResultResponse(BaseModel):
    debate_id: str
    status: DebateStatus
    transcript: List[DebateTurnData]
    final_result: Optional[DebateEndData] = None