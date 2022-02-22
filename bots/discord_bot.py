import asyncio
import datetime
import json
import os
import random
import subprocess
import sys
import traceback
import typing
import urllib.parse
from os.path import exists
from typing import Any, Iterable, Tuple

import aiofiles
import aiohttp
import disnake
import humanfriendly
import pymongo
import topgg
import validators
from async_timeout import timeout
from disnake.ext import commands, tasks
from dotenv import dotenv_values
from PIL import Image, ImageDraw, ImageFont
from statcord import StatcordClient

token = dotenv_values(".env")["DISCORD"]
sr_api_key = dotenv_values(".env")["SRAPI"]
topggtoken = dotenv_values(".env")["TOPGG"]
statcordkey = dotenv_values(".env")["STATCORD"]

upsince = datetime.datetime.now()
version = "4.2.1"

intents = disnake.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or("!!"),
	intents=intents,
	chunk_guilds_at_startup=False,
)
bot.topggpy = topgg.DBLClient(
	bot, topggtoken, autopost=True, post_shard_count=True)
bot.statcord_client = StatcordClient(bot, statcordkey)

mongoclient = pymongo.MongoClient()
db = mongoclient.among_us_dumpy_bot
guild_preferences = db.guild_preferences


def default_guild_preferences(guild_id: int):
	prefs = {
		"guild_id": guild_id,
		"show_ads": True,
		"disabled_channels": [],
		"blacklisted_members": []
	}
	if guild_preferences.find_one({"guild_id": guild_id}) == None:
		guild_preferences.insert_one(prefs)


def cannot_be_run(guild_id, channel_id, member_id):
	try:
		data = guild_preferences.find_one({"guild_id": guild_id})
		disabled_channels = data["disabled_channels"]
		blacklisted_members = data["blacklisted_members"]
		if channel_id in disabled_channels or member_id in blacklisted_members:
			return True
		return False
	except:
		return False


class PromoButtons(disnake.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(disnake.ui.Button(
			style=disnake.ButtonStyle.link,
			label="GitHub",
			emoji=bot.get_emoji(922251058527473784),
			url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker",
			row=0
		))
		self.add_item(disnake.ui.Button(
			style=disnake.ButtonStyle.link,
			label="Support server",
			emoji=bot.get_emoji(922251654869434448),
			url="https://discord.gg/VRawXXybvd",
			row=0
		))
		self.add_item(disnake.ui.Button(
			style=disnake.ButtonStyle.link,
			label="Vote on top.gg!",
			emoji=bot.get_emoji(922252075667185716),
			url="https://top.gg/bot/847164104161361921/vote",
			row=0
		))
		self.add_item(
			disnake.ui.Button(
				style=disnake.ButtonStyle.link,
				label="Invite to your server!",
				emoji=bot.get_emoji(851566828596887554),
				url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands",
				row=1
			))


async def ads(guild_id):
	try:
		if guild_preferences.find_one({"guild_id": guild_id})["show_ads"] == False:
			return None
	except:
		pass
	return PromoButtons()

async def asyncimage(url, filename):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			f = await aiofiles.open(filename, mode="wb")
			await f.write(await resp.read())
			await f.close()
	img = Image.open(filename)
	discord_file = disnake.File(filename, filename=filename)
	return discord_file

async def asyncrun(cmd):
	proc = await asyncio.create_subprocess_shell(
		cmd,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE)

	stdout, stderr = await proc.communicate()

	print(f"[{cmd!r} exited with {proc.returncode}]")
	if stdout:
		print(f"[stdout]\n{stdout.decode()}")
	if stderr:
		print(f"[stderr]\n{stderr.decode()}")

def draw_text(text: str, sussy: bool, filename: str, mode: str):
	if mode  == "transparent":
		background = (0, 0, 0, 0)
		foreground = (255, 255, 255, 255)
	elif mode  == "dark":
		background = (0, 0, 0, 255)
		foreground = (255, 255, 255, 255)
	elif mode == "light":
		background = (255, 255, 255, 255)
		foreground = (0, 0, 0, 255)
	font = ImageFont.truetype(f"fonts/{'amongsus' if sussy else 'amongus'}.ttf", 100)
	image = Image.new(mode="RGBA", size=font.getsize(text), color=background)
	draw = ImageDraw.Draw(image)
	draw.text((0, 0), text, font=font, fill=foreground)
	image.save(filename)
	discord_file = disnake.File(filename, filename=filename)
	return discord_file

class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(inter, error):
		if hasattr(inter, 'on_error'):
			return
		ignored = (commands.errors.CommandNotFound,
				   commands.errors.UserInputError)
		error = getattr(error, 'original', error)
		if isinstance(error, ignored):
			return
		elif isinstance(error, commands.errors.DisabledCommand):
			return await inter.send(content=f'{inter.command} has been disabled.')
		elif isinstance(error, commands.errors.NoPrivateMessage):
			try:
				return await inter.author.send(f'{inter.command} can not be used in Private Messages.')
			except:
				pass
		elif isinstance(error, commands.errors.BadArgument):
			if inter.command.qualified_name == 'tag list':
				return await inter.send(content='I could not find that member. Please try again.')
		elif isinstance(error, commands.errors.CommandOnCooldown):
			return await inter.send(content="You're on cooldown, you sussy baka!")
		print(f"Ignoring exception in command {inter.command}:", file=sys.stderr)
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
		await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"slash commands on {len(bot.guilds):,} servers!"))


