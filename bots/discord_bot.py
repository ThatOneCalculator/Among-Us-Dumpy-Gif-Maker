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
import disnake
import humanfriendly
import pymongo
import topgg
from async_timeout import timeout
from disnake.ext import commands, tasks
from disputils import BotConfirmation, BotEmbedPaginator, BotMultipleChoice
from dotenv import dotenv_values
from PIL import Image
from statcord import StatcordClient

token = dotenv_values(".env")["DISCORD"]
sr_api_key = dotenv_values(".env")["SRAPI"]
topggtoken = dotenv_values(".env")["TOPGG"]
statcordkey = dotenv_values(".env")["STATCORD"]

upsince = datetime.datetime.now()
version = "4.1.0"

intents = disnake.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or("!!"),
	intents=intents,
	chunk_guilds_at_startup=False,
)
bot.topggpy = topgg.DBLClient(bot, topggtoken, autopost=True, post_shard_count=True)
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

def ads(guild_id):
	try:
		if guild_preferences.find_one({"guild_id": guild_id})["show_ads"] == False:
			return None
	except:
		pass
	return PromoButtons()

def blocking(messageid, mode, lines, background):
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar --lines {lines} --file attach_{messageid}.png --mode {mode} --extraoutput {messageid} {background}")
	subprocess.check_call(cmd)


async def asyncimage(url, filename):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			f = await aiofiles.open(filename, mode="wb")
			await f.write(await resp.read())
			await f.close()
	img = Image.open(filename)
	file = disnake.File(filename, filename=filename)
	return file


class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(inter, error):
		if hasattr(inter, 'on_error'):
			return
		ignored = (commands.errors.CommandNotFound, commands.errors.UserInputError)
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
		await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"slash commands on {len(bot.guilds):,} servers!"))

@bot.slash_command(description="Brings you to the bot's statcord page.")
async def statcord(inter: disnake.ApplicationCommandInteraction):
	await inter.send(content="https://statcord.com/bot/847164104161361921")

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command(description="Sees if someone is the impostor!")
async def eject(inter: disnake.ApplicationCommandInteraction, person: disnake.Member, impostor: str=commands.Param(choices=["Random", "True", "False"])):
	default_guild_preferences(inter.guild.id)
	if impostor == "Random":
		outcome = random.choice(["true", "false"])
	elif impostor ==  "True":
		outcome = "true"
	elif impostor == "False":
		outcome = "false"
	url = str(person.avatar.url)
	file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={person.name[0:35]}&imposter={outcome}", f"eject{inter.id}.gif")
	await inter.edit_original_message(
		content="Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
		file=file,
		view=ads(inter.guild.id)
		)
	rm = shlex.split(f"bash -c 'rm ./eject{inter.id}.gif'")
	subprocess.check_call(rm)

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.slash_command(description="Writes something out, but sus.")
async def text(inter: disnake.ApplicationCommandInteraction, text: str):
	default_guild_preferences(inter.guild.id)
	mytext = urllib.parse.quote(text).upper()
	file = await asyncimage(f"https://img.dafont.com/preview.php?text={mytext}&ttf=among_us0&ext=1&size=57&psize=m&y=58", "text.png")
	await inter.send(
		content="Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
		file=file,
		view=ads(inter.guild.id)
	)

@commands.cooldown(1, 15, commands.BucketType.user)
@bot.slash_command(description="Makes a tall sussy impostor!")
async def tall(inter: disnake.ApplicationCommandInteraction, height: int):
	if height == None or type(height) != int:
		height = 0
	if height > 20:
		return await inter.send(content="That's taller than 20, you sussy baka!")
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
			"aroace",
			"bisexual",
			"boyflux",
			"demiboy",
			"demigirl",
			"gay",
			"genderfluid",
			"genderflux",
			"lesbian",
			"nonbinary",
			"omnisexual",
			"pansexual",
			"polyamorous",
			"polysexual",
			"pride",
			"transgender",
			"vincian"
			]
		return [i for i in CHOICES if user_input.lower() in i]

