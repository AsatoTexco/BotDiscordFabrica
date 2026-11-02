import asyncio
import os
import re
from gtts import gTTS

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

DEFAULT_EDGE_VOICE = "pt-BR-AntonioNeural"
DEFAULT_EDGE_RATE = "+30%"
USED_EDGE_LAST = False


def limpar_texto_para_fala(text: str, max_chars: int = 2500) -> str:
    if not text:
        return "Olá!"

    texto = text
    texto = re.sub(r"https?://\S+", "", texto)
    texto = re.sub(r"<[@#!&]*\d+>", "", texto)
    texto = re.sub(r"<a?:\w+:\d+>", "", texto)
    texto = re.sub(r"[*_`#~>|]+", "", texto)
    texto = re.sub(r"[^\w\s,.!?:;()\-áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ\"']", " ", texto)
    texto = re.sub(r"\s*\n+\s*", ". ", texto)
    texto = re.sub(r"\s{2,}", " ", texto).strip()

    if len(texto) > max_chars:
        corte = texto[:max_chars]
        ultimo_ponto = max(corte.rfind("."), corte.rfind("!"), corte.rfind("?"))
        texto = corte[: ultimo_ponto + 1] if ultimo_ponto > 200 else corte

    return texto if texto else "Olá!"


async def _gerar_edge_tts(texto: str, output_file: str, voice: str, rate: str) -> bool:
    communicate = edge_tts.Communicate(text=texto, voice=voice, rate=rate)
    await communicate.save(output_file)
    return os.path.exists(output_file) and os.path.getsize(output_file) > 0


def get_ffmpeg_tts_options() -> str:
    if USED_EDGE_LAST:
        return '-vn -af "apad=pad_dur=0.6"'
    return '-vn -af "atempo=1.35,apad=pad_dur=0.6"'


def text_to_speech(text: str, output_file: str) -> bool:
    global USED_EDGE_LAST
    clean_text = limpar_texto_para_fala(text)

    out_dir = os.path.dirname(os.path.abspath(output_file))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    voice = os.getenv("TTS_VOICE", DEFAULT_EDGE_VOICE).strip() or DEFAULT_EDGE_VOICE
    rate = os.getenv("TTS_RATE", DEFAULT_EDGE_RATE).strip() or DEFAULT_EDGE_RATE

    if HAS_EDGE_TTS:
        try:
            if asyncio.run(_gerar_edge_tts(clean_text, output_file, voice, rate)):
                USED_EDGE_LAST = True
                return True
        except Exception as e:
            print(f"Aviso: falha no Edge-TTS ({e}), usando gTTS...")

    USED_EDGE_LAST = False
    tts = gTTS(text=clean_text, lang="pt", tld="com.br", slow=False)
    tts.save(output_file)
    return True