@bot.slash_command()
async def statcord(inter: disnake.ApplicationCommandInteraction):
	"""Brings you to the bot's Statcord page"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	await inter.send(content="https://statcord.com/bot/847164104161361921")


@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command()
async def eject(inter: disnake.ApplicationCommandInteraction, person: disnake.Member, impostor: str = commands.Param(choices=["Random", "True", "False"])):
	"""Sees if someone is the impostor

	Parameters
	----------
	person: disnake.Member
		The person to eject
	impostor: str
		Whether the person was the impostor
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	await inter.response.defer()
	default_guild_preferences(inter.guild.id)
	if impostor == "Random":
		outcome = random.choice(["true", "false"])
	elif impostor == "True":
		outcome = "true"
	elif impostor == "False":
		outcome = "false"
	url = str(person.avatar.url)
	file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={person.name[0:35]}&imposter={outcome}", f"eject{inter.id}.gif")
	await inter.edit_original_message(
		content="Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
		file=file,
		view=await ads(inter.guild.id)
	)
	await asyncrun(f"bash -c 'rm ./eject{inter.id}.gif'")

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.slash_command()
async def text(
	inter: disnake.ApplicationCommandInteraction,
	text: str,
	sussy: bool = True,
	mode: str = commands.Param(default="dark", choices=["dark", "light", "transparent"])):
	"""Writes something out, but sus

	Parameters
	----------
	text: str
		The text to write out
	sussy:
		Whether the font is sussy or not
	mode: str
		The coloring of the text
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	loop = asyncio.get_running_loop()
	await inter.response.defer()
	default_guild_preferences(inter.guild.id)
	text = text.upper()
	file = await loop.run_in_executor(None, draw_text, text, sussy, f"text{inter.id}.png", mode)
	await inter.edit_original_message(
		content="Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
		file=file,
		view=await ads(inter.guild.id)
	)
	await asyncrun(f"bash -c 'rm ./text{inter.id}.png'")

@commands.cooldown(1, 15, commands.BucketType.user)
@bot.slash_command()
async def tall(
    inter: disnake.ApplicationCommandInteraction,
    height: int = commands.Range[1, 20]):
	"""Makes a tall sussy impostor

	Parameters
	----------
	height: int
		The height of the impostor
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	lb = "\n"
	await inter.send(f"<:tallamongus_1:853680242124259338>\n{('<:tallamongus_2:853680316110602260>' + lb) * height}<:tallamongus_3:853680372554268702>")


