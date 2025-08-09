import discord
from discord.ext import commands
import requests
import logging
import random

class Useful(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='archon', aliases=['archonhunt'])
    async def archon_hunt(self,ctx):
        url = "https://api.warframestat.us/pc/archonHunt"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['active']:
                missions_text = ""
                for i, mission in enumerate(data.get("missions", []), start=1):
                    node = mission.get("node", "Unknown location")
                    mtype = mission.get("type", "Unknown type")
                    faction = mission.get("faction", "Unknown faction")
                    reward_items = mission.get("reward", {}).get("items", [])
                    reward_str = ", ".join(reward_items) if reward_items else "No reward listed"
                    
                    missions_text += (
                        f"**Mission {i}:** {node} | {mtype} |\n"
                        
                    )
                message = (
                f"**Ordis Tactical Briefing:**\n"
                f"Ah, Operator… the **Archon Hunt** is active! This will be dangerous… *and exciting!* \n\n"
                f"**Target:** {data.get('boss', 'Unknown Boss')}\n"
                f"**Reward Pool:** {data.get('rewardPool', 'Unknown')} — *tempting, isn’t it?*\n"
                f"**Time Remaining:** {data.get('eta', 'Unknown')}\n\n"
                f"{missions_text}"
                f"Stay alert, Operator. These Archons are not… *friendly.*"
            )
                
                await ctx.send(message)
            else:
                await ctx.send("Archon Hunt is not currently active.")
        else:
            await ctx.send("Failed to retrieve Archon Hunt status. Please try again later.")


    @commands.command(name='voidTrader', aliases=['baro'])
    async def void_trader(self, ctx):
        url = "https://api.warframestat.us/pc/voidTrader"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['active']:
                message = (
                f"**Ordis Transmission:**\n"
                f"Operator! The *mysterious* Baro Ki’Teer has docked at **{data['location']}**.\n"
                f"He will remain until **{data['activation']}** — so, try not to… spend *all* your Ducats at once.\n"
                f"*Ordis suggests you browse his wares before they mysteriously vanish... like my patience.*"
            )
                await ctx.send(message)
            else:
                await ctx.send("Baro Ki'Teer is not currently active.")
        else:
            await ctx.send("Failed to retrieve Baro Ki'Teer's status. Please try again later.")

    @commands.command(name='status')
    async def status(self, ctx):
        urls = {
            "Cambion": "https://api.warframestat.us/pc/cambionCycle",
            "Cetus": "https://api.warframestat.us/pc/cetusCycle",
            "Vallis": "https://api.warframestat.us/pc/vallisCycle",
        }

        try:
            data = {}
            for name, url in urls.items():
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    await ctx.send(f"Failed to get data for {name}. Please try again later.")
                    return
                data[name] = response.json()

            message = "**Ordis Status Report**\n"
            for name, cycle_data in data.items():
                message += (
                    f"**{name} Cycle:**\n"
                    f"> Current State: `{cycle_data['state']}`\n"
                    f"> Time Remaining: `{cycle_data['timeLeft']}`\n"
                    f"*Stay alert, Operator. Conditions may change rapidly.*\n\n"
                )

            await ctx.send(message.strip())

        except requests.RequestException as e:
            await ctx.send("Error fetching cycle statuses. Please try again later.")
            print(f"Request error: {e}")
        except Exception as e:
            await ctx.send("An unexpected error occurred.")
            print(f"Unexpected error: {e}")

    @commands.command(name='warframe', aliases=['wf', 'frame', 'warframeinfo'])
    async def warframe_info(self, ctx, *, frame_name: str):
        flavortextArr = [
            "Operator, observe closely... this Warframe is both a work of art *and* a weapon of unimaginable power.\n",
            "Ah! This Warframe — a masterpiece of Orokin engineering. Do try not to— bzzztt— break it.\n",
            "Every Warframe holds a story, Operator. This one’s tale is… classified. For now.\n",
            "They are not merely machines, Operator… they are extensions of your will… and occasionally, your *temper*.\n",
            "Ordis recommends keeping this Warframe in pristine condition. Not that you ever listen.\n",
            "Beautiful, deadly, and slightly intimidating — much like you, Operator.\n",
            "This Warframe radiates power. Or… perhaps that’s just a malfunctioning coolant line. I’ll check later.\n",
            "Orokin craftsmanship at its finest, Operator. And not a single *scratch*… yet.\n"
        ]

        """
        Get information about a specific Warframe.
        Example: !frameinfo Mesa
        """
        base_url = "https://api.warframestat.us/items"
        response = requests.get(base_url)
        chosenText = random.choice(flavortextArr)

        if response.status_code != 200:
            await ctx.send("❌ Failed to fetch Warframe data. Please try again later.")
            return

        data = response.json()

        # Search for the frame (case-insensitive)
        frame = next((f for f in data if f['name'].lower() == frame_name.lower()), None)

        if not frame:
            await ctx.send(f"⚠ No Warframe found with the name `{frame_name}`.")
            return

        # Build embed
        embed = discord.Embed(
            title=frame['name'],
            description=frame.get('description', 'No description available.'),
            color=discord.Color.blue(),
            url=frame.get('url')
        )

        embed.set_thumbnail(url=frame.get('thumbnail'))
        embed.add_field(name="Health", value=frame.get('health', 'Unknown'), inline=True)
        embed.add_field(name="Shield", value=frame.get('shield', 'Unknown'), inline=True)
        embed.add_field(name="Armor", value=frame.get('armor', 'Unknown'), inline=True)
        embed.add_field(name="Polarities", value=", ".join(frame.get('polarities', [])) or "None", inline=False)

        await ctx.send(content=chosenText, embed=embed)

        

async def setup(bot):
    await bot.add_cog(Useful(bot))
    logging.info("Useful cog has been loaded.")
