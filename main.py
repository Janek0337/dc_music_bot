import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import server_state
import math

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
command_character = '?'
bot = commands.Bot(command_prefix=command_character, intents=intents)

states = {}
def get_state(ctx):
    gid = ctx.guild.id
    if gid not in states:
        states[gid] = server_state.ServerState(bot, ctx)
    return states[gid]

@bot.event
async def on_ready():
    print("Siema eniu")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if 'barotrauma' in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} był niegrzeczny :v")
    
    await bot.process_commands(message)

@bot.command(pass_context = True)
async def play(ctx, url=None, position=0):
    if(ctx.author.voice):
        voice_ch = ctx.message.author.voice.channel
        if not ctx.voice_client:
            await voice_ch.connect()
        if url is None:
            await ctx.send(f"No arguments to command play, consider using \"{command_character}help\"")
            return
        state = get_state(ctx)
        try:
            new_position = int(position)
            if position == 0:
                new_position = len(state.queue)
            elif new_position < 0 or new_position > len(state.queue):
                raise ValueError
            else:
                new_position -= 1
        except ValueError:
            await ctx.send(f'\"{position}\" is not a valid integer')
            return

        await state.add_song(url, new_position)
        if not state.isPlaying:
            await state.play_next(ctx)

@bot.command(pass_context = True)
async def stop(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()

@bot.command(pass_context = True, name='queue')
async def list_songs(ctx, page=1):
    state = get_state(ctx)
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
    await state.list_songs(page-1, pages_count)

@bot.command(pass_context = True)
async def skip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await ctx.send('Nothing is being played')
        return
    
    state = get_state(ctx)
    ctx.voice_client.stop()
    await state.send_message('Skipping...')

@bot.command(pass_context = True)
async def remove(ctx, position=0):
    state = get_state(ctx)
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
    await state.delete_song(new_position)

@bot.command(pass_context = True)
async def move(ctx, pos_from=None, pos_to=None):
    state = get_state(ctx)
    qlen = len(state.queue)
    try:
        pos_from_int = int(pos_from)
        pos_to_int = int(pos_to)
        if not (0 < pos_from_int < qlen) or not (0 < pos_to_int < qlen):
            raise ValueError
    except ValueError:
        await ctx.send(f'\"{pos_from}\" or \"{pos_to}\" is not a valid integer')
        return
    await state.move(pos_from_int-1, pos_to_int-1)

bot.run(token=token, log_handler=handler)