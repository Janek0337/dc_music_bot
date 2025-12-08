import audio_reader as AR
import discord

class ServerState:
    def __init__(self, bot):
        self.queue = []
        self.isPlaying = False
        self.bot = bot

    async def add_song(self, ctx, url, index):
        song_info = await self.bot.loop.run_in_executor(None, lambda: AR.play_music(url))
        if song_info is None:
            await ctx.send("Cannot get information about given data")
            return
        self.queue.insert(index, song_info)
        await ctx.send(f"Added to queue: **\"{song_info[1]}\"** at position **{index+1}**")

    async def delete_song(self, ctx, position):
        await ctx.send(f"Removed: **\"{self.queue[position][1]}\"**")
        self.queue.pop(position)

    async def list_songs(self, ctx, page, pages_count):
        start_idx = page*10
        end_idx = page*10 + 10
        
        page_songs = self.queue[start_idx:end_idx]

        message = f"Current queue (page {page+1}/{pages_count}):\n"
        for i, song in enumerate(page_songs, start=start_idx+1):
            message += f"{i}. {song[1]}\n"
        await ctx.send(message)

    async def play_next(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            self.isPlaying = False
            self.queue = []
            return
        
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
                await ctx.send(f"**Playing now: {name}**")
                ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            else:
                await ctx.send("Invalid link")
                await self.play_next(ctx)
        else:
            self.isPlaying = False
            await ctx.send("**The end of the queue**")

    async def move(self, ctx, pos_from, pos_to):
        await ctx.send(f"Moving **\"{self.queue[pos_from][1]}\"** to position **{pos_to+1}**")
        self.queue.insert(pos_to, self.queue.pop(pos_from))