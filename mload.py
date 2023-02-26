import urllib.request, urllib.parse, urllib.error
import ssl
import sqlite3
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


conn = sqlite3.connect('mdata.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Pages (id INTEGER PRIMARY KEY, html TEXT)')

MAX_ID = 293000

baseurl = 'https://www.genealogy.math.ndsu.nodak.edu/id.php?id='


# Pick up where we left off
start = None
cur.execute('SELECT max(id) FROM Pages' )
try:
    row = cur.fetchone()
    if row is None:
        start = 0
    else:
        start = row[0]
except:
    start = 0
if start is None:
    start = 0

many = 0
count = 0
while True:
    if many < 1:
        conn.commit()
        sval = input('How many pages:')
        if len(sval) < 1:
            break
        many = int(sval)
    start = start + 1
    if start > MAX_ID:
        print('Exceeded MAX_ID')
        break
    try:
        url = baseurl+str(start)
        print(url)
        document = urllib.request.urlopen(url, context=ctx)
        if document.getcode() != 200:
            print('Error on page:', document.getcode())
        else:
            html = document.read().decode()
        
            #this chunk of the webpage contains everything we need
            chunkstart = html.find('chtml.js') + 20
            chunkend = html.find('MGP ID') + 35
            chunk = html[chunkstart:chunkend]

            cur.execute('INSERT OR IGNORE INTO Pages (id, html) VALUES (?, ?)', (start, chunk))
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except:
        print('Unable to read page with id', start)

        
    count = count + 1
    many = many - 1

    if count % 50 == 0:
        conn.commit()
    if count % 100 == 0:
        time.sleep(2)

        
conn.commit()
cur.close()