# Existing content of webhook.py

@app.route("/call", methods=["GET"])
def call():
    return {"message": "Hello, World!"}, 200

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200