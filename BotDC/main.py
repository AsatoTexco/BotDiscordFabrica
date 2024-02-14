import discord
import sys  
from discord.ext import commands
from exs import *
import random
from ias import *  
from text_to_speech import *
from dotenv import load_dotenv   
import os 
from functools import partial
from pytube import YouTube 
import asyncio 
from youtubesearchpython import VideosSearch
from musicController import *
from playlist import *



load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Configurar a intenção como True

bot = commands.Bot(intents=intents, command_prefix='$',description='esse é o Bot')

# o discord dos donos do BOT 
donos = ['ninjasupremobr']

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
    print(f'Logged on as {bot.user}!')
    channel_id = 1176698533039059055  # Substitua pelo ID do canal desejado
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(" :fire:  **Estou online e pronto!**  :fire:") 

# @bot.command()
# async def teste(ctx, *args):
#     # Responder ao comando !teste com a mensagem "teste"
#     msg = " ".join(args)
#     await ctx.send(f"{msg}")

@bot.command()
async def commands(ctx):
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
        
    await ctx.send(embed=embed)


@bot.command()
async def pix(ctx):
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
    async def pix1(interaction: discord.Interaction):  
        await interaction.response.send_message(embed=create_embed_pix(1),view=create_btns_pix_enviado())
        
    async def pix5(interaction: discord.Interaction):  
        await interaction.response.send_message(embed=create_embed_pix(5),view=create_btns_pix_enviado())
        # o generoso de doar através do Pix, mas também por fazer parte da nossa comunidade. Seu apoio é fundamental para o crescimento e sucesso do Mega Bow. Muito obrigado por fazer parte dessa jornada conosco!
    async def pix10(interaction: discord.Interaction):  
        await interaction.response.send_message(embed=create_embed_pix(10),view=create_btns_pix_enviado())

    button1.callback = pix1
    button2.callback = pix5
    button3.callback = pix10 
    
    # Criar uma view e adicionar o botão a ela
    view = discord.ui.View()
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    # Enviar o embed com a view para o canal
    await ctx.send(embed=embed_doacao, view=view)


@bot.command()
async def ex(ctx):
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
    
    await ctx.send(embed=embed)
    
