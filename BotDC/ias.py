import os
import httpx

DEFAULT_PROMPT = (
    "Você é um bot descontraído e inteligente para Discord chamado 'Fábrica de Software'. "
    "Responda sempre em português do Brasil de forma clara, prestativa e bem-humorada."
)


def get_system_prompt() -> str:
    return os.getenv("AI_SYSTEM_PROMPT", DEFAULT_PROMPT).strip()


async def generate_chatGPT(text: str) -> str:
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
                    "temperature": 0.5,
                    "max_tokens": 450,
                }
                resp = await client.post("https://api.edenai.run/v2/text/chat", json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    generated = (data.get("openai") or {}).get("generated_text")
                    if generated:
                        return generated[:4000]
            except Exception as e:
                print(f"Aviso: falha ao consultar EdenAI ({e}), usando fallback...")

        try:
            fallback_payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                "model": "openai",
            }
            resp = await client.post("https://text.pollinations.ai/", json=fallback_payload)
            if resp.status_code == 200 and resp.text.strip():
                return resp.text.strip()[:4000]
        except Exception as e:
            print(f"Erro no fallback de IA: {e}")

    return "Não consegui processar sua pergunta no momento. Tente novamente em instantes! 🤖"
