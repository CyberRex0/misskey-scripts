const { Client } = require('pg')
const fs = require('fs')
const stream = require('stream')
const util = require('util')
const path = require('path')
const axios = require('axios')

const streamPipeline = util.promisify(stream.pipeline)
const CLA = require('command-line-args')
const cmdargs = [
    {
        name: 'user',
        alias: 'u',
        type: String,
    },
    {
        name: 'password',
        alias: 'p',
        type: String
    },
    {
        name: 'host',
        alias: 's',
        type: String
    },
    {
        name: 'database',
        alias: 'd',
        type: String
    },
    {
        name: 'include-remote',
        type: Boolean,
        defaultValue: false
    },
    {
        name: 'port',
        type: Number,
        defaultValue: 5432
    }
]

const args = CLA(cmdargs)

function checkArg(params, name) {
    if (!params[name]) {
        console.error(`--${name} is required`)
        process.exit(1)
    }
}

checkArg(args, 'user')
checkArg(args, 'password')
checkArg(args, 'host')
checkArg(args, 'database')



const db = new Client({
    user: args.user,
    password: args.password,
    host: args.host,
    database: args.database,
    port: args.port
})


async function main() {

    console.log('Misskey Emoji Export Tool v1.0-node\n(C)2022 CyberRex')

    process.stdout.write('Connecting to database...')
    await db.connect()
    process.stdout.write('OK\n\n')

    // 絵文字取得
    let where_clause = args['include-remote'] ? '' : 'WHERE host IS NULL'
    let emoji_query = await db.query('SELECT * FROM emoji ' + where_clause)

    let date = new Date()
    let datetime_str = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}_${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}`

    fs.mkdirSync('emoji_export_' + datetime_str)

    let outdir = 'emoji_export_' + datetime_str

    for (let i=0; i<emoji_query.rows.length; i++) {
        let emoji = emoji_query.rows[i]
        let fileext = path.extname(emoji.url)

        // 絵文字ダウンロード
        process.stdout.write('Downloading ' + emoji.name + '...')

        let r = null
        try {
            r = await axios.get(emoji.url, { responseType: 'arraybuffer' })
        } catch (e) {
            process.stdout.write(`Failed (${e.response.status})\n`) 
            continue
        }
        
        outname = `${emoji.name}`

        if (!fileext) {
            if (r.headers['content-type'] == 'image/png') {
                outname += '.png'
            }
            if (r.headers['content-type'] == 'image/jpeg') {
                outname += '.jpg'
            }
            if (r.headers['content-type'] == 'image/gif') {
                outname += '.gif'
            }
            if (r.headers['content-type'] == 'image/svg+xml' || r.headers['content-type'] == 'image/svg') {
                outname += '.svg'
            }
            if (r.headers['content-type'] == 'image/webp') {
                outname += '.webp'
            }
        } else {
            outname += fileext
        }

        fs.writeFileSync(outdir + '/' + outname, r.data)
        process.stdout.write('OK\n')
    }
}
main().then(function () {
    db.end().then(() => {
        print('ALL DONE!')
        process.exit(0)
    })
})