import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import server_state

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
async def list_songs(ctx):
    state = get_state(ctx)
    if len(state.queue) < 1:
        await ctx.send("Empty queue")
        return
    await state.list_songs()

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

bot.run(token=token, log_handler=handler)