import disnake
from discord_components import (Button, ButtonStyle, DiscordComponents, InteractionType)
from disnake.ext import commands, tasks

with open("token.txt", "r") as f:
	lines = f.readlines()
	token = lines[0].strip()


intents = disnake.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or("!!"),
	intents=intents,
	chunk_guilds_at_startup=False
)


@commands.slash_command(description="Brings you to the bot's statcord page.")
async def statcord(inter: disnake.ApplicationCommandInteraction):
	await inter.send(content="https://statcord.com/bot/847164104161361921")

# bot.remove_command("help")

@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
