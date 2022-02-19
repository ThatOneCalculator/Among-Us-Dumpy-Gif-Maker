# Adapted from https://github.com/CyberRex0/miq-fedi/blob/main/bot.py

import asyncio
import websockets
import aiofiles
import aiohttp
import validators
import sys
import subprocess
from misskey import Misskey
from async_timeout import timeout
from dotenv import dotenv_values

token = dotenv_values(".env")["MISSKEY_TOKEN"]
url = dotenv_values(".env")["MISSKEY_URL"]

WS_URL = f"wss://{url}/streaming?i={token}"
msk = Misskey(url, i=token)
i = msk.i()
session = aiohttp.ClientSession()

receivedNotes = set()


async def on_post_note(note):
    pass


async def on_mention(note):
    if note['id'] in receivedNotes:
        return

    receivedNotes.add(note['id'])
    print(note['files'])
    command = False
    split_text = note['text'].split(' ')
    new_st = []

    for t in split_text:
        if t.startswith('@'):
            if (not t == f'@{i["username"]}') and (not t == f'@{i["username"]}@{url}'):
                pass
            else:
                new_st.append(t)
        else:
            new_st.append(t)

    note['text'] = ' '.join(new_st)

    try:
        content = note['text'].strip().split(' ', 1)[1].strip()
        command = True
    except IndexError:
        pass

    if note.get('reply'):
        reply_note = note['reply']
        if reply_note['user']['id'] == MY_ID:
            return

        if reply_note['cw']:
            reply_note['text'] = reply_note['cw'] + '\n' + reply_note['text']

        img = BASE_WHITE_IMAGE.copy()
        if not reply_note['user'].get('avatarUrl'):
            msk.notes_create(text='アイコン画像がないので作れません', reply_id=note['id'])
            return
        async with session.get(reply_note['user']['avatarUrl']) as resp:
            if resp.status != 200:
                msk.notes_create(text='アイコン画像ダウンロードに失敗しました',
                                 reply_id=note['id'])
                return
            avatar = await resp.read()

        # icon = Image.open(BytesIO(avatar))
        # icon = icon.resize((720, 720), Image.ANTIALIAS)

        id = reply_note['user']['username']
        try:
            data = BytesIO()
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
            msk.notes_create(
                "I'm such a sussy baka...I couldn't even complete my upload task! I must be the impostor...",
                reply_id=note['id'])
            return

        msk.notes_create(text='.', file_ids=[f['id']], reply_id=note['id'])
        return

    if command:

        if content == 'ping':

            postdate = datetime.datetime.fromisoformat(
                note['createdAt'][:-1]).timestamp()
            nowdate = datetime.datetime.utcnow().timestamp()
            sa = nowdate - postdate
            text = f'{sa*1000:.2f}ms'
            msk.notes_create(text=text, reply_id=note['id'])


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

        print('Listening ws')
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
