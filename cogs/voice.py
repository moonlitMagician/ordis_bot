import discord
from discord.ext import commands, tasks
import os
import random
import asyncio

VOICE_CHANNEL_ID = 1257806077085352111  # Replace with your VC ID
AUDIO_FOLDER = "./audio"  # Path to folder with MP3s

class OrdisVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.play_random_lines.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("OrdisVoice is ready!")
        # Ensure bot is connected to VC on startup
        await self.join_vc()

    async def join_vc(self):
        channel = self.bot.get_channel(VOICE_CHANNEL_ID)
        if channel and isinstance(channel, discord.VoiceChannel):
            if self.bot.voice_clients:
                await self.bot.voice_clients[0].move_to(channel)
            else:
                await channel.connect()

    @tasks.loop(seconds=60)  # check every 60s
    async def play_random_lines(self):
        """Plays a random MP3 at random intervals while bot is in VC."""
        await self.join_vc()  # Ensure we stay in VC

        if not self.bot.voice_clients:
            return

        vc = self.bot.voice_clients[0]
        if vc.is_playing():
            return  # wait until current audio is done

        # Pick random file from folder
        files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith(".mp3")]
        if not files:
            print("⚠ No MP3 files found in folder.")
            return

        chosen_file = random.choice(files)
        file_path = os.path.join(AUDIO_FOLDER, chosen_file)

        # Play the file
        vc.play(discord.FFmpegPCMAudio(file_path))
        print(f"🎵 Ordis says: {chosen_file}")

        # Wait a random time between lines (e.g. 30–90 seconds)
        await asyncio.sleep(random.randint(30, 90))

    @play_random_lines.before_loop
    async def before_play_random_lines(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(OrdisVoice(bot))
