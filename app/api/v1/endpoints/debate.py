import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.schemas.debate_schemas import (
    StartDebateRequest, 
    StartDebateResponse, 
    DebateResultResponse
)
from app.services.debate_engine import generate_debate_stream, debates_db, transcripts_db

router = APIRouter()

debate_configs_db = {}

@router.post("/start-debate", response_model=StartDebateResponse)
async def start_debate(request: StartDebateRequest):
    debate_id = f"deb_{uuid.uuid4().hex[:8]}"
    
    debate_configs_db[debate_id] = request.rounds
    return StartDebateResponse(debate_id=debate_id, status="started")

@router.get("/stream-debate/{debate_id}")
async def stream_debate(debate_id: str,rounds: int = Query(1, description="Number of debate rounds")):
    # Pass arbitrary problem_id and rounds for the mock
    rounds = debate_configs_db.get(debate_id, 1)
    
    generator = generate_debate_stream(debate_id, problem_id="mock_prob", rounds=2)
    return StreamingResponse(
        generator, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # Prevents Nginx/Proxies from buffering the stream
        }
    )

@router.get("/result/{debate_id}", response_model=DebateResultResponse)
async def get_result(debate_id: str):
    if debate_id not in transcripts_db:
        raise HTTPException(status_code=404, detail="Debate not found")
        
    return DebateResultResponse(
        debate_id=debate_id,
        status="completed" if debate_id in debates_db else "started",
        transcript=transcripts_db.get(debate_id, []),
        final_result=debates_db.get(debate_id)
    )