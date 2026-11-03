import base64
import os
import re
import httpx

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

TIKTOK_TTS_URL = "https://tiktok-tts.weilnet.workers.dev/api/generation"
GOOGLE_TTS_URL = "https://translate.google.com/translate_tts"
DEFAULT_TIKTOK_VOICE = "br_005"


def limpar_texto_para_fala(text: str, max_chars: int = 1200) -> str:
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
        texto = corte[: ultimo_ponto + 1] if ultimo_ponto > 100 else corte

    return texto if texto else "Olá!"


def dividir_em_frases(texto: str, max_bytes: int = 220) -> list[str]:
    partes_brutas = [p.strip() for p in re.split(r"(?<=[.!?])\s+", texto) if p.strip()]
    if not partes_brutas:
        partes_brutas = [texto]

    chunks: list[str] = []
    atual = ""

    for frase in partes_brutas:
        candidato = f"{atual} {frase}".strip() if atual else frase
        if len(candidato.encode("utf-8")) <= max_bytes:
            atual = candidato
            continue

        if atual:
            chunks.append(atual)
            atual = ""

        if len(frase.encode("utf-8")) <= max_bytes:
            atual = frase
        else:
            palavras = frase.split()
            for palavra in palavras:
                cand_p = f"{atual} {palavra}".strip() if atual else palavra
                if len(cand_p.encode("utf-8")) <= max_bytes:
                    atual = cand_p
                else:
                    if atual:
                        chunks.append(atual)
                    atual = palavra[:50]

    if atual:
        chunks.append(atual)

    return chunks if chunks else ["Olá!"]


def _gerar_chunk_tiktok(chunk: str, output_path: str, voice: str = DEFAULT_TIKTOK_VOICE) -> bool:
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.post(TIKTOK_TTS_URL, json={"text": chunk, "voice": voice})
            if resp.status_code == 200:
                data = resp.json()
                b64_audio = data.get("data")
                if b64_audio:
                    audio_bytes = base64.b64decode(b64_audio)
                    if len(audio_bytes) > 500:
                        with open(output_path, "wb") as f:
                            f.write(audio_bytes)
                        return True
    except Exception as e:
        print(f"Aviso TikTok TTS: {e}")
    return False


def _gerar_chunk_google(chunk: str, output_path: str) -> bool:
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            params = {"ie": "UTF-8", "client": "tw-ob", "tl": "pt-BR", "q": chunk[:200]}
            resp = client.get(GOOGLE_TTS_URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 500:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return True
    except Exception as e:
        print(f"Aviso Google HTTP TTS: {e}")

    if HAS_GTTS:
        try:
            tts = gTTS(text=chunk, lang="pt", tld="com.br", slow=False)
            tts.save(output_path)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            print(f"Aviso gTTS: {e}")
    return False


def gerar_audios_tts(text: str, out_dir: str, prefix: str = "tts") -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    clean_text = limpar_texto_para_fala(text)
    chunks = dividir_em_frases(clean_text)
    voice = os.getenv("TTS_VOICE", DEFAULT_TIKTOK_VOICE).strip() or DEFAULT_TIKTOK_VOICE

    arquivos: list[str] = []
    for idx, chunk in enumerate(chunks):
        caminho = os.path.join(out_dir, f"{prefix}_{idx}.mp3")
        ok = _gerar_chunk_tiktok(chunk, caminho, voice=voice)
        if not ok:
            ok = _gerar_chunk_google(chunk, caminho)
        if ok and os.path.exists(caminho):
            arquivos.append(caminho)

    return arquivos


def text_to_speech(text: str, output_file: str) -> bool:
    out_dir = os.path.dirname(os.path.abspath(output_file)) or "."
    os.makedirs(out_dir, exist_ok=True)
    clean_text = limpar_texto_para_fala(text)
    chunks = dividir_em_frases(clean_text)
    voice = os.getenv("TTS_VOICE", DEFAULT_TIKTOK_VOICE).strip() or DEFAULT_TIKTOK_VOICE

    if _gerar_chunk_tiktok(chunks[0], output_file, voice=voice):
        return True
    return _gerar_chunk_google(chunks[0], output_file)
