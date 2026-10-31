import os
import re
from gtts import gTTS


def text_to_speech(text: str, output_file: str) -> bool:
    clean_text = re.sub(r"[*_`#~>]+", "", (text or "")).strip()
    if not clean_text:
        clean_text = "Olá!"

    out_dir = os.path.dirname(os.path.abspath(output_file))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    tts = gTTS(text=clean_text[:500], lang="pt")
    tts.save(output_file)
    return True
