try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("You need to install psycopg2 from pip")
    exit()
import requests
import time
import argparse
import datetime
import os

import mysql.connector as msql

print('Misskey Emoji Export Tool v1.0')
print('(C)2022 CyberRex\n')

parser = argparse.ArgumentParser(description='Misskey Emoji Export Tool')
parser.add_argument('-s', '--host', help='hostname of database server', required=True)
parser.add_argument('-u', '--username', help='username to login database', required=True)
parser.add_argument('-p', '--password', help='password to login database', required=True)
parser.add_argument('-d', '--database', help='name of database', required=True)
parser.add_argument('--include-remote', help='include remote emoji', default=False, action='store_true')
parser.add_argument('--port', type=int, help='port of database server (optional, Default: 5432)', default=5432, required=False)

args = parser.parse_args()

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; MisskeyDBEmojiExportTool)'

print(f'Connecting to {args.username}@{args.host}:{args.port}...' , end='')
try:
    db = psycopg2.connect(database=args.database, user=args.username, password=args.password, host=args.host, port=args.port or 5432)
except Exception as e:
    print('Failed!')
    print(str(e))
db.commit()
print('OK\n')

with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute('SELECT * FROM "public"."emoji" ' + ('WHERE "host" IS NULL' if not args.include_remote else ''))
    r = [dict(x) for x in cur.fetchall()]


outdir = 'emoji_export_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
os.mkdir(outdir)

for emoji in r:
    print(f'Downloading {emoji["name"]}...', end='')
    name = os.path.splitext(emoji['url'])

    if len(name) == 1:
        print('Skipping (no file extension)')
        continue

    fname = f'{emoji["name"]}{name[1]}'

    r = requests.get(emoji['url'], headers={'User-Agent': USER_AGENT})
    if r.status_code != 200:
        print(f'Failed! ({r.status_code})')
        continue

    ftype = r.headers.get('Content-Type')

    if name[1] == '':
        if ftype == 'image/png':
            fname = f'{emoji["name"]}.png'
        elif ftype == 'image/jpeg' or ftype == 'image/jpg':
            fname = f'{emoji["name"]}.jpg'
        elif ftype == 'image/svg+xml':
            fname = f'{emoji["name"]}.svg'
        elif ftype == 'image/webp':
            fname = f'{emoji["name"]}.webp'
        elif ftype == 'image/bmp':
            fname = f'{emoji["name"]}.bmp'
        elif ftype == 'image/gif':
            fname = f'{emoji["name"]}.gif'

    with open(f'{outdir}/{fname}', 'wb') as f:
        f.write(r.content)
    print('OK')

db.close()
print('ALL DONE!')
