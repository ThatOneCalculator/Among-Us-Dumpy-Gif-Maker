import asyncio
import codecs
import datetime
import time
import humanfriendly
import io
import itertools
import json
import logging
import math
import os
import pprint
import random
import re
import shlex
import shutil
import string
import subprocess
import sys
import threading
import traceback
import typing
import urllib.parse
import urllib.request

from io import StringIO
from typing import Any
from typing import Iterable
from typing import Tuple

import aiofiles
import aiohttp
import discord
import requests

from async_timeout import timeout
from discord import AsyncWebhookAdapter
from discord import RequestsWebhookAdapter
from discord import Webhook
from discord.ext import commands
from discord.ext import tasks
from discord_buttons import DiscordButton, Button, ButtonStyle, InteractionType

upsince = datetime.datetime.now()

logchannel = None
intents = discord.Intents.default()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(
	"!!"), intents=intents, chunk_guilds_at_startup=True)
ddb = DiscordButton(bot)


class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, 'on_error'):
			return
		ignored = (commands.CommandNotFound, commands.UserInputError)
		error = getattr(error, 'original', error)
		if isinstance(error, ignored):
			return
		elif isinstance(error, commands.DisabledCommand):
			return await ctx.send(f'{ctx.command} has been disabled.')
		elif isinstance(error, commands.NoPrivateMessage):
			try:
				return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
			except:
				pass
		elif isinstance(error, commands.BadArgument):
			if ctx.command.qualified_name == 'tag list':
				return await ctx.send('I could not find that member. Please try again.')
		print('Ignoring exception in command {}:'.format(
			ctx.command), file=sys.stderr)
		traceback.print_exception(
			type(error), error, error.__traceback__, file=sys.stderr)


class HelpCommand(commands.Cog):

	@commands.command(name="help")
	async def help_(self, ctx):
		await ctx.send(f"{ctx.author.mention} {ctx.guild.owner.mention} The main bot is now verified! Please invite that to your server!\n\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")

	@commands.command()
	async def literallynobot(self, ctx):
		await ctx.send("https://top.gg/bot/646156214237003777")

	@commands.command()
	async def invite(self, ctx):
		await ctx.send(f"{ctx.author.mention} {ctx.guild.owner.mention} The main bot is now verified! Please invite that to your server!\n\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")


def blocking(messageid, number, dither):
	ditheropt = "true" if dither else "false"
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-1.5.1-all.jar {number} {ditheropt} attach_{messageid}.png {messageid}")
	subprocess.check_call(cmd)


def rmblocking(messageid):
	rmcmd = shlex.split(f"rm ./attach_{messageid}.png ./dumpy{messageid}.gif")
	subprocess.check_call(rmcmd)


class TheStuff(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.update_status.start()

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["twerk", "amogus"])
	async def dumpy(self, ctx, number: typing.Union[discord.Member, int, str] = 10, ditheropt: str = "false"):
		await ctx.send(f"{ctx.author.mention} {ctx.guild.owner.mention} The main bot is now verified! Please invite that to your server!\n\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")

	@commands.command(name="ping")
	async def ping(self, ctx):
		allmembers = 0
		for guild in self.bot.guilds:
			allmembers += guild.member_count
		ping = await ctx.send(f":ping_pong: Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.")
		beforeping = datetime.datetime.now()
		await ping.edit(content="Pinging!")
		afterping = datetime.datetime.now()
		pingdiff = afterping - beforeping
		pingdiffms = pingdiff.microseconds / 1000
		uptime = afterping - upsince
		await ping.edit(content=f"🏓 Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.\n☎️ API latency is {str(round((pingdiffms),2))} milliseconds.\n:coffee: I have been up for {humanfriendly.format_timespan(uptime)}.\n\nI am in {str(len(self.bot.guilds))} servers with a total of {allmembers} people.")

	@tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"MAIN BOT NOW VERIFIED!"))


bot.remove_command("help")
bot.add_cog(HelpCommand(bot))
bot.add_cog(TheStuff(bot))
bot.add_cog(CommandErrorHandler(bot))


@bot.event
async def on_ready():
	print("Ready")
	for i in bot.guilds:
		try:
			await i.owner.send("The main bot is now verified! Please invite that to your server!\n\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")
		except:
			print(f"I couldn't dm server {i.id}'s owner {i.owner.name}/{i.owner.discriminator}")


def read_token():
	with open("token.txt", "r") as f:
		lines = f.readlines()
		return lines[0].strip()


bot.run(read_token())
