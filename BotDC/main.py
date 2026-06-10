import discord
import time   
from exs import *
import random
from ias import *  
from text_to_speech import *
from dotenv import load_dotenv     
import asyncio     
from discord import app_commands 
 
from Models.Dj import Dj

load_dotenv()

punishments = {} # {user: *call para callback}
intents = discord.Intents.default()
intents.message_content = True  # Configurar a intenção como True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
 
# o discord dos donos do BOT 
donos = ['ninjasupremobr']
perm_stroll = ['ninjasupremobr',]
perm_punishment = ['ninjasupremobr']

def create_embed_pix(valor):
    url = ""
    pix_copy = ""
    if(valor == 1):
        url = "https://iili.io/Jo2sYdu.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com52040000530398654041.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***630413F0"
    elif(valor == 5):
        url = "https://iili.io/Jo2ZW1S.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com52040000530398654045.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***63044AD0"
    elif(valor == 10):
        url = "https://iili.io/Jo2t4n4.png"
        pix_copy = "00020101021126510014br.gov.bcb.pix0129arthur2006.teixeira@gmail.com520400005303986540510.005802BR5922ARTHUR S DE A TEIXEIRA6012CAMPO GRANDE62070503***6304A955"
        
    embed_pix = discord.Embed(
            title=f"**Receba o seu Cookie**",
            description=f"**R$ {valor},00** :cookie:",
            color=0x00ffff
    )

    embed_pix.set_image(url=url)
    embed_pix.set_thumbnail(url="https://iili.io/Jo3AOhu.png")
    embed_pix.add_field(name="Copia e Cola:", value=f"{pix_copy}", inline=False)

    embed_pix.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")  
    return embed_pix

