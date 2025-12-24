from discord.ext import commands
import Music_Service
import math

class Music_Controller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def get_state(self, ctx):
        gid = ctx.guild.id
        if gid not in self.states:
            self.states[gid] = Music_Service.ServerState(self.bot)
        return self.states[gid]
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Unknown command: **{ctx.invoked_with}**")
            await ctx.send(f"Use **{self.bot.command_prefix}help** to get more info about commands")
        else:
            if isinstance(error, commands.PrivateMessageOnly):
                return
            
    @commands.command(name='play')
    async def play(self, ctx, *url):
        """
        args: <url or description> [position] ; default position = 1
        """
        if(ctx.author.voice):
            voice_ch = ctx.message.author.voice.channel
            if not ctx.voice_client:
                await voice_ch.connect()

            state = self.get_state(ctx)

            if len(url) == 0:
                await ctx.send(f"No arguments to command play, consider using \"{self.bot.command_character}help\"")
                return
            elif len(url) == 1:
                music_query = url[0]
                position = len(state.queue)
            else:
                music_query = ' '.join(url[:-1])
                position = url[-1]
            
            try:
                new_position = int(position)
                if new_position <= 0 or new_position > len(state.queue):
                    raise ValueError
                else:
                    new_position -= 1
            except ValueError:
                new_position = len(state.queue)

            await state.add_song(ctx, music_query, new_position)
            if not state.isPlaying:
                await state.play_next(ctx)

    @commands.command(name='stop')
    async def stop(self, ctx):
        """
        no args
        clear queue and disconnect
        """
        if(ctx.voice_client):
            state = self.get_state(ctx)
            state.isPlaying = False
            await ctx.guild.voice_client.disconnect()

    @commands.command(name='queue')
    async def list_songs(self, ctx, page=1):
        """
        args: [page] ; default page = 1
        list current queue
        """
        state = self.get_state(ctx)
        if len(state.queue) < 1:
            await ctx.send("Empty queue")
            return
        try:
            page = int(page)
            pages_count = math.ceil(len(state.queue) / 10)
            
            if page < 1 or page > pages_count:
                raise ValueError
        except ValueError:
            await ctx.send(f'\"{page}\" is not a valid page number')
            return
        await state.list_songs(ctx, page-1, pages_count)

    @commands.command(name='skip')
    async def skip(self, ctx):
        """
        no args
        skips current song
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send('Nothing is being played')
            return
        
        ctx.voice_client.stop()
        await ctx.send('Skipping...')

    @commands.command(name='remove')
    async def remove(self, ctx, position=0):
        """
        args: <pos>
        removes queue element at *pos* position
        """
        state = self.get_state(ctx)
        elems = len(state.queue)
        if elems < 0:
            await ctx.send("Nothing to be removed")
            return
        try:
            new_position = int(position)
            if position == 0:
                new_position = elems
            elif new_position < 0 or new_position > elems:
                raise ValueError
            else:
                new_position -= 1
        except ValueError:
            await ctx.send(f'\"{position}\" is not a valid integer')
            return
        await state.delete_song(ctx, new_position)

    @commands.command(name='move')
    async def move(self, ctx, pos_from=None, pos_to=None):
        """
        args: <pos1> <pos2>
        move queue element from *pos1* to *pos2*
        """
        if pos_from is None or pos_to is None:
            await ctx.send("Invalid amount of arguments")
            return
        state = self.get_state(ctx)
        qlen = len(state.queue)
        try:
            pos_from_int = int(pos_from)
            pos_to_int = int(pos_to)
            if not (0 < pos_from_int <= qlen) or not (0 < pos_to_int <= qlen):
                raise ValueError
        except ValueError:
            await ctx.send(f'\"{pos_from}\" or \"{pos_to}\" is not a valid integer')
            return
        await state.move(ctx, pos_from_int-1, pos_to_int-1)

    @commands.command(name='pause')
    async def pause(self, ctx):
        """
        no args
        pauses streaming music
        """
        voice_client = ctx.voice_client
        is_playing = voice_client.is_playing()
        if voice_client and is_playing:
            voice_client.pause()
            await ctx.send("**Paused**")
        elif not is_playing:
            await ctx.send("Already paused")
        else:
            await ctx.send("Not in a voice channel")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """
        no args
        resumes paused music stream
        """
        voice_client = ctx.voice_client
        is_paused = voice_client.is_paused()
        
        if voice_client and is_paused:
            voice_client.resume()
            await ctx.send("**Resumed**")
        elif not is_paused:
            await ctx.send("Already playing")
        else:
            await ctx.send("Not in a voice channel")

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        """
        no args
        randomly shuffles queue
        """
        state = self.get_state(ctx)
        await state.shuffle()
        await ctx.send("**Shuffled queue**")


async def setup(bot):
    await bot.add_cog(Music_Controller(bot))