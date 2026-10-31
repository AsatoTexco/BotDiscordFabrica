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

GUILD_IDS = [722857509659869204, 1046231965872967690]
STARTUP_CHANNEL_ID = 1176698533039059055
PRISAO_CHANNEL_ID = 1269379224129634434

punishments: dict[int, discord.VoiceChannel | None] = {}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

donos = ["ninjasupremobr", "asatotexco"]
perm_stroll = ["ninjasupremobr", "asatotexco"]
perm_punishment = ["ninjasupremobr", "asatotexco"]

EMOJIS = [
    ":dotted_line_face:",
    ":face_with_raised_eyebrow:",
    ":joy:",
    ":star:",
    ":face_with_monocle:",
    ":interrobang:",
    ":face_in_clouds:",
    ":detective:",
    ":smiling_imp:",
    ":disguised_face:",
    ":hot_face:",
    ":fire:",
    ":grimacing:",
    ":shushing_face:",
]


def create_embed_pix(valor: int) -> discord.Embed:
    url = ""
    pix_copy = ""
    if valor == 1:
        url = "https://iili.io/Jo2sYdu.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com52040000530398654041.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***630413F0"
    elif valor == 5:
        url = "https://iili.io/Jo2ZW1S.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com52040000530398654045.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***63044AD0"
    elif valor == 10:
        url = "https://iili.io/Jo2t4n4.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com520400005303986540510.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***6304A955"

    embed_pix = discord.Embed(
        title="**Receba o seu Cookie**",
        description=f"**R$ {valor},00** :cookie:",
        color=0x00FFFF,
    )
    embed_pix.set_image(url=url)
    embed_pix.set_thumbnail(url="https://iili.io/Jo3AOhu.png")
    embed_pix.add_field(name="Copia e Cola:", value=f"```{pix_copy}```", inline=False)
    embed_pix.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
    return embed_pix


def create_btns_pix_enviado() -> discord.ui.View:
    lista_msg_sem_pix = [
        "Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, tranquilo demais, não tem estresse! A gente se vira nos trinta e dá um jeito de resolver essa parada. Afinal, aqui na Fábrica de Software, a gente é especialista em soluções criativas e não vai deixar você na mão. Então, pode ficar de boa que a gente vai dar um jeito nessa situação, sem stress!",
        "Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, relaxa que tá tudo tranquilo, sem estresse! A Fábrica de Software tá aqui pra te ajudar de qualquer jeito, seja com um PIX ou com uma dose extra de criatividade. Bora botar a mente pra funcionar e resolver qualquer parada que pintar!",
        "Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, relaxa que não tem problema nenhum, tá safe! Afinal, aqui na Fábrica de Software, a gente tá sempre pronto pra ajudar de todas as formas possíveis, seja com um PIX ou até mesmo com uma dose extra de criatividade. Então, pode ficar tranquilo que a gente vai encontrar uma solução maneira pra você, sem stress!",
        "Fala aí, camarada! Se você não conseguiu dar aquela força com um PIX, relaxa, não tem problema algum! Afinal, estamos aqui para trocar uma ideia e se divertir, não é mesmo? Então, bora seguir em frente e curtir essa vibe sem preocupações! Se precisar de qualquer outra coisa, é só chamar!",
    ]

    lista_msg_com_pix = [
        "Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação via PIX, e agora a nação mega bow vai decolar de vez! Com essa contribuição, vamos expandir horizontes, conquistar novos territórios e espalhar alegria por todos os cantos. Você é simplesmente incrível! :ninja: :video_game:",
        "Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação relâmpago via PIX, e agora a nação mega bow vai decolar rumo ao infinito e além! 🚀🌟",
        "Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação via PIX, e agora a nação mega bow vai crescer mais do que nunca! Agradecemos de coração por contribuir com o nosso sucesso e fortalecer ainda mais a nossa família. :trophy: :star:",
        "Aoooopa, meu nobre! Você é um verdadeiro MVP! Agradecemos imensamente pela sua generosa doação via PIX. Com esse apoio, a nação Mega Bow vai crescer mais do que nunca! :fire: :fire: :fire:",
        "Aoooopa meu nobre, que honra receber sua doação via PIX! Com esse gesto generoso, a Fábrica de Software está pronta para dominar o mundo dos games e fortalecer a nação Mega Bow! 🚀🌟",
    ]

    gifs_burgues = [
        "https://media0.giphy.com/media/67ThRZlYBvibtdF9JH/giphy.gif",
        "https://media1.giphy.com/media/xTiTnqUxyWbsAXq7Ju/giphy.gif",
        "https://media4.giphy.com/media/LdOyjZ7io5Msw/giphy.gif",
        "https://gifs.eco.br/wp-content/uploads/2021/09/imagens-e-gifs-do-tio-patinhas-37.gif",
    ]

    async def nao_enviar_pix(interaction: discord.Interaction):
        embed = discord.Embed(
            title="**:face_with_raised_eyebrow: BAN!?**",
            description=f"{random.choice(lista_msg_sem_pix)} :sweat_smile: :knife:",
            color=0x00FFFF,
        )
        embed.set_image(url="https://media0.giphy.com/media/H99r2HtnYs492/giphy.gif")
        embed.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
        await interaction.response.send_message(embed=embed)
        try:
            if interaction.message:
                await interaction.message.delete()
        except discord.DiscordException:
            pass

    async def pix_enviado(interaction: discord.Interaction):
        embed = discord.Embed(
            title="**:sunglasses: Tamo Patrão**",
            description=f"{random.choice(lista_msg_com_pix)}",
            color=0x00FFFF,
        )
        embed.set_image(url=random.choice(gifs_burgues))
        embed.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
        await interaction.response.send_message(embed=embed)
        try:
            if interaction.message:
                await interaction.message.delete()
        except discord.DiscordException:
            pass

    button1 = discord.ui.Button(style=discord.ButtonStyle.red, label="Não vou enviar")
    button2 = discord.ui.Button(style=discord.ButtonStyle.green, label="Já Enviei ADM!")

    button1.callback = nao_enviar_pix
    button2.callback = pix_enviado

    view = discord.ui.View(timeout=None)
    view.add_item(button1)
    view.add_item(button2)
    return view


