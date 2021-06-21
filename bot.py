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
from typing import Any, Iterable, Tuple

import aiofiles
import aiohttp
import discord
import humanfriendly
import topgg
from async_timeout import timeout
from discord.ext import commands, tasks
from discord_components import (Button, ButtonStyle, DiscordComponents, InteractionType)
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

upsince = datetime.datetime.now()
version = "2.0.2"

intents = discord.Intents.default()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or("!!"), intents=intents, chunk_guilds_at_startup=False)
ddb = DiscordComponents(bot)
bot.topggpy = topgg.DBLClient(bot, topggtoken, autopost=True, post_shard_count=True)
slash = SlashCommand(bot, sync_commands=True)

promobuttons = [
	[
		Button(
			style=ButtonStyle.URL,
			label="See my GitHub!",
			url="https://github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker"
		),

		Button(
			style=ButtonStyle.URL,
			label="Join the support server!",
			url="https://discord.gg/VRawXXybvd"
		),

		Button(
			style=ButtonStyle.URL,
			label="Vote on top.gg!",
			url="https://top.gg/bot/847164104161361921/vote"
		)
	],
	Button(
		style=ButtonStyle.URL,
		label="Invite to your server!",
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
		votes = await self.bot.topggpy.get_bot_info()["monthlyPoints"]
		await ctx.send(f"I have {int(votes):,} votes on top.gg!",
			components=[
				Button(
					style=ButtonStyle.URL,
					label="Vote on top.gg!",
					url="https://top.gg/bot/847164104161361921/vote"
				)
			]
		)

class HelpCommand(commands.Cog):

	@commands.command(name="help")
	async def help_(self, ctx):
		embed = discord.Embed(
			title="My commands!",
			description="Made by ThatOneCalculator#1337 and Dsim64#8145!",
			color=0x976BE1
		)
		embed.add_field(
			name="`!!dumpy (height) (@person)`",
			value="Makes a dumpy gif from whatever image you post, whatever image was the latest in chat, or from a person's avatar. Height can be a number between 2 and 35, the default is 10. If you tag a person after the height, it will use their avatar instead of the last image in chat.",
			inline=False
		)
		embed.add_field(
			name="`!!eject <@person>`",
			value="Sees if someone is the imposter! You can also do `!!crewmate` and `!!imposter` to guarantee the output."
		)
		embed.add_field(
			name="`!!text <text>`",
			value="Writes something out, but sus."
		)
		embed.add_field(
			name="`!!tall <number>`",
			value="Makes a tall sussy imposter!"
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
			name="`!!literallynobot`",
			value="Directs you to ThatOneCalculator's main bot LiterallyNoBot."
		)
		embed.add_field(
			name="Tips and tricks",
			value="- You can add `nodumpy` to a channel topic to disable the bot there.\n- If you need more lines, go to the GitHub and use the desktop version.",
			inline=False
		)
		embed.set_footer(text=f"Among Us Dumpy Bot version {version}. Licensed under the GPL-3. Thank you server boosters: AdminDolphin(OFFICIAL)#6542, shermy the cat#0002")
		try:
			await ctx.send(embed=embed, components=promobuttons)
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


def blocking(messageid, number):
	cmd = shlex.split(
		f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar {number} attach_{messageid}.png {messageid}")
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
			return await ctx.send("That's too tall, you sussy baka!")
		lb = "\n"
		await ctx.send(f"<:tallamongus_1:853680242124259338>\n{('<:tallamongus_2:853680316110602260>' + lb) * number}<:tallamongus_3:853680372554268702>")

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(aliases=["twerk", "amogus"])
	async def dumpy(self, ctx, number: typing.Union[int, str] = 10, victim: typing.Union[discord.Member, str] = None):
		loop = asyncio.get_running_loop()
		messageid = str(ctx.message.id)
		if type(number) != int:
			number = 10
		if number > 30 and number < 36:
			msg = await ctx.send("Validating vote...")
			voted = await self.bot.topggpy.get_user_vote(ctx.author.id)
			await asyncio.sleep(0.2)
			await msg.delete()
			if not voted:
				return await ctx.send(f"The limit for non-voters is 30! {ctx.author.mention}, vote on top.gg to increase it to 35!\nAll you need to do is sign in with Discord and click the button.\nhttps://top.gg/bot/847164104161361921/vote")
		if number > 35 or number < 1:
			return await ctx.send("Number must be between 1 and 30 (35 if you vote!) Defaults to 10.",
				components=[
					Button(
						style=ButtonStyle.URL,
						label="Vote on top.gg!",
						url="https://top.gg/bot/847164104161361921/vote"
					)
				])
		async with ctx.typing():
			if len(ctx.message.attachments) > 0:
				await ctx.message.attachments[0].save(f"attach_{messageid}.png")
			else:
				if victim != None and type(victim) == discord.Member:
					await asyncimage(str(victim.avatar_url_as(format='png', size=128)), f"attach_{messageid}.png")
				else:
					sus=True
					try:
						async for message in ctx.channel.history(limit=20):
							if len(message.attachments) > 0 and sus and message.author != ctx.guild.me:
								await message.attachments[0].save(f"attach_{messageid}.png")
								sus = False
					except Exception as e:
						return await ctx.send("I couldn't find an image, you sussy baka!")
			await asyncio.sleep(0.2)
			img = Image.open(f"attach_{messageid}.png")
			if img.height / img.width <= 0.05:
				subprocess.check_call(shlex.split(
					f"bash -c 'rm ./attach_{messageid}.png'"))
				return await ctx.send("This image is way too long, you're the imposter!")
			await loop.run_in_executor(None, blocking, messageid, number)
			filename = f"dumpy{messageid}.gif"
			try:
				await ctx.send(
					f"{ctx.author.mention} Please leave a star on the GitHub and vote on top.gg, it's free and helps out a lot!",
					file=discord.File(filename, filename=filename),
					components=promobuttons
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
		votes = await self.bot.topggpy.get_bot_info()["monthlyPoints"]
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
		await ping.edit(content=f"""
🏓 Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.
☎️ API latency is {str(round((pingdiffms),2))} milliseconds.
☕ I have been up for {humanfriendly.format_timespan(uptime)}.
🔮 This guild is on shard {ctx.guild.shard_id}, with a total of {len(shards)} shards.
👪 I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.
📈 I have {int(votes):,} votes on top.gg.
🧑‍💻 I am on version {version}.
""", components=promobuttons)

	@commands.command()
	async def shards(self, ctx):
		shardscounter = []
		allmembers = 0
		for guild in bot.guilds:
			if guild.shard_id not in shardscounter:
				shardscounter.append(guild.shard_id)
			allmembers += guild.member_count
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
			embed.add_field(name=f"Shard {i.id}", value=f"Guilds: {gcount}, Members: {mcount}, Status: {'Down' if i.is_closed() else 'Ready'}, Ping: {round((i.latency * 1000),2)}")
			if count == len(shards):
				embedlist.append(embed)
		embedlist[-1].add_field(name="Total", value=f"Guilds: {len(bot.guilds)}, Members: {allmembers}, Shards down: {closedcount}, Average ping: {round(sum(totpings)/len(totpings),2)}")
		shardpaginator = BotEmbedPaginator(ctx, embedlist)
		await shardpaginator.run()

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
	if (message.channel.topic != None and message.channel.topic.find("nodumpy") != -1) and message.content.startswith("!!"):
		return await message.channel.send("**Commands have been disabled in this channel.**")
	await bot.process_commands(message)

@bot.event
async def on_ready():
	print("Ready")

bot.run(token)
