import discord
from discord.ext import commands
import requests
import logging
import urllib.parse
import random



class Useful(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Ordis Help Menu",
            description="Here are some commands you can use, Operator!",
            color=discord.Color.blue()
        )
        embed.add_field(name="!archon", value="Get information about the current Archon Hunt.", inline=False)
        embed.add_field(name="!voidTrader", value="Check if Baro Ki'Teer is currently active.", inline=False)
        embed.add_field(name="!status", value="Get the current status of various Warframe cycles.", inline=False)
        embed.add_field(name="!warframe <name>", value="Get information about a specific Warframe.", inline=False)
        embed.add_field(name="!market <item name>", value="Get market orders for a specific item.", inline=False)
        embed.set_footer(text="Ordis is pleased to assist you, Operator!")
        
        await ctx.send(embed=embed)

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

    @commands.command(name='market')
    async def market(self, ctx, *, item_name: str):
        slug_item_name = item_name.strip().lower().replace(" ", "_")
        url = f"https://api.warframe.market/v1/items/{slug_item_name}/orders?include=item"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                await ctx.send(f"❌ Could not find item `{item_name}` or API error.")
                return

            data = response.json()
            orders = data.get("payload", {}).get("orders", [])
            if not orders:
                await ctx.send(f"No orders found for `{item_name}`.")
                return

            # Filter sell orders AND only sellers who are online and orders visible
            sell_orders_online = [
                o for o in orders
                if o.get("order_type") == "sell" and o.get("visible", False) and o.get("user", {}).get("status") == "online"
            ]
            if not sell_orders_online:
                await ctx.send(f"No active sell orders found for `{item_name}` from online sellers.")
                return

            # Sort by lowest platinum price
            sell_orders_online.sort(key=lambda o: o.get("platinum", 999999))

            embed = discord.Embed(
                title=f"Sell Orders for {slug_item_name.replace('_', ' ').title()} (Online Sellers Only)",
                color=discord.Color.blurple()
            )

            for order in sell_orders_online[:5]:
                user = order.get("user", {})
                seller = user.get("ingame_name", "Unknown Seller")
                price = order.get("platinum", 0)
                quantity = order.get("quantity", 0)
                last_seen = user.get("last_seen", "Unknown time")
                platform = user.get("platform", "Unknown")
                status = user.get("status", "offline").capitalize()

                embed.add_field(
                    name=f"{seller} ({platform}, {status})",
                    value=f"Price: {price} Platinum\nQuantity: {quantity}\nLast Seen: {last_seen}",
                    inline=False
                )

            await ctx.send(embed=embed)

        except requests.RequestException as e:
            logging.error(f"Market API request failed: {e}")
            await ctx.send("Error: Could not retrieve data from Warframe Market API.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            await ctx.send("An unexpected error occurred while processing your request.")


async def setup(bot):
    await bot.add_cog(Useful(bot))
    logging.info("Useful cog has been loaded.")
