import os
import httpx

DEFAULT_PROMPT = (
    "Você é um bot descontraído e inteligente para Discord chamado 'Fábrica de Software'. "
    "Responda sempre em português do Brasil de forma clara, prestativa e bem-humorada."
)


def get_system_prompt() -> str:
    return os.getenv("AI_SYSTEM_PROMPT", DEFAULT_PROMPT).strip()


REFUSAL_TERMS = (
    "desculpe,",
    "desculpe, mas",
    "não posso ajudar",
    "não posso atender",
    "não posso cumprir",
    "não posso criar",
    "não posso gerar",
    "não posso fazer",
    "infelizmente, não posso",
    "lamento, mas não",
    "como uma ia",
    "como um modelo de linguagem",
    "i'm sorry",
    "i cannot",
    "i can't",
)


def is_refusal(text: str) -> bool:
    if not text or not text.strip():
        return True
    low = text.strip().lower()
    return any(term in low for term in REFUSAL_TERMS)


async def generate_chatGPT(
    text: str,
    fallback: str = "Não consegui processar sua pergunta no momento. Tente novamente em instantes! 🤖",
) -> str:
    eden_key = os.getenv("EDENAI_API_KEY", "").strip()
    system_prompt = get_system_prompt()

    async with httpx.AsyncClient(timeout=25.0) as client:
        if eden_key and eden_key != "sua_chave_edenai_aqui":
            try:
                headers = {"Authorization": f"Bearer {eden_key}"}
                payload = {
                    "providers": "openai",
                    "text": text,
                    "chatbot_global_action": system_prompt,
                    "previous_history": [],
                    "temperature": 0.7,
                    "max_tokens": 500,
                }
                resp = await client.post("https://api.edenai.run/v2/text/chat", json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    generated = (data.get("openai") or {}).get("generated_text")
                    if generated and not is_refusal(generated):
                        return generated.strip()[:4000]
            except Exception as e:
                print(f"Aviso: falha ao consultar EdenAI ({e}), usando fallback...")

        for model_name in ("openai", "mistral"):
            try:
                fallback_payload = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "model": model_name,
                }
                resp = await client.post("https://text.pollinations.ai/", json=fallback_payload)
                if resp.status_code == 200 and resp.text.strip() and not is_refusal(resp.text):
                    return resp.text.strip()[:4000]
            except Exception as e:
                print(f"Erro no fallback de IA ({model_name}): {e}")

    return fallback