@commands.cooldown(1, 15, commands.BucketType.user)
@bot.slash_command(description="Set background image for /dumpy. bg_choice can be transparent, any color, or any pride flag.")
async def background(inter: disnake.ApplicationCommandInteraction, bg_choice: str = commands.Param(autocomplete=autocomplete_bg_choices)):
	await inter.response.defer()
	bg_choice = bg_choice.lower()
	if bg_choice in ["delete", "default", "remove", "gray", "grey"]:
		if exists(f"custom_bgs/background_{inter.author.id}.png"):
			rmcmd = shlex.split(
				f"bash -c 'rm custom_bgs/background_{inter.author.id}.png'")
			subprocess.check_call(rmcmd)
			return await inter.edit_original_message(content="Your background has been deleted!")
	elif bg_choice.startswith("#"):
		if len(bg_choice) != 7:
			return await inter.edit_original_message(content="Invalid length! Example: `#0ab32c`")
		await asyncimage(f"https://some-random-api.ml/canvas/colorviewer?key={sr_api_key}&hex={argument[1:]}", f"custom_bgs/background_{inter.author.id}.png")
		return await inter.edit_original_message(content="Set your background!")
	else:
		if exists(f"backgrounds/{bg_choice}.png"):
			cpcmd = shlex.split(
				f"bash -c 'cp ./backgrounds/{bg_choice}.png ./custom_bgs/background_{inter.author.id}.png'")
			subprocess.check_call(cpcmd)
			return await inter.edit_original_message(content="Set your background!")
		else:
			return await inter.edit_original_message(content="I couldn't find that background preset! Options avaliable:\n- `delete`/`remove`/`default`\n- Basics (ex `black`/`white`/`transparent`)\n- Basic colors (ex `red`, `orange`, `yellow`)\n- Custom colors (hex, start with `#`)\n- Pride flags (ex `gay`, `lesbian`, `vincian`, `bisexual`, `transgender`)\n- Custom images (upload image with no argument)")
	# elif len(inter) > 0:
	# 	try:
	# 		await inter.attachments[0].save(f"custom_bgs/background_{inter.author.id}.png")
	# 	except Exception as e:
	# 		await inter.edit_original_message(content=f"```{e}```")
	# 	return await inter.edit_original_message(content="Saved your background!")

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.slash_command(description="Makes a Dumpy GIF! Uses the last image posted, but person/image_url overrides this. Lines are 1-40.")
async def dumpy(inter: disnake.ApplicationCommandInteraction, mode: str=commands.Param(choices=["default", "furry", "sans", "isaac", "bounce"]), lines: int = 10, person: disnake.Member = None, image_url: str = None):
	await bot.wait_until_ready()
	await inter.response.defer()
	loop = asyncio.get_running_loop()
	default_guild_preferences(inter.guild.id)
	messageid = str(inter.id)
	if lines > 35 and lines < 41:
		voted = await bot.topggpy.get_user_vote(inter.author.id)
		if not voted and inter.author.id != 454847501787463680:
			return await inter.edit_original_message(content=f"The limit for non-voters is 35! {inter.author.mention}, vote on top.gg to increase it to 40!\nAll you need to do is sign in with Discord and click the button. Please note that votes reset every 12 hours.\nhttps://top.gg/bot/847164104161361921/vote")
	if lines > 40 or lines < 1:
		return await inter.edit_original_message(content="Number must be between 1 and 35 (40 if you vote!) Defaults to 10. Vote here: https://top.gg/bot/847164104161361921/vote")
	if person != None:
		await asyncimage(person.avatar.url, f"attach_{messageid}.png")
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
			return await inter.edit_original_message(content="I couldn't find an image, you sussy baka!")
	await asyncio.sleep(0.1)
	img = Image.open(f"attach_{messageid}.png")
	if img.height / img.width <= 0.05:
		subprocess.check_call(shlex.split(
			f"bash -c 'rm ./attach_{messageid}.png'"))
		return await inter.edit_original_message(content="This image is way too long, you're the impostor!")
	custom_bg_path = f"custom_bgs/background_{inter.author.id}.png"
	background = f"--background {custom_bg_path}" if exists(custom_bg_path) else ""
	await loop.run_in_executor(None, blocking, messageid, mode, lines, background)
	filename = f"dumpy{messageid}.gif"
	try:
		await inter.edit_original_message(
			content="Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
			file=disnake.File(filename, filename=filename),
			view=ads(inter.guild.id)
			)
	except Exception as e:
		await inter.edit_original_message(content=f"An error occurred! I might not have the permission `Attach Files` in this channel.\n```\n{e}```")
	rmcmds = [
		shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"),
		shlex.split(f"bash -c 'rm ./dumpy{messageid}.gif'")
	]
	for i in rmcmds:
		subprocess.check_call(i)