def create_btns_pix_enviado():
    lista_msg_sem_pix = [
        'Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, tranquilo demais, não tem estresse! A gente se vira nos trinta e dá um jeito de resolver essa parada. Afinal, aqui na Fábrica de Software, a gente é especialista em soluções criativas e não vai deixar você na mão. Então, pode ficar de boa que a gente vai dar um jeito nessa situação, sem stress!',
        'Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, relaxa que tá tudo tranquilo, sem estresse! A Fábrica de Software tá aqui pra te ajudar de qualquer jeito, seja com um PIX ou com uma dose extra de criatividade. Bora botar a mente pra funcionar e resolver qualquer parada que pintar!',
        'Fala aí, meu consagrado! Se você não conseguiu dar aquela força com um PIX, relaxa que não tem problema nenhum, tá safe! Afinal, aqui na Fábrica de Software, a gente tá sempre pronto pra ajudar de todas as formas possíveis, seja com um PIX ou até mesmo com uma dose extra de criatividade. Então, pode ficar tranquilo que a gente vai encontrar uma solução maneira pra você, sem stress! Bora botar essa fábrica pra funcionar e resolver qualquer parada que pintar no caminho, parceiro!',
        'Fala aí, camarada! Se você não conseguiu dar aquela força com um PIX, relaxa, não tem problema algum! Afinal, estamos aqui para trocar uma ideia e se divertir, não é mesmo? Então, bora seguir em frente e curtir essa vibe sem preocupações! Se precisar de qualquer outra coisa, é só chamar! Estamos aqui para te ajudar e animar o seu dia!'
    ]
    
    lista_msg_com_pix = [
        
        'Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação via PIX, e agora a nação mega bow vai decolar de vez! Com essa contribuição, vamos expandir horizontes, conquistar novos territórios e espalhar alegria por todos os cantos. Você é simplesmente incrível! Juntos, vamos fazer a diferença e transformar o mundo em um lugar mais divertido e cheio de energia positiva. Muito obrigado por fazer parte dessa jornada épica! :ninja: :video_game: ',
        'Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação relâmpago via PIX, e agora a nação mega bow vai decolar rumo ao infinito e além! 🚀🌟',
        'Aoooopa meu nobre, olha só que maravilha! Recebemos com gratidão a sua doação via PIX, e agora a nação mega bow vai crescer mais do que nunca! Agradecemos de coração por contribuir com o nosso sucesso e fortalecer ainda mais a nossa família. Juntos, vamos conquistar o mundo dos games e espalhar alegria por todos os servidores! Você é demais! :trophy: :star: ',
        'Aoooopa, meu nobre! Você é um verdadeiro MVP! Agradecemos imensamente pela sua generosa doação via PIX. Com esse apoio, a nação Mega Bow vai crescer mais do que nunca! Juntos, vamos conquistar o mundo dos games e espalhar alegria por todos os servidores. Você é simplesmente incrível!:fire: :fire: :fire: ',
        'Aoooopa meu nobre, que honra receber sua doação via PIX! Com esse gesto generoso, a Fábrica de Software está pronta para dominar o mundo dos games e fortalecer a nação Mega Bow! Juntos, vamos criar um império virtual repleto de diversão e vitórias épicas. Prepare-se para embarcar nessa jornada incrível ao nosso lado, onde a criatividade e a inovação são as nossas maiores armas. Vamos conquistar o universo dos jogos e deixar nossa marca como os verdadeiros mestres da diversão! 🚀🌟'
        
    ]
    
    gifs_burgues = [
        'https://media0.giphy.com/media/67ThRZlYBvibtdF9JH/giphy.gif?cid=ecf05e47aephvc1kk139nz20gjj7thtetpmhwgf8s5z1v7oi&ep=v1_gifs_search&rid=giphy.gif&ct=g',
        'https://media1.giphy.com/media/xTiTnqUxyWbsAXq7Ju/giphy.gif?cid=ecf05e47bukbe6l3m2uclv98yzr3g6krs506h7cd10ikaa5d&ep=v1_gifs_related&rid=giphy.gif&ct=g',
        'https://media4.giphy.com/media/LdOyjZ7io5Msw/giphy.gif?cid=ecf05e47aephvc1kk139nz20gjj7thtetpmhwgf8s5z1v7oi&ep=v1_gifs_search&rid=giphy.gif&ct=g',
        'https://gifs.eco.br/wp-content/uploads/2021/09/imagens-e-gifs-do-tio-patinhas-37.gif'
        
    ]
    
    async def nao_enviar_pix(interaction: discord.Interaction): 
        embed = discord.Embed(
            title=f"**:face_with_raised_eyebrow: BAN!?**",
            description=f"{random.choice(lista_msg_sem_pix)} :sweat_smile: :knife:  ",
            color=0x00ffff
        )
        embed.set_image(url='https://media0.giphy.com/media/H99r2HtnYs492/giphy.gif?cid=ecf05e47wxkljw4gj9e3nolqw69q65aa6gu205mxdrmoiypc&ep=v1_gifs_search&rid=giphy.gif&ct=g')
        embed.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
        await interaction.message.delete()
        
        
        await interaction.response.send_message(embed=embed)
         
    async def pix_enviado(interaction: discord.Interaction): 
        
        embed = discord.Embed(
            title=f"**:sunglasses: Tamo Patrão**",
            description=f"{random.choice(lista_msg_com_pix)}",
            color=0x00ffff
        )
        embed.set_image(url=f'{random.choice(gifs_burgues)}')
        embed.set_footer(text="© Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")  
        await interaction.message.delete()
        
        
        await interaction.response.send_message(embed=embed)
         
    
    button1 = discord.ui.Button(style=discord.ButtonStyle.red, label="Não vou enviar")
    button2 = discord.ui.Button(style=discord.ButtonStyle.green, label="Já Enviei ADM!")
    
    button1.callback = nao_enviar_pix
    button2.callback = pix_enviado
    
    view = discord.ui.View()
    view.add_item(button1)
    view.add_item(button2)
    
    return view
    
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=722857509659869204))
    print(f'Logged on as {bot.user}!')
    channel_id = 1176698533039059055  # Substitua pelo ID do canal desejado
    channel = bot.get_channel(channel_id)

   
 
     

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="A Ascensão do Mega Bow 🎥",
            timestamps = {'start':1420070400000},
            state='🍿',
            assets={
                'large_image': '1207840321027706901',
                'large_text' : 'TIRANIA',
                'small_image': '1207840321027706901',
            }
        )
    )
    if channel:
        await channel.send(" :fire:  **Estou online e pronto!**  :fire:") 

 
