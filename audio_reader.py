import yt_dlp

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
            
            return stream_url, title
            
        except Exception as e:
            print(f"Błąd podczas pobierania strumienia: {e}")
            return None, None