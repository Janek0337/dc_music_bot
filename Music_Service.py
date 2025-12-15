import audio_reader as AR
import discord
import random

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
            duration = song[2]
            if stream_url is not None:
                ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
                timer_source = AR.TimerAudioSource(source, duration)
                await ctx.send(f"**Playing now: {name}**")
                ctx.voice_client.play(timer_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            else:
                await ctx.send("Invalid link")
                await self.play_next(ctx)
        else:
            self.isPlaying = False
            await ctx.send("**The end of the queue**")

    async def move(self, ctx, pos_from, pos_to):
        await ctx.send(f"Moving **\"{self.queue[pos_from][1]}\"** to position **{pos_to+1}**")
        self.queue.insert(pos_to, self.queue.pop(pos_from))

    async def shuffle(self):
        random.shuffle(self.queue)

    async def get_time(self, ctx):
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            source = voice_client.source
            if isinstance(source, discord.PCMVolumeTransformer):
                source = source.original
            if hasattr(source, "get_progress") and hasattr(source, "duration"):
                secs, mins, hours = self.get_time_from_secs(source.get_progress())
                max_seconds, max_minutes, max_hours = self.get_time_from_secs(source.duration)
                await ctx.send("Currently playing time: **{hrs}{mins}{secs} / {max_hrs}{max_mins}{max_secs}**"
                            .format(hrs=f"{hours:02}:" if hours > 0 else "", mins=f"{mins:02}:", secs=f"{secs:02}",
                                    max_hrs=f"{max_hours:02}:" if max_hours > 0 else "", max_mins=f"{max_minutes:02}:", max_secs=f"{max_seconds:02}"))
            else:
                await ctx.send("Cannot read time")
        else:
            await ctx.send("Nothing to play")

    def get_time_from_secs(self, all_seconds):
        if all_seconds is None:
            return (0,0,0)
        
        good_seconds = int(all_seconds)
        secs = good_seconds % 60
        hours = good_seconds // 3600
        minutes = (good_seconds - hours * 3600) // 60
        return (secs, minutes, hours)