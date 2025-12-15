import yt_dlp
import discord
import time

def play_music(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'no_warnings' : True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]

            stream_url = info['url'] 
            title = info['title']
            duration = info['duration']

            return (stream_url, title, duration)
            
        except Exception as e:
            print(f"Error while obtaning stream: {e}")
            return (None, None, None)
        

class TimerAudioSource(discord.AudioSource):
    def __init__(self, original_source, duration):
        self.original = original_source
        self.count_20ms = 0
        self.duration = duration

    def read(self):
        chunk = self.original.read()
        if chunk:
            self.count_20ms += 1
        return chunk

    def cleanup(self):
        self.original.cleanup()

    def get_progress(self):
        return self.count_20ms * 0.02