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
import discord
import humanfriendly
import statcord
import topgg
from async_timeout import timeout
from discord.ext import commands, tasks
from discord_components import (
	Button, ButtonStyle, DiscordComponents, InteractionType)
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option
from disputils import BotConfirmation, BotEmbedPaginator, BotMultipleChoice
from PIL import Image

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
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(
	"!!"), intents=intents, chunk_guilds_at_startup=False)
ddb = DiscordComponents(bot)
bot.topggpy = topgg.DBLClient(
	bot, topggtoken, autopost=True, post_shard_count=True)
slash = SlashCommand(bot, sync_commands=True)
api = statcord.Client(bot, statcordkey)
emoji_amongass, emoji_sustopgg, emoji_gitsus, emoji_crewmatedead = "", "", "", ""
api.start_loop()

promobuttons = [
	[
		Button(
			style=ButtonStyle.URL,
			label="GitHub",
			# emoji="<:gitsus:922251058527473784>",
			url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"
		),

		Button(
			style=ButtonStyle.URL,
			label="Support server",
			# emoji="<:crewmatedead:922251654869434448>",
			url="https://discord.gg/VRawXXybvd"
		),

		Button(
			style=ButtonStyle.URL,
			label="Vote on top.gg!",
			# emoji="<:sustopgg:922252075667185716>",
			url="https://top.gg/bot/847164104161361921/vote"
		)
	],
	Button(
		style=ButtonStyle.URL,
		label="Invite to your server!",
		# emoji="<a:amongassdumpy:851566828596887554>",
		url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"
	)
]


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


