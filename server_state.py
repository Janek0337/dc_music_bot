import audio_reader as AR
import discord
from discord.ext import commands

class ServerState:
    def __init__(self, bot, ctx):
        self.queue = []
        self.isPlaying = False
        self.bot = bot
        self.ctx = ctx

    async def add_song(self, url, position=-1):
        pos = len(self.queue) if position == -1 else position
        self.queue.insert(pos, url)
        await self.ctx.send(f"Added to queue: {url} at position {pos}")

    async def delete_song(self, position):
        self.queue.remove(position)
        await self.ctx.send(f"Removed: {position}")

    async def play_next(self, ctx):
        self.isPlaying = True
        if self.queue:
            url = self.queue.pop(0)
            stream_url = AR.play_music(url)
            if stream_url is not None:
                ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
                self.bot.loop.create_task(self.ctx.send(f"Playing now: {url}"))
                ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            else:
                print("Zły link")
        else:
            self.isPlaying = False
            print("Koniec kolejki")