import asyncio
import datetime
import json
import os
import random
import shlex
import subprocess
import sys
import traceback
import typing
import urllib.parse
from os.path import exists
from typing import Any, Iterable, Tuple

import aiofiles
import aiohttp
import disnake as discord
import humanfriendly
import topgg
from async_timeout import timeout
from discord_components import (Button, ButtonStyle, DiscordComponents, InteractionType)
from disnake.ext import commands, tasks
from disputils import BotConfirmation, BotEmbedPaginator, BotMultipleChoice
from PIL import Image
from statcord import StatcordClient

with open("srapi.txt", "r") as f:
	lines = f.readlines()
	sr_api_key = lines[0].strip()

with open("token.txt", "r") as f:
	lines = f.readlines()
	token = lines[0].strip()

with open("topgg.txt", "r") as f:
	lines = f.readlines()
	topggtoken = lines[0].strip()

with open("statcord.txt", "r") as f:
	lines = f.readlines()
	statcordkey = lines[0].strip()

upsince = datetime.datetime.now()
version = "4.1.0"

intents = discord.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or("!!"),
	intents=intents,
	chunk_guilds_at_startup=False,
	sync_commands=True
)
ddb = DiscordComponents(bot)
bot.topggpy = topgg.DBLClient(
	bot, topggtoken, autopost=True, post_shard_count=True)
bot.statcord_client = StatcordClient(bot, statcordkey)

def promobuttons():
	return [
		[
			Button(
				style=ButtonStyle.URL,
				label="GitHub",
				emoji=bot.get_emoji(922251058527473784),
				url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"
			),

			Button(
				style=ButtonStyle.URL,
				label="Support server",
				emoji=bot.get_emoji(922251654869434448),
				url="https://discord.gg/VRawXXybvd"
			),

			Button(
				style=ButtonStyle.URL,
				label="Vote on top.gg!",
				emoji=bot.get_emoji(922252075667185716),
				url="https://top.gg/bot/847164104161361921/vote"
			)
		],
		Button(
			style=ButtonStyle.URL,
			label="Invite to your server!",
			emoji=bot.get_emoji(851566828596887554),
			url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands "
		)
	]

def blocking(messageid, mode, number, background):
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar --lines {number} --file attach_{messageid}.png --mode {mode} --extraoutput {messageid} {background}")
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


class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(inter, error):
		if hasattr(inter, 'on_error'):
			return
		ignored = (commands.CommandNotFound, commands.UserInputError)
		error = getattr(error, 'original', error)
		if isinstance(error, ignored):
			return
		elif isinstance(error, commands.DisabledCommand):
			return await inter.send(content=f'{inter.command} has been disabled.')
		elif isinstance(error, commands.NoPrivateMessage):
			try:
				return await inter.author.send(f'{inter.command} can not be used in Private Messages.')
			except:
				pass
		elif isinstance(error, commands.BadArgument):
			if inter.command.qualified_name == 'tag list':
				return await inter.send(content='I could not find that member. Please try again.')
		elif isinstance(error, commands.CommandOnCooldown):
			return await inter.send(content="You're on cooldown, you sussy baka!")
		print('Ignoring exception in command {}:'.format(
			inter.command), file=sys.stderr)
		traceback.print_exception(
			type(error), error, error.__traceback__, file=sys.stderr)


