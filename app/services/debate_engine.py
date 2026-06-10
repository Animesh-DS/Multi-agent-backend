import uuid
import json
import asyncio
from datetime import datetime
from app.schemas.debate_schemas import DebateTurnData, DebateEndData

# Mock DB for hackathon velocity
debates_db = {}
transcripts_db = {}

async def generate_debate_stream(debate_id: str, problem_id: str, rounds: int):
    """Yields SSE payloads formatted exactly to the frontend contract."""
    agents = ["aria", "rex", "nova", "zara"]
    transcripts_db[debate_id] = []
    
    try:
        for r in range(1, rounds + 1):
            for i, agent in enumerate(agents):
                # 1. Yield Turn Event (Event 1)
                turn_data = DebateTurnData(
                    turn_id=f"turn_{uuid.uuid4().hex[:8]}",
                    agent=agent,
                    round=r,
                    message=f"[{agent.upper()}] Hardcoded hackathon mock argument for round {r}.",
                    targets=[agents[i-1]] if i > 0 else ["nova", "zara"],
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                
                # Save to history for Endpoint D
                transcripts_db[debate_id].append(turn_data)
                
                # Format exactly as SSE Event
                yield f"event: debate_turn\ndata: {turn_data.model_dump_json()}\n\n"
                
                await asyncio.sleep(1) # Simulate LLM delay
                
        # 2. Yield End Event (Event 2)
        end_data = DebateEndData(
            verdict="The project should proceed with modified timelines.",
            confidence=85,
            summary_by_agent={
                "aria": "Optimistic about market capture.",
                "rex": "Successfully argued timeline delays.",
                "nova": "Provided historical data.",
                "zara": "Argued for a total pivot."
            },
            winning_argument="consensus"
        )
        
        debates_db[debate_id] = end_data # Save final result
        yield f"event: debate_end\ndata: {end_data.model_dump_json()}\n\n"

    except Exception as e:
        # 3. Yield Error Event (Event 3)
        error_payload = json.dumps({"message": f"LLM generation failed: {str(e)}"})
        yield f"event: error\ndata: {error_payload}\n\n"