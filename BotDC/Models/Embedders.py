import discord


def embed_music(data: dict, inter: discord.Interaction) -> discord.Embed:
    title = data.get("title", "Música")
    channel_info = data.get("channel") or {}
    channel_name = channel_info.get("name", "YouTube")
    channel_link = channel_info.get("link", data.get("link", "https://youtube.com"))

    embed = discord.Embed(
        title=f"**{title}**",
        description=f"**[{channel_name}]({channel_link})**",
        color=0x00FFFF,
    )

    thumbnails = data.get("thumbnails") or []
    if thumbnails and thumbnails[-1].get("url"):
        embed.set_image(url=thumbnails[-1]["url"])

    channel_thumbs = channel_info.get("thumbnails") or []
    channel_thumb_url = channel_thumbs[0].get("url") if channel_thumbs else None
    if channel_thumb_url:
        embed.set_thumbnail(url=channel_thumb_url)

    embed.add_field(name="Publicado", value=str(data.get("publishedTime", "N/A")), inline=True)
    embed.add_field(name="Duration", value=str(data.get("duration", "N/A")), inline=True)
    view_short = (data.get("viewCount") or {}).get("short", "N/A")
    embed.add_field(name="Views", value=str(view_short), inline=True)
    embed.add_field(name="Request", value=f"{inter.user.mention}", inline=True)
    embed.add_field(name="Video", value=f"[Ir para Video]({data.get('link', 'https://youtube.com')})", inline=True)

    snippets = data.get("descriptionSnippet") or []
    snippet_text = snippets[0].get("text") if snippets and isinstance(snippets[0], dict) else None
    if snippet_text:
        embed.set_footer(
            text=snippet_text[:200],
            icon_url=channel_thumb_url,
        )

    return embed


def embedListaMusics(listMusics, atual: int, inter: discord.Interaction) -> discord.Embed:
    lines = []
    for i, item in enumerate(listMusics):
        label = item.get("title", item.get("query", str(item))) if isinstance(item, dict) else str(item)
        if i == atual:
            lines.append(f":arrow_forward: **{i + 1}° - {label}** :arrow_backward:")
        else:
            lines.append(f"{i + 1}° - {label}")

    str_list = "\n".join(lines) if lines else "Nenhuma música na fila."
    if len(str_list) > 4000:
        str_list = str_list[:3997] + "..."

    embed_lista = discord.Embed(
        title="🎵 Fila de Músicas",
        description=str_list,
        color=0x00FFFF,
    )
    return embed_lista


def generateViewMusic(c1, c2, c3, c4, c5, c6) -> discord.ui.View:
    button1 = discord.ui.Button(style=discord.ButtonStyle.green, label="◀")
    button2 = discord.ui.Button(style=discord.ButtonStyle.primary, label="⏸")
    button3 = discord.ui.Button(style=discord.ButtonStyle.primary, label="▶")
    button4 = discord.ui.Button(style=discord.ButtonStyle.green, label="⏭")
    button5 = discord.ui.Button(style=discord.ButtonStyle.red, label="⏹")
    button6 = discord.ui.Button(style=discord.ButtonStyle.grey, label="💠")

    button1.callback = c1
    button2.callback = c2
    button3.callback = c3
    button4.callback = c4
    button5.callback = c5
    button6.callback = c6

    view = discord.ui.View(timeout=None)
    view.add_item(button6)
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)
    view.add_item(button5)
    return view


def previewMusic(data: dict) -> discord.Embed:
    title = data.get("title", "Música")
    embed = discord.Embed(
        title=f"**{title}**",
        description="**Música adicionada à Lista de Músicas**",
        color=0x00FFFF,
    )

    channel_info = data.get("channel") or {}
    channel_thumbs = channel_info.get("thumbnails") or []
    channel_thumb_url = channel_thumbs[0].get("url") if channel_thumbs else None
    if not channel_thumb_url:
        thumbs = data.get("thumbnails") or []
        channel_thumb_url = thumbs[-1].get("url") if thumbs else None

    if channel_thumb_url:
        embed.set_thumbnail(url=channel_thumb_url)

    embed.add_field(name="Video", value=f"[Ir para Video]({data.get('link', 'https://youtube.com')})", inline=True)

    snippets = data.get("descriptionSnippet") or []
    snippet_text = snippets[0].get("text") if snippets and isinstance(snippets[0], dict) else None
    if snippet_text:
        embed.set_footer(text=snippet_text[:200], icon_url=channel_thumb_url)

    return embed
