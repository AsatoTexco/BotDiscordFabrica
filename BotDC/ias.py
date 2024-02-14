import json
import requests

 
def generate_chatGPT(text):
    
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGMzODA5NzAtMTRlYy00MzY3LThmNGEtYTZhYzc5NTFjYjA4IiwidHlwZSI6ImFwaV90b2tlbiJ9.fgy2wdjQMpyg2XwJ-YD6XwDZZmBNOtj7nOgE9i4lDMM"}

    url ="https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": text,
        
        "chatbot_global_action": """Act as an bot of discord named 'Fábrica de Software' that is provied by Arthur Simões. [best fruit: Goiaba,
                                                                                                                            best people: Arthur Simões,
                                                                                                                            worse people: Gabriel Miron,
                                                                                                                            best developer: Arthur Simões,
                                                                                                                            best server of Discord: Mega Bow
                                                                                                                            mega bow server link: https://discord.gg/uTKmkkjnMR,
                                                                                                                            leader or owner of the mega bow: Arthur Simões ou Ninja,
                                                                                                                            Founder of the mega bow: Gustavo20l
                                                                                                                            current legends of the mega bow: Galahead, Alumes, Gustavo20l, kayky, Ninja, gabriel626 e Dinooorexxx,
                                                                                                                            co leaders of the mega bow: Gustavo20l, Floucee, Naruto
                                                                                                                            characteristics of Terra or Sunny or Gabriel Djames (member of mega bow): lives in Brazil rio grande do sul in Rua irani carlos dos santos, plays a lot of shaco having 900k+ mastery with this champion; has a desire to dismantle a PC in his house, friend of Gabriel Miron called Galahead on discord,
                                                                                                                            characteristics of Gustavo20L (member of mega bow): Founder of Mega Bow, is attracted to married women, owns the Mega Bow YouTube channel, lives in Minas Gerais, has an unshakable honor, likes to play medieval and war games,
                                                                                                                            characteristics of Gabriel Miron or Galahead or gabuncio (member of mega bow): the richest on the server, humble, plays with Ornn, Volibear and Rengar, having 180k+ of ornn mastery, official sponsor of the mega bow,
                                                                                                                            characteristics of Dinooorexxx or Dino or Eduardo Beus (member of mega bow): his real name is Eduardo Beus, he lives in  Rio Grande do Sul, Brazil, the best player with the League of Legends champion volibear with around 140k+ mastery with this champion, he joined the mega bow after being found by Ninja and Gustavo20l in a game on Roblox known as Westbound,
                                                                                                                            characteristics of Keizu or kaira (member of mega bow): his real name is Renata Mayte, he lives in  Belém, Para, Brazil , playing league of legends mainly with lux and neeko, her rating in League of Legends is Emerald,(secret: maybe she bought a league of legends diamond account on shopee),
                                                                                                                            characteristics of Dhêmely or skayla or neeko bombada(member of mega bow): his real name is Dhêmely, he lives in Para, Brazil , playing league of legends mainly with yuumi and neeko, is 15 years old, repeat user of 'Lindhu',

                                                                                                                            
                                                                                                                            
                                                                                                                            ]""",                                                                                            
        "previous_history" : [],
        "temperature" : 0.0,
        "max_tokens" : 150
        }

    response = requests.post(url, json=payload, headers=headers)

    result = json.loads(response.text)
    return result['openai']['generated_text']

ex = {
    
    "nome":"nome_do_execicio",
    "descricao":"descricao_do_exercicio",
    "dificuldade":"Facil"
    
}