@tree.command(
    name="commands",
    description="Veja todos os comandos disposníveis para mim 😉",
    guild=discord.Object(id=722857509659869204)
)
async def commands(interaction: discord.Interaction):
    msg = """**$ex** - gera um exercício de maratonas de programação(Codewars e Senac)
**$play {nome/link}** - Escolha uma música por vez e aproveite :)
**$stop** - Pare a sua música
**$voice {pergunta}** - Faça uma pergunta para o Bot e ele te responderá em call
**$conselho** - Receba um conselho do Bot
**$chat {pergunta}** - Converse com o bot
**$piada** -  Gera uma piada
**$d {numero}** -  Roda um dado que vc escolher
**$img {img_desejada}** - Gera uma imagem sobre o que preferir
**$pix** - Ajude o criador com um PIX e ganhe um Cookie :cookie: 
**$commands** - Todos os comandos do BOT
"""

    embed = discord.Embed(
    title=f"**COMANDOS**",
    description=f"{msg}",
    color=0x00ffff
    )
        
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="pix",
    description="Ajude o criador do BOT com um Pixxx! 🤑",
    guild=discord.Object(id=722857509659869204)
)
async def pix(interaction:discord.Interaction):
    # Criar um objeto Embed
    embed_doacao = discord.Embed(
        title=":dollar: **PIX** :euro:", 
        description="Ajude o criador com um humilde PIX e será recompensado pelo destino", 
        color=0x00ffff
    )
    embed_doacao.set_image(url='https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmo5dHV4bnJsejlseWV2YWVianQyZGVmODE4emRqNnBwbWJzNnZlZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6dC4L3ygv5Cikt4xwS/source.gif')
    
    # Adicionar um botão
    button1 = discord.ui.Button(style=discord.ButtonStyle.green, label="R$ 1,00(Café)")
    button2 = discord.ui.Button(style=discord.ButtonStyle.green, label="R$ 5,00(Capuccino)")
    button3 = discord.ui.Button(style=discord.ButtonStyle.green , label="R$ 10,00(Cookie)")
    
    # Definir a função de retorno de chamada para o botão
    async def pix1(inter: discord.Interaction):  
        await inter.response.send_message(embed=create_embed_pix(1),view=create_btns_pix_enviado())
        
    async def pix5(inter: discord.Interaction):  
        await inter.response.send_message(embed=create_embed_pix(5),view=create_btns_pix_enviado())
        # o generoso de doar através do Pix, mas também por fazer parte da nossa comunidade. Seu apoio é fundamental para o crescimento e sucesso do Mega Bow. Muito obrigado por fazer parte dessa jornada conosco!
    async def pix10(inter: discord.Interaction):  
        await inter.response.send_message(embed=create_embed_pix(10),view=create_btns_pix_enviado())

    button1.callback = pix1
    button2.callback = pix5
    button3.callback = pix10 
    
    # Criar uma view e adicionar o botão a ela
    view = discord.ui.View()
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    # Enviar o embed com a view para o canal
    await interaction.response.send_message(embed=embed_doacao, view=view)


@tree.command(
    name="ex",
    description="Busque exercícios de maratonas de programação para se preparar",
    guild=discord.Object(id=722857509659869204)
)
async def ex(interaction: discord.Interaction):
    emojis=[":dotted_line_face:",":face_with_raised_eyebrow:",":joy:",":star:",":face_with_monocle:",":interrobang:",":face_in_clouds:",":detective:",":smiling_imp:",":disguised_face:",":hot_face:",":fire:",":grimacing:",":shushing_face:"]
    questao = random_ex()
    print(questao[0])
    
    if(questao[0] == 1 or questao[0] == 2):

        embed = discord.Embed(
        title=f"{random.choice(emojis)} {questao[1]['dificuldade']} - {questao[1]['nome']}",
        description=f"{questao[1]['descricao']}",
        color=0x00ffff,
        )
        embed.set_image(url=questao[1]['image'])
        embed.set_thumbnail(url="https://iili.io/JKT3QWX.png")
        embed.set_footer(text="© Questão Original da Fábrica de Software", icon_url="https://iili.io/JKT3QWX.png")
   
    else: 
        
        embed = discord.Embed(
        title=f"{random.choice(emojis)} {questao[1][0]}",
        description=questao[1][1],
        color=0x00ffff
        ) 
    
    await interaction.response.send_message(embed=embed)
    