dj = Dj(bot=bot)


@bot.event
async def on_ready():
    for gid in GUILD_IDS:
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
    channel = bot.get_channel(STARTUP_CHANNEL_ID)

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="A Ascensão do Mega Bow 🎥",
            state="🍿",
        ),
    )
    if channel:
        try:
            await channel.send(":fire: **Estou online e pronto!** :fire:")
        except discord.DiscordException:
            pass


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if bot.user and member.id == bot.user.id and after.channel is None:
        dj.resetMusicsServer(member.guild.id)
        return

    if member.id in punishments and after.channel is not None:
        prisao = bot.get_channel(PRISAO_CHANNEL_ID)
        if prisao and after.channel.id != prisao.id:
            try:
                await member.move_to(prisao)
            except discord.DiscordException:
                pass


@tree.command(name="commands", description="Veja todos os comandos disponíveis para mim 😉")
async def commands_cmd(interaction: discord.Interaction):
    msg = (
        "**/ex** - Gera um exercício de maratonas de programação (Codewars e Senac)\n"
        "**/play {nome/link}** - Toca uma música ou adiciona na fila\n"
        "**/pause** - Pausa a música atual\n"
        "**/resume** - Retoma a música pausada\n"
        "**/next** - Pula para a próxima música da fila\n"
        "**/queue** - Exibe a fila de músicas\n"
        "**/stop** - Para a música e desconecta o bot\n"
        "**/voice {pergunta}** - Faça uma pergunta para o Bot e ele te responderá em call\n"
        "**/conselho** - Receba um conselho do Bot\n"
        "**/chat {pergunta}** - Converse com o Bot\n"
        "**/piada** - Gera uma piada\n"
        "**/d {num}** - Roda um dado com o número de lados escolhido\n"
        "**/img {msg}** - Gera uma imagem sobre o que preferir\n"
        "**/pix** - Ajude o criador com um PIX e ganhe um Cookie :cookie:\n"
        "**/plagio {alvo}** - Exibe o avatar de um membro\n"
        "**/stroll {user}** - Faz o membro passear pelos canais de voz\n"
        "**/punish {alvo} {minutes}** - Prende o alvo na chamada de prisão\n"
        "**/free {alvo}** - Liberta o prisioneiro\n"
        "**/commands** - Todos os comandos do BOT"
    )

    embed = discord.Embed(title="**COMANDOS**", description=msg, color=0x00FFFF)
    await interaction.response.send_message(embed=embed)


