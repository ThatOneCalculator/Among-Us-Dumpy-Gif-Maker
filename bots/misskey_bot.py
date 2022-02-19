# Adapted from https://github.com/CyberRex0/miq-fedi/blob/main/bot.py

import asyncio
import websockets
import aiofiles
import json
import time
import aiohttp
import validators
import sys
import subprocess
from misskey import Misskey
from async_timeout import timeout
from dotenv import dotenv_values

token = dotenv_values(".env")["MISSKEY_TOKEN"]
url = dotenv_values(".env")["MISSKEY_URL"]
version = "4.2.1"

WS_URL = f"wss://{url}/streaming?i={token}"
msk = Misskey(url, i=token)
i = msk.i()

receivedNotes = set()

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

async def asyncimage(url, filename):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			f = await aiofiles.open(filename, mode="wb")
			await f.write(await resp.read())
			await f.close()

async def on_post_note(note):
    pass


async def on_mention(note):
    if note['id'] in receivedNotes:
        return
    receivedNotes.add(note['id'])
    if note.get('reply'):
        reply_note = note['reply']
        # msk.notes_create(
        #             "Test reply.",
        #             reply_id=note['id'])

        if len(reply_note['files']) == 0:
            msk.notes_create(
                text="I can't find an image to dumpify, you sussy impostor!",
                reply_id=note['id'])
            return

        imagename = f"attach_{postid}.png"
        async with session.get(reply_note['files'][0]['thumbnailUrl']) as resp:
            if resp.status != 200:
                msk.notes_create(
                    text="I'm such a sussy baka, I can't even download the image!~ *dies cutely*",
                    reply_id=note['id'])
                return
            image = await resp.read()

        postid = reply_note['id']
        image = Image.save(imagename, image)
        print("dumpifying")
        await asyncrun(f"java -jar ./Among-Us-Dumpy-Gif-Maker-{version}-all.jar --lines {lines} --file {imagename} {postid}")

        id = reply_note['user']['username']
        try:
            data = open(f"dumpy{postid}.gif", "rb")
            f = msk.drive_files_create(
                file=data, name=f'{datetime.datetime.utcnow().timestamp()}.jpg')
            msk.drive_files_update(
                file_id=f['id'], comment=f'"{reply_note["text"]}" —{reply_note["user"]["name"]}')
        except Exception as e:
            if 'INTERNAL_ERROR' in str(e):
                msk.notes_create(
                    "Misskey voted and ejected me! I wasn't even the impostor tho... :(",
                    reply_id=note['id'])
                return
            elif 'RATE_LIMIT_EXCEEDED' in str(e):
                msk.notes_create(
                    "I'm being ratelimited, you sussy baka! Try again in a bit.",
                    reply_id=note['id'])
                return
            else:
                msk.notes_create(
                    "I'm such a sussy baka...I couldn't even complete my upload task! I must be the impostor...",
                    reply_id=note['id'])
                return

        msk.notes_create(text="You're so sussy!", file_ids=[f['id']], reply_id=note['id'])
        return

async def on_followed(user):
    try:
        msk.following_create(user['id'])
    except:
        pass


async def main():
    print('Connecting to ' + url + '...', end='')
    async with websockets.connect(WS_URL) as ws:
        print('OK')
        print('Attemping to watching timeline...', end='')
        p = {
            'type': 'connect',
            'body': {
                'channel': 'globalTimeline',
                'id': 'GTL1'
            }
        }
        await ws.send(json.dumps(p))
        p = {
            'type': 'connect',
            'body': {
                'channel': 'homeTimeline',
                'id': 'HTL1'
            }
        }
        await ws.send(json.dumps(p))
        print('OK')
        p = {
            'type': 'connect',
            'body': {
                'channel': 'main'
            }
        }
        await ws.send(json.dumps(p))

        print('Listening to WebSocket')
        while True:
            data = await ws.recv()
            j = json.loads(data)
            if j['type'] == 'channel':
                if j['body']['type'] == 'note':
                    note = j['body']['body']
                    try:
                        await on_post_note(note)
                    except Exception as e:
                        print(traceback.format_exc())
                        continue

                if j['body']['type'] == 'mention':
                    note = j['body']['body']
                    try:
                        await on_mention(note)
                    except Exception as e:
                        print(traceback.format_exc())
                        continue

                if j['body']['type'] == 'followed':
                    try:
                        await on_followed(j['body']['body'])
                    except Exception as e:
                        print(traceback.format_exc())
                        continue


reconnect_counter = 0

while True:
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        break
    except:
        time.sleep(10)
        reconnect_counter += 1
        print('Reconnecting...', end='')
        if reconnect_counter > 10:
            print('Too many reconnects. Exiting.')
            sys.exit(1)
        continue
