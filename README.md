# misskey-scripts
This place storing useful scripts which made by me.

## icon-repair
Repair broken remote user's icon.
This script will be tried to repair icons by re-fetching remote users profile directly.

**Note: This script bypasses cache settings of Misskey. If you did run this script, URL of icon will be replaced with remote URL. Maybe data usage of clients are increased.**

Requirements: Python3.7+, requests, psycopg2

Usage: `python3 misskey-icon-repair.py -s HOST_TO_DB_SERVER -u USERNAME -p PASSWORD -d DATABASE_NAME [-p DB_SERVER_PORT]`