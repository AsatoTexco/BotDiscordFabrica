import discord


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
    embed_music.add_field(name="Request", value=f"{inter.user.mention}", inline=True)
    embed_music.add_field(name="Video", value=f"[Ir para Video]({data['link']})", inline=True)

    if (data.get('descriptionSnippet') and len(data['descriptionSnippet']) > 0 and     data['descriptionSnippet'][0].get('text') and data.get('channel') and data['channel'].get('thumbnails') and len(data['channel']['thumbnails']) > 0 and data['channel']['thumbnails'][0].get('url')):

        embed_music.set_footer(
            text=f"{data['descriptionSnippet'][0]['text']}", 
            icon_url=f"{data['channel']['thumbnails'][0]['url']}"
        )
    # embed_music.set_footer(text=f"{data['descriptionSnippet'][0]['text']}", icon_url=f"{data['channel']['thumbnails'][0]['url']}")  
    
    return embed_music

def embedListaMusics(listMusics, atual:int, inter:discord.Interaction):
    embed_lista = discord.Embed(
        title="Fila de Músicas",
        color=0x00ffff
    ) 
    strListMusics = ""
    for i in range(len(listMusics)):
        if(i == atual):
            strListMusics = strListMusics + "\n" + f":arrow_forward: **{i+1}° - {listMusics[i]}** :arrow_backward:"
        else:
            strListMusics = strListMusics + "\n" + f"{i+1}° - {listMusics[i]}"
    embed_lista.add_field(name="Lista",value=f"{strListMusics}")
    return embed_lista

def generateViewMusic(c1,c2,c3,c4,c5,c6):
    button1 = discord.ui.Button(style=discord.ButtonStyle.green,    label="◀")
    button2 = discord.ui.Button(style=discord.ButtonStyle.primary,  label="⏹")
    button3 = discord.ui.Button(style=discord.ButtonStyle.primary , label="⏺")
    button4 = discord.ui.Button(style=discord.ButtonStyle.green ,   label="▶")
    button5 = discord.ui.Button(style=discord.ButtonStyle.red ,   label="❌")
    button6 = discord.ui.Button(style=discord.ButtonStyle.grey,    label="💠")

    button1.callback = c1
    button2.callback = c2
    button3.callback = c3
    button4.callback = c4
    button5.callback = c5
    button6.callback = c6

    view = discord.ui.View()
    view.add_item(button6)
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)
    view.add_item(button5)
    return view

def previewMusic(data):

    embed_music = discord.Embed(
            title=f"**{data['title']}**",
            description=f"**Música adicionada à Lista de Músicas**",
            color=0x00ffff
    )  
     
    embed_music.set_thumbnail(url=f"{data['channel']['thumbnails'][0]['url']}")    
    embed_music.add_field(name="Video", value=f"[Ir para Video]({data['link']})", inline=True)

    if(data['descriptionSnippet'] is not None and data['channel']['thumbnails'] is not None):
        if(data['descriptionSnippet'][0]['text'] is not None and data['channel']['thumbnails'][0]['url'] is not None):
            embed_music.set_footer(text=f"{data['descriptionSnippet'][0]['text']}", icon_url=f"{data['channel']['thumbnails'][0]['url']}")  
    
    return embed_music
