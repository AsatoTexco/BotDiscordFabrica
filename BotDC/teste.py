import os
import discord
from dotenv import load_dotenv
from Models.Dj import Dj

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
dj = Dj(bot)

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if token:
        bot.run(token=token)
