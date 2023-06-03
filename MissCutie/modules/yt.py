import youtube_dl
from telethon.sync import TelegramClient
from telethon import events
from telethon.tl.types import InputFile
from youtubesearchpython import VideosSearch
from MissCutie import telethn as client

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


@client.on(events.NewMessage(pattern='/yt'))
async def handle_song(event):
    chat = await event.get_chat()
    message = event.message
    song_name = message.text.replace('/yt', '').strip()

    if not song_name:
        await event.respond('Please provide a song name.')
        return

    query = f'{song_name} lyrics'
    try:
        videos = VideosSearch(query, limit=1).result()['result']
        if len(videos) > 0:
            video = videos[0]
            url = video['link']
            title = video['title']
            filename = f'{title}.mp3'

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                ydl.download([url])

            with open(filename, 'rb') as f:
                result = await client.upload_file(f)
                audio_input_file = InputFile(result.file_id, result.parts, result.name)

            await client.send_file(chat, file=audio_input_file, caption=title)
            await event.respond('Song downloaded and sent.')
        else:
            await event.respond('No search results found for the given song name.')
    except Exception as e:
        await event.respond(f'An error occurred: {str(e)}')

