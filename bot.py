import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

class Ordis(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f'Loaded cog: {filename[:-3]}')


bot = Ordis(command_prefix='!', intents=intents)
bot.remove_command('help')  # Remove default help command

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} is ONLINE (ID: {bot.user.id})')

    # channel_id = 1346808740288135241
    # channel = bot.get_channel(channel_id)
    # if channel is not None:
       # await channel.send(f'@here\n**System check complete! All systems online, sanity… questionable. Ready for orders, Operator!**')
    # else:
       # logging.error(f'Channel with ID {channel_id} not found.')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    else:
        logging.error(f'Error in command {ctx.command}: {error}')
        await ctx.send("An error occurred while processing your command.")


bot.run(TOKEN)