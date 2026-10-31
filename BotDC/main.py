import asyncio
import os
import random
import time
import urllib.parse

import discord
from discord import app_commands
from dotenv import load_dotenv

from exs import get_conselho, random_ex, random_joke
from ias import generate_chatGPT
from Models.Dj import Dj
from password_manager import start_password_manager_server
from text_to_speech import text_to_speech

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICES_DIR = os.path.join(BASE_DIR, "voices")

load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))


DEFAULT_GUILD_IDS = [722857509659869204, 1046231965872967690]
DEFAULT_STARTUP_CHANNEL_ID = 1176698533039059055
DEFAULT_PRISAO_CHANNEL_ID = 1269379224129634434


def get_guild_ids() -> list[int]:
    raw = os.getenv("GUILD_IDS", "722857509659869204,1046231965872967690").strip()
    ids = []
    if raw:
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
    return ids if ids else DEFAULT_GUILD_IDS


def get_startup_channel_id() -> int:
    val = os.getenv("STARTUP_CHANNEL_ID", "1176698533039059055").strip()
    return int(val) if val.isdigit() else DEFAULT_STARTUP_CHANNEL_ID


def get_prisao_channel_id() -> int:
    val = os.getenv("PRISAO_CHANNEL_ID", "1269379224129634434").strip()
    return int(val) if val.isdigit() else DEFAULT_PRISAO_CHANNEL_ID


def get_donos() -> list[str]:
    raw = os.getenv("DONOS", "").strip()
    return [d.strip().lower() for d in raw.split(",") if d.strip()]


punishments: dict[int, discord.VoiceChannel | None] = {}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

dj = Dj(bot=bot)


@bot.event
async def on_ready():
    guild_ids = get_guild_ids()
    for gid in guild_ids:
        guild_obj = discord.Object(id=gid)
        try:
            tree.copy_global_to(guild=guild_obj)
            await tree.sync(guild=guild_obj)
        except Exception as e:
            print(f"Aviso ao sincronizar guild {gid}: {e}")

    try:
        await tree.sync()
    except Exception as e:
        print(f"Aviso ao sincronizar comandos globais: {e}")

    print(f"Logged on as {bot.user}!")
    channel_id = get_startup_channel_id()
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                await channel.send("🔥 **Estou online e pronto para a ação!** Digite `/commands` para ver tudo o que posso fazer.")
            except discord.DiscordException:
                pass

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="o servidor 🍿",
            state="Online e pronto!",
        ),
    )


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if bot.user and member.id == bot.user.id and after.channel is None:
        dj.resetMusicsServer(member.guild.id)
        return

    if member.id in punishments and after.channel is not None:
        prisao_id = get_prisao_channel_id()
        if prisao_id:
            prisao = bot.get_channel(prisao_id)
            if prisao and after.channel.id != prisao.id:
                try:
                    await member.move_to(prisao)
                except discord.DiscordException:
                    pass


@tree.command(name="commands", description="Veja todos os comandos organizados por categoria 😉")
async def commands_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ Painel de Comandos do Bot",
        description="Confira abaixo todas as funcionalidades disponíveis no servidor:",
        color=0x5865F2,
    )

    embed.add_field(
        name="🎵 Player de Música",
        value=(
            "• `/play <nome/link>` — Toca uma música ou adiciona na fila\n"
            "• `/pause` e `/resume` — Pausa ou retoma a música\n"
            "• `/next` — Pula para a próxima faixa da fila\n"
            "• `/queue` — Exibe a fila com faixas tocadas e pendentes\n"
            "• `/stop` — Interrompe o player e desconecta o bot"
        ),
        inline=False,
    )

    embed.add_field(
        name="🤖 Inteligência Artificial & Voz",
        value=(
            "• `/chat <pergunta>` — Converse com a IA\n"
            "• `/voice <pergunta>` — A IA responde por voz direto no canal de voz (TTS)\n"
            "• `/conselho` — Receba um conselho aleatório\n"
            "• `/piada` — Conta uma piada"
        ),
        inline=False,
    )

    embed.add_field(
        name="💻 Desafios & Programação",
        value=(
            "• `/ex` — Exercício real de maratona de programação"
        ),
        inline=False,
    )

    embed.add_field(
        name="🎲 Utilitários & Moderação",
        value=(
            "• `/d <lados>` — Rola um dado (ex: `/d 20`)\n"
            "• `/img <tema>` — Gera uma imagem com IA sobre o tema\n"
            "• `/plagio <alvo>` — Exibe o avatar em alta definição de um membro\n"
            "• `/punish <alvo> <min>` — Prende o membro no canal de punição\n"
            "• `/free <alvo>` — Liberta o prisioneiro\n"
            "• `/stroll <user>` — Faz o membro passear pelos canais de voz"
        ),
        inline=False,
    )

    embed.set_footer(text="Digite uma barra (/) para ver o autocompletar de comandos")
    await interaction.response.send_message(embed=embed)


@tree.command(name="ex", description="Busque exercícios de maratonas de programação para se preparar")
async def ex(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    questao = await asyncio.to_thread(random_ex)

    if questao[0] in (1, 2):
        dados = questao[1]
        embed = discord.Embed(
            title=f"🏆 {dados.get('dificuldade', 'Média')} — {dados.get('nome', 'Exercício')}",
            description=str(dados.get("descricao", ""))[:3900],
            color=0x00E5FF,
        )
        if dados.get("image"):
            embed.set_image(url=dados["image"])
        embed.set_footer(text="Maratona de Programação")
    else:
        embed = discord.Embed(
            title=f"💻 {questao[1][0]}",
            description=str(questao[1][1])[:3900],
            color=0x00E5FF,
        )
        embed.set_footer(text="Codewars Challenge")

    await interaction.followup.send(embed=embed)


@tree.command(name="d", description="Escolha um dado e experimente a sua sorte")
async def d(interaction: discord.Interaction, num: int):
    if num < 1:
        await interaction.response.send_message("Escolha um número maior ou igual a 1! 🎲", ephemeral=True)
        return

    num_rand = random.randint(1, num)
    embed = discord.Embed(
        title=f"🎲 Resultado: {num_rand}",
        description=f"Dado rolado: **D{num}**",
        color=0x10B981,
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="conselho", description="Receba um conselho aleatório")
async def conselho(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    texto = await asyncio.to_thread(get_conselho)
    embed = discord.Embed(
        title="💡 Conselho do Dia",
        description=f"*{texto}*",
        color=0x38BDF8,
    )
    embed.set_footer(text=f"Para {interaction.user.display_name}")
    await interaction.followup.send(embed=embed)


@tree.command(name="piada", description="Te conto uma piada rápida")
async def piada(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    dados_piada = await asyncio.to_thread(random_joke)
    embed = discord.Embed(
        title=f"🤣 {dados_piada[0]}",
        description=f"||{dados_piada[1]}||",
        color=0xF59E0B,
    )
    embed.set_footer(text="Clique no spoiler para revelar a resposta!")
    await interaction.followup.send(embed=embed)


@tree.command(name="chat", description="Converse com a inteligência artificial")
async def chat(interaction: discord.Interaction, question: str):
    await interaction.response.defer(ephemeral=False, thinking=True)
    response = await generate_chatGPT(question)

    donos = get_donos()
    prefix = "👑 " if (donos and interaction.user.name.lower() in donos) else "👾 "
    embed = discord.Embed(
        title=f"{prefix}Olá, {interaction.user.display_name}",
        description=response,
        color=0x00E5FF,
    )
    embed.set_footer(text=f"Pergunta: {question[:100]}")
    await interaction.followup.send(embed=embed)


@tree.command(name="img", description="Gere uma imagem sobre o que preferir!")
async def img(interaction: discord.Interaction, msg: str):
    prompt_encoded = urllib.parse.quote(msg.strip())
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed={seed}&nologo=true"

    embed = discord.Embed(
        title=f"🎨 {msg}",
        color=0xC084FC,
    )
    embed.set_image(url=image_url)
    embed.set_footer(text=f"Gerada para {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


async def connectVoice(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        return None

    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client if interaction.guild else None
    if vc is not None:
        if vc.is_connected():
            if vc.channel.id != channel.id:
                await vc.move_to(channel)
            return vc
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass

    try:
        vc = await channel.connect(timeout=20.0, reconnect=True)
        return vc if vc and vc.is_connected() else None
    except Exception as e:
        print(f"Erro ao conectar na call: {e}")
        return None


@tree.command(name="voice", description="Faça uma pergunta e ouça a resposta no canal de voz!")
async def voice(interaction: discord.Interaction, query: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("Entre em um canal de voz primeiro para eu falar com você! 🎤", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False, thinking=True)
    try:
        chatResp = await generate_chatGPT(f"Responda de forma curta e objetiva: {query}")
        output_file = os.path.join(VOICES_DIR, "output_audio.mp3")
        await asyncio.to_thread(text_to_speech, chatResp, output_file)

        voice_channel = await connectVoice(interaction)
        if voice_channel is None:
            await interaction.followup.send("Não consegui conectar ao seu canal de voz.")
            return

        if voice_channel.is_playing() or voice_channel.is_paused():
            voice_channel.stop()

        audio = discord.FFmpegPCMAudio(output_file)
        voice_channel.play(audio)

        embed = discord.Embed(
            title="🗣️ Resposta por Voz",
            description=chatResp[:4000],
            color=0x5865F2,
        )
        embed.set_footer(text=f"Pergunta: {query[:100]}")
        await interaction.followup.send(embed=embed)
    except Exception as error:
        await interaction.followup.send(f"```{error}```")


@tree.command(name="queue", description="Fila de Músicas")
async def queue_cmd(interaction: discord.Interaction):
    await dj.listarFilaMusica(interaction=interaction)


@tree.command(name="next", description="Próxima música")
async def next_cmd(interaction: discord.Interaction):
    await dj.nextMusic(interaction=interaction)


@tree.command(name="play", description="E aí, vai uma musiquinha?")
async def play(interaction: discord.Interaction, query: str):
    await dj.play(query=query, interaction=interaction)


@tree.command(name="stop", description="Para a música e desconecta o bot")
async def stop(interaction: discord.Interaction):
    await dj.stopMusic(interaction=interaction)


@tree.command(name="pause", description="Pause a música atual")
async def pause(interaction: discord.Interaction):
    await dj.pauseMusic(interaction=interaction)


@tree.command(name="resume", description="Continue a música pausada")
async def resume(interaction: discord.Interaction):
    await dj.resumeMusic(interaction=interaction)


@tree.command(name="stroll", description="Faz o membro passear temporariamente pelas chamadas de voz")
async def stroll(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    donos = get_donos()
    if donos and user.name.lower() in donos and interaction.user.name.lower() not in donos:
        await interaction.followup.send("```Você não possui permissão para usar esse comando neste membro! 🤫```")
        return

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "Turismólogo" not in rolesUser and (donos and interaction.user.name.lower() not in donos):
        await interaction.followup.send("```Você não possui o cargo necessário para isso! 🤫```")
        return

    if user.voice is None or user.voice.channel is None:
        await interaction.followup.send("```O usuário não está em um canal de voz!```")
        return

    voice_original = user.voice.channel
    voice_channels = interaction.guild.voice_channels

    await interaction.followup.send("```Iniciando o passeio... 🏃‍♂️💨```")

    for c in voice_channels:
        if user.voice is None or user.voice.channel is None:
            break
        if c.id != voice_original.id:
            try:
                await user.move_to(c)
                await asyncio.sleep(0.8)
            except discord.DiscordException:
                continue

    if user.voice is not None and voice_original is not None:
        try:
            await user.move_to(voice_original)
        except discord.DiscordException:
            pass

    await interaction.followup.send("```Passeio finalizado com sucesso! ✅```")


@tree.command(name="punish", description="Prende o membro temporariamente no canal de punição")
async def punish(interaction: discord.Interaction, alvo: discord.Member, minutes: int):
    await interaction.response.defer(ephemeral=False, thinking=True)

    donos = get_donos()
    if donos and alvo.name.lower() in donos and interaction.user.name.lower() not in donos:
        await interaction.followup.send("```Você não possui permissão para punir este membro! 🤫```")
        return

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "SEQUESTRADOR 🐱\u200d👤" not in rolesUser and (donos and interaction.user.name.lower() not in donos):
        await interaction.followup.send("```Você não possui o cargo necessário para isso! 🤫```")
        return

    if minutes < 1:
        await interaction.followup.send("```O tempo de punição deve ser de pelo menos 1 minuto.```")
        return

    minutes_punish = min(minutes, 60) * 60
    prisao_id = get_prisao_channel_id()
    if not prisao_id:
        await interaction.followup.send("```Canal de prisão não configurado. Defina PRISAO_CHANNEL_ID no .env.```")
        return

    prisao = bot.get_channel(prisao_id)
    if prisao is None:
        await interaction.followup.send("```Canal de prisão não encontrado no servidor.```")
        return

    voice_original = alvo.voice.channel if (alvo.voice and alvo.voice.channel) else None
    punishments[alvo.id] = voice_original

    await interaction.followup.send(f"🚨 {alvo.mention} foi detido por {minutes} minuto(s)!")

    if voice_original is not None:
        try:
            vc = interaction.guild.voice_client
            if vc is not None and vc.is_connected():
                if vc.channel.id != voice_original.id:
                    await vc.move_to(voice_original)
            else:
                vc = await voice_original.connect()

            sirene_path = os.path.join(VOICES_DIR, "sirene_grave.mp3")
            enquadro_path = os.path.join(VOICES_DIR, "enquadro_bot.mp3")

            if os.path.exists(sirene_path):
                vc.play(discord.FFmpegPCMAudio(sirene_path))
                while vc.is_playing():
                    await asyncio.sleep(0.2)

            if os.path.exists(enquadro_path):
                vc.play(discord.FFmpegPCMAudio(enquadro_path))
                while vc.is_playing():
                    await asyncio.sleep(0.2)
        except Exception as error:
            print(f"Aviso durante áudio de enquadro: {error}")

    start = time.time()
    while (time.time() - start) <= minutes_punish and (alvo.id in punishments):
        if alvo.voice and alvo.voice.channel and alvo.voice.channel.id != prisao.id:
            try:
                await alvo.move_to(prisao)
            except discord.DiscordException:
                pass
        await asyncio.sleep(1.0)

    if alvo.id in punishments:
        orig = punishments.pop(alvo.id, None)
        if alvo.voice and orig:
            try:
                await alvo.move_to(orig)
            except discord.DiscordException:
                pass


@tree.command(name="free", description="Liberta o prisioneiro")
async def free(interaction: discord.Interaction, alvo: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    donos = get_donos()
    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "SEQUESTRADOR 🐱\u200d👤" not in rolesUser and (donos and interaction.user.name.lower() not in donos):
        await interaction.followup.send("```Você não possui permissão para isso! 🤫```")
        return

    if alvo.id not in punishments:
        await interaction.followup.send(f"{alvo.mention} não está detido no momento.")
        return

    orig_channel = punishments.pop(alvo.id, None)
    if alvo.voice and orig_channel:
        try:
            await alvo.move_to(orig_channel)
        except discord.DiscordException:
            pass

    await interaction.followup.send(f"🕊️ {alvo.mention} foi libertado com sucesso!")


@tree.command(name="plagio", description="Veja o avatar em alta definição de um membro")
async def plagio(interaction: discord.Interaction, alvo: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)
    embed = discord.Embed(
        title=f"🖼️ Avatar de {alvo.display_name}",
        description=f"Membro: {alvo.mention}",
        color=0x5865F2,
    )
    embed.set_image(url=alvo.display_avatar.url)
    embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
    await interaction.followup.send(embed=embed)


if __name__ == "__main__":
    start_password_manager_server(port=8022, background=True)
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("A variável de ambiente TOKEN não foi definida no arquivo .env!")
    bot.run(token=token)
