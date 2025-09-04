# app.py
from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('sample_client')

app = Flask(__name__)


# --- Simple home route: render your own page ---
# Put your HTML at: templates/index.html
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# --- OAuth callback: supports GET (query) and POST (form_post) ---
@app.route("/callback", methods=["GET", "POST"])
def callback():
    # Accept parameters from either mode
    params = {}
    if request.method == "POST":
        params = request.form.to_dict(flat=True)
    else:
        params = request.args.to_dict(flat=True)

    # For convenience, keep the most common values in variables
    code = params.get("code")
    state = params.get("state")
    error = params.get("error")
    error_description = params.get("error_description")

    # Show what we got back (JSON for easy debugging)
    payload = {
        "method": request.method,
        "received_params": params,
        "notes": "POST indicates response_mode=form_post on the AS; GET is the default query mode."
    }

    # Optionally, redirect to /exchange if a code is present and AUTO_EXCHANGE=true
    if os.getenv("AUTO_EXCHANGE", "true").lower() == "true" and code:
        logger.info("Auto-exchanging code for token...")
        return redirect(url_for("exchange", code=code, state=state))

    return jsonify(payload), 200


# --- Optional token exchange endpoint (for quick local testing) ---
# Supply config via environment variables:
#   TOKEN_ENDPOINT  (required to exchange)
#   CLIENT_ID
#   CLIENT_SECRET   (omit or leave blank for public clients/PKCE)
#   REDIRECT_URI
#   CODE_VERIFIER   (if you used PKCE)
@app.route("/exchange", methods=["GET", "POST"])
def exchange():
    # Allow providing 'code' via GET (from redirect) or POST body (JSON/form)
    if request.method == "POST":
        params = request.form.to_dict(flat=True)
    else:
        params = request.args.to_dict(flat=True)
    code = params.get("code")

    if not code:
        return jsonify({"error": "missing_code", "message": "Provide ?code=... or POST code"}), 400

    token_endpoint = os.getenv("TOKEN_ENDPOINT")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    code_verifier = os.getenv("CODE_VERIFIER")  # required if you used PKCE

    if not token_endpoint:
        return jsonify({"error": "missing_config", "message": "Set TOKEN_ENDPOINT env var"}), 500

    data = {
        "grant_type": "authorization_code",
        "code": code,
    }
    if redirect_uri:
        data["redirect_uri"] = redirect_uri
    if client_id:
        data["client_id"] = client_id
    # Include secret only if you have one (confidential clients)
    if client_secret:
        data["client_secret"] = client_secret
    # Include PKCE code_verifier when applicable
    if code_verifier:
        data["code_verifier"] = code_verifier

    try:
        resp = requests.post(token_endpoint, data=data, timeout=15)
        # return jsonify({
        #     "request": {"url": token_endpoint, "data": data},
        #     "status_code": resp.status_code,
        #     "headers": dict(resp.headers),
        #     "body": safe_json(resp)
        # }), resp.status_code
        logger.info(safe_json(resp))
        return render_template("success.html", json_response=safe_json(resp))
    except requests.RequestException as e:
        return jsonify({"error": "request_exception", "message": str(e)}), 502


@app.route("/get_user", methods=["POST"])
def get_user():
    # Accept parameters from either mode
    data = request.get_json()
    print(data)

    # For convenience, keep the most common values in variables
    token = data.get("token")
    user_id = data.get("user_id")

    get_user_endpoint = f'{os.getenv("GET_USER_ENDPOINT")}/{user_id}'

    if not get_user_endpoint:
        return jsonify({"error": "missing_config", "message": "Set TOKEN_ENDPOINT env var"}), 500

    logger.info(f"Making request to {get_user_endpoint} with token {token}")

    try:
        resp = requests.get(
            get_user_endpoint,
            timeout=15,
            headers={"Authorization": f"Bearer {token}"},
        )
        logger.info(safe_json(resp))
        return jsonify({"birth_date": safe_json(resp)['user']['birth_date']}), 200
    except requests.RequestException as e:
        return jsonify({"error": "request_exception", "message": str(e)}), 502


def safe_json(response):
    """Try to parse JSON, otherwise return text."""
    try:
        return response.json()
    except ValueError:
        return {"raw_text": response.text}


if __name__ == "__main__":
    # Bind to 0.0.0.0 for convenience; change if you prefer localhost only
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