@tree.command(
    name="d",
    description="Escolha um dado e exeperimente a sua sorte",
    guild=discord.Object(id=722857509659869204)
)
async def d(interaction: discord.Interaction, num: int):
    num_rand = random.randint(1, num)
    descricao = "Hummm, la ele" if num_rand in (4, 24) else ""
        
    embed = discord.Embed(
        title=f"{num_rand}",
        description=descricao,
        color=0x00ff00   
    )
    
    await interaction.response.send_message(embed=embed)

@tree.command(
    name="conselho",
    description="Relaxa, que eu vou te aconselhar",
    guild=discord.Object(id=722857509659869204)
)
async def conselho(interaction:discord.Interaction):
    embed = discord.Embed(
        title=f"**Conselho**",
        description=f"{get_conselho()}",
        color=0x032078   
    )
    
    await interaction.response.send_message(embed=embed)
@tree.command(
    name="piada",
    description="Te conto um piada tão horrivel que você vai rir 😄",
    guild=discord.Object(id=722857509659869204)
)
async def piada(interaction:discord.Interaction):
    
    emojis=[":dotted_line_face:",":face_with_raised_eyebrow:",":joy:",":star:",":face_with_monocle:",":interrobang:",":face_in_clouds:",":detective:",":smiling_imp:",":disguised_face:",":hot_face:",":fire:",":grimacing:",":shushing_face:"]
    piada = random_joke()
    embed = discord.Embed(
        
        title=f"{random.choice(emojis)} **{piada[0]}**",
        description=f"{piada[1]}", 
        color=0x00ffff   
    )
    await interaction.response.send_message(embed=embed)

@tree.command(
    name="chat",
    description="Me pergunte sobre qualquer coisa! EU SABO",
    guild=discord.Object(id=722857509659869204)
)
async def chat(interaction: discord.Interaction, *, question: str):
     
        

        await interaction.response.defer(ephemeral=False,thinking=True) 
         
        # Gerar a resposta de forma assíncrona
        response = await generate_chatGPT(question)

        prefix = "Vossa Majestade Imperial" if str(interaction.user) in donos else ""
        
        embed = discord.Embed(
            title=f":space_invader: Olá, {prefix} {interaction.user}",
            description=response,
            color=0x00ffff  # Cor do embed (ciano)
        )

        # await interaction.response.send_message(embed=embed)  # Enviar a resposta final

        await interaction.followup.send(embed=embed) 
    
           
@tree.command(
    name="img",
    description="Gere uma imagem aleatória!",
    guild=discord.Object(id=722857509659869204)
)
async def img(interaction:discord.Interaction,*,msg:str):
     
    msg = msg.replace(" ","-")
    
    
    embed = discord.Embed(
        
        title=f":frame_photo: **{msg}**", 
        color=0x00ffff  # Cor do embed (verde)
    ) 
    embed.set_image(url=f"https://source.unsplash.com/400x300/?{msg}") 
    await interaction.response.send_message(embed=embed)
    
 

async def connectVoice(interaction):
    
    if interaction.user.voice:  # verifica se o autor da mensagem está em um canal de voz
        channel = interaction.user.voice.channel

        # Se estiver conectado
        if interaction.guild.voice_client is not None:
            voice_channel = interaction.guild.voice_client
        else:
            voice_channel = await channel.connect() # aqui retorna esse erro: list index out of range

        return voice_channel

@tree.command(
    name="voice",
    description="Mande uma pergunte que te respondo na lábia! EU SABO",
    guild=discord.Object(id=722857509659869204)
)
async def voice(interaction: discord.Interaction, *, query: str):
    try:
        embed = discord.Embed(
            title=f" :yawning_face: **Essa eu sabo!**",
            description=f"Estou gankando para te ajudar",
            color=0x032078  
        )
        await interaction.response.send_message(embed=embed)
        
        chatResp = await generate_chatGPT(f"Responda com gírias do League of Legends: {query}") 
        text_to_speech(chatResp, './voices/output_audio.mp3')

        voice_channel = await connectVoice(interaction)
        audio =  discord.FFmpegPCMAudio('./voices/output_audio.mp3') 
        voice_channel.play(audio)
         
 
    except Exception as error:
        await interaction.followup.send(f"```{error}```")
 
 

