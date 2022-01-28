try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("You need to install psycopg2 from pip")
    exit()
import requests
import time
import argparse

print('Misskey Icon Repairing Tool v1.0')
print('(C)2021 CyberRex\n')

parser = argparse.ArgumentParser(description='Misskey Icon Repairing Tool')
parser.add_argument('-s', '--host', help='hostname of database server', required=True)
parser.add_argument('-u', '--username', help='username to login database', required=True)
parser.add_argument('-p', '--password', help='password to login database', required=True)
parser.add_argument('-d', '--database', help='name of database', required=True)
parser.add_argument('--port', type=int, help='port of database server (optional, Default: 5432)', default=5432, required=False)
parser.add_argument('-a' , '--acct', help='Account name (single mode)', required=False)

args = parser.parse_args()

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; MisskeyDBRepairTool)'

print(f'Connecting to {args.username}@{args.host}:{args.port}...')
db = psycopg2.connect(database=args.database, user=args.username, password=args.password, host=args.host, port=args.port or 5432)
db.commit()
print('\n')

with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    if args.acct:
         u = args.acct.split('@', 1)
         if len(u)!=2:
            print('Bad acct')
            exit()
         cur.execute('SELECT * FROM "public"."user" WHERE "host" = %s AND "username" = %s', (u[1], u[0]))
    else:
         cur.execute('SELECT * FROM "public"."user" WHERE "host" IS NOT NULL')
    r = [dict(x) for x in cur.fetchall()]

for user in r:
    print(f'Fetching {user["username"]}@{user["host"]}\'s metadata...', end='')
    # Fetch WebFinger
    try:
        r = requests.get(f'https://{user["host"]}/.well-known/webfinger?resource=acct:{user["username"]}@{user["host"]}', headers={'User-Agent': USER_AGENT})
        if r.status_code != 200:
            print(f'Failed ({r.status_code})\n')
            continue
        webfinger = r.json()
    except:
        print('Failed (exception)\n')
        continue
    # Parse webfinger infomation
    i = [x for x in webfinger['links'] if x['rel'] == 'self']
    if not i:
        print('Failed (Bad WebFinger infomation)\n')
        continue
    profile_url = i[0]
    print('OK')
    print(f'Fetching {user["username"]}@{user["host"]}\'s profile...', end='')
    try:
        r = requests.get(profile_url['href'], headers={'Accept': profile_url['type'], 'User-Agent': USER_AGENT})
        if r.status_code != 200:
            if r.status_code == 404:
                print('Failed (User not found)\n')
                continue
            print(f'Failed ({r.status_code})\n')
            continue
        profile = r.json()
    except:
        print('Failed (exception)\n')
        continue
    print('OK')
    print(f'Updating {user["username"]}@{user["host"]}\'s icon...', end='')
    # Update Icon
    if profile.get('icon'):
        icon_url = profile['icon']['url']
        with db.cursor() as cur:
            cur.execute('UPDATE "public"."user" SET "avatarUrl" = %s WHERE "id" = %s', (icon_url, user['id']))
        print('OK\n')
    else:
        print('Skipping (No icon)\n')
    
    time.sleep(0.1)


print('Commiting to Database...', end='')
db.commit()
print('Completed.\n')
print('**REWRITING SUCCESS**')
db.close()
