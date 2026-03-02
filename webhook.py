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
    lkapi = api.LiveKitAPI()
    await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="hire-a-human",
            room=f"outbound-{phone_number}",
            metadata=phone_number
        )
    )
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
    app.run(port=5000)