dj = Dj(bot=bot)


@tree.command(
    name="queue",
    description="Fila de Músicas",
    # guild=discord.Object(id=722857509659869204)
    guilds=[discord.Object(id=722857509659869204),discord.Object(id=1046231965872967690)]
) 
async def queue(interaction: discord.Interaction):  
    await dj.listarFilaMusica(interaction=interaction)


@tree.command(
    name="next",
    description="Próxima música ",
    guilds=[discord.Object(id=722857509659869204),discord.Object(id=1046231965872967690)]
) 
async def queue(interaction: discord.Interaction):  
    await interaction.response.defer(ephemeral=False,thinking=True) 
    await dj.nextMusic(interaction=interaction)
    await interaction.followup.send("A próxima ta na fila ;)") 

   
@tree.command(
    name="play",
    description="E aí, vai uma musiquinha?",
    # guild=discord.Object(id=722857509659869204)
    guilds=[discord.Object(id=722857509659869204),discord.Object(id=1046231965872967690)]
) 
async def play(interaction: discord.Interaction, *, query: str):  
    await dj.play(query=query,interaction=interaction) 

@tree.command(
    name="stop",
    description="Ta bão, Chega, não vou aguentar mais não! para a música",
    guild=discord.Object(id=722857509659869204)
)
async def stop(interaction: discord.Interaction):
    await dj.stopMusic(interaction=interaction)
 
  

@tree.command(
    name="pause",
    description="Pause a música! (só não pode pausar kaan mary jane)",
    guild=discord.Object(id=722857509659869204)
)
async def pause(interaction: discord.Interaction):
    await dj.pauseMusic(interaction=interaction)
   


@tree.command(
    name="resume",
    description="Pause a música! (só não pode pausar kaan mary jane)",
    guild=discord.Object(id=722857509659869204)
)
async def resume(interaction: discord.Interaction):
    await dj.resumeMusic(interaction=interaction)
 






def embed_music(data,inter):
    embed_music = discord.Embed(
            title=f"**{data['title']}**",
            description=f"**[{data['channel']['name']}]({data['channel']['link']})**",
            color=0x00ffff
        ) 

    embed_music.set_image(url=data['thumbnails'][-1]['url'])
    embed_music.set_thumbnail(url=f"{data['channel']['thumbnails'][0]['url']}")
    embed_music.add_field(name="Publicado", value=f"{data['publishedTime']}", inline=True)
    embed_music.add_field(name="Duration", value=f"{data['duration']}", inline=True)
    embed_music.add_field(name="Views", value=f"{data['viewCount']['short']}", inline=True)
    embed_music.add_field(name="Request", value=f"{inter.mention}", inline=True)
    embed_music.add_field(name="Video", value=f"[Ir para Video]({data['link']})", inline=True)

    embed_music.set_footer(text=f"{data['descriptionSnippet'][0]['text']}", icon_url=f"{data['channel']['thumbnails'][0]['url']}")  
    
    return embed_music


@tree.command(
    name="stroll",
    description="Vamos Passear -sett",
    guild=discord.Object(id=722857509659869204)
) 
async def stroll(interaction: discord.Interaction, *, user:discord.Member):

    await interaction.response.defer(ephemeral=False,thinking=True)

    if(user.name == "asatotexco" and interaction.user.name != "asatotexco"):
        await interaction.followup.send("```Ta achando que é gente? 🤫```")
        return
    
    rolesUser = [role.name for role in interaction.user.roles ] 
    if("Turismólogo" not in rolesUser):
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
        return
    
    await interaction.followup.send("```Sequestrando...```")
 
    guild = interaction.guild
    voice_channels = guild.voice_channels
    voice_original = user.voice.channel

    time_inicio = time.time()
    min_castigo = 5  # minutes
    delay_time =  5  # seconds
    for c in voice_channels:
        if(user.voice is None): 
            if((time.time() - time_inicio) <= (min_castigo * 60)):
                await asyncio.sleep(delay_time)
                continue 
            interaction.response.send_message("```O Usuário não está em um canal de voz```")
            break
        if(c != voice_original): 
            try: 
                await user.move_to(c)
            except:
                continue
            await asyncio.sleep(0.01)

    await user.move_to(voice_original) 
    await interaction.followup.send("```Sequestrado com Sucesso!```") 

