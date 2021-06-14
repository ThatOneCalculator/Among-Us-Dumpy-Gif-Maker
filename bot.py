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
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from PIL import Image

with open("srapi.txt", "r") as f:
	lines = f.readlines()
	sr_api_key = lines[0].strip()

with open("token.txt", "r") as f:
	lines = f.readlines()
	token = lines[0].strip()

upsince = datetime.datetime.now()
version = "1.7.2"

logchannel = None
intents = discord.Intents.default()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(
	"!!"), intents=intents, chunk_guilds_at_startup=False)
ddb = DiscordComponents(bot)
slash = SlashCommand(bot, sync_commands=True)


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
		elif isinstance(error, commands.CommandOnCooldown):
			return await ctx.send("You're on cooldown, you sussy baka!")
		print('Ignoring exception in command {}:'.format(
			ctx.command), file=sys.stderr)
		traceback.print_exception(
			type(error), error, error.__traceback__, file=sys.stderr)


class HelpCommand(commands.Cog):

	@commands.command(name="help")
	async def help_(self, ctx):
		embed = discord.Embed(
			title="My commands!", description="Made by ThatOneCalculator#1337 and Dsim64#8145!", color=0x976BE1)
		embed.add_field(name="`!!dumpy (height) (dither)`",
				  value="Makes a dumpy gif from whatever image you post or whatever image was the latest in chat. Both height and dither are optional. Height is a number between 2 and 35, the default is 10. Add \"dither\" to the end to dither the image, which usually looks better with higher resolution images, and worse with lower resolution images.", inline=False)
		embed.add_field(name="`!!eject <@person>`",
						value="Sees if someone is the imposter! You can also do `!!crewmate` and `!!imposter` to guarantee the output.")
		embed.add_field(name="`!!ping`", value="Pings the bot, and gives some information.")
		embed.add_field(name="`!!literallynobot`",
						value="Directs you to ThatOneCalculator's main bot LiterallyNoBot.")
		embed.add_field(name="Tips and tricks", value="- You can add `nodumpy` to a channel topic to disable the bot there.\n- If you need more lines, go to the GitHub and use the desktop version.", inline=False)
		embed.set_footer(
			text=f"Among Us Dumpy Bot version {version}. Licensed under the GPL-3. Thank you server boosters: AdminDolphin(OFFICIAL)#6542, shermy the cat#0002")
		try:
			await ctx.send(embed=embed,
				components=[
					[
						Button(style=ButtonStyle.URL, label="Invite to your server!",
								url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

						Button(style=ButtonStyle.URL, label="See my GitHub!",
								url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

						Button(style=ButtonStyle.URL, label="Join the support server!",
								url="https://discord.gg/VRawXXybvd")
					]
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

	@commands.command()
	async def support(self, ctx):
		await ctx.send("https://discord.gg/VRawXXybvd")


def blocking(messageid, number, dither):
	ditheropt = "true" if dither else "false"
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar {number} {ditheropt} attach_{messageid}.png {messageid}")
	subprocess.check_call(cmd)

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
	@commands.command(aliases=["sus"])
	async def eject(self, ctx, *, victim: typing.Union[discord.Member, str] = ""):
		if type(victim) != discord.Member:
			return await ctx.send("You need to mention someone!")
		imposter = random.choice(["true", "false"])
		url = str(victim.avatar_url_as(format="png"))
		async with ctx.typing():
			file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={victim.name[0:35]}&imposter={imposter}", f"eject{ctx.message.id}.gif")
			await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
							file=file,
							components=[
								[
									Button(style=ButtonStyle.URL, label="Invite to your server!",
										   url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

									Button(style=ButtonStyle.URL, label="See my GitHub!",
										   url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

							  		Button(style=ButtonStyle.URL, label="Join the support server!",
										   url="https://discord.gg/VRawXXybvd")
								]
							]
				  )
		rm = shlex.split(f"bash -c 'rm ./eject{ctx.message.id}.gif'")
		subprocess.check_call(rm)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["impostor"])
	async def imposter(self, ctx, *, victim: typing.Union[discord.Member, str] = ""):
		if type(victim) != discord.Member:
			return await ctx.send("You need to mention someone!")
		url = str(victim.avatar_url_as(format="png"))
		async with ctx.typing():
			file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={victim.name[0:35]}&imposter=true", f"eject{ctx.message.id}.gif")
			await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
				file=file,
				components=[
					[
						Button(style=ButtonStyle.URL, label="Invite to your server!",
								url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

						Button(style=ButtonStyle.URL, label="See my GitHub!",
								url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

						Button(style=ButtonStyle.URL, label="Join the support server!",
								url="https://discord.gg/VRawXXybvd")
					]
				]
			)
		rm = shlex.split(f"bash -c 'rm ./eject{ctx.message.id}.gif'")
		subprocess.check_call(rm)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command()
	async def crewmate(self, ctx, *, victim: typing.Union[discord.Member, str] = ""):
		if type(victim) != discord.Member:
			return await ctx.send("You need to mention someone!")
		url = str(victim.avatar_url_as(format="png"))
		async with ctx.typing():
			file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={victim.name[0:35]}&imposter=false", f"eject{ctx.message.id}.gif")
			await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
							file=file,
							components=[
								[
									Button(style=ButtonStyle.URL, label="Invite to your server!",
										   url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

									Button(style=ButtonStyle.URL, label="See my GitHub!",
										   url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

									Button(style=ButtonStyle.URL, label="Join the support server!",
											url="https://discord.gg/VRawXXybvd")
								]
							]
				  )
		rm = shlex.split(f"bash -c 'rm ./eject{ctx.message.id}.gif'")
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
				img = Image.open(f"attach_{messageid}.png")
				if img.height / img.width <= 0.05:
					subprocess.check_call(shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"))
					return await ctx.send("This image is way too long, you're the imposter!")
				if dither:
					await loop.run_in_executor(None, blocking, messageid, number, True)
				else:
					await loop.run_in_executor(None, blocking, messageid, number, False)
				filename = f"dumpy{messageid}.gif"
				try:
					await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
						file=discord.File(filename, filename=filename),
						components=[
							[
								Button(style=ButtonStyle.URL, label="Invite to your server!",
									url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

								Button(style=ButtonStyle.URL, label="See my GitHub!",
									url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

								Button(style=ButtonStyle.URL, label="Join the support server!",
									url="https://discord.gg/VRawXXybvd")
							]
						]
					)
				except:
					pass
					# await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
				rmcmds = [
					shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"),
					shlex.split(f"bash -c 'rm ./dumpy{messageid}.gif'")
				]
				for i in rmcmds:
					subprocess.check_call(i)
			else:
				sus=True
				try:
					async for message in ctx.channel.history(limit=20):
						if len(message.attachments) > 0 and sus and message.author != ctx.guild.me:
							await message.attachments[0].save(f"attach_{messageid}.png")
							img = Image.open(f"attach_{messageid}.png")
							if img.height / img.width <= 0.05:
								subprocess.check_call(shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"))
								return await ctx.send("This image is way too long, you're the imposter!")
							if dither:
								await loop.run_in_executor(None, blocking, messageid, number, True)
							else:
								await loop.run_in_executor(None, blocking, messageid, number, False)
							filename=f"dumpy{messageid}.gif"
							try:
								await ctx.send(f"{ctx.author.mention} Please leave a star on the GitHub, it's free and helps out a lot!",
									file=discord.File(filename, filename=filename),
									components=[
										[
											Button(style=ButtonStyle.URL, label="Invite to your server!",
													url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"),

											Button(style=ButtonStyle.URL, label="See my GitHub!",
													url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"),

											Button(style=ButtonStyle.URL, label="Join the support server!",
													url="https://discord.gg/VRawXXybvd")
										]
									]
								)
							except:
								pass
								# await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
							sus=False
							rmcmds = [
								shlex.split(
									f"bash -c 'rm ./attach_{messageid}.png'"),
								shlex.split(
									f"bash -c 'rm ./dumpy{messageid}.gif'")
							]
							for i in rmcmds:
								subprocess.check_call(i)
				except Exception as e:
					return await ctx.send("I couldn't find an image, you sussy baka!")

	@commands.command(name="ping")
	async def ping(self, ctx):
		shardscounter = []
		for guild in self.bot.guilds:
			if guild.shard_id not in shardscounter:
				shardscounter.append(guild.shard_id)
		shards = []
		for i in shardscounter:
			shards.append(self.bot.get_shard(i))
		allmembers=0
		for guild in self.bot.guilds:
			allmembers += guild.member_count
		ping=await ctx.send(f":ping_pong: Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.")
		beforeping=datetime.datetime.now()
		await ping.edit(content="Pinging!")
		afterping=datetime.datetime.now()
		pingdiff=afterping - beforeping
		pingdiffms=pingdiff.microseconds / 1000
		uptime=afterping - upsince
		await ping.edit(content=f"🏓 Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.\n☎️ API latency is {str(round((pingdiffms),2))} milliseconds.\n:coffee: I have been up for {humanfriendly.format_timespan(uptime)}.\n🔮 This guild is on shard {ctx.guild.shard_id}, with a total of {len(shards)} shards.\n\nI am in {str(len(self.bot.guilds))} servers with a total of {allmembers} people on version {version}.")

	@tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"!!help on {len(self.bot.guilds)} servers!"))
		# await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"New support server! | {len(self.bot.guilds)} servers!"))

bot.remove_command("help")
bot.add_cog(HelpCommand(bot))
bot.add_cog(TheStuff(bot))
bot.add_cog(CommandErrorHandler(bot))

@bot.event
async def on_message(message):
	if (message.channel.topic != None and message.channel.topic.find("nodumpy") != -1) and message.content.startswith("!!"):
		return await message.channel.send("**Commands have been disabled in this channel.**")
	await bot.process_commands(message)

@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
