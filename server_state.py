import audio_reader as AR
import discord

class ServerState:
    def __init__(self, bot, ctx):
        self.queue = []
        self.isPlaying = False
        self.bot = bot
        self.ctx = ctx

    async def add_song(self, url, position=-1):
        pos = len(self.queue) if position == -1 else position
        song_info = await self.bot.loop.run_in_executor(None, lambda: AR.play_music(url))
        if song_info is None:
            await self.send_message("Cannot get information about given data")
            return
        self.queue.insert(pos, song_info)
        await self.send_message(f"Added to queue: {song_info[1]} at position {pos}.")

    async def delete_song(self, position):
        self.queue.remove(position)
        await self.send_message(f"Removed: {self.queue[position][1]}")

    async def list_songs(self):
        if not self.queue:
            await self.send_message("Empty queue")
            return
        message = "Current queue:\n"
        for i, song in enumerate(self.queue):
            message += f"{i}. {song[1]}\n"
        await self.send_message(message)
        
    
    async def send_message(self, message):
        await self.ctx.send(message)

    async def play_next(self, ctx):
        self.isPlaying = True
        if self.queue:
            song = self.queue.pop(0)
            stream_url = song[0]
            name = song[1]
            if stream_url is not None:
                ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
                await self.send_message(f"**Playing now: {name}**")
                ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            else:
                print("Zły link")
        else:
            self.isPlaying = False
            await self.send_message("**End of the queue**")