@bot.command()
async def d(ctx,num): 
    
    num_rand = random.randrange(1, int(num) + 1)
    if(num_rand == 4 or num_rand == 24):
        descricao = "Hummm, la ele"
        
    else:
        descricao = ""
        
    embed = discord.Embed(
        title=f"{num_rand}",
        description=descricao,
        color=0x00ff00   
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def conselho(ctx):
    embed = discord.Embed(
        title=f"**Conselho**",
        description=f"{get_conselho()}",
        color=0x032078   
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def piada(ctx):
    
    emojis=[":dotted_line_face:",":face_with_raised_eyebrow:",":joy:",":star:",":face_with_monocle:",":interrobang:",":face_in_clouds:",":detective:",":smiling_imp:",":disguised_face:",":hot_face:",":fire:",":grimacing:",":shushing_face:"]
    piada = random_joke()
    embed = discord.Embed(
        
        title=f"{random.choice(emojis)} **{piada[0]}**",
        description=f"{piada[1]}", 
        color=0x00ffff   
    )
    await ctx.send(embed=embed)

@bot.command()
async def chat(ctx,*args):
    msg = " ".join(args)
    
    
    prefix = "Vossa Majestade Imperial" if str(ctx.author) in donos else "" 
    embed = discord.Embed(
        
        title=f":space_invader: Olá, {prefix} {ctx.author}",
        title=f":space_invader: Olá, {prefix} {ctx.author}",
        description=f"{generate_chatGPT(msg)}", 
        color=0x00ffff  # Cor do embed (verde)
    )
    await ctx.send(embed=embed)
     
     
           
@bot.command()
async def img(ctx,*args):
    msg = " ".join(args)
    # msg = Translator().translate(msg,'en').text
    # msg = Translator().translate(msg,'en').text
    msg = msg.replace(" ","-")
    
    
    embed = discord.Embed(
        
        title=f":frame_photo: **{msg}**", 
        color=0x00ffff  # Cor do embed (verde)
    ) 
    embed.set_image(url=f"https://source.unsplash.com/400x300/?{msg}") 
    await ctx.send(embed=embed)
    
# @bot.event
# async def on_message(message):
#     if isinstance(message.channel, discord.DMChannel): 
#         server = bot.get_guild(1046231965872967690)
        
#         channel = server.get_channel(1165027062545928243)
        
#         if server and channel: 
#             await channel.send(f"{message.author}: {message.content}")
#     await bot.process_commands(message) 


async def connectVoice(ctx):
     if ctx.author.voice:  # verifica se o autor da mensagem está em um canal de voz
            channel = ctx.author.voice.channel

            # Se estiver conectado
            if ctx.voice_client is not None:
                
                # se não estiver tocando algo 
                if(ctx.voice_client.is_playing() == False): 
                    # await ctx.voice_client.disconnect() 
                    print("Eis o criminoso")
                voice_channel = ctx.voice_client
            else:

                voice_channel = await channel.connect()

            return voice_channel

@bot.command()
async def voice(ctx, *query):
    try: 
        embed = discord.Embed(
                    title=f" :yawning_face: **Essa eu sabo!**",
                    description=f"Estou gankando para te ajudar ",
                    color=0x032078  
                )
        await ctx.send(embed=embed)
         
        chatResp = generate_chatGPT(f"Resuma muito sua resposta: {' '.join(query)}") 
        await text_to_speech(chatResp,'output_audio.mp3')


        voice_channel = await connectVoice(ctx=ctx)
        audio = discord.FFmpegPCMAudio(f'output_audio.mp3', executable='ffmpeg.exe')
 
        voice_channel.play(audio)
 
    except Exception as error:
        await ctx.send(f"```{error}```")


musicController = MusicController(bot)
@bot.command(name="play",help='isso é algo incrivel')
async def play(ctx, *url):
    try:  
        # await musicController.play(' '.join(url),ctx)
 


        # Conecta ao canal de voz solicitado
        voice_channel = await connectVoice(ctx)
     

        video_search = VideosSearch(query=' '.join(url), limit=1)
        results = video_search.result() 

        if(len(results['result']) == 0):
            emojis=[":dotted_line_face:",":face_with_raised_eyebrow:",":joy:",":star:",":face_with_monocle:",":interrobang:",":face_in_clouds:",":detective:",":smiling_imp:",":disguised_face:",":hot_face:",":fire:",":grimacing:",":shushing_face:"]
            embed = discord.Embed(
                title=f"{random.choice(emojis)} **Música não encotrada**",
                description=f"Infelizmente não foi possível encontrar a sua música :musical_note: ",
                color=0x032078  
            )
            await ctx.send(embed=embed)
            return 
        
        urlImplementada = results['result'][0]['link'] 
  
        await ctx.send(embed=embed_music(results['result'][0],ctx)) 

        if(ctx.voice_client is not None): 
            if(ctx.voice_client.is_playing()): 
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1) 

        youTube = YouTube(url=urlImplementada) 

        audio_stream = youTube.streams.filter(only_audio=True).first().download(filename=f'{ctx.author.voice.channel.id}.mp3')

        audio = discord.FFmpegPCMAudio(f'{ctx.author.voice.channel.id}.mp3')

        # Reproduz o áudio no canal de voz
        voice_channel.play(audio, after=lambda e: print('Aopa'))

        while voice_channel.is_playing():
            await asyncio.sleep(1)

        await voice_channel.disconnect()
    except Exception as error:
        await ctx.send(f"```{error}```")


def embed_music(data,ctx):
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
    embed_music.add_field(name="Request", value=f"{ctx.author.mention}", inline=True)
    embed_music.add_field(name="Video", value=f"[Ir para Video]({data['link']})", inline=True)

    embed_music.set_footer(text=f"{data['descriptionSnippet'][0]['text']}", icon_url=f"{data['channel']['thumbnails'][0]['url']}")  
    
    return embed_music

@bot.command()
async def stop(ctx):
    try: 
        await ctx.voice_client.disconnect()  
    except Exception as error:
        await ctx.send(bot.channel, "```{error}```".format(error=error))
 

token = 'MTE2NTAxNjk5OTQ3NTMwMjUzMg.GIfPjC.fP_bsyJd1S_brISlvy-j6bMf6gK7nlwfJzBQug'
bot.run(token=token) 
