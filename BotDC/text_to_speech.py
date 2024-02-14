from gtts import gTTS

import os


async def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='pt')  # 'pt' para português, mas você pode mudar conforme necessário
    tts.save(output_file)
    return True
 