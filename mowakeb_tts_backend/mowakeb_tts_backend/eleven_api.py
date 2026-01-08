
import os
import base64

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
DEFAULT_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")

if not ELEVEN_API_KEY:
    raise RuntimeError("ELEVEN_API_KEY is not set")
if not DEFAULT_VOICE_ID:
    raise RuntimeError("ELEVEN_VOICE_ID is not set")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mowakeb.netlify.app",
        "https://mowakeb-final.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice_id: str | None = None

@app.post("/api/podcast-tts")
async def podcast_tts(req: TTSRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    voice_id = req.voice_id or DEFAULT_VOICE_ID

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.85,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"ElevenLabs error: {resp.status_code} - {resp.text[:200]}",
        )

    audio_bytes = resp.content
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return {"audioContent": audio_b64}
