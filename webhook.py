from flask import Flask, request
from livekit import api
import asyncio, os
from dotenv import load_dotenv

load_dotenv(".env.local")
app = Flask(__name__)

@app.route("/call", methods=["POST"])
def call():
    phone = request.json.get("phone")
    asyncio.run(make_call(phone))
    return {"status": "call initiated"}

async def make_call(phone_number):
    url = os.getenv("LIVEKIT_URL") or "https://demo-82i5xlaz.livekit.cloud"
    if url.startswith("wss://"):
        url = "https://" + url[len("wss://"):]  
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    # Normalize values: trim whitespace and drop accidental trailing backslashes
    if api_key:
        api_key = api_key.strip().rstrip("\\")
    if api_secret:
        api_secret = api_secret.strip().rstrip("\\")
    if not api_key or not api_secret:
        raise RuntimeError(
            "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env.local"
        )
    lkapi = api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret)
    try:
        await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="hire-a-human",
            room=f"outbound-{phone_number}",
            metadata=phone_number
        )
        )
    except Exception as exc:
        raise RuntimeError(
            "LiveKit create_dispatch failed (401 likely): check LIVEKIT_API_KEY/SECRET and LIVEKIT_URL."
        ) from exc
    await lkapi.sip.create_sip_participant(
        api.CreateSIPParticipantRequest(
            room_name=f"outbound-{phone_number}",
            sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
            sip_call_to=phone_number,
            participant_identity="phone_user",
        )
    )
    await lkapi.aclose()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)