@bot.slash_command(description="Blacklist a server member from using the bot. Can also be used to unblacklist.")
async def blacklist(inter: disnake.ApplicationCommandInteraction, person: disnake.Member):
	if inter.author.guild_permissions.kick_members == False:
		return inter.send("You must be have the ability to kick members from this server to use this command, you impostor!")
	blacklist = guild_preferences.find_one({"guild_id": inter.guild.id})["blacklisted_members"]
	blacklist.remove(person.id) if person.id in blacklist else blacklist.append(person.id)
	blacklist = guild_preferences.update_one({"guild_id": inter.guild.id}, {"blacklisted_members": blacklist})
	inter.respond(f"{person.mention} has been {'blacklisted' if person.id in blacklist else 'unblacklisted'}.")

class SettingsView(disnake.ui.View):
	def __init__(self, guild_id, channel_id):
		super().__init__(timeout=60.0)
		self.guild_id = guild_id
		self.channel_id = channel_id
		self.show_ads = guild_preferences.find_one({"guild_id": self.guild_id})["show_ads"]
		self.disabled_channels = guild_preferences.find_one({"guild_id": self.guild_id})["disabled_channels"]
		self.this_channel_disabled = True if self.channel_id in self.disabled_channels else False
		###
		print(f"""
self.guild_id: {self.guild_id} ({type(self.guild_id)})
self.channel_id: {self.channel_id} ({type(self.channel_id)})
self.show_ads: {self.show_ads} ({type(self.show_ads)})
self.disabled_channels: {self.disabled_channels} ({type(self.disabled_channels)})
self.this_channel_disabled: {self.this_channel_disabled} ({type(self.this_channel_disabled)})
""")

	@disnake.ui.button(
		emoji=bot.get_emoji(923380567960080404),
		style=disnake.ButtonStyle.red,
		label="Channel has commands off",
		row=0)
	async def swap_channel_state(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		if not self.this_channel_disabled:
			button.emoji = bot.get_emoji(923380599195058176)
			button.style = disnake.ButtonStyle.green
			button.label = "Channel has commands on"
		if self.channel_id in self.disabled_channels:
			self.disabled_channels.remove(self.channel_id)
		else:
			self.disabled_channels.append(self.channel_id)
		self.disabled_channels = guild_preferences.update_one({"guild_id": self.guild_id}, {"disabled_channels": self.disabled_channels})
		self.this_channel_disabled = not self.this_channel_disabled
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923380567960080404),
		style=disnake.ButtonStyle.red,
		label="Promo buttons are off",
		row=0)
	async def swap_ad_state(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		if self.show_ads:
			button.emoji = bot.get_emoji(923380599195058176)
			button.style = disnake.ButtonStyle.green
			button.label = "Promo buttons are on"
		self.show_ads = not self.show_ads
		guild_preferences.update_one({"guild_id": self.guild_id}, {"show_ads": self.show_ads})
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923427463193829497),
		style=disnake.ButtonStyle.primary,
		label="Show blacklisted members",
		row=1)
	async def show_blacklisted_members(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		embed = disnake.Embed(title="Blacklisted members")
		for i in guild_preferences.find_one({"guild_id": self.guild_id})["blacklisted_members"]:
			embed.description += f"<@{i}>\n"
		await interaction.send(embed=embed)
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923424476165726239),
		style=disnake.ButtonStyle.primary,
		label="Show disabled channels",
		row=1)
	async def show_disabled_channels(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		message = ""
		for i in guild_preferences.find_one({"guild_id": self.guild_id})["disabled_channels"]:
			message += f"<#{i}>\n"
		if len(message) == 0:
			message = "No channels are disabled."
		await interaction.send(content=message)
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923425234063859752),
		style=disnake.ButtonStyle.secondary,
		label="Clear blacklisted members",
		row=2)
	async def clear_blacklisted_members(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		guild_preferences.update_one({"guild_id": self.guild_id}, {"blacklisted_members": []})
		await interaction.send("No more blacklisted members!")
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923424942819786794),
		style=disnake.ButtonStyle.secondary,
		label="Clear disabled channels",
		row=2)
	async def clear_disabled_channels(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		guild_preferences.update_one({"guild_id": self.guild_id}, {"disabled_channels": []})
		await interaction.send("No more disabled channels!")
		self.stop()

	@disnake.ui.button(
		emoji=bot.get_emoji(923424476614516766),
		style=disnake.ButtonStyle.red,
		label="Exit settings menu",
		row=3)
	async def stop_settings(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
		self.stop()

@bot.slash_command(description="Settings for server administrators.")
async def settings(inter: disnake.ApplicationCommandInteraction):
	if inter.author.guild_permissions.administrator == False:
		return inter.send("You must be an admin on this server to use this command, you impostor!")
	default_guild_preferences(inter.guild.id)
	show_ads = guild_preferences.find_one({"guild_id": inter.guild.id})["show_ads"]
	disabled_channels = guild_preferences.find_one({"guild_id": inter.guild.id})["disabled_channels"]
	this_channel_disabled = True if inter.channel.id in disabled_channels else False
	embed = disnake.Embed(title="Among Us Dumpy Bot Settings")
	embed.add_field(
		name="Bot enabled in this channel",
		value=f"{'<:amongusthumbsdown:923380567960080404>' if this_channel_disabled else '<:amongusthumbsup:923380599195058176>'}",
		inline=False
	)
	embed.add_field(
		name="Bot shows promo buttons",
		value=f"{'<:amongusthumbsdown:923380567960080404>' if not show_ads else '<:amongusthumbsup:923380599195058176>'}",
		inline=False
	)
	embed.add_field(
		name="Blacklisted members",
		value=str(len(guild_preferences.find_one({"guild_id": inter.guild.id})["blacklisted_members"]))
	)
	embed.add_field(
		name="Disabled channels",
		value=str(len(guild_preferences.find_one({"guild_id": inter.guild.id})["disabled_channels"]))
	)
	await inter.send(embed=embed, view=SettingsView(inter.guild.id, inter.channel.id))

@bot.slash_command(description="Gives some helpful information about the bot.")
async def info(inter: disnake.ApplicationCommandInteraction):
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
		description="Made by ThatOneCalculator#0001 and pixer415#8145!",
		color=0x976BE1,
		url="https://dumpy.t1c.dev/"
	)
	embed.add_field(
		name="🤔 How to use",
		value=f"Just type `/`, and navigate to Among Us Dumpy Bot to see all the commands!",
		inline=False
	)
	embed.add_field(
		name="💁 Creators",
		value=f"ThatOneCalculator#0001 and pixer415#8145.",
		inline=False
	)
	embed.add_field(
		name="🏓 Ping",
		value=f"Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.",
		inline=False
	)
	embed.add_field(
		name="☕ Uptime",
		value=f"I have been up for {humanfriendly.format_timespan(uptime)}.",
		inline=False
	)
	embed.add_field(
		name="🔮 Shards",
		value=f"This guild is on shard {inter.guild.shard_id}, with a total of {len(shards)} shards.",
		inline=False
	)
	embed.add_field(
		name="👪 Bot stats",
		value=f"I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.",
		inline=False
	)
	embed.add_field(
		name="📈 Votes",
		value=f"I have {int(votes):,} mothly votes and {int(allvotes):,} all-time votes on top.gg.",
		inline=False
	)
	embed.add_field(
		name="🧑‍💻 Version",
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
		return await message.channel.send("I have moved to slash commands! Type `/` and select me to get started. All commands are the same, but they start with `/` instead of `!!`. You can also type `/info` for more info.\n\nIf you do not see slash commands, ask a server administrator or the server owner to click this link to reinvite the bot with slash command permissions: https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot%20applications.commands")
	# elif (message.channel.topic != None and message.channel.topic.find("nodumpy") != -1) and message.content.startswith("!!"):
	# 	return await message.channel.send("**Commands have been disabled in this channel.**")
	await bot.process_commands(message)

@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