async def autocomplete_bg_choices(inter: disnake.ApplicationCommandInteraction, user_input: str):
	CHOICES = [
		"transparent",
		"#",
		"gray",
		"white",
		"black",
		"red",
		"orange",
		"yellow",
		"green",
		"blue",
		"purple",
		"pink",
		"brown",
		"asexual",
		"aromantic",
		"agender",
		"bisexual",
		"gay",
		"lesbian",
		"nonbinary",
		"pansexual",
		"pride",
		"transgender",
		"vincian"
	]
	return [i for i in CHOICES if user_input.lower() in i]


@commands.cooldown(1, 15, commands.BucketType.user)
@bot.slash_command()
async def background(inter: disnake.ApplicationCommandInteraction, bg_choice: str = commands.Param(autocomplete=autocomplete_bg_choices)):
	"""Set background image for /dumpy.

	Parameters
	----------
	bg_choice: str
		Can be transparent, any color (a name like "red" or a hex color like "#FDFC26), or any pride flag.
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	await inter.response.defer()
	bg_choice = bg_choice.lower()
	if bg_choice in ["delete", "default", "remove", "gray", "grey"]:
		if exists(f"custom_bgs/background_{inter.author.id}.png"):
			await asyncrun(f"bash -c 'rm custom_bgs/background_{inter.author.id}.png'")
			return await inter.edit_original_message(content="Your background has been deleted!")
	elif bg_choice.startswith("#"):
		if len(bg_choice) != 7:
			return await inter.edit_original_message(content="Invalid length! Example: `#0ab32c`")
		await asyncimage(f"https://some-random-api.ml/canvas/colorviewer?key={sr_api_key}&hex={argument[1:]}", f"custom_bgs/background_{inter.author.id}.png")
		return await inter.edit_original_message(content="Set your background!")
	else:
		if exists(f"backgrounds/{bg_choice}.png"):
			await asyncrun(f"bash -c 'cp ./backgrounds/{bg_choice}.png ./custom_bgs/background_{inter.author.id}.png'")
			return await inter.edit_original_message(content="Set your background!")
		else:
			return await inter.edit_original_message(content="I couldn't find that background preset! Options avaliable:\n- `delete`/`remove`/`default`\n- Basics (ex `black`/`white`/`transparent`)\n- Basic colors (ex `red`, `orange`, `yellow`)\n- Custom colors (hex, start with `#`)\n- Pride flags (ex `gay`, `lesbian`, `vincian`, `bisexual`, `transgender`)\n- Custom images (upload image with no argument)")
	# elif len(inter.attachments) > 0:
	# 	try:
	# 		await inter.attachments[0].save(f"custom_bgs/background_{inter.author.id}.png")
	# 	except Exception as e:
	# 		await inter.edit_original_message(content=f"```{e}```")
	# 	return await inter.edit_original_message(content="Saved your background!")


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.slash_command()
async def dumpy(
		inter: disnake.ApplicationCommandInteraction,
		mode: str = commands.Param(
			default="default",
			choices=["default", "furry", "sans", "spamton", "isaac", "bounce"]),
		lines: int = commands.Param(default=10, ge=1, le=40),
		person: disnake.Member = None,
		#image_attachment: disnake.Attachment = None,
		image_url: str = None):
	"""Makes a Dumpy GIF! Uses the last image posted, but person/image_url overrides this.

	Parameters
	----------
	mode: str
		The character the GIF will be made with.
	lines: int
		The number of lines the GIF will have. Max 35 (40 for voters!)
	person: disnake.Member
		Overrides the target by making it the PFP of whoever the person is.
	image_attachment: disnake.Attachment
		Overrides the target by making it the attached image.
	image_url: str
		Overrides the target by making it the image of the url.
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	await bot.wait_until_ready()
	await inter.response.defer()
	default_guild_preferences(inter.guild.id)
	messageid = str(inter.id)
	if lines > 35:
		voted = await bot.topggpy.get_user_vote(inter.author.id)
		if not voted and inter.author.id != 454847501787463680:
			return await inter.edit_original_message(content=f"The limit for non-voters is 35! {inter.author.mention}, vote on top.gg to increase it to 40!\nAll you need to do is sign in with Discord and click the button. Please note that votes reset every 12 hours.\nhttps://top.gg/bot/847164104161361921/vote")
	if person != None and image_url == None:
		await asyncimage(person.avatar.url, f"attach_{messageid}.png")
	elif image_url != None:
		if not validators.url(image_url):
			return await inter.send("Invalid URL!")
		await asyncimage(image_url, f"attach_{messageid}.png")
	#elif image_attachment != None:
	#	await image_attachment.save(f"attach_{messageid}.png")
	else:
		sus = True
		try:
			async for message in inter.channel.history(limit=20):
				if len(message.attachments) > 0 and sus and message.author != inter.guild.me:
					await message.attachments[0].save(f"attach_{messageid}.png")
					sus = False
		except Exception as e:
			await inter.edit_original_message(content="I couldn't find an image, you sussy baka!")
			print(f"---\n\n{e}\n\n---")
			return
	await asyncio.sleep(0.4)
	img = Image.open(f"attach_{messageid}.png")
	if img.height / img.width <= 0.05:
		await asyncrun(f"bash -c 'rm ./attach_{messageid}.png'")
		return await inter.edit_original_message(content="This image is way too long, you're the impostor!")
	custom_bg_path = f"custom_bgs/background_{inter.author.id}.png"
	background = f"--background {custom_bg_path}" if exists(custom_bg_path) else ""
	await asyncio.sleep(0.2)
	await asyncrun(f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar --lines {lines} --file attach_{messageid}.png --mode {mode} --extraoutput {messageid} {background}")
	filename = f"dumpy{messageid}.gif"
	try:
		await inter.edit_original_message(
			content="Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
			file=disnake.File(filename, filename=filename),
			view=await ads(inter.guild.id)
		)
	except Exception as e:
		await inter.edit_original_message(content=f"An error occurred! I might not have the permission `Attach Files` in this channel.\n```\n{e}```")
	await asyncio.sleep(5)
	rmcmds = [
		f"bash -c 'rm ./attach_{messageid}.png'",
		f"bash -c 'rm ./dumpy{messageid}.gif'"
	]
	for i in rmcmds:
		await asyncrun(i)


@bot.slash_command()
async def blacklist(inter: disnake.ApplicationCommandInteraction, person: disnake.Member):
	"""Blacklist a server member from using the bot. Can also be used to unblacklist.

	Parameters
	----------
	person: disnake.Member
		The person to blacklist/unblacklist.
	"""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	if inter.author.guild_permissions.kick_members == False:
		return inter.send("You must be have the ability to kick members from this server to use this command, you impostor!")
	data = guild_preferences.find_one({"guild_id": inter.guild.id})
	blacklist = data["blacklisted_members"]
	if person.id in blacklist:
		blacklist.remove(person.id)
		guild_preferences.update_one({"guild_id": inter.guild.id}, {
									 "$set": {"blacklisted_members": blacklist}})
		inter.send(f"<@{person.id}> has been taken off the blacklist!")
	else:
		blacklist.append(person.id)
		guild_preferences.update_one({"guild_id": inter.guild.id}, {
									 "$set": {"blacklisted_members": blacklist}})
		inter.send(f"<@{person.id}> has been put on the blacklist!")


class SettingsView(disnake.ui.View):
	def __init__(self, guild_id, channel_id):
		super().__init__(timeout=60.0)
		self.guild_id = guild_id
		self.channel_id = channel_id

	@disnake.ui.button(
		emoji="<:sabatoge:923423633295179796>",
		style=disnake.ButtonStyle.green,
		label="Channel commands on/off",
		row=0)
	async def swap_channel_state(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		data = guild_preferences.find_one({"guild_id": self.guild_id})
		disabled_channels = data["disabled_channels"]
		if self.channel_id in disabled_channels:
			disabled_channels.remove(self.channel_id)
		else:
			disabled_channels.append(self.channel_id)
		guild_preferences.update_one({"guild_id": self.guild_id}, {
									 "$set": {"disabled_channels": disabled_channels}})
		await inter.response.edit_message(content="Done!", embed=None, view=None)
		self.stop()

	@disnake.ui.button(
		emoji="<:report:923424476459311144>",
		style=disnake.ButtonStyle.green,
		label="Promo buttons on/off",
		row=0)
	async def swap_ad_state(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		data = guild_preferences.find_one({"guild_id": self.guild_id})
		guild_preferences.update_one({"guild_id": self.guild_id}, {
									 "$set": {"show_ads": not data["show_ads"]}})
		await inter.response.edit_message(content="Done!", embed=None, view=None)
		self.stop()

	@disnake.ui.button(
		emoji="<:vitals:923427463193829497>",
		style=disnake.ButtonStyle.primary,
		label="Show blacklisted members",
		row=1)
	async def show_blacklisted_members(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		embed = disnake.Embed(title="Blacklisted members", description="")
		data = guild_preferences.find_one({"guild_id": self.guild_id})
		blacklisted_members = data["blacklisted_members"]
		for i in blacklisted_members:
			embed.description += f"<@{i}>\n"
		await inter.response.edit_message(embed=embed, view=None)
		self.stop()

	@disnake.ui.button(
		emoji="<:security:923424476165726239>",
		style=disnake.ButtonStyle.primary,
		label="Show disabled channels",
		row=1)
	async def show_disabled_channels(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		message = ""
		data = guild_preferences.find_one({"guild_id": self.guild_id})
		disabled_channels = data["disabled_channels"]
		for i in disabled_channels:
			message += f"<#{i}>\n"
		if len(message) == 0:
			message = "No channels are disabled."
		await inter.response.edit_message(content=message, embed=None, view=None)
		self.stop()

	@disnake.ui.button(
		emoji="<:protect:923425234063859752>",
		style=disnake.ButtonStyle.red,
		label="Clear blacklisted members",
		row=2)
	async def clear_blacklisted_members(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		guild_preferences.update_one({"guild_id": self.guild_id}, {
									 "$set": {"blacklisted_members": []}})
		await inter.response.edit_message(content="No more blacklisted members!", embed=None, view=None)
		self.stop()

	@disnake.ui.button(
		emoji="<:cleanthevents:923424942819786794>",
		style=disnake.ButtonStyle.red,
		label="Clear disabled channels",
		row=2)
	async def clear_disabled_channels(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
		guild_preferences.update_one({"guild_id": self.guild_id}, {
									 "$set": {"disabled_channels": []}})
		await inter.send(content="No more disabled channels!", embed=None, view=None)
		self.stop()


@bot.slash_command()
async def settings(inter: disnake.ApplicationCommandInteraction):
	"""Settings for server administrators."""
	if inter.author.guild_permissions.administrator == False:
		return inter.send("You must be an admin on this server to use this command, you impostor!", ephemeral=True)
	default_guild_preferences(inter.guild.id)
	data = guild_preferences.find_one({"guild_id": inter.guild.id})
	show_ads = data["show_ads"]
	disabled_channels = data["disabled_channels"]
	this_channel_disabled = True if inter.channel.id in disabled_channels else False
	embed = disnake.Embed(title="Among Us Dumpy Bot Settings")
	embed.add_field(
		name="Bot enabled in this channel",
		value="<:amongusthumbsdown:923380567960080404>" if this_channel_disabled else "<:amongusthumbsup:923380599195058176>",
		inline=False
	)
	embed.add_field(
		name="Bot shows promo buttons",
		value="<:amongusthumbsdown:923380567960080404>" if not show_ads else "<:amongusthumbsup:923380599195058176>",
		inline=False
	)
	embed.add_field(
		name="Blacklisted members",
		value=str(len(data["blacklisted_members"]))
	)
	embed.add_field(
		name="Disabled channels",
		value=str(len(data["disabled_channels"]))
	)
	await inter.send(embed=embed, view=SettingsView(inter.guild.id, inter.channel.id), ephemeral=True)


@bot.slash_command()
async def info(inter: disnake.ApplicationCommandInteraction):
	"""Gives some helpful information about the bot."""
	if cannot_be_run(inter.guild.id, inter.channel.id, inter.author.id):
		return
	botinfo = await bot.topggpy.get_bot_info()
	votes = botinfo["monthly_points"]
	allvotes = botinfo["points"]
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
	uptime = datetime.datetime.now() - upsince
	embed = disnake.Embed(
		title="Among Us Dumpy Bot",
		color=0x976BE1,
		url="https://dumpy.t1c.dev/"
	)
	embed.add_field(
		name="<:amongthink:923710573445779456> How to use",
		value=f"Just type `/`, and navigate to Among Us Dumpy Bot to see all the commands!",
		inline=False
	)
	embed.add_field(
		name="<:kill:923424476614516766> Creators",
		value=f"ThatOneCalculator#0001 and pixer415#8145.\nGuest artists: [twistCMYK](https://twitter.com/twistCMYK) for the `furry` mode, [Coco](https://twitter.com/CocotheMunchkin) for the `sans` mode, and [Advos](https://twitter.com/AdvosArt) for the `spamton` mode.",
		inline=False
	)
	embed.add_field(
		name="<:report:923424476459311144> Ping",
		value=f"Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.",
		inline=False
	)
	embed.add_field(
		name="<:vitals:923427463193829497> Uptime",
		value=f"I have been up for {humanfriendly.format_timespan(uptime)}.",
		inline=False
	)
	embed.add_field(
		name="<:sabatoge:923423633295179796> Shards",
		value=f"This guild is on shard {inter.guild.shard_id}, with a total of {len(shards)} shards.",
		inline=False
	)
	embed.add_field(
		name="<:protect:923425234063859752> Bot stats",
		value=f"I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.",
		inline=False
	)
	embed.add_field(
		name="<:vent:923424476417388594> Votes",
		value=f"I have {int(votes):,} mothly votes and {int(allvotes):,} all-time votes on top.gg.",
		inline=False
	)
	embed.add_field(
		name="<:security:923424476165726239> Version",
		value=f"I am on jar version {version}. This bot uses disnake. Both the bot and the jar are licensed under the A-GPLv3 code license. See the GitHub for more info.",
		inline=False
	)
	await inter.send(content=None, embed=embed, view=PromoButtons())

bot.remove_command("help")
bot.add_cog(Tasks(bot))
bot.add_cog(CommandErrorHandler(bot))


@bot.event
async def on_message(message):
	if message.guild == None and message.author.bot == False:
		return await message.channel.send("Looks like you're trying to use this command in a DM! You need to invite me to a server to use my commands.\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands ")
	if message.content.startswith("!!"):
		return await message.channel.send("**I have moved to slash commands!**\nType `/` and select me to get started.\nSome commands have changed a bit, but feel free to try out `/dumpy` and `/info`.\nIf you do not see slash commands, ask a server administrator or the server owner to click this link to reinvite the bot with slash command permissions: https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands")
	await bot.process_commands(message)


@bot.event
async def on_ready():
	print("------\nReady\n------\n")

bot.run(token)
