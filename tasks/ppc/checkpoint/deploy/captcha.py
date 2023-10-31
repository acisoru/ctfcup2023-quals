import os
import secrets
import string
import io

import pydub

VOICES = []

for voice_name in sorted(os.listdir("voices")):
    voice = {}
    for file in os.listdir(f"voices/{voice_name}"):
        letter = file.split(".")[0]
        recording = pydub.AudioSegment.from_wav(f"voices/{voice_name}/{file}")
        voice[letter] = recording

    VOICES.append(voice)


def generate_captcha_text(length):
    ALPHABET = string.ascii_lowercase
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_captcha(length) -> tuple[str, bytes]:
    SILENCE = pydub.AudioSegment.silent(duration=500)

    text = generate_captcha_text(length)

    recording = SILENCE
    for letter in text:
        voice = secrets.choice(VOICES)
        recording += voice[letter] + SILENCE

    result = io.BytesIO()
    recording.export(result, format="mp3")
    return text, result.read()
