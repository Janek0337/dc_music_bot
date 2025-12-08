import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
command_character = '?'
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class HelpClass(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Available commands", color=discord.Color.dark_blue())
        embed.description = """
        Argument types:
            <mandatory argument>
            [optional argument]\n
        """
        all_commands = []
        for cog_commands in mapping.values():
            all_commands.extend(cog_commands)
            
        filtered_commands = await self.filter_commands(all_commands, sort=True)
        
        if filtered_commands:
            cmd_list = [
                f"`{self.context.clean_prefix}{cmd.name}` - {cmd.help or 'No description'}"
                for cmd in filtered_commands
            ]
            
            cmds_text = "\n".join(cmd_list)
            embed.description += cmds_text

        embed.set_footer(text=f"Type {self.context.clean_prefix}help <command> for details")
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Help for: {command.name}", 
            color=discord.Color.green()
        )
        embed.add_field(name="Description", value=command.help or "No description", inline=False)
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)
        
        channel = self.get_destination()
        await channel.send(embed=embed)

class BotLauncher(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('Music_Controller')

    async def on_ready(self):
        print("=====================")
        print("= BOT IS NOW ONLINE =")
        print("=====================")

bot = BotLauncher(
    command_prefix=command_character, 
    intents=intents, 
    help_command=HelpClass()
)

bot.run(token=token, log_handler=handler, log_level=logging.INFO)

'''
@bot.command(pass_context = True, name = 'helpme')
async def help(ctx):
    help_message = f"""
    **INFO**
        <arg> - mandatory argument
        [arg] - optional argument

    **COMMANDS**
        - {command_character}play <link/name> [index] - default index at the end of the queue
        - {command_character}skip - skip song
        - {command_character}stop - drop queue and disconnect
        - {command_character}queue [page] - lists 10 queue elements, defualt page = 1
        - {command_character}remove <pos> - removes queue element at *pos* position
        - {command_character}move <pos1> <pos2> - moves queue element from *pos1* to *pos2*
    """
    await ctx.send(help_message)
'''