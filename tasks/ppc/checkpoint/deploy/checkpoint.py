from flask import Flask, session, send_file, redirect, url_for, request
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from captcha import generate_captcha
import uuid
import io

CAPTCHA_LENGTH = 10
CAPTCHA_LIFETIME = timedelta(seconds=5)
CAPTCHAS_REQUIRED = 100

app = Flask(__name__)
app.secret_key = os.urandom(32)


@dataclass
class Captcha:
    text: str
    audio: bytes
    generated_at: datetime


captchas: dict[str, Captcha] = {}


def session_captcha_stale() -> bool:
    if "captcha_id" not in session:
        return True

    captcha_id = session["captcha_id"]

    captcha = captchas.get(captcha_id)
    if captcha is None:
        return True
    elif datetime.now(timezone.utc) >= captcha.generated_at + CAPTCHA_LIFETIME:
        del captchas[captcha_id]
        return True

    return False


def new_session_captcha():
    text, audio = generate_captcha(CAPTCHA_LENGTH)
    captcha = Captcha(
        text=text,
        audio=audio,
        generated_at=datetime.now(timezone.utc),
    )

    captcha_id = str(uuid.uuid4())
    captchas[captcha_id] = captcha
    session["captcha_id"] = captcha_id


@app.post("/captcha/generate")
def generate():
    if session.get("captcha_passed") == True:
        new_session_captcha()
        del session["captcha_passed"]
    elif session_captcha_stale():
        new_session_captcha()
        session["captchas_solved"] = 0

    captcha = captchas[session["captcha_id"]]
    return send_file(
        io.BytesIO(captcha.audio),
        mimetype="audio/mpeg",
        as_attachment=False,
    )


@app.post("/captcha/submit")
def submit():
    if session_captcha_stale():
        return "", 403

    captcha_id = session.pop("captcha_id")
    captcha = captchas.pop(captcha_id)
    text = request.form.get("text")

    if text != captcha.text:
        del session["captchas_solved"]
        return "", 403

    session["captcha_passed"] = True
    session["captchas_solved"] += 1

    if session["captchas_solved"] >= CAPTCHAS_REQUIRED:
        return os.getenv("FLAG")

    return "", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=24242,
        debug=False,
        use_debugger=False,
        use_evalex=False,
        threaded=False,
        processes=1,
    )