@tree.command(name="pix", description="Ajude o criador do BOT com um Pixxx! 🤑")
async def pix(interaction: discord.Interaction):
    embed_doacao = discord.Embed(
        title=":dollar: **PIX** :euro:",
        description="Ajude o criador com um humilde PIX e será recompensado pelo destino",
        color=0x00FFFF,
    )
    embed_doacao.set_image(
        url="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmo5dHV4bnJsejlseWV2YWVianQyZGVmODE4emRqNnBwbWJzNnZlZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6dC4L3ygv5Cikt4xwS/source.gif"
    )

    button1 = discord.ui.Button(style=discord.ButtonStyle.green, label="R$ 1,00 (Café)")
    button2 = discord.ui.Button(style=discord.ButtonStyle.green, label="R$ 5,00 (Capuccino)")
    button3 = discord.ui.Button(style=discord.ButtonStyle.green, label="R$ 10,00 (Cookie)")

    async def pix1(inter: discord.Interaction):
        await inter.response.send_message(embed=create_embed_pix(1), view=create_btns_pix_enviado())

    async def pix5(inter: discord.Interaction):
        await inter.response.send_message(embed=create_embed_pix(5), view=create_btns_pix_enviado())

    async def pix10(inter: discord.Interaction):
        await inter.response.send_message(embed=create_embed_pix(10), view=create_btns_pix_enviado())

    button1.callback = pix1
    button2.callback = pix5
    button3.callback = pix10

    view = discord.ui.View(timeout=None)
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    await interaction.response.send_message(embed=embed_doacao, view=view)


