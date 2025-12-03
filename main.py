import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import audio_reader as AR

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

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
async def play(ctx, url):
    if(ctx.author.voice):
        voice_ch = ctx.message.author.voice.channel
        vc = await voice_ch.connect()
        
        stream_url = AR.play_music(url)
        if stream_url is None:
           pass
         
        ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
        }
        source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
    
        ctx.voice_client.play(source)

@bot.command(pass_context = True)
async def stop(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()

bot.run(token=token, log_handler=handler)