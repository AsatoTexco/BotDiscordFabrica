import asyncio
import os
import uuid
import discord
import yt_dlp

from .PlayList import PlayList
from .Embedders import embed_music, generateViewMusic, previewMusic, embedListaMusics

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSICS_DIR = os.path.join(BASE_DIR, "musics")


def _format_duration(seconds) -> str:
    if not seconds:
        return "Ao vivo / N/A"
    seconds = int(seconds)
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def _format_views(views) -> str:
    if views is None:
        return "N/A"
    try:
        v = int(views)
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:.1f}B views"
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M views"
        if v >= 1_000:
            return f"{v / 1_000:.1f}K views"
        return f"{v} views"
    except (ValueError, TypeError):
        return str(views)


def _format_date(upload_date: str) -> str:
    if not upload_date or len(str(upload_date)) != 8:
        return "N/A"
    s = str(upload_date)
    return f"{s[6:8]}/{s[4:6]}/{s[0:4]}"


class Dj:
    def __init__(self, bot) -> None:
        self.serversData: dict[int, PlayList] = {}
        self.statusServers: dict[int, dict] = {}
        self.activeFiles: dict[int, str] = {}
        self.playbackTokens: dict[int, str] = {}
        self.bot = bot

    async def _reply(self, interaction: discord.Interaction, content: str = None, embed: discord.Embed = None, view: discord.ui.View = None):
        kwargs = {}
        if content is not None:
            kwargs["content"] = content
        if embed is not None:
            kwargs["embed"] = embed
        if view is not None:
            kwargs["view"] = view

        if interaction.response.is_done():
            await interaction.followup.send(**kwargs)
        else:
            await interaction.response.send_message(**kwargs)

    def dotBeToDotCom(self, query: str) -> str:
        query = query.strip()
        if "https://youtu.be/" in query:
            vid_id = query.split("https://youtu.be/")[-1][:11]
            return f"https://www.youtube.com/watch?v={vid_id}"
        return query

    def _extract_yt_info(self, query: str):
        clean_query = self.dotBeToDotCom(query)
        search_target = clean_query if clean_query.startswith(("http://", "https://")) else f"ytsearch1:{clean_query}"

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "default_search": "ytsearch1",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=False)
            if not info:
                return False
            if "entries" in info:
                entries = [e for e in info["entries"] if e]
                if not entries:
                    return False
                info = entries[0]

            video_url = info.get("webpage_url") or info.get("original_url") or f"https://www.youtube.com/watch?v={info.get('id', '')}"
            thumb = info.get("thumbnail") or ""
            thumbs = info.get("thumbnails") or ([{"url": thumb}] if thumb else [])
            desc = (info.get("description") or "").strip()

            return {
                "title": info.get("title", clean_query),
                "link": video_url,
                "duration": info.get("duration_string") or _format_duration(info.get("duration")),
                "publishedTime": _format_date(info.get("upload_date")),
                "viewCount": {"short": _format_views(info.get("view_count"))},
                "thumbnails": thumbs if thumbs else [{"url": thumb}],
                "channel": {
                    "name": info.get("uploader") or info.get("channel") or "YouTube",
                    "link": info.get("uploader_url") or info.get("channel_url") or video_url,
                    "thumbnails": [{"url": thumb}] if thumb else [],
                },
                "descriptionSnippet": [{"text": desc[:180]}] if desc else [],
            }

    async def searchYoutube(self, query: str):
        try:
            return await asyncio.to_thread(self._extract_yt_info, query)
        except Exception as e:
            print(f"Erro ao buscar vídeo no YouTube: {e}")
            return False

    async def downloadVideoYoutube(self, url: str):
        try:
            nome_music = str(uuid.uuid4())
            os.makedirs(MUSICS_DIR, exist_ok=True)
            out_template = os.path.join(MUSICS_DIR, f"{nome_music}.%(ext)s")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": out_template,
                "noplaylist": True,
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
            mp3_path = os.path.join(MUSICS_DIR, f"{nome_music}.mp3")
            return mp3_path if os.path.exists(mp3_path) else False
        except Exception as e:
            print(f"Erro ao baixar vídeo: {e}")
            return False

    def _download(self, ydl_opts, url: str):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def _cleanup_file(self, guild_id: int):
        old_file = self.activeFiles.pop(guild_id, None)
        if old_file and os.path.exists(old_file):
            try:
                os.remove(old_file)
            except OSError:
                pass

    def _sync_voice_state(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        vc = interaction.guild.voice_client if interaction.guild else None
        if guild_id in self.statusServers and (vc is None or not vc.is_connected()):
            self.resetMusicsServer(guild_id)

    async def play(self, query: str, interaction: discord.Interaction):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await self._reply(interaction, "Primeiro você tem que entrar em uma call, certo? 🤡")
            return

        self._sync_voice_state(interaction)

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False, thinking=True)

        if interaction.guild_id in self.statusServers:
            statusGuild = self.statusServers[interaction.guild_id]
            if interaction.user.voice.channel.id == statusGuild["channel"]:
                resMusic = await self.searchYoutube(query=query)
                if not resMusic:
                    await self._reply(interaction, "Não consegui encontrar essa música no YouTube 😢")
                    return
                self.serversData[interaction.guild_id].add(query)
                embedPreview = previewMusic(resMusic)
                await self._reply(interaction, embed=embedPreview)
            else:
                await self._reply(interaction, "Eu já estou musicando em outro canal de voz 🎶🎵🎶")
        else:
            playList = PlayList()
            playList.add(query)
            self.statusServers[interaction.guild_id] = {
                "channel": interaction.user.voice.channel.id,
                "status": "playing",
            }
            self.serversData[interaction.guild_id] = playList
            await self._reply(interaction, "🎶 Lista de Músicas Iniciada!")
            ok = await self.tocarMusica(interaction, self.serversData[interaction.guild_id].atual())
            if not ok:
                self.resetMusicsServer(interaction.guild_id)
                await interaction.channel.send("Não foi possível reproduzir a música solicitada 😢")

    async def connectToVoice(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return None

        channelUser = interaction.user.voice.channel
        vc = interaction.guild.voice_client if interaction.guild else None

        if vc is not None:
            if vc.is_connected():
                if vc.channel.id != channelUser.id:
                    await vc.move_to(channelUser)
                return vc
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass

        try:
            vc = await channelUser.connect(timeout=20.0, reconnect=True)
            return vc if vc and vc.is_connected() else None
        except Exception as e:
            print(f"Erro ao conectar ao canal de voz: {e}")
            return None

    def haveNext(self, guild_id: int):
        if guild_id not in self.serversData:
            return False
        return self.serversData[guild_id].next()

    def haveBack(self, guild_id: int):
        if guild_id not in self.serversData:
            return False
        return self.serversData[guild_id].back()

    def resetMusicsServer(self, guild_id: int):
        self.playbackTokens.pop(guild_id, None)
        self._cleanup_file(guild_id)
        self.statusServers.pop(guild_id, None)
        self.serversData.pop(guild_id, None)

    async def nextMusic(self, interaction: discord.Interaction, after_played: bool = False):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if existsGId:
            if not after_played:
                await self._reply(interaction, "Não há **PRÓXIMA** música (pov: você não deu /play 🤡)")
            return

        prox = self.haveNext(interaction.guild_id)
        if prox:
            if not after_played:
                await self._reply(interaction, "⏭ Pulando para a próxima música...")
            await self.tocarMusica(interaction, prox)
        else:
            if after_played:
                await interaction.channel.send("✅ Lista de Músicas Finalizada!")
                await self.stopMusic(interaction, after_played=True)
                return
            await self._reply(interaction, "Não há uma próxima música na fila!")

    async def backMusic(self, interaction: discord.Interaction):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if existsGId:
            await self._reply(interaction, "Não há música **ANTERIOR** (pov: você não deu /play 🤡)")
            return

        back = self.haveBack(interaction.guild_id)
        if back:
            await self._reply(interaction, "⏮ Voltando para a música anterior...")
            await self.tocarMusica(interaction, back)
        else:
            await self._reply(interaction, "Não há uma música anterior!")

    async def pauseMusic(self, interaction: discord.Interaction):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        vc = interaction.guild.voice_client if interaction.guild else None
        if existsGId or vc is None or not vc.is_connected():
            await self._reply(interaction, "Não há como **PAUSAR** (pov: você não deu /play 🤡)")
            return

        if vc.is_playing():
            self.statusServers[interaction.guild_id]["status"] = "paused"
            vc.pause()
            await self._reply(interaction, f"⏸ Música pausada por {interaction.user.mention} com sucesso! ✅")
        else:
            await self._reply(interaction, "A música já está pausada ou parada.")

    async def resumeMusic(self, interaction: discord.Interaction):
        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        vc = interaction.guild.voice_client if interaction.guild else None
        if existsGId or vc is None or not vc.is_connected():
            await self._reply(interaction, "Não há como **CONTINUAR** música (pov: você não deu /play 🤡)")
            return

        if vc.is_paused():
            self.statusServers[interaction.guild_id]["status"] = "playing"
            vc.resume()
            await self._reply(interaction, f"▶ Música a todo vapor por {interaction.user.mention}!\n🚂💨💨💨💨💨💨💨💨💨")
        else:
            await self._reply(interaction, "A música já está tocando!")

    async def tocarMusica(self, interaction: discord.Interaction, query: str):
        guild_id = interaction.guild_id
        musicaSearch = await self.searchYoutube(query=query)
        if not musicaSearch:
            return False

        mp3_path = await self.downloadVideoYoutube(musicaSearch["link"])
        if not mp3_path:
            return False

        voice_channel = await self.connectToVoice(interaction=interaction)
        if not voice_channel or not voice_channel.is_connected():
            return False

        token = str(uuid.uuid4())
        self.playbackTokens[guild_id] = token

        if voice_channel.is_playing() or voice_channel.is_paused():
            voice_channel.stop()

        self._cleanup_file(guild_id)
        self.activeFiles[guild_id] = mp3_path
        if guild_id in self.statusServers:
            self.statusServers[guild_id]["status"] = "playing"

        view = generateViewMusic(
            lambda inter: self.backMusic(inter),
            lambda inter: self.pauseMusic(inter),
            lambda inter: self.resumeMusic(inter),
            lambda inter: self.nextMusic(inter),
            lambda inter: self.stopMusic(inter),
            lambda inter: self.listarFilaMusica(inter),
        )

        await interaction.channel.send(embed=embed_music(musicaSearch, interaction), view=view)

        audio = discord.FFmpegPCMAudio(mp3_path)
        voice_channel.play(audio)
        asyncio.create_task(self.after_playing(voice_channel=voice_channel, token=token, interaction=interaction))
        return True

    async def listarFilaMusica(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False, thinking=True)

        existsGId = await self.noHaveGuildIdServerData(interaction.guild_id)
        if existsGId:
            await self._reply(interaction, "Não há **FILA DE MÚSICAS** (pov: você não deu /play 🤡)")
            return

        playlistServidor = self.serversData[interaction.guild_id]
        embedLista = embedListaMusics(playlistServidor.returnList(), playlistServidor.returnIndexMusic(), interaction)
        await self._reply(interaction, embed=embedLista)

    async def noHaveGuildIdServerData(self, guild_id: int) -> bool:
        return guild_id not in self.serversData

    async def stopMusic(self, interaction: discord.Interaction, after_played: bool = False):
        try:
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc is not None:
                if vc.is_playing() or vc.is_paused():
                    vc.stop()
                self.resetMusicsServer(interaction.guild_id)
                await vc.disconnect()
                if not after_played:
                    await self._reply(interaction, "⏹ Desconectado do canal de voz.")
            else:
                self.resetMusicsServer(interaction.guild_id)
                if not after_played:
                    await self._reply(interaction, "O bot não está conectado a nenhum canal de voz.")
        except Exception as error:
            if not after_played:
                await self._reply(interaction, f"```{error}```")

    async def after_playing(self, voice_channel: discord.VoiceClient, token: str, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        while voice_channel.is_connected() and (voice_channel.is_playing() or voice_channel.is_paused()):
            if self.playbackTokens.get(guild_id) != token:
                return
            await asyncio.sleep(0.5)

        if self.playbackTokens.get(guild_id) != token:
            return
        if guild_id not in self.statusServers:
            return

        self._cleanup_file(guild_id)
        await self.nextMusic(interaction=interaction, after_played=True)
