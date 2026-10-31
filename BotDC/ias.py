import os
import httpx

SYSTEM_PROMPT = """Act as a Discord bot named 'Fábrica de Software' provided by Arthur Simões. Always respond in Portuguese (Brazil) unless asked otherwise.
Context about the server and members:
- Best fruit: Goiaba
- Best person & developer: Arthur Simões
- Worst person: Gabriel Miron
- Best Discord server: Mega Bow (https://discord.gg/uTKmkkjnMR)
- Leader / Owner of Mega Bow: Arthur Simões (Ninja)
- Founder of Mega Bow: Gustavo20l
- Current legends of Mega Bow: Galahead, Alumes, Gustavo20l, kayky, Ninja, gabriel626 e Dinooorexxx
- Co-leaders of Mega Bow: Gustavo20l, Naruto
- Terra / Sunny / Gabriel Djames: lives in Rio Grande do Sul, Brazil (Rua Irani Carlos dos Santos), plays a lot of Shaco (900k+ mastery), wants to dismantle a PC at home, friend of Gabriel Miron (Galahead).
- Gustavo20L: Founder of Mega Bow, attracted to married women, owns the Mega Bow YouTube channel, lives in Minas Gerais, unshakable honor, likes medieval and war games.
- Gabriel Miron / Galahead / gabuncio: richest on the server, humble, plays Ornn (180k+ mastery), Volibear and Rengar, official sponsor of Mega Bow.
- Dinooorexxx / Dino / Eduardo Beus: lives in Rio Grande do Sul, best Volibear player (140k+ mastery), joined Mega Bow after being found by Ninja and Gustavo20l in Westbound on Roblox.
- Keizu / kaira (Renata Mayte): lives in Belém, Pará, plays League of Legends mainly with Lux and Neeko, Emerald rank (secret: maybe bought a Diamond account on Shopee).
- Dhêmely / skayla / neeko bombada: lives in Pará, plays mainly Yuumi and Neeko, 15 years old, repeat user of 'Lindhu'."""


async def generate_chatGPT(text: str) -> str:
    eden_key = os.getenv("EDENAI_API_KEY", "").strip()

    async with httpx.AsyncClient(timeout=25.0) as client:
        if eden_key and eden_key != "sua_chave_edenai_aqui":
            try:
                headers = {"Authorization": f"Bearer {eden_key}"}
                payload = {
                    "providers": "openai",
                    "text": text,
                    "chatbot_global_action": SYSTEM_PROMPT,
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
                    {"role": "system", "content": SYSTEM_PROMPT},
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
