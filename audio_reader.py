import subprocess

def play_music(url):
    cmd_get_url = ["yt-dlp", "-g",  "-f", "bestaudio", "--extractor-args", "youtube:player_client=default", url]

    try:
        process = subprocess.run(cmd_get_url, stdout=subprocess.PIPE, text=True, check=True)
        audio_url = process.stdout.strip()
        return audio_url
    except subprocess.CalledProcessError:
        print("Błąd pobierania URL")
        return None