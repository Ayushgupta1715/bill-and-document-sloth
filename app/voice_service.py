"""ElevenLabs Voice & Audio Integration for Bill & Document Sloth.
Best Use of ElevenLabs Category ($100 Prize).
Gives our Sloth AI agent a voice to deliver spoken bill reminders,
upcoming deadline briefings, and voice narration for paperwork management.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional
from app.database import get_connection

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
# Default chill / narrator voice ID (Adam or George)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")


def generate_sloth_briefing_text() -> str:
    """Generate friendly, calm sloth voice briefing based on active documents."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT issuer, total_amount, currency, due_date
        FROM documents
        WHERE due_date IS NOT NULL AND status != 'rejected'
        ORDER BY due_date ASC
        LIMIT 3
        """
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Hello! I am your Bill Sloth. You have no pending paperwork or upcoming bills right now. Kick back, relax, and enjoy your day!"

    items = []
    for r in rows:
        issuer = r["issuer"] or "utility"
        amt = f"{r['currency'] or 'rupees'} {int(r['total_amount'])}" if r['total_amount'] else "an amount"
        items.append(f"{issuer} for {amt} due on {r['due_date']}")

    bill_summary = ", and ".join(items)
    script = f"Hello! I am your Bill Sloth. Here is your paperwork briefing: You have {len(rows)} bills needing attention. {bill_summary}. All documents have been analyzed and filed safely on your machine. Take it slow and steady!"
    return script


def synthesize_elevenlabs_audio(text: str) -> Optional[bytes]:
    """Call ElevenLabs Text-to-Speech API to synthesize voice audio."""
    if not ELEVENLABS_API_KEY:
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                return response.read()
    except Exception as e:
        print(f"[ElevenLabs Service] Error calling API: {e}")
        return None


def get_voice_briefing() -> Dict[str, Any]:
    """Get briefing text, audio status, and Web Speech synthesis parameters."""
    script = generate_sloth_briefing_text()
    has_api_key = bool(ELEVENLABS_API_KEY)

    return {
        "script": script,
        "provider": "ElevenLabs" if has_api_key else "WebSpeech / Sloth Local Voice",
        "has_elevenlabs_key": has_api_key,
        "voice_id": ELEVENLABS_VOICE_ID,
        "audio_stream_url": "/api/voice/stream" if has_api_key else None
    }
