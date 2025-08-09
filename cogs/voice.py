import discord
from discord.ext import commands, tasks
import os
import random
import asyncio

VOICE_CHANNEL_ID = 1257806077085352111  # Replace with your VC ID
AUDIO_FOLDER = "./audio"  # Path to folder with MP3s
FFMPEG_PATH = r"C:\Users\User\Desktop\ffmpeg-2025-08-07-git-fa458c7243-full_build\bin\ffmpeg.exe"  # Full path to ffmpeg.exe

MIN_WAIT = 150  # Minimum wait time before playing next audio
MAX_WAIT = 180  # Maximum wait time before playing next audio

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
        if not channel or not isinstance(channel, discord.VoiceChannel):
            print("Voice channel not found or invalid.")
            return None

        voice_client = discord.utils.get(self.bot.voice_clients, guild=channel.guild)
        if voice_client:
            if voice_client.channel.id != channel.id:
                await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
        return voice_client

    @tasks.loop(seconds=1)
    async def play_random_lines(self):
        vc = await self.join_vc()
        if not vc:
            print("Failed to join voice channel")
            return

        # Wait until voice client is actually connected (add a timeout)
        for _ in range(10):  # wait up to 10 * 0.5 = 5 seconds
            if vc.is_connected():
                break
            await asyncio.sleep(0.5)
        else:
            print("Voice client did not connect in time.")
            return

        if vc.is_playing():
            return  # Wait until current audio is done

        files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith(".mp3")]
        if not files:
            print("⚠ No MP3 files found in folder.")
            return

        chosen_file = random.choice(files)
        file_path = os.path.join(AUDIO_FOLDER, chosen_file)

        print(f"Playing file: {file_path}")
        vc.play(discord.FFmpegPCMAudio(file_path, executable=FFMPEG_PATH))
        print(f"🎵 Ordis says: {chosen_file}")

        wait_time = random.randint(MIN_WAIT, MAX_WAIT)
        print(f"Waiting {wait_time} seconds before next audio...")
        await asyncio.sleep(wait_time)

    @play_random_lines.before_loop
    async def before_play_random_lines(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(OrdisVoice(bot))
