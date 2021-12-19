import asyncio
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
import revolt
from revolt.ext import commands
from async_timeout import timeout
from PIL import Image

with open("revolt.txt", "r") as f:
	lines = f.readlines()
	token = lines[0].strip()

with open("srapi.txt", "r") as f:
	lines = f.readlines()
	sr_api_key = lines[0].strip()

class Client(commands.CommandsClient):
	async def get_prefix(self, message: revolt.Message):
		return "!!"

	@commands.command()
	async def help(self, ctx: commands.Context):
		await ctx.send("""# $\color{#FCF332}\text{Commands:}$
### $\color{#FF76AB}\blacksquare$ `!!dumpy`:
Makes a dumpy gif from whatever image you post or from a person's avatar. Height can be a number between 2 and 35, the default is 10. If you tag a person after the height, it will use their avatar instead of the last image in chat.
### $\color{#FF76AB}\blacksquare$ `!!furry`:
The same as `!!dumpy`, but uses the furry template, UwU~ (Template by [twistCMYK](https://twitter.com/twistCMYK)).
### $\color{#FF76AB}\blacksquare$ `!!sans`:
The same as `!!dumpy`, but uses the Sans template (Template by [Coco](https://twitter.com/CocotheMunchkin)).
### $\color{#FF76AB}\blacksquare$ `!!isaac`:
The same as `!!dumpy`, but uses the Binding of Isaac template.
### $\color{#FF76AB}\blacksquare$ `!!bounce`:
The same as `!!dumpy`, but uses the bouncing Among Us template.
### $\color{#FF76AB}\blacksquare$ `!!background`:
Set a custom background image for `!!dumpy` (and subsequent commands). Run `!!background delete` to remove your current background, run `!!background color` for a solid color, `!!background #AAAAAA` for a custom color background, `!!background flag` for pride flags (gay, lesbian, trans, etc) and run `!!background` and attach an image for a custom image as a background.
### $\color{#FF76AB}\blacksquare$ `!!eject`:
Sees if someone is the impostor! You can also do `!!crewmate` and `!!impostor` to guarantee the output.
### $\color{#FF76AB}\blacksquare$ `!!text`:
Writes something out, but sus.

# $\color{#FCF332}\text{Credits:}$
## github.com/ThatOneCalculator/Among-Us-Dumpy-Gif-Maker
Revolt bot specifically made by ThatOneCalculator (\@t1c)
""")

	@commands.command(aliases=["sus", "impostor", "imposter", "crewmate"])
	async def eject(self, ctx, *, victim: typing.Union[revolt.Member, str] = ""):
		if type(victim) != revolt.Member:
			return await ctx.send("You need to mention someone!")
		impostor = random.choice(["true", "false"])
		if "impost" in ctx.message.content:
			impostor = "true"
		elif "crewmate" in ctx.message.content:
			impostor = "false"
		url = str(victim.avatar.url)
		name = str(victim.name)[0:35]
		file = await asyncimage(f"https://some-random-api.ml/premium/amongus?avatar={url}&key={sr_api_key}&username={name}&imposter={impostor}", f"eject{ctx.message.id}.gif")
		await ctx.send(
			f"<@{ctx.author.id}>",
			file=file
		)
		rm = shlex.split(f"bash -c 'rm ./eject{ctx.message.id}.gif'")
		subprocess.check_call(rm)

	@commands.command(aliases=["font", "write"])
	async def text(self, ctx, *, text):
		if text == None:
			return await ctx.send("You have to give something to write, you sussy baka!")
		mytext = urllib.parse.quote(text).upper()
		file = await asyncimage(f"https://img.dafont.com/preview.php?text={mytext}&ttf=among_us0&ext=1&size=57&psize=m&y=58", "text.png")
		await ctx.send(
			f"<@{ctx.author.id}>",
			file=file
		)

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

	@commands.command(aliases=["twerk", "amogus", "furry", "twist", "isaac", "bounce"])
	async def dumpy(self, ctx, number: typing.Union[int, str] = 10, victim: typing.Union[revolt.Member, str] = None):
		await bot.wait_until_ready()
		loop = asyncio.get_running_loop()
		messageid = str(ctx.message.id)
		if type(number) != int:
			number = 10
		if number > 40 or number < 1:
			return await ctx.send("Number must be between 1 and 40! Defaults to 10.")
		if len(ctx.message.attachments) > 0:
			await ctx.message.attachments[0].save(f"attach_{messageid}.png")
		else:
			if victim != None and type(victim) == revolt.Member:
				await asyncimage(str(victim.avatar.url, f"attach_{messageid}.png"))
			else:
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
					f"<@{ctx.author.id}>",
					file=revolt.File(Image.open(filename), filename=filename)
				)
			except:
				await ctx.send("An error occurred! I might not have the permission `Attach Files` in this channel.")
			rmcmds = [
				shlex.split(f"bash -c 'rm ./attach_{messageid}.png'"),
				shlex.split(f"bash -c 'rm ./dumpy{messageid}.gif'")
			]
			for i in rmcmds:
				subprocess.check_call(i)

async def main():
	async with aiohttp.ClientSession() as session:
		client = Client(session, token)
		await client.start()

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
	file = revolt.File(img, filename=filename)
	return file

asyncio.run(main())