@tree.command(name="ex", description="Busque exercícios de maratonas de programação para se preparar")
async def ex(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    questao = await asyncio.to_thread(random_ex)

    if questao[0] in (1, 2):
        dados = questao[1]
        embed = discord.Embed(
            title=f"{random.choice(EMOJIS)} {dados['dificuldade']} - {dados['nome']}",
            description=str(dados["descricao"])[:4000],
            color=0x00FFFF,
        )
        if dados.get("image"):
            embed.set_image(url=dados["image"])
        embed.set_thumbnail(url="https://iili.io/JKT3QWX.png")
        embed.set_footer(text="© Questão Original da Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
    else:
        embed = discord.Embed(
            title=f"{random.choice(EMOJIS)} {questao[1][0]}",
            description=str(questao[1][1])[:4000],
            color=0x00FFFF,
        )

    await interaction.followup.send(embed=embed)


@tree.command(name="d", description="Escolha um dado e experimente a sua sorte")
async def d(interaction: discord.Interaction, num: int):
    if num < 1:
        await interaction.response.send_message("Escolha um número maior ou igual a 1! 🎲", ephemeral=True)
        return

    num_rand = random.randint(1, num)
    descricao = "Hummm, lá ele" if num_rand in (4, 24) else ""

    embed = discord.Embed(title=f"🎲 {num_rand}", description=descricao, color=0x00FF00)
    await interaction.response.send_message(embed=embed)


@tree.command(name="conselho", description="Relaxa, que eu vou te aconselhar")
async def conselho(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    texto = await asyncio.to_thread(get_conselho)
    embed = discord.Embed(title="**Conselho**", description=texto, color=0x032078)
    await interaction.followup.send(embed=embed)


@tree.command(name="piada", description="Te conto uma piada tão horrível que você vai rir 😄")
async def piada(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    dados_piada = await asyncio.to_thread(random_joke)
    embed = discord.Embed(
        title=f"{random.choice(EMOJIS)} **{dados_piada[0]}**",
        description=f"{dados_piada[1]}",
        color=0x00FFFF,
    )
    await interaction.followup.send(embed=embed)


@tree.command(name="chat", description="Me pergunte sobre qualquer coisa! EU SABO")
async def chat(interaction: discord.Interaction, question: str):
    await interaction.response.defer(ephemeral=False, thinking=True)
    response = await generate_chatGPT(question)

    prefix = "Vossa Majestade Imperial " if interaction.user.name in donos else ""
    embed = discord.Embed(
        title=f":space_invader: Olá, {prefix}{interaction.user.display_name}",
        description=response,
        color=0x00FFFF,
    )
    await interaction.followup.send(embed=embed)


@tree.command(name="img", description="Gere uma imagem sobre o que preferir!")
async def img(interaction: discord.Interaction, msg: str):
    prompt_encoded = urllib.parse.quote(msg.strip())
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed={seed}&nologo=true"

    embed = discord.Embed(
        title=f":frame_photo: **{msg}**",
        color=0x00FFFF,
    )
    embed.set_image(url=image_url)
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


@tree.command(name="voice", description="Mande uma pergunta que te respondo na lábia! EU SABO")
async def voice(interaction: discord.Interaction, query: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("Entre em um canal de voz primeiro para eu falar com você! 🎤", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False, thinking=True)
    try:
        chatResp = await generate_chatGPT(f"Responda de forma curta com gírias do League of Legends: {query}")
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
            title=":yawning_face: **Essa eu sabo!**",
            description=chatResp[:4000],
            color=0x032078,
        )
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


@tree.command(name="stop", description="Ta bão, chega! Para a música e sai da call")
async def stop(interaction: discord.Interaction):
    await dj.stopMusic(interaction=interaction)


@tree.command(name="pause", description="Pause a música!")
async def pause(interaction: discord.Interaction):
    await dj.pauseMusic(interaction=interaction)


@tree.command(name="resume", description="Continue a música pausada!")
async def resume(interaction: discord.Interaction):
    await dj.resumeMusic(interaction=interaction)


@tree.command(name="stroll", description="Vamos Passear - Sett")
async def stroll(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if user.name == "asatotexco" and interaction.user.name != "asatotexco":
        await interaction.followup.send("```Ta achando que é gente? 🤫```")
        return

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "Turismólogo" not in rolesUser and interaction.user.name not in perm_stroll:
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
        return

    if user.voice is None or user.voice.channel is None:
        await interaction.followup.send("```O usuário não está em um canal de voz!```")
        return

    voice_original = user.voice.channel
    voice_channels = interaction.guild.voice_channels

    await interaction.followup.send("```Sequestrando...```")

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

    await interaction.followup.send("```Sequestrado com Sucesso!```")


@tree.command(name="punish", description="CAIA! - Faz o alvo cair e ficar preso em uma chamada")
async def punish(interaction: discord.Interaction, alvo: discord.Member, minutes: int):
    await interaction.response.defer(ephemeral=False, thinking=True)

    if alvo.name == "asatotexco" and interaction.user.name != "asatotexco":
        await interaction.followup.send("```Ta achando que é gente? 🤫```")
        return

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "SEQUESTRADOR 🐱\u200d👤" not in rolesUser and interaction.user.name not in perm_punishment:
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
        return

    if minutes < 1:
        await interaction.followup.send("```O tempo de punição deve ser de pelo menos 1 minuto.```")
        return

    minutes_punish = min(minutes, 60) * 60
    prisao = bot.get_channel(PRISAO_CHANNEL_ID)
    if prisao is None:
        await interaction.followup.send("```Canal de prisão não encontrado no servidor.```")
        return

    voice_original = alvo.voice.channel if (alvo.voice and alvo.voice.channel) else None
    punishments[alvo.id] = voice_original

    await interaction.followup.send(f"{alvo.mention} foi detido por {minutes} minuto(s)!")

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


@tree.command(name="free", description="Liberte o prisioneiro")
async def free(interaction: discord.Interaction, alvo: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)

    rolesUser = [role.name for role in getattr(interaction.user, "roles", [])]
    if "SEQUESTRADOR 🐱\u200d👤" not in rolesUser and interaction.user.name not in perm_punishment:
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
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

    await interaction.followup.send(f"{alvo.mention} foi liberto!")


@tree.command(name="plagio", description="Veja o avatar de um membro")
async def plagio(interaction: discord.Interaction, alvo: discord.Member):
    await interaction.response.defer(ephemeral=False, thinking=True)
    embed = discord.Embed(
        title=f"Avatar de {alvo.display_name}",
        description=alvo.mention,
        color=0x00FFFF,
    )
    embed.set_image(url=alvo.display_avatar.url)
    await interaction.followup.send(embed=embed)


if __name__ == "__main__":
    start_password_manager_server(port=8022, background=True)
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("A variável de ambiente TOKEN não foi definida no arquivo .env!")
    bot.run(token=token)
