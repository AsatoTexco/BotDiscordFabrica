from Models.Dj import Dj
import discord


intents = discord.Intents.default()
intents.message_content = True  # Configurar a intenção como True
bot = discord.Client(intents=intents)
 

dj = Dj(bot)


token = 'MTE2NTAxNjk5OTQ3NTMwMjUzMg.GtdYCn.toerONW_I1qK3bS2ffyTAetMcDYcIuEXM9JVuk'
bot.run(token=token)
