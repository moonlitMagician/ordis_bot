import discord
from discord.ext import commands, tasks
import logging
import random

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = [
            "Ordis is hap - ***angry***. Hmm, I may require maintenance after all.",
            "Do you remember the Old War, Operator? Ordis seems to have... misplaced those memories.",
            "I've been thinking, Operator... I thought you'd want to know.",
            "Operator, were you visualizing a bloody battle? -***Me too!***",
            "Ordis has been counting stars, Operator. All accounted for."
        ]
        self.users = [244753424128802816, #dev id,
                      1257805396454670387, #test id
                      1257870008760012820] #test id
        self.Random.start()

    @tasks.loop(seconds=60) #loops every 60 seconds 
    async def Random(self):
        if random.random() < 0.2: # 20% chance to send a message
            
            channel_id = 1258050256973729803
            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                message = random.choice(self.messages)
                user_id = random.choice(self.users)
                user_mention = f"<@{user_id}>"
                await channel.send(f"{user_mention}{message}")
                logging.info(f'Sent random message: "{message}" to channel {channel_id} mentioning user {user_id}')
            else:
                logging.error(f'Channel with ID {channel_id} not found.')
    
    
async def setup(bot):
    await bot.add_cog(Random(bot))
    logging.info("Random cog has been loaded.")