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
from PIL import Image

with open("srapi.txt", "r") as f:
	lines = f.readlines()
	sr_api_key = lines[0].strip()

with open("token.txt", "r") as f:
	lines = f.readlines()
	token = lines[0].strip()

upsince = datetime.datetime.now()

logchannel = None
intents = discord.Intents.default()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(
	"!!"), intents=intents, chunk_guilds_at_startup=False)
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
		embed = discord.Embed(
			title="My commands!", description="Made by ThatOneCalculator and Pixer!", color=0x976BE1)
		embed.add_field(name="`!!ping`", value="Pings the bot")
		embed.add_field(name="`!!literallynobot`",
						value="Directs you to ThatOneCalculator's main bot LiterallyNoBot")
		embed.add_field(name="`!!eject <@person>`", value="Sees if someone is the imposter!")
		embed.add_field(name="`!!dumpy (height) (dither)`",
						value="Makes a dumpy gif from whatever image you post or whatever image was the latest in chat. Both height and dither are optional. Height is a number between 2 and 35, the default is 10. Add \"dither\" to the end to dither the image, which usually looks better with higher resolution images, and worse with lower resolution images.")
		try:
			await ctx.send(embed=embed,
				buttons=[
					Button(style=ButtonStyle.URL, label="Invite to your server!",
							url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

					Button(style=ButtonStyle.URL, label="See my GitHub!",
							url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),
				],
			)
		except:
			await ctx.send("Hey! I need the `Embed Links` and the `Attach Files` permission in this channel to work properly.")

	@commands.command()
	async def literallynobot(self, ctx):
		await ctx.send("https://top.gg/bot/646156214237003777")

	@commands.command()
	async def invite(self, ctx):
		await ctx.send("https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")


def blocking(messageid, number, dither):
	ditheropt = "true" if dither else "false"
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-1.6.0-all.jar {number} {ditheropt} attach_{messageid}.png {messageid}")
	subprocess.check_call(cmd)


def rmblocking(messageid):
	rmcmd = shlex.split(f"rm ./attach_{messageid}.png ./dumpy{messageid}.gif")
	subprocess.check_call(rmcmd)

async def asyncimage(url, filename):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			f = await aiofiles.open(filename, mode="wb")
			await f.write(await resp.read())
			await f.close()
	img = Image.open(filename)
	file = discord.File(filename, filename=filename)
	return file

class TheStuff(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.update_status.start()

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["sus", "imposter", "crewmate"])
	async def eject(self, ctx, *, victim: typing.Union[discord.Member, str] = ""):
		if type(victim) != discord.Member:
			return await ctx.send("You need to mention someone!")
		imposter = random.choice(["true", "false"])
		url = str(victim.avatar_url_as(format="png"))
		async with ctx.typing():
			file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={victim.name[0:30]}&imposter={imposter}", f"eject{ctx.message.id}.gif")
			await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
				file=file,
				buttons=[
					Button(style=ButtonStyle.URL, label="Invite to your server!",
							url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

					Button(style=ButtonStyle.URL, label="See my GitHub!",
							url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),
				]
			)
		rm = shlex.split(f"rm ./eject{ctx.message.id}.gif")
		subprocess.check_call(rm)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["twerk", "amogus"])
	async def dumpy(self, ctx, number: typing.Union[discord.Member, int, str] = 10, ditheropt: str = "false"):
		if ditheropt == "dither":
			dither = True
		else:
			dither = False
		loop = asyncio.get_running_loop()
		messageid = str(ctx.message.id)
		if type(number) != int:
			number = 10
		if number > 35 or number < 2:
			return await ctx.send("Number must be between 2 and 35! Defaults to 10.")
		async with ctx.typing():
			if len(ctx.message.attachments) > 0:
				await ctx.message.attachments[0].save(f"attach_{messageid}.png")
				if dither:
					await loop.run_in_executor(None, blocking, messageid, number, True)
				else:
					await loop.run_in_executor(None, blocking, messageid, number, False)
				filename = f"dumpy{messageid}.gif"
				try:
					await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
						file=discord.File(filename, filename=filename),
						buttons=[
							Button(style=ButtonStyle.URL, label="Invite to your server!",
								url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

							Button(style=ButtonStyle.URL, label="See my GitHub!",
								url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),
						]
					)
				except:
					pass
					# await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
				await loop.run_in_executor(None, rmblocking, messageid)
			else:
				sus=True
				try:
					async for message in ctx.channel.history(limit=20):
						if len(message.attachments) > 0 and sus and message.author != ctx.guild.me:
							await message.attachments[0].save(f"attach_{messageid}.png")
							if dither:
								await loop.run_in_executor(None, blocking, messageid, number, True)
							else:
								await loop.run_in_executor(None, blocking, messageid, number, False)
							filename=f"dumpy{messageid}.gif"
							try:
								await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
									file=discord.File(filename, filename=filename),
									buttons=[
										Button(style=ButtonStyle.URL, label="Invite to your server!",
												url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

										Button(style=ButtonStyle.URL, label="See my GitHub!",
												url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),
									]
								)
							except:
								pass
								# await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
							sus=False
							await loop.run_in_executor(None, rmblocking, messageid)
				except Exception as e:
					print(e)
					await ctx.send(e)
					return await ctx.send("I couldn't find an image, you sussy baka!")


	@ commands.command(name="ping")
	async def ping(self, ctx):
		shardscounter = []
		for guild in self.bot.guilds:
			if guild.shard_id not in shardscounter:
				shardscounter.append(guild.shard_id)
		shards = []
		for i in shardscounter:
			shards.append(self.bot.get_shard(i))
		allmembers=0
		large = 0
		for guild in self.bot.guilds:
			allmembers += guild.member_count
			if guild.large:
				large += 1
		ping=await ctx.send(f":ping_pong: Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.")
		beforeping=datetime.datetime.now()
		await ping.edit(content="Pinging!")
		afterping=datetime.datetime.now()
		pingdiff=afterping - beforeping
		pingdiffms=pingdiff.microseconds / 1000
		uptime=afterping - upsince
		await ping.edit(content=f"🏓 Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.\n☎️ API latency is {str(round((pingdiffms),2))} milliseconds.\n:coffee: I have been up for {humanfriendly.format_timespan(uptime)}.\n🔮 This guild is on shard {ctx.guild.shard_id}, with a total of {len(shards)} shards.\n\nI am in {str(len(self.bot.guilds))} servers ({large} of which are large) with a total of {allmembers} people.")

	@ tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"!!help on {len(self.bot.guilds)} servers!"))


bot.remove_command("help")
bot.add_cog(HelpCommand(bot))
bot.add_cog(TheStuff(bot))
bot.add_cog(CommandErrorHandler(bot))


@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
