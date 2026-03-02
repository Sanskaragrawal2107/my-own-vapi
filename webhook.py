from flask import Flask, request, jsonify
import asyncio
import os
import nest_asyncio
from livekit import api

nest_asyncio.apply()
app = Flask(__name__)

@app.route("/call", methods=["POST"])
def call():
    try:
        data = request.get_json()
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "phone required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(make_call(phone))
        loop.close()
        
        return jsonify({"status": "call initiated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def make_call(phone_number):
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    room_name = f"outbound-{phone_number.replace('+', '')}"
    
    # ✅ SIP ONLY - no agent dispatch needed
    await lkapi.sip.create_sip_participant(
        api.CreateSIPParticipantRequest(
            room_name=room_name,
            sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
            sip_call_to=phone_number,
            participant_identity="phone_user",
        )
    )
    
    await lkapi.aclose()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
