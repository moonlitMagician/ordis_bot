import discord
from discord.ext import commands

class Debugging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Responds with 'Pong!'"""
        await ctx.send('Pong!')

async def setup(bot):
    await bot.add_cog(Debugging(bot))
    print("PingCog has been loaded.")