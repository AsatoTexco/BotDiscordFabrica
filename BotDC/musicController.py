
import asyncio 
from pytube import YouTube 
from youtubesearchpython import VideosSearch
import discord
from playlist import *
from threading import Thread


class MusicController:
    def __init__(self,bot) -> None:
        self.bot = bot
        self.ctx = None
        self.connected = False
        self.voice_channel = None
        self.guilds = {}
        

    async def connectVoice(self,ctx):
        self.ctx = ctx
        if(self.connected == False): 
            self.connected = True
            channel = self.ctx.author.voice.channel
            self.voice_channel = await channel.connect() 

            return True 
        else:
            print("Ja esta conectado monengue")

    async def disconnect(self):
        if(self.connected == True):
            if(self.voice_channel != None):
                if(self.voice_channel.is_connected()):
                    self.voice_channel.disconnect()
 
    async def play(self,query,ctx):
        try: 

            result = ''

            # se nunca foi instanciado esse servidor no bot 
            if(ctx.guild.id not in self.guilds): 
                # instancia uma playlist [0] 
                
                await self.connectVoice(ctx)
             
                # ======= play music ========
                result = self.search_youtube(query)
                embed_music = self.embed_music_generate(result,ctx)
                await ctx.send(embed=embed_music)
                # await ctx.send(embed=self.embed_music(ctx))
                self.download_yt(result)
                audio = discord.FFmpegPCMAudio(f'./musics/61261236.mp3', executable='ffmpeg.exe')


                async def after_next_song():
                    await self.next_song(ctx.guild.id, ctx)

                # Reproduz o áudio no canal de voz
                self.voice_channel.play(audio, after=lambda e: after_next_song())
                # ===========================
 
                playList = PlayList()
                self.guilds[ctx.guild.id] = [playList]

            else:
                self.guilds[ctx.guild.id][0].add(query)

              
 

            return result
        

        except Exception as erro:
            print(erro)
            return


    async def next_song(self,guild_id,ctx):
        print('next song')
        next_song = self.guilds[guild_id].next()
        if(next_song is not False):

             # ======= play music ========
            result = self.search_youtube(next_song)
            # embed_music = self.embed_music_generate(result,ctx)
            # await ctx.send(embed=embed_music) 

            self.download_yt(result)
            audio = discord.FFmpegPCMAudio(f'./musics/61261236.mp3', executable='ffmpeg.exe')
            # Reproduz o áudio no canal de voz
            self.voice_channel.play(audio, after=lambda e: self.next_song(ctx.guild.id))


    def download_yt(self,data):
        print('baixando...')
        youTube = YouTube(url=data['link'])  
        audio_stream = youTube.streams.filter(only_audio=True).first().download('./musics',filename=f'61261236.mp3')
        return True

    def search_youtube(self,query):
        print('pesquisando...')
        video_search = VideosSearch(query=query, limit=1)
        results = video_search.result() 
        if(len(results['result']) > 0):
            return results['result'][0]


    def embed_music_generate(self,data,ctx):
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


 