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

bot = commands.Bot(command_prefix='?', intents=intents)

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

@bot.command()
async def play(ctx, url, position=-1):
    if(ctx.author.voice):
        voice_ch = ctx.message.author.voice.channel
        if not ctx.voice_client:
            await voice_ch.connect()
        state = get_state(ctx)
        await state.add_song(url, position)
        if not state.isPlaying:
            await state.play_next(ctx)

@bot.command()
async def stop(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()

@bot.command(name='queue')
async def list_songs(ctx):
    state = get_state(ctx)
    await state.list_songs()

bot.run(token=token, log_handler=handler)