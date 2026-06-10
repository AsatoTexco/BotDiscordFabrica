import asyncio
import discord
from youtubesearchpython import VideosSearch 
import yt_dlp 
from .PlayList import PlayList
import uuid
from .Embedders import embed_music, generateViewMusic, previewMusic, embedListaMusics 
import os

class Dj:
    def __init__(self,bot) -> None:
        self.serversData = {} # [id_server] => playlist

        self.statusServers = {}
        # EX:
        # self.statusServers[interaction.guild_id] = {'channel':interaction.channel_id,'status':'playing'}

        self.bot = bot
    
    def dotBeToDotCom(self, query:str): 
        if('https://youtu.be/' not in query):
            return query  
        query = query.replace("https://youtu.be/",'') 
        query = 'https://www.youtube.com/watch?v='+ query[0:11]
        return query


    def searchYoutube(self,query:str):
        video_search = VideosSearch(query=self.dotBeToDotCom(query), limit=1).result()['result'] 
        if(len(video_search) == 0):
            return False 
        result = video_search[0] 
        return result
    
    async def downloadVideoYoutube(self, url: str):
        try:
            nome_music = str(uuid.uuid4())
            output_dir = "./musics"

            os.makedirs(output_dir, exist_ok=True)

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{output_dir}/{nome_music}.%(ext)s",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "quiet": True,
                "no_warnings": True,
            }

            await asyncio.to_thread(self._download, ydl_opts, url)

            return nome_music

        except Exception as e:
            print(f"Erro ao baixar vídeo: {e}")
            return False

    def _download(self, ydl_opts, url):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    async def play(self,query,interaction:discord.Interaction):  

        # {722857509659869204: {'channel': 1176698533039059055, 'status': 'playing'}}
        # [id_server] => playlist
   
        if(interaction.user.voice is not None):  
            
            if(interaction.guild_id in self.statusServers):
                
                statusGuild = self.statusServers[interaction.guild_id]
                if(interaction.user.voice.channel.id == statusGuild['channel']):
                    # "Estão no mesmo canal de voz!" 
                    self.serversData[interaction.guild_id].add(query)
                    resMusic = self.searchYoutube(query=query)
                    embedPreview = previewMusic(resMusic)
                    await interaction.response.send_message(embed=embedPreview)
                    
                else:
                    await interaction.response.send_message("Eu já estou Musicando por aí 🎶🎵🎶") 
            else:
            
                # BOT ESTA SEM FAZER NADA bah   
                await interaction.response.defer(ephemeral=False,thinking=True) 
                playList = PlayList()
                playList.add(query)
                self.statusServers[interaction.guild_id] = {'channel':interaction.user.voice.channel.id,'status':'playing'}
                self.serversData[interaction.guild_id] = playList
                await interaction.followup.send("Lista de Músicas Iniciada")
                await self.tocarMusica(interaction, self.serversData[interaction.guild_id].atual())
        else: 
            await interaction.response.send_message("Primeiro Você tem que entrar em uma call, certo? 🤡")


    async def connectToVoice(self, interaction:discord.Interaction):

        if(interaction.guild.voice_client and interaction.guild.voice_client.is_connected()):
            return interaction.guild.voice_client

        channelUser = interaction.user.voice.channel
        vc = await channelUser.connect()
        return vc
    
    def haveNext(self, guild_id): 
        if(guild_id not in self.serversData):
            return False 
        return self.serversData[guild_id].next()
    
    def haveBack(self, guild_id): 
        if(guild_id not in self.serversData):
            return False 
        return self.serversData[guild_id].back()
    
    
    def resetMusicsServer(self, guild_id):
        if(guild_id in self.statusServers and guild_id in self.serversData):
            del self.statusServers[guild_id]
            del self.serversData[guild_id]


    async def nextMusic(self,interaction:discord.Interaction, after_played=False): 
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if(existsGId):  
            await interaction.response.send_message("Não há **PRÓXIMA** música (pov: você não deu /play 🤡)")
            return
 
        prox = self.haveNext(interaction.guild_id)
        if(prox): 
            await self.tocarMusica(interaction, prox)
        else:
            if(after_played):
                await interaction.channel.send("Lista de Músicas Finalizada")
                await self.stopMusic(interaction,after_played)
                return
            await interaction.response.send_message("Não há uma próxima música!") 
            
    async def backMusic(self,interaction:discord.Interaction): 
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if(existsGId): 
            await interaction.response.send_message("Não há música **ANTERIOR** (pov: você não deu /play 🤡)")
            return

        back = self.haveBack(interaction.guild_id)
        if(back): 
            await self.tocarMusica(interaction, back)
        else:
            await interaction.response.send_message("Não há uma música anterior!") 
    

    async def pauseMusic(self, interaction:discord.Interaction):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if(existsGId): 
            await interaction.response.send_message("Não há como **PAUSAR** (pov: você não deu /play 🤡)")
            return
        
        self.statusServers[interaction.guild_id]['status'] = "paused" 
        interaction.guild.voice_client.pause()
        await interaction.response.send_message(f"Música pausada por {interaction.user.mention} com sucesso! ✅") 


    

    async def resumeMusic(self, interaction:discord.Interaction):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if(existsGId): 
            await interaction.response.send_message("Não há como **CONTINUAR** música (pov: você não deu /play 🤡)")
            return

        self.statusServers[interaction.guild_id]['status'] = "playing" 
        interaction.guild.voice_client.resume() 
        await interaction.response.send_message(f"Música a todo vapor por {interaction.user.mention}!\n🚂💨💨💨💨💨💨💨💨💨 ")

    async def tocarMusica(self, interaction:discord.Interaction, query):
         
        musicaSearch = self.searchYoutube(query=query) 

        if(musicaSearch == False):
            # MUSICA NÃO ENCONTRADA
            return False 
        
        view = generateViewMusic( 
            lambda inter:  self.backMusic(inter),
            lambda inter:  self.pauseMusic(inter),
            lambda inter:  self.resumeMusic(inter),
            lambda inter:  self.nextMusic(inter),
            lambda inter:  self.stopMusic(inter), 
            lambda inter:  self.listarFilaMusica(inter), 
        )
         
        await interaction.channel.send(embed=embed_music(musicaSearch,interaction),view=view) 
        voice_channel = await self.connectToVoice(interaction=interaction) 
        nome_musica = await self.downloadVideoYoutube(musicaSearch['link'])  
        audio = discord.FFmpegPCMAudio(f'./musics/{nome_musica}.mp3')

        if(voice_channel.is_playing()):
            voice_channel.stop() 
        
        voice_channel.play(audio)
        await self.after_playing(voice_channel=voice_channel, musT=query, interaction=interaction)

    async def listarFilaMusica(self, interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=False,thinking=True) 
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if(existsGId): 
            await interaction.followup.send("Não há **FILA DE MÚSICAS** (pov: você não deu /play 🤡)")
            return 

        playlistServidor = self.serversData[interaction.guild_id]
        embedLista = embedListaMusics(playlistServidor.returnList(),playlistServidor.returnIndexMusic(),interaction)
        await interaction.followup.send(embed=embedLista) 

    async def noHaveGuildIdServerData(self, guild_id:int): 
        return guild_id not in self.serversData

    async def stopMusic(self,interaction:discord.Interaction,after_played=False):
        try:
            if interaction.guild.voice_client is not None:
                self.resetMusicsServer(interaction.guild_id)
                await interaction.guild.voice_client.disconnect()
                if(not after_played):
                    await interaction.response.send_message("Desconectado do canal de voz.")
            else:
                await interaction.response.send_message("O bot não está conectado a nenhum canal de voz.")
        except Exception as error:
            await interaction.followup.send(f"```{error}```")

    
    async def after_playing(self,voice_channel:discord.VoiceClient, musT, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        while voice_channel.is_playing():
            # fica esperando aqui ate a música tocando acabar 
            await asyncio.sleep(0.1)   
        
        if(guild_id not in self.statusServers):
            return
        if(self.serversData[guild_id].atual() == musT and self.statusServers[interaction.guild_id]['status'] == "playing" ):
            await self.nextMusic(interaction=interaction,after_played=True)

         

        
            