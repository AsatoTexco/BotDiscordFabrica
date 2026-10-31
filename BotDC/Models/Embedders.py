import discord


def embed_music(data: dict, inter: discord.Interaction) -> discord.Embed:
    title = data.get("title", "Música Desconhecida")
    channel_info = data.get("channel") or {}
    channel_name = channel_info.get("name", "YouTube")
    channel_link = channel_info.get("link", data.get("link", "https://youtube.com"))

    embed = discord.Embed(
        title=f"🎵 {title}",
        url=data.get("link", "https://youtube.com"),
        description=f"Canal: **[{channel_name}]({channel_link})**",
        color=0x5865F2,
    )

    thumbnails = data.get("thumbnails") or []
    if thumbnails and thumbnails[-1].get("url"):
        embed.set_image(url=thumbnails[-1]["url"])

    channel_thumbs = channel_info.get("thumbnails") or []
    channel_thumb_url = channel_thumbs[0].get("url") if channel_thumbs else None
    if channel_thumb_url:
        embed.set_thumbnail(url=channel_thumb_url)

    embed.add_field(name="⏱ Duração", value=f"`{data.get('duration', 'N/A')}`", inline=True)
    view_short = (data.get("viewCount") or {}).get("short", "N/A")
    embed.add_field(name="👁 Views", value=f"`{view_short}`", inline=True)
    embed.add_field(name="📅 Lançamento", value=f"`{data.get('publishedTime', 'N/A')}`", inline=True)
    embed.add_field(name="🎧 Pedido por", value=inter.user.mention, inline=True)
    embed.add_field(name="🔗 Link Direto", value=f"[Assistir no YouTube]({data.get('link', 'https://youtube.com')})", inline=True)

    snippets = data.get("descriptionSnippet") or []
    snippet_text = snippets[0].get("text") if snippets and isinstance(snippets[0], dict) else None
    if snippet_text:
        footer_icon = channel_thumb_url if channel_thumb_url else None
        embed.set_footer(text=f"📌 {snippet_text[:160]}...", icon_url=footer_icon)

    return embed


def embedListaMusics(listMusics, atual: int, inter: discord.Interaction) -> discord.Embed:
    lines = []
    for i, item in enumerate(listMusics):
        label = item.get("title", item.get("query", str(item))) if isinstance(item, dict) else str(item)
        if i == atual:
            lines.append(f"▶ **{i + 1:02d}.** `{label}` *(Tocando agora)*")
        elif i < atual:
            lines.append(f"✔ ~~{i + 1:02d}. {label}~~")
        else:
            lines.append(f"▫ **{i + 1:02d}.** {label}")

    str_list = "\n".join(lines) if lines else "Nenhuma música na fila."
    if len(str_list) > 3900:
        str_list = str_list[:3890] + "\n... *(e mais músicas)*"

    embed = discord.Embed(
        title="📑 Fila de Reprodução",
        description=str_list,
        color=0x00E5FF,
    )
    embed.set_footer(text=f"Total: {len(listMusics)} música(s) • Solicitado por {inter.user.display_name}")
    return embed


def generateViewMusic(c1, c2, c3, c4, c5, c6) -> discord.ui.View:
    btn_back = discord.ui.Button(style=discord.ButtonStyle.secondary, label="Voltar", emoji="⏮")
    btn_pause = discord.ui.Button(style=discord.ButtonStyle.primary, label="Pausar", emoji="⏸")
    btn_resume = discord.ui.Button(style=discord.ButtonStyle.success, label="Tocar", emoji="▶")
    btn_next = discord.ui.Button(style=discord.ButtonStyle.secondary, label="Pular", emoji="⏭")
    btn_stop = discord.ui.Button(style=discord.ButtonStyle.danger, label="Parar", emoji="⏹")
    btn_queue = discord.ui.Button(style=discord.ButtonStyle.secondary, label="Fila", emoji="📋")

    btn_back.callback = c1
    btn_pause.callback = c2
    btn_resume.callback = c3
    btn_next.callback = c4
    btn_stop.callback = c5
    btn_queue.callback = c6

    view = discord.ui.View(timeout=None)
    view.add_item(btn_back)
    view.add_item(btn_pause)
    view.add_item(btn_resume)
    view.add_item(btn_next)
    view.add_item(btn_stop)
    view.add_item(btn_queue)
    return view


def previewMusic(data: dict) -> discord.Embed:
    title = data.get("title", "Música")
    embed = discord.Embed(
        title="➕ Adicionada à Fila",
        description=f"**[{title}]({data.get('link', 'https://youtube.com')})**",
        color=0x10B981,
    )

    channel_info = data.get("channel") or {}
    channel_thumbs = channel_info.get("thumbnails") or []
    channel_thumb_url = channel_thumbs[0].get("url") if channel_thumbs else None
    if not channel_thumb_url:
        thumbs = data.get("thumbnails") or []
        channel_thumb_url = thumbs[-1].get("url") if thumbs else None

    if channel_thumb_url:
        embed.set_thumbnail(url=channel_thumb_url)

    embed.add_field(name="⏱ Duração", value=f"`{data.get('duration', 'N/A')}`", inline=True)
    embed.add_field(name="👤 Canal", value=f"`{channel_info.get('name', 'YouTube')}`", inline=True)
    return embed
