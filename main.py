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
def get_state(guild_id):
    if guild_id not in states:
        states[guild_id] = server_state.ServerState()
    return states[guild_id]

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
async def play(ctx, url, position=-1):
    if(ctx.author.voice):
        voice_ch = ctx.message.author.voice.channel
        if not ctx.voice_client:
            await voice_ch.connect()
        state = get_state(ctx.guild.id)
        state.add_song(url, position)
        if not state.isPlaying:
            state.play_next(ctx)
        

@bot.command(pass_context = True)
async def stop(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()

bot.run(token=token, log_handler=handler)