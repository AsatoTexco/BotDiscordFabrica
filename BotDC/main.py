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
DEFAULT_PROTECTED_USERS = ["408471589366136833", "asatotexco"]


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


def get_protected_users() -> list[str]:
    raw = os.getenv("PROTECTED_USERS", "408471589366136833,asatotexco").strip()
    users = [u.strip().lower() for u in raw.split(",") if u.strip()]
    return users if users else DEFAULT_PROTECTED_USERS


def is_protected_user(member: discord.Member) -> bool:
    if not member:
        return False
    protected = get_protected_users()
    candidates = {
        str(member.id),
        member.name.lower(),
        member.display_name.lower(),
    }
    if getattr(member, "global_name", None):
        candidates.add(member.global_name.lower())
    return any(c in protected for c in candidates)


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
        name="🎲 Utilitários, Jogos & Moderação",
        value=(
            "• `/d <lados>` — Rola um dado (ex: `/d 20`)\n"
            "• `/img <tema>` — Gera uma imagem com IA sobre o tema\n"
            "• `/plagio <alvo>` — Exibe o avatar em alta definição de um membro\n"
            "• `/punish <alvo> <min>` — Prende o membro no canal de punição\n"
            "• `/free <alvo>` — Liberta o prisioneiro\n"
            "• `/stroll <user>` — Faz o membro passear pelos canais de voz\n"
            "• `/tribunal <acusado> <crime>` — Abre votação com juiz de IA e prisão\n"
            "• `/roleta` — Roleta russa entre os membros da call atual\n"
            "• `/roast <alvo>` — IA cria uma zoeira e lê no canal de voz\n"
            "• `/fofoca <mensagem>` — Plantão anônimo falado na call mais cheia\n"
            "• `/duelo <oponente>` — X1 de D20 valendo 1 minuto de prisão"
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


async def executar_punish(
    interaction: discord.Interaction,
    alvo: discord.Member,
    minutes: int = 1,
    reverso: bool = False,
    alvo_protegido: discord.Member | None = None,
):
    if not interaction.guild or not isinstance(alvo, discord.Member):
        await interaction.followup.send("```Este comando só pode ser utilizado dentro de um servidor.```")
        return

    if not reverso and minutes < 1:
        await interaction.followup.send("```O tempo de punição deve ser de pelo menos 1 minuto.```")
        return

    minutes = max(1, minutes)

    if alvo.voice is None or alvo.voice.channel is None:
        if reverso and alvo_protegido is not None:
            await interaction.followup.send(
                f"🔄 **Feitiço virou contra o feiticeiro!** {alvo.mention} tentou usar o comando em {alvo_protegido.mention}, mas não está em um canal de voz para ser preso!"
            )
        else:
            await interaction.followup.send("```O usuário não está em um canal de voz!```")
        return

    minutes_punish = min(minutes, 60) * 60
    prisao_id = get_prisao_channel_id()
    if not prisao_id:
        await interaction.followup.send("```Canal de prisão não configurado. Defina PRISAO_CHANNEL_ID no .env.```")
        return

    prisao = interaction.guild.get_channel(prisao_id) or bot.get_channel(prisao_id)
    if prisao is None:
        await interaction.followup.send("```Canal de prisão não encontrado no servidor.```")
        return

    voice_original = alvo.voice.channel if (alvo.voice and alvo.voice.channel) else None
    punishments[alvo.id] = voice_original

    if reverso and alvo_protegido is not None:
        await interaction.followup.send(
            f"🔄 **Feitiço virou contra o feiticeiro!** {alvo.mention} tentou sequestrar {alvo_protegido.mention} e foi detido por {minutes} minuto(s)! 🚨"
        )
    else:
        await interaction.followup.send(f"🚨 {alvo.mention} foi detido por {minutes} minuto(s)!")

    if voice_original is not None:
        try:
            vc = interaction.guild.voice_client
            if vc is not None:
                if vc.is_connected():
                    if vc.channel.id != voice_original.id:
                        await vc.move_to(voice_original)
                else:
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass
                    vc = await voice_original.connect(timeout=20.0, reconnect=True)
            else:
                vc = await voice_original.connect(timeout=20.0, reconnect=True)

            if vc and vc.is_connected():
                if vc.is_playing() or vc.is_paused():
                    vc.stop()

                sirene_path = os.path.join(VOICES_DIR, "sirene_grave.mp3")
                enquadro_path = os.path.join(VOICES_DIR, "enquadro_bot.mp3")

                if os.path.exists(sirene_path):
                    vc.play(discord.FFmpegPCMAudio(sirene_path))
                    while vc.is_connected() and vc.is_playing():
                        await asyncio.sleep(0.2)

                if os.path.exists(enquadro_path) and vc.is_connected():
                    vc.play(discord.FFmpegPCMAudio(enquadro_path))
                    while vc.is_connected() and vc.is_playing():
                        await asyncio.sleep(0.2)
        except Exception as error:
            print(f"Aviso durante áudio de enquadro: {error}")

    start = time.time()
    while (time.time() - start) <= minutes_punish and (alvo.id in punishments):
        if alvo.voice and alvo.voice.channel and alvo.voice.channel.id != prisao.id:
            try:
                await alvo.move_to(prisao)
            except Exception:
                pass
        await asyncio.sleep(1.0)

    if alvo.id in punishments:
        orig = punishments.pop(alvo.id, None)
        if alvo.voice and alvo.voice.channel and orig:
            try:
                await alvo.move_to(orig)
            except Exception:
                pass


@tree.command(name="stroll", description="Faz o membro passear temporariamente pelas chamadas de voz")
async def stroll(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if is_protected_user(user):
        await executar_punish(interaction, interaction.user, minutes=1, reverso=True, alvo_protegido=user)
        return

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

    if user.voice is not None and user.voice.channel is not None and voice_original is not None:
        try:
            await user.move_to(voice_original)
        except discord.DiscordException:
            pass

    await interaction.followup.send("```Passeio finalizado com sucesso! ✅```")


@tree.command(name="punish", description="Prende o membro temporariamente no canal de punição")
async def punish(interaction: discord.Interaction, alvo: discord.Member, minutes: int):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if is_protected_user(alvo):
        await executar_punish(interaction, interaction.user, minutes=max(1, minutes), reverso=True, alvo_protegido=alvo)
        return

    donos = get_donos()
    if donos and alvo.name.lower() in donos and interaction.user.name.lower() not in donos:
        await interaction.followup.send("```Você não possui permissão para punir este membro! 🤫```")
        return

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "SEQUESTRADOR 🐱\u200d👤" not in rolesUser and (donos and interaction.user.name.lower() not in donos):
        await interaction.followup.send("```Você não possui o cargo necessário para isso! 🤫```")
        return

    await executar_punish(interaction, alvo, minutes=minutes, reverso=False)


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


async def falar_no_canal(guild: discord.Guild, channel: discord.VoiceChannel, texto: str):
    if not guild or not channel:
        return
    try:
        output_file = os.path.join(VOICES_DIR, "output_audio.mp3")
        await asyncio.to_thread(text_to_speech, texto, output_file)

        vc = guild.voice_client
        if vc is not None:
            if vc.is_connected():
                if vc.channel.id != channel.id:
                    await vc.move_to(channel)
            else:
                try:
                    await vc.disconnect(force=True)
                except Exception:
                    pass
                vc = await channel.connect(timeout=20.0, reconnect=True)
        else:
            vc = await channel.connect(timeout=20.0, reconnect=True)

        if vc and vc.is_connected():
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            vc.play(discord.FFmpegPCMAudio(output_file))
            while vc.is_connected() and vc.is_playing():
                await asyncio.sleep(0.2)
    except Exception as e:
        print(f"Aviso ao falar no canal: {e}")


async def executar_stroll_rapido(guild: discord.Guild, member: discord.Member):
    if not guild or not member or not member.voice or not member.voice.channel:
        return
    voice_original = member.voice.channel
    for c in guild.voice_channels[:5]:
        if not member.voice or not member.voice.channel:
            break
        if c.id != voice_original.id:
            try:
                await member.move_to(c)
                await asyncio.sleep(0.7)
            except Exception:
                continue
    if member.voice and member.voice.channel and voice_original:
        try:
            await member.move_to(voice_original)
        except Exception:
            pass


class TribunalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.inocente: set[int] = set()
        self.culpado: set[int] = set()

    @discord.ui.button(label="Inocente (0)", style=discord.ButtonStyle.success, emoji="✅")
    async def btn_inocente(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        self.culpado.discard(uid)
        self.inocente.add(uid)
        button.label = f"Inocente ({len(self.inocente)})"
        self.children[1].label = f"Culpado ({len(self.culpado)})"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Culpado (0)", style=discord.ButtonStyle.danger, emoji="🚨")
    async def btn_culpado(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        self.inocente.discard(uid)
        self.culpado.add(uid)
        self.children[0].label = f"Inocente ({len(self.inocente)})"
        button.label = f"Culpado ({len(self.culpado)})"
        await interaction.response.edit_message(view=self)


@tree.command(name="tribunal", description="Julgue um membro com votação do servidor, juiz de IA e prisão!")
async def tribunal(interaction: discord.Interaction, acusado: discord.Member, crime: str):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if is_protected_user(acusado):
        await executar_punish(interaction, interaction.user, minutes=1, reverso=True, alvo_protegido=acusado)
        return

    view = TribunalView()
    embed = discord.Embed(
        title="⚖️ Tribunal do Servidor em Sessão!",
        description=(
            f"**Réu:** {acusado.mention}\n"
            f"**Acusação:** *{crime}*\n\n"
            "⏳ Vocês têm **20 segundos** para votar nos botões abaixo!"
        ),
        color=0xF59E0B,
    )
    msg = await interaction.followup.send(embed=embed, view=view)
    await asyncio.sleep(20)

    for child in view.children:
        child.disabled = True
    try:
        await msg.edit(view=view)
    except Exception:
        pass

    votos_culpado = len(view.culpado)
    votos_inocente = len(view.inocente)
    condenado = votos_culpado > votos_inocente

    resultado_str = "CULPADO" if condenado else "INOCENTE"
    sentenca = await generate_chatGPT(
        f"Aja como um juiz debochado e dê uma sentença de 1 frase curta declarando {acusado.display_name} {resultado_str} pelo crime: {crime}"
    )

    veredito_embed = discord.Embed(
        title=f"👨‍⚖️ Veredito Final: {resultado_str}!",
        description=f"*{sentenca}*\n\n🚨 **Culpado:** {votos_culpado} voto(s) | ✅ **Inocente:** {votos_inocente} voto(s)",
        color=0xEF4444 if condenado else 0x10B981,
    )
    await interaction.followup.send(embed=veredito_embed)

    canal_voz = (
        acusado.voice.channel
        if (acusado.voice and acusado.voice.channel)
        else (interaction.user.voice.channel if (interaction.user.voice and interaction.user.voice.channel) else None)
    )
    if canal_voz and interaction.guild:
        await falar_no_canal(interaction.guild, canal_voz, sentenca)

    if condenado:
        await executar_punish(interaction, acusado, minutes=1, reverso=False)


@tree.command(name="roleta", description="Roleta russa entre os membros do seu canal de voz!")
async def roleta(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("```Entre em um canal de voz primeiro para girar a roleta! 🎲```")
        return

    canal = interaction.user.voice.channel
    candidatos = [m for m in canal.members if not m.bot and not is_protected_user(m)]
    if not candidatos:
        await interaction.followup.send("```Não há alvos válidos neste canal de voz!```")
        return

    sorteado = random.choice(candidatos)
    giro = random.randint(1, 6)

    if giro <= 4:
        await interaction.followup.send(
            f"🔫 **Click!** A roleta apontou para {sorteado.mention} (tiro `{giro}/6`), mas a câmara estava vazia! Escapou ileso!"
        )
    elif giro == 5:
        await interaction.followup.send(
            f"🌀 **Rasante!** A roleta caiu em `{giro}/6` e {sorteado.mention} ganhou um passeio relâmpago pelas calls!"
        )
        await executar_stroll_rapido(interaction.guild, sorteado)
    else:
        await interaction.followup.send(
            f"💥 **BANG!** Tirou `{giro}/6`! {sorteado.mention} perdeu na roleta russa e vai direto para a prisão!"
        )
        await executar_punish(interaction, sorteado, minutes=1, reverso=False)


@tree.command(name="roast", description="A IA cria uma zoeira para o alvo e fala no canal de voz!")
async def roast(interaction: discord.Interaction, alvo: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    alvo_real = interaction.user if is_protected_user(alvo) else alvo
    zoeira = await generate_chatGPT(
        f"Faça uma zoeira curta, engraçada e criativa de 1 ou 2 frases zoando o amigo {alvo_real.display_name} no Discord."
    )

    embed = discord.Embed(
        title=f"🔥 Roast para {alvo_real.display_name}",
        description=zoeira[:4000],
        color=0xEF4444,
    )
    await interaction.followup.send(embed=embed)

    canal = (
        alvo_real.voice.channel
        if (alvo_real.voice and alvo_real.voice.channel)
        else (interaction.user.voice.channel if (interaction.user.voice and interaction.user.voice.channel) else None)
    )
    if canal and interaction.guild:
        await falar_no_canal(interaction.guild, canal, zoeira)


@tree.command(name="fofoca", description="Envia um plantão de fofoca anônimo falado na call mais cheia!")
async def fofoca(interaction: discord.Interaction, mensagem: str):
    await interaction.response.defer(ephemeral=True, thinking=True)

    if not interaction.guild:
        await interaction.followup.send("Este comando só funciona em um servidor.", ephemeral=True)
        return

    canais_com_gente = [
        c for c in interaction.guild.voice_channels if len([m for m in c.members if not m.bot]) > 0
    ]
    if not canais_com_gente:
        await interaction.followup.send("Não há ninguém em canais de voz no momento para ouvir a fofoca! 🤫", ephemeral=True)
        return

    canal_alvo = max(canais_com_gente, key=lambda c: len([m for m in c.members if not m.bot]))
    await interaction.followup.send(
        f"🕵️ Sua fofoca anônima está sendo transmitida no canal **{canal_alvo.name}**!",
        ephemeral=True,
    )

    texto_plantao = f"Atenção servidor, plantão urgente da fofoca: {mensagem}"
    await falar_no_canal(interaction.guild, canal_alvo, texto_plantao)


class DueloView(discord.ui.View):
    def __init__(self, desafiante: discord.Member, oponente: discord.Member):
        super().__init__(timeout=60)
        self.desafiante = desafiante
        self.oponente = oponente
        self.finalizado = False

    @discord.ui.button(label="Aceitar Duelo ⚔️", style=discord.ButtonStyle.primary)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.oponente.id:
            await interaction.response.send_message("Apenas o membro desafiado pode aceitar este duelo!", ephemeral=True)
            return
        if self.finalizado:
            return
        self.finalizado = True
        button.disabled = True
        await interaction.response.edit_message(view=self)

        d1 = random.randint(1, 20)
        d2 = random.randint(1, 20)
        while d1 == d2:
            d1 = random.randint(1, 20)
            d2 = random.randint(1, 20)

        vencedor = self.desafiante if d1 > d2 else self.oponente
        perdedor = self.oponente if d1 > d2 else self.desafiante

        embed = discord.Embed(
            title="⚔️ Resultado do Duelo!",
            description=(
                f"🎲 **{self.desafiante.display_name}** tirou **{d1}**\n"
                f"🎲 **{self.oponente.display_name}** tirou **{d2}**\n\n"
                f"🏆 **Vencedor:** {vencedor.mention}\n"
                f"🚨 **Perdedor (1 min de prisão):** {perdedor.mention}"
            ),
            color=0x10B981,
        )
        await interaction.followup.send(embed=embed)
        await executar_punish(interaction, perdedor, minutes=1, reverso=False)


@tree.command(name="duelo", description="Desafie alguém para um X1 de dados valendo 1 minuto de prisão!")
async def duelo(interaction: discord.Interaction, oponente: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if oponente.bot or oponente.id == interaction.user.id:
        await interaction.followup.send("```Escolha outro membro válido do servidor para duelar! ⚔️```")
        return

    if is_protected_user(oponente):
        await executar_punish(interaction, interaction.user, minutes=1, reverso=True, alvo_protegido=oponente)
        return

    view = DueloView(interaction.user, oponente)
    embed = discord.Embed(
        title="⚔️ Desafio de Duelo!",
        description=(
            f"{interaction.user.mention} desafiou {oponente.mention} para um X1 de **D20**!\n"
            "Quem tirar o menor número vai preso por **1 minuto**.\n\n"
            f"{oponente.mention}, clique no botão abaixo em até 60s para aceitar!"
        ),
        color=0x5865F2,
    )
    await interaction.followup.send(embed=embed, view=view)


if __name__ == "__main__":
    start_password_manager_server(port=8022, background=True)
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("A variável de ambiente TOKEN não foi definida no arquivo .env!")
    bot.run(token=token)
