import discord
from discord.ext import commands, tasks
import os
import random
import asyncio

VOICE_CHANNEL_ID = 1346808740288135244  # Replace with your VC ID
AUDIO_FOLDER = "./audio"
FFMPEG_PATH = r"C:\Users\User\Desktop\ffmpeg-2025-08-07-git-fa458c7243-full_build\bin\ffmpeg.exe"

MIN_WAIT = 150
MAX_WAIT = 180

class OrdisVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc: discord.VoiceClient = None
        self.connected_once = False  # Track if we've connected successfully at least once

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready.")
        await asyncio.sleep(2)  # small delay to avoid race conditions
        await self.connect_once()

        if self.vc and self.vc.is_connected():
            if not self.play_random_lines.is_running():
                self.play_random_lines.start()

    async def connect_once(self):
        """Connects only if not already connected, with retry handling."""
        if self.vc and self.vc.is_connected():
            return

        channel = self.bot.get_channel(VOICE_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            print("❌ Voice channel not found.")
            return

        try:
            self.vc = await channel.connect(timeout=15, reconnect=True)
            print(f"✅ Connected to VC: {channel.name}")
            self.connected_once = True
        except asyncio.TimeoutError:
            print("⏳ Timed out connecting to voice channel, will retry later.")
            self.vc = None
        except discord.ClientException:
            # Already connected somewhere — reuse existing
            self.vc = discord.utils.get(self.bot.voice_clients, guild=channel.guild)
            if self.vc:
                print("♻ Reusing existing voice connection.")

    @tasks.loop(seconds=1)
    async def play_random_lines(self):
        """Loop to play audio with random delays."""
        if not self.vc or not self.vc.is_connected():
            await self.connect_once()
            if not self.vc:
                await asyncio.sleep(10)  # backoff if still not connected
                return

        if self.vc.is_playing():
            return  # wait for current audio to finish

        files = [f for f in os.listdir(AUDIO_FOLDER) if f.lower().endswith(".mp3")]
        if not files:
            print("⚠ No audio files found.")
            await asyncio.sleep(10)
            return

        chosen_file = random.choice(files)
        file_path = os.path.join(AUDIO_FOLDER, chosen_file)

        if not os.path.isfile(file_path):
            print(f"⚠ File not found: {file_path}")
            return

        print(f"▶ Playing: {chosen_file}")
        self.vc.play(
            discord.FFmpegPCMAudio(file_path, executable=FFMPEG_PATH),
            after=lambda e: print(f"Finished playing {chosen_file}" if not e else f"Error: {e}")
        )

        wait_time = random.randint(MIN_WAIT, MAX_WAIT)
        print(f"⏳ Waiting {wait_time} seconds before next line...")
        await asyncio.sleep(wait_time)

    @play_random_lines.before_loop
    async def before_loop(self):
        print("⏳ Waiting for bot to be ready before starting audio loop...")
        await self.bot.wait_until_ready()

        

async def setup(bot):
    await bot.add_cog(OrdisVoice(bot))