class Tasks(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.update_stats.start()
		self.update_status.start()
		self.update_channels.start()

	@tasks.loop(minutes=30.0)
	async def update_stats(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(5)
		try:
			await self.bot.topggpy.post_guild_count()
		except Exception as e:
			print(f"\nServer update on top.gg failed\n{e}\n")

	@tasks.loop(minutes=5)
	async def update_channels(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(10)
		botinfo = await self.bot.topggpy.get_bot_info()
		votes = botinfo["monthly_points"]
		allmembers = 0
		try:
			for guild in self.bot.guilds:
				try:
					allmembers += guild.member_count
				except:
					pass
		except:
			pass
		guild = self.bot.get_guild(849516341933506561)
		await guild.get_channel(861384764383428658).edit(name=f"Servers: {len(bot.guilds):,}")
		await guild.get_channel(861384798429380618).edit(name=f"Users: {allmembers:,}")
		await guild.get_channel(861384904780808222).edit(name=f"Votes: {int(votes):,}")

	@tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help on {len(bot.guilds):,} servers!"))


@commands.slash_command(description="Check the number of votes on top.gg, and vote for the bot.")
async def votes(inter: discord.ApplicationCommandInteraction):
	botinfo = await bot.topggpy.get_bot_info()
	votes = botinfo["monthly_points"]
	allvotes = botinfo["points"]
	await inter.send(content=f"I have {int(votes):,} mothly votes and {int(allvotes):,} all-time votes on top.gg!",
					components=[
						Button(
							style=ButtonStyle.URL,
							label="Vote on top.gg!",
							emoji=bot.get_emoji(922252075667185716),
							url="https://top.gg/bot/847164104161361921/vote"
						)
					]
					)

@commands.slash_command(description="Brings you to the bot's statcord page.")
async def statcord(inter: discord.ApplicationCommandInteraction):
	await inter.send(content="https://statcord.com/bot/847164104161361921")

@commands.cooldown(1, 10, commands.BucketType.user)
@commands.slash_command(description="Sees if someone is the impostor!")
async def eject(inter: discord.ApplicationCommandInteraction, person: discord.Member, impostor: str=commands.Param(choices=["Random", "True", "False"])):
	if impostor == "Random":
		outcome = random.choice(["true", "false"])
	elif impostor ==  "True":
		outcome = "true"
	elif impostor == "False":
		outcome = "false"
	url = str(person.avatar_url_as(format="png"))
	file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={person.name[0:35]}&imposter={outcome}", f"eject{inter.id}.gif")
	await inter.send(
		content="Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
		file=file,
		components=promobuttons()
	)
	rm = shlex.split(f"bash -c 'rm ./eject{inter.id}.gif'")
	subprocess.check_call(rm)

@commands.cooldown(1, 5, commands.BucketType.user)
@commands.slash_command(description="Writes something out, but sus.")
async def text(inter: discord.ApplicationCommandInteraction, text: str):
	mytext = urllib.parse.quote(text).upper()
	file = await asyncimage(f"https://img.dafont.com/preview.php?text={mytext}&ttf=among_us0&ext=1&size=57&psize=m&y=58", "text.png")
	await inter.send(
		content="Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
		file=file,
		components=promobuttons()
	)

@commands.cooldown(1, 15, commands.BucketType.user)
@commands.slash_command(description="Makes a tall sussy impostor!")
async def tall(inter: discord.ApplicationCommandInteraction, number: int):
	if number == None or type(number) != int:
		number = 0
	if number > 20:
		return await inter.send(content="That's taller than 20, you sussy baka!")
	lb = "\n"
	await inter.send(f"<:tallamongus_1:853680242124259338>\n{('<:tallamongus_2:853680316110602260>' + lb) * number}<:tallamongus_3:853680372554268702>")

@commands.cooldown(1, 15, commands.BucketType.user)
@commands.slash_command(description="Set a custom background image for `/dumpy` (and subsequent commands. Run `/background delete` to remove your current background, run `/background color` for a solid color, `/background #AAAAAA` for a custom color background, `/background flag` for pride flags (gay, lesbian, trans, etc and run `/background` and attach an image for a custom image as a background.")
async def background(inter: discord.ApplicationCommandInteraction, bg_choice: str = None):
	if bg_choice != None:
		bg_choice = bg_choice.lower()
		if bg_choice in ["delete", "default", "remove", "gray", "grey"]:
			if exists(f"custom_bgs/background_{inter.author.id}.png"):
				rmcmd = shlex.split(
					f"bash -c 'rm custom_bgs/background_{inter.author.id}.png'")
				subprocess.check_call(rmcmd)
				return await inter.send(content="Your background has been deleted!")
		elif bg_choice.startswith("#"):
			if len(bg_choice) != 7:
				return await inter.send(content="Invalid length! Example: `#0ab32c`")
			await asyncimage(f"https://some-random-api.ml/canvas/colorviewer?key={sr_api_key}&hex={argument[1:]}", f"custom_bgs/background_{inter.author.id}.png")
			return await inter.send(content="Set your background!")
		else:
			if exists(f"backgrounds/{bg_choice}.png"):
				cpcmd = shlex.split(
					f"bash -c 'cp ./backgrounds/{bg_choice}.png ./custom_bgs/background_{inter.author.id}.png'")
				subprocess.check_call(cpcmd)
				return await inter.send(content="Set your background!")
			else:
				return await inter.send(content="I couldn't find that background preset! Options avaliable:\n- `delete`/`remove`/`default`\n- Basics (ex `black`/`white`/`transparent`)\n- Basic colors (ex `red`, `orange`, `yellow`)\n- Custom colors (hex, start with `#`)\n- Pride flags (ex `gay`, `lesbian`, `vincian`, `bisexual`, `transgender`)\n- Custom images (upload image with no argument)")
	elif len(inter) > 0:
		try:
			await inter.attachments[0].save(f"custom_bgs/background_{inter.author.id}.png")
		except Exception as e:
			await inter.send(content=f"```{e}```")
		return await inter.send(content="Saved your background!")

@commands.cooldown(1, 5, commands.BucketType.user)
@commands.slash_command(description="Makes a dumpy gif from whatever image you want! By default, it will use the last image in chat. Height can be a number between 1 and 40, the default is 10. If you add `person`, it will use that person's avatar. If you add `image_url`, it will use the image in that url (must be jpg or png).")
async def dumpy(inter: discord.ApplicationCommandInteraction, mode: str=commands.Param(choices=["default", "furry", "sans", "isaac", "bounce"]), number: int = 10, person: discord.Member = None, image_url: str = None):
	await bot.wait_until_ready()
	loop = asyncio.get_running_loop()
	messageid = str(inter.id)
	if type(number) != int:
		number = 10
	if number > 35 and number < 41:
		msg = await inter.send("Validating vote... <:sustopgg:922252075667185716>")
		voted = await bot.topggpy.get_user_vote(inter.author.id)
		await asyncio.sleep(0.2)
		await msg.delete()
		if not voted and inter.author.id != 454847501787463680:
			return await inter.send(content=f"The limit for non-voters is 35! {inter.author.mention}, vote on top.gg to increase it to 40!\nAll you need to do is sign in with Discord and click the button. Please note that votes reset every 12 hours.\nhttps://top.gg/bot/847164104161361921/vote")
	if number > 40 or number < 1:
		return await inter.send(content="Number must be between 1 and 35 (40 if you vote!) Defaults to 10.",
								components=[
									Button(
										style=ButtonStyle.URL,
										label="Vote on top.gg!",
										emoji=bot.get_emoji(922252075667185716),
										url="https://top.gg/bot/847164104161361921/vote"
									)
								])
	if person != None:
		await asyncimage(str(person.avatar_url_as(format='png', size=128)), f"attach_{messageid}.png")
	elif image_url != None:
		await asyncimage(image_url, f"attach_{messageid}.png" )
	else:
		sus = True
		try:
			async for message in inter.channel.history(limit=20):
				if len(message.attachments) > 0 and sus and message.author != inter.guild.me:
					await message.attachments[0].save(f"attach_{messageid}.png")
					sus = False
				elif len(message.embeds) > 0 and message.author != inter.guild.me:
					await asyncimage(message.embeds[0].url, f"attach_{messageid}.png")
					sus = False
		except Exception as e:
			return await inter.send(content="I couldn't find an image, you sussy baka!")
	await asyncio.sleep(0.1)
	img = Image.open(f"attach_{messageid}.png")
	if img.height / img.width <= 0.05:
		subprocess.check_call(shlex.split(
			f"bash -c 'rm ./attach_{messageid}.png'"))
		return await inter.send(content="This image is way too long, you're the impostor!")
	background = f"--background custom_bgs/background_{inter.author.id}.png" if exists(
		f"custom_bgs/background_{inter.author.id}.png") else ""
	await loop.run_in_executor(None, blocking, messageid, mode, number, background)
	filename = f"dumpy{messageid}.gif"
	allmembers = 0
	for guild in bot.guilds:
		try:
			allmembers += guild.member_count
		except:
			pass
	try:
		await inter.send(content="Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
			file=discord.File(filename, filename=filename),
			components=promobuttons()
		)
		await inter.send(content=f"Remember to invite the bot to your server(s)! I'm trying to get to 50,000 servers, and I'm currently at {len(bot.guilds):,}!\n<https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands >",
						components=[
							Button(
								style=ButtonStyle.URL,
								label="Tap here!",
								emoji=bot.get_emoji(851566828596887554),
								url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands "
							)
						]
						)
	except:
		await inter.send(content="An error occurred! I might not have the permission `Attach Files` in this channel.")
	rmcmds = [
		shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"),
		shlex.split(f"bash -c 'rm ./dumpy{messageid}.gif'")
	]
	for i in rmcmds:
		subprocess.check_call(i)

@commands.slash_command(description="Gives some helpful information about the bot.")
async def info(inter: discord.ApplicationCommandInteraction):
	botinfo = await bot.topggpy.get_bot_info()
	votes = botinfo["monthly_points"]
	shardscounter = []
	for guild in bot.guilds:
		if guild.shard_id not in shardscounter:
			shardscounter.append(guild.shard_id)
	shards = []
	for i in shardscounter:
		shards.append(bot.get_shard(i))
	allmembers = 0
	for guild in bot.guilds:
		try:
			allmembers += guild.member_count
		except:
			pass
	beforeping = datetime.datetime.now()
	ping = await inter.send(f"Give me a second, you sussy impostor...")
	afterping = datetime.datetime.now()
	pingdiff = afterping - beforeping
	pingdiffms = pingdiff.microseconds / 1000
	uptime = afterping - upsince
	embed = discord.Embed(
		title="Among Us Dumpy Bot",
		description="Made by ThatOneCalculator#0001 and pixer415#8145! `()` = optional, `<>` = mandatory.",
		color=0x976BE1,
		url="https://dumpy.t1c.dev/"
	)
	embed.add_field(
		name="🤔 How to use",
		text=f"Just type `/`, and navigate to Among Us Dumpy Bot to see all the commands!",
		inline=False
	)
	embed.add_field(
		name="💁 Creators",
		text=f"ThatOneCalculator#0001 and pixer415#8145.",
		inline=False
	)
	embed.add_field(
		name="🏓 Ping",
		text=f"Bot latency is {str(round((bot.latency * 1000),2))} milliseconds. API latency is {str(round((pingdiffms),2))} milliseconds.",
		inline=False
	)
	embed.add_field(
		name="☕ Uptime",
		text=f"I have been up for {humanfriendly.format_timespan(uptime)}.",
		inline=False
	)
	embed.add_field(
		name="🔮 Shards",
		text=f"This guild is on shard {inter.guild.shard_id}, with a total of {len(shards)} shards. Type `/shards` for more info.",
		inline=False
	)
	embed.add_field(
		name="👪 Bot stats",
		text=f"I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.",
		inline=False
	)
	embed.add_field(
		name="📈 Votes",
		text=f"I have {int(votes):,} monthly votes on top.gg. Type `/votes` for more info.",
		inline=False
	)
	embed.add_field(
		name="🧑‍💻 Version",
		text=f"I am on jar version {version}. This bot uses disnake. Both the bot and the jar are licensed under the A-GPLv3 code license. See the GitHub for more info.",
		inline=False
	)
	await ping.edit(content=None, embed=embed, components=promobuttons())

@commands.slash_command(description="Shows all bot shards.")
async def shards(inter: discord.ApplicationCommandInteraction):
	shardscounter = []
	allmembers = 0
	for guild in bot.guilds:
		if guild.shard_id not in shardscounter:
			shardscounter.append(guild.shard_id)
		try:
			allmembers += guild.member_count
		except:
			pass
	shards = []
	for i in shardscounter:
		shards.append(bot.get_shard(i))
	embedlist = []
	totpings = []
	closedcount = 0
	count = 0
	embed = discord.Embed(title=f"Bot shards")
	for i in shards:
		gcount = 0
		mcount = 0
		for j in bot.guilds:
			if j.shard_id == i.id:
				gcount += 1
				mcount += j.member_count
		if count % 9 == 0 and count != 0:
			embedlist.append(embed)
			embed = discord.Embed(title=f"Bot shards:")
		count += 1
		totpings.append(round((i.latency * 1000), 2))
		if i.is_closed():
			closedcount += 1
		embed.add_field(
			name=f"Shard {i.id}", value=f"Guilds: {gcount}, Members: {mcount}, Status: {'Down' if i.is_closed() else 'Ready'}, Ping: {round((i.latency * 1000),2)}")
		if count == len(shards):
			embedlist.append(embed)
	shardpaginator = BotEmbedPaginator(ctx, embedlist)
	staticembed = discord.Embed(
		title="Total", description=f"Guilds: {len(bot.guilds)}, Members: {allmembers}, Shards down: {closedcount}, Average ping: {round(sum(totpings)/len(totpings),2)}")
	await inter.send(embed=staticembed)
	await shardpaginator.run()


bot.remove_command("help")
bot.add_cog(Tasks(bot))
bot.add_cog(CommandErrorHandler(bot))


@bot.event
async def on_message(message):
	if message.guild == None and message.author.bot == False:
		return await message.channel.send("Looks like you're trying to use this command in a DM! You need to invite me to a server to use my commands.\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands ")
	if message.content.startswith("!!"):
		return await message.channel.send("I have moved to slash commands! Type `/` and select me to get started. All commands are the same, but they start with `/` instead of `!!`. You can also type `/info` for more info.\n\nIf you do not see slash commands, ask a server administrator or the server owner to click this link to reinvite the bot with slash command permissions: https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands")
	# elif (message.channel.topic != None and message.channel.topic.find("nodumpy") != -1) and message.content.startswith("!!"):
	# 	return await message.channel.send("**Commands have been disabled in this channel.**")
	await bot.process_commands(message)


@bot.event
async def on_command(ctx):
	api.command_run(ctx)


@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