@tree.command(
    name="punish",
    description="CAIA! - faz o alvo cair e ficar preso em uma chamada",
    guild=discord.Object(id=722857509659869204)
) 
async def punish(interaction: discord.Interaction,*,alvo: discord.Member, minutes: int):
     
    await interaction.response.defer(ephemeral=False,thinking=True)   

    if(alvo.name == "asatotexco" and interaction.user.name != "asatotexco"):
        await interaction.followup.send("```Ta achando que é gente? 🤫```")
        return
     
    
    rolesUser = [role.name for role in interaction.user.roles ] 
    if("SEQUESTRADOR 🐱\u200d👤" not in rolesUser):
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
        return

    minutes_punish =  minutes * 60  
    prisao = bot.get_channel(1269379224129634434) 

    await interaction.followup.send(f"{alvo.mention} foi detido por {minutes} minutos!")
 
    if(alvo.voice is not None): 

        voice_original = alvo.voice.channel
        punishments[alvo] = voice_original

        # Dando enquadro
        voice_channel = alvo.voice.channel 
         
        if interaction.guild.voice_client is not None:
            if(interaction.guild.voice_client.channel.id == alvo.voice.channel.id): 
                voice_channel = interaction.guild.voice_client
            else:
                print("esta em canal diferente e o bot esta conectado na call")
                try:  
                    await interaction.guild.voice_client.disconnect()  
                except Exception as error:
                    await interaction.followup.send(f"```{error}```")

                voice_channel = await voice_channel.connect()
        else:
            voice_channel = await voice_channel.connect() 

        audio =  discord.FFmpegPCMAudio('./voices/sirene_grave.mp3')
        voice_channel.play(audio) 
        while voice_channel.is_playing():
            await asyncio.sleep(0.1) 
        audio2 =  discord.FFmpegPCMAudio('./voices/enquadro_bot.mp3')
        voice_channel.play(audio2) 
        while voice_channel.is_playing():
            await asyncio.sleep(0.5) 

    start = time.time() 

    while (((time.time() - start) <= minutes_punish) and (alvo in punishments)):
        if(alvo.voice is None):
            continue
        await alvo.move_to(prisao) 

    if(alvo in punishments):
        if(alvo.voice is not None):
            await alvo.move_to(voice_original) 
        del punishments[alvo]

@tree.command(
    name="free",
    description="Liberte o prisioneiro",
    guild=discord.Object(id=722857509659869204)
) 
async def free(interaction: discord.Interaction,*,alvo: discord.Member):

    await interaction.response.defer(ephemeral=False,thinking=True) 

    rolesUser = [role.name for role in interaction.user.roles ] 
    if("SEQUESTRADOR 🐱\u200d👤" not in rolesUser):
        await interaction.followup.send("```Você não possui a HONRA para isso! 🤫```")
        return
    
    if(alvo in punishments):
        await alvo.move_to(punishments[alvo]) 
    del punishments[alvo]

    await interaction.followup.send(f"{alvo.mention} foi liberto!") 


@tree.command(
    name="plagio",
    description="Liberte o prisioneiro",
    guild=discord.Object(id=722857509659869204)
) 
async def plagio(interaction: discord.Interaction,*, alvo: discord.Member):

    await interaction.response.defer(ephemeral=False,thinking=True) 
    embed = discord.Embed(  
        title=f"Avatar de {alvo.name}",
        description=alvo.mention,
        color=0x00ffff,
    )
    embed.set_image(url=alvo.avatar) 

    await interaction.followup.send(embed=embed) 

 
token = 'MTE2NTAxNjk5OTQ3NTMwMjUzMg.GtdYCn.toerONW_I1qK3bS2ffyTAetMcDYcIuEXM9JVuk'
bot.run(token=token) 