class TopGG(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.update_stats.start()

	@tasks.loop(minutes=30.0)
	async def update_stats(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(5)
		try:
			await self.bot.topggpy.post_guild_count()
		except Exception as e:
			print(f"\nServer update on top.gg failed\n{e}\n")

	@commands.command(aliases=["voters", "top", "topgg", "vote"])
	async def votes(self, ctx):
		botinfo = await self.bot.topggpy.get_bot_info()
		votes = botinfo["monthly_points"]
		allvotes = botinfo["points"]
		await ctx.send(f"I have {int(votes):,} mothly votes and {int(allvotes):,} all-time votes on top.gg!",
					   components=[
						   Button(
							   style=ButtonStyle.URL,
							   label="Vote on top.gg!",
							   # emoji="<:sustopgg:922252075667185716>",
							   url="https://top.gg/bot/847164104161361921/vote"
						   )
					   ]
					   )


class HelpCommand(commands.Cog):

	@commands.command(name="help")
	async def help_(self, ctx):
		embed = discord.Embed(
			title="My commands!",
			description="Made by ThatOneCalculator#0001 and pixer415#8145! `()` = optional, `<>` = mandatory.",
			color=0x976BE1
		)
		embed.add_field(
			name="`!!dumpy (height) (@person)`",
			value="Makes a dumpy gif from whatever image you post, whatever image was the latest in chat, or from a person's avatar. Height can be a number between 2 and 35, the default is 10. If you tag a person after the height, it will use their avatar instead of the last image in chat.",
			inline=False
		)
		embed.add_field(
			name="`!!furry (height) (@person)`",
			value="The same as `!!dumpy`, but uses the furry template, UwU~ (Template by [twistCMYK](https://twitter.com/twistCMYK)).",
			inline=False
		)
		embed.add_field(
			name="`!!sans (height) (@person)`",
			value="The same as `!!dumpy`, but uses the Sans template <a:sansdumpy:922243828109439107> (Template by [Coco](https://twitter.com/CocotheMunchkin)).",
			inline=False
		)
		embed.add_field(
			name="`!!isaac (height) (@person)`",
			value="The same as `!!dumpy`, but uses the Binding of Isaac template.",
			inline=False
		)
		embed.add_field(
			name="`!!bounce (height) (@person)`",
			value="The same as `!!dumpy`, but uses the bouncing Among Us template.",
			inline=False
		)
		embed.add_field(
			name="`!!background (option)`",
			value="Set a custom background image for `!!dumpy` (and subsequent commands). Run `!!background delete` to remove your current background, run `!!background color` for a solid color, `!!background #AAAAAA` for a custom color background, `!!background flag` for pride flags (gay, lesbian, trans, etc) and run `!!background` and attach an image for a custom image as a background.",
			inline=False
		)
		embed.add_field(
			name="`!!eject <@person>`",
			value="Sees if someone is the impostor! You can also do `!!crewmate` and `!!impostor` to guarantee the output."
		)
		embed.add_field(
			name="`!!text <text>`",
			value="Writes something out, but sus."
		)
		embed.add_field(
			name="`!!tall <number>`",
			value="Makes a tall sussy impostor!"
		)
		embed.add_field(
			name="`!!ping`",
			value="Pings the bot, and gives some information."
		)
		embed.add_field(
			name="`!!topgg`",
			value="Check the number of votes on top.gg, and vote for the bot."
		)
		embed.add_field(
			name="`!!statcord`",
			value="Brings you to the bot's statcord page."
		)
		embed.add_field(
			name="Tips and tricks",
			value="- You can add `nodumpy` to a channel topic to disable the bot there.\n- If you need more lines, go to the GitHub and use the desktop version.",
			inline=False
		)
		embed.set_footer(
			text=f"Among Us Dumpy Bot jar version {version}. Licensed under the AGPL-3.")
		try:
			await ctx.send(embed=embed, components=promobuttons)
		except:
			await ctx.send("Hey! I need the `Embed Links` and the `Attach Files` permission in this channel to work properly.")

	@commands.command()
	async def statcord(self, ctx):
		await ctx.send("https://statcord.com/bot/847164104161361921")

	@commands.command()
	async def invite(self, ctx):
		await ctx.send("https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")

	@commands.command()
	async def support(self, ctx):
		await ctx.send("https://discord.gg/VRawXXybvd")


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


class TheStuff(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.update_status.start()
		self.update_channels.start()

	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.command(aliases=["sus", "imposter", "impostor", "crewmate"])
	async def eject(self, ctx, *, victim: typing.Union[discord.Member, str] = ""):
		if type(victim) != discord.Member:
			return await ctx.send("You need to mention someone!")
		imposter = random.choice(["true", "false"])
		if "impost" in ctx.message.content:
			imposter = "true"
		elif "crewmate" in ctx.message.content:
			imposter = "false"
		url = str(victim.avatar_url_as(format="png"))
		async with ctx.typing():
			file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={victim.name[0:35]}&imposter={imposter}", f"eject{ctx.message.id}.gif")
			await ctx.send(
				f"{ctx.author.mention} Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
				file=file,
				components=promobuttons
			)
		rm = shlex.split(f"bash -c 'rm ./eject{ctx.message.id}.gif'")
		subprocess.check_call(rm)

	@commands.command(aliases=["font", "write"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def text(self, ctx, *, text):
		if text == None:
			return await ctx.send("You have to give something to write, you sussy baka!")
		mytext = urllib.parse.quote(text).upper()
		file = await asyncimage(f"https://img.dafont.com/preview.php?text={mytext}&ttf=among_us0&ext=1&size=57&psize=m&y=58", "text.png")
		await ctx.send(
			f"{ctx.author.mention} Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
			file=file,
			components=promobuttons
		)

	@commands.command()
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def tall(self, ctx, number: int):
		if number == None or type(number) != int:
			number = 0
		if number > 20:
			return await ctx.send("That's taller than 20, you sussy baka!")
		lb = "\n"
		await ctx.send(f"<:tallamongus_1:853680242124259338>\n{('<:tallamongus_2:853680316110602260>' + lb) * number}<:tallamongus_3:853680372554268702>")

	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command()
	async def background(self, ctx, *, ar: str = None):
		if ar != None:
			ar = ar.lower()
			if ar in ["delete", "default", "remove", "gray", "grey"]:
				if exists(f"custom_bgs/background_{ctx.author.id}.png"):
					rmcmd = shlex.split(
						f"bash -c 'rm custom_bgs/background_{ctx.author.id}.png'")
					subprocess.check_call(rmcmd)
					return await ctx.send("Your background has been deleted!")
			elif ar.startswith("#"):
				if len(ar) != 7:
					return await ctx.send("Invalid length! Example: `#0ab32c`")
				await asyncimage(f"https://some-random-api.ml/canvas/colorviewer?key={sr_api_key}&hex={argument[1:]}", f"custom_bgs/background_{ctx.author.id}.png")
				return await ctx.send("Set your background!")
			else:
				if exists(f"backgrounds/{ar}.png"):
					cpcmd = shlex.split(
						f"bash -c 'cp ./backgrounds/{ar}.png ./custom_bgs/background_{ctx.author.id}.png'")
					subprocess.check_call(cpcmd)
					return await ctx.send("Set your background!")
				else:
					return await ctx.send("I couldn't find that background preset! Options avaliable:\n- `delete`/`remove`/`default`\n- Basics (ex `black`/`white`/`transparent`)\n- Basic colors (ex `red`, `orange`, `yellow`)\n- Custom colors (hex, start with `#`)\n- Pride flags (ex `gay`, `lesbian`, `vincian`, `bisexual`, `transgender`)\n- Custom images (upload image with no argument)")
		elif len(ctx.message.attachments) > 0:
			try:
				await ctx.message.attachments[0].save(f"custom_bgs/background_{ctx.author.id}.png")
			except Exception as e:
				await ctx.send(f"```{e}```")
			return await ctx.send("Saved your background!")
		else:
			return await ctx.send("You NEED to attach a file in your message to set your background. Try again in 30 seconds.\nTo delete your background, run `!!background delete`.")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["twerk", "amogus", "furry", "twist", "isaac", "bounce", "sans"])
	async def dumpy(self, ctx, number: typing.Union[int, str] = 10, victim: typing.Union[discord.Member, str] = None):
		await bot.wait_until_ready()
		# await ctx.send("The `!!background` command has been updated! Run `!!background delete` to remove your current background, run `!!background color` for a solid color, `!!background #AAAAAA` for a custom color background, `!!background flag` for pride flags (gay, lesbian, trans, etc) and run `!!background` and attach an image for a custom image as a background.")
		loop = asyncio.get_running_loop()
		messageid = str(ctx.message.id)
		if type(number) != int:
			number = 10
		if number > 35 and number < 41:
			msg = await ctx.send("Validating vote... <:sustopgg:922252075667185716>")
			voted = await self.bot.topggpy.get_user_vote(ctx.author.id)
			await asyncio.sleep(0.2)
			await msg.delete()
			if not voted and ctx.author.id != 454847501787463680:
				return await ctx.send(f"The limit for non-voters is 35! {ctx.author.mention}, vote on top.gg to increase it to 40!\nAll you need to do is sign in with Discord and click the button. Please note that votes reset every 12 hours.\nhttps://top.gg/bot/847164104161361921/vote")
		if number > 40 or number < 1:
			return await ctx.send("Number must be between 1 and 35 (40 if you vote!) Defaults to 10.",
								  components=[
									  Button(
										  style=ButtonStyle.URL,
										  label="Vote on top.gg!",
										  # emoji="<:sustopgg:922252075667185716>",
										  url="https://top.gg/bot/847164104161361921/vote"
									  )
								  ])
		async with ctx.typing():
			if len(ctx.message.attachments) > 0:
				await ctx.message.attachments[0].save(f"attach_{messageid}.png")
			elif len(ctx.message.embeds) > 0:
				await asyncimage(ctx.message.embeds[0].url, f"attach_{messageid}.png")
			else:
				if victim != None and type(victim) == discord.Member:
					await asyncimage(str(victim.avatar_url_as(format='png', size=128)), f"attach_{messageid}.png")
				else:
					sus = True
					try:
						async for message in ctx.channel.history(limit=20):
							if len(message.attachments) > 0 and sus and message.author != ctx.guild.me:
								await message.attachments[0].save(f"attach_{messageid}.png")
								sus = False
							elif len(message.embeds) > 0 and message.author != ctx.guild.me:
								await asyncimage(message.embeds[0].url, f"attach_{messageid}.png")
								sus = False
					except Exception as e:
						return await ctx.send("I couldn't find an image, you sussy baka!")
			await asyncio.sleep(0.1)
			img = Image.open(f"attach_{messageid}.png")
			if img.height / img.width <= 0.05:
				subprocess.check_call(shlex.split(
					f"bash -c 'rm ./attach_{messageid}.png'"))
				return await ctx.send("This image is way too long, you're the impostor!")
			mode = "default"
			if "furry" in ctx.message.content or "twist" in ctx.message.content:
				mode = "furry"
			elif "isaac" in ctx.message.content:
				mode = "isaac"
			elif "bounce" in ctx.message.content:
				mode = "bounce"
			elif "sans" in ctx.message.content or "undertale" in ctx.message.content:
				mode = "sans"
			background = f"--background custom_bgs/background_{ctx.author.id}.png" if exists(
				f"custom_bgs/background_{ctx.author.id}.png") else ""
			await loop.run_in_executor(None, blocking, messageid, mode, number, background)
			filename = f"dumpy{messageid}.gif"
			allmembers = 0
			for guild in self.bot.guilds:
				try:
					allmembers += guild.member_count
				except:
					pass
			try:
				await ctx.send(
					f"{ctx.author.mention} Please leave a star on the GitHub, vote on top.gg, and most of all invite the bot to your server! These are all free and helps out a lot!",
					file=discord.File(filename, filename=filename),
					components=promobuttons
				)
				await ctx.send(f"Remember to invite the bot to your server(s)! I'm trying to get to 50,000 servers, and I'm currently at {len(self.bot.guilds):,}!\n<https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot>",
							   components=[
								   Button(
									   style=ButtonStyle.URL,
									   label="Tap here!",
									   # emoji=emoji_amongass,
									   url="https://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot"
								   )
							   ]
							   )
			except:
				await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
			rmcmds = [
				shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"),
				shlex.split(f"bash -c 'rm ./dumpy{messageid}.gif'")
			]
			for i in rmcmds:
				subprocess.check_call(i)

	@commands.command(aliases=["stats"])
	async def ping(self, ctx):
		botinfo = await self.bot.topggpy.get_bot_info()
		votes = botinfo["monthly_points"]
		shardscounter = []
		for guild in self.bot.guilds:
			if guild.shard_id not in shardscounter:
				shardscounter.append(guild.shard_id)
		shards = []
		for i in shardscounter:
			shards.append(self.bot.get_shard(i))
		allmembers = 0
		for guild in self.bot.guilds:
			try:
				allmembers += guild.member_count
			except:
				pass
		beforeping = datetime.datetime.now()
		ping = await ctx.send(f":ping_pong: Pong! Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.")
		afterping = datetime.datetime.now()
		pingdiff = afterping - beforeping
		pingdiffms = pingdiff.microseconds / 1000
		uptime = afterping - upsince
		await ping.edit(content=f"""
🏓 Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.
☎️ API latency is {str(round((pingdiffms),2))} milliseconds.
☕ I have been up for {humanfriendly.format_timespan(uptime)}.
🔮 This guild is on shard {ctx.guild.shard_id}, with a total of {len(shards)} shards.
👪 I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.
📈 I have {int(votes):,} monthly votes on top.gg.
🧑‍💻 I am on jar version {version}.
""", components=promobuttons)

	@commands.command()
	async def shards(self, ctx):
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
		await ctx.send(embed=staticembed)
		await shardpaginator.run()

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
		guild = bot.get_guild(849516341933506561)
		await guild.get_channel(861384764383428658).edit(name=f"Servers: {len(bot.guilds):,}")
		await guild.get_channel(861384798429380618).edit(name=f"Users: {allmembers:,}")
		await guild.get_channel(861384904780808222).edit(name=f"Votes: {int(votes):,}")

	@tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(10)
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"!!help on {len(bot.guilds):,}  servers!"))


bot.remove_command("help")
bot.add_cog(HelpCommand(bot))
bot.add_cog(TheStuff(bot))
bot.add_cog(TopGG(bot))
bot.add_cog(CommandErrorHandler(bot))


@bot.event
async def on_message(message):
	if message.guild == None and message.author.bot == False:
		return await message.channel.send("Looks like you're trying to use this command in a DM! You need to invite me to a server to use my commands.\nhttps://discord.com/api/oauth2/authorize?client_id=847164104161361921&permissions=117760&scope=bot")
	elif (message.channel.topic != None and message.channel.topic.find("nodumpy") != -1) and message.content.startswith("!!"):
		return await message.channel.send("**Commands have been disabled in this channel.**")
	await bot.process_commands(message)


@bot.event
async def on_command(ctx):
	api.command_run(ctx)


@bot.event
async def on_ready():
	print("Ready")
	# try:
	# 	support_guild = bot.get_guild(849516341933506561)
	# 	if not support_guild.chunked:
	# 		await support_guild.chunk()
	# 		print("Chunked support server!")
	# except:
	# 	pass
	# global emoji_amongass, emoji_sustopgg, emoji_gitsus, emoji_crewmatedead
	# emoji_amongass = bot.get_emoji(851566828596887554)
	# emoji_sustopgg = bot.get_emoji(922252075667185716)
	# emoji_gitsus = bot.get_emoji(922251058527473784)
	# emoji_crewmatedead = bot.get_emoji(922251654869434448)

bot.run(token)
