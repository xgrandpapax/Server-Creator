import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import Button, View
import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.guild_messages = True

LOG_CHANNEL_NAME = "📜・admin-logs"

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, application_id="YOUR_APP_ID")

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# Define theme structures
themes = {
    "space": {
        "🌌・Cosmic Lounge": ["💫・chat", "🌠・memes", "🚀・bot-commands"],
        "🔭・Stellar Info": ["📡・black-holes", "🪐・planets", "☄・galaxies"]
    },
    "cottage": {
        "🌿・Forest": ["🍄・chat", "🌼・memes"],
        "🍵・Tea Time": ["🧁・recipes", "📚・book-talk"]
    }
}

async def log_admin_action(guild, user, command):
    log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        embed = discord.Embed(title="🔧 Admin Command Used",
                              description=f"**{user}** used `{command}`",
                              color=discord.Color.orange(),
                              timestamp=datetime.datetime.utcnow())
        await log_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Prefix command
@bot.command()
async def setup_theme(ctx, theme_name):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("You need admin permissions to use this command.")

    theme = themes.get(theme_name.lower())
    if not theme:
        return await ctx.send("Theme not found. Available: " + ", ".join(themes.keys()))

    await ctx.send(f"Setting up the **{theme_name}** theme...")

    for category_name, channels in theme.items():
        category = await ctx.guild.create_category(name=category_name)
        for channel_name in channels:
            await ctx.guild.create_text_channel(name=channel_name, category=category)

    await log_admin_action(ctx.guild, ctx.author, f"!setup_theme {theme_name}")
    await ctx.send(f"✅ Theme **{theme_name}** has been set up!")

# Slash command
@bot.tree.command(name="setup_theme", description="Set up a themed server structure")
@app_commands.describe(theme_name="Name of the theme to apply")
async def setup_theme_slash(interaction: Interaction, theme_name: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You need admin permissions to use this command.", ephemeral=True)

    theme = themes.get(theme_name.lower())
    if not theme:
        return await interaction.response.send_message("Theme not found. Available: " + ", ".join(themes.keys()), ephemeral=True)

    await interaction.response.send_message(f"Setting up the **{theme_name}** theme...", ephemeral=True)

    for category_name, channels in theme.items():
        category = await interaction.guild.create_category(name=category_name)
        for channel_name in channels:
            await interaction.guild.create_text_channel(name=channel_name, category=category)

    await log_admin_action(interaction.guild, interaction.user, f"/setup_theme {theme_name}")
    await interaction.followup.send(f"✅ Theme **{theme_name}** has been set up!", ephemeral=True)

# Embedded theme list with button
class ThemeView(View):
    def __init__(self):
        super().__init__()
        for theme in themes:
            self.add_item(Button(label=theme.title(), custom_id=theme))

@bot.command()
async def list_themes(ctx):
    embed = discord.Embed(title="Available Themes", description="Click a button below to auto-setup that theme!", color=0x7289da)
    await ctx.send(embed=embed, view=ThemeView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        theme_name = interaction.data["custom_id"]
        theme = themes.get(theme_name.lower())

        if not theme:
            return await interaction.response.send_message("Theme not found.", ephemeral=True)

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You need admin permissions to do this.", ephemeral=True)

        await interaction.response.send_message(f"Setting up the **{theme_name}** theme...", ephemeral=True)

        for category_name, channels in theme.items():
            category = await interaction.guild.create_category(name=category_name)
            for channel_name in channels:
                await interaction.guild.create_text_channel(name=channel_name, category=category)

        await log_admin_action(interaction.guild, interaction.user, f"Button click: {theme_name}")
        await interaction.followup.send(f"✅ Theme **{theme_name}** has been set up!", ephemeral=True)

# Replace with your bot token and application ID
bot.run("YOUR BOT TOKEN")
