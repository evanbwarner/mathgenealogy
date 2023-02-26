import sqlite3
import html

VERBOSE = False

#read-only input from raw database
rawconn = sqlite3.connect('file:mdata.sqlite?mode=ro', uri=True)
rawcur = rawconn.cursor()

#writing to this database
conn = sqlite3.connect('mgooddata.sqlite')
cur = conn.cursor()


cur.execute('DROP TABLE IF EXISTS Mathematicians')
cur.execute('DROP TABLE IF EXISTS Nations')
cur.execute('DROP TABLE IF EXISTS Universities')
cur.execute('DROP TABLE IF EXISTS Degrees')
cur.execute('DROP TABLE IF EXISTS AdvisingRelationships')

cur.execute('CREATE TABLE IF NOT EXISTS Mathematicians (id INTEGER PRIMARY KEY UNIQUE, name TEXT, MSNid INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS Nations (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT UNIQUE)')
cur.execute('CREATE TABLE IF NOT EXISTS Universities (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT UNIQUE, nation_id INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS Degrees (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, mathematician_id INTEGER, university_id INTEGER, year INTEGER, type TEXT, title TEXT, MSCnumber INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS AdvisingRelationships (advisor_id INTEGER, degree_id INTEGER, UNIQUE(advisor_id, degree_id))')


rawcur.execute('SELECT id, html FROM Pages')

count = 0;
problems = set()
errors = set()

for page in rawcur:
    MGPid = int(page[0])
    rawhtml = page[1]
    if len(rawhtml) < 20:  #id not assigned to mathematician
        continue

    namebegin = rawhtml.find('>') + 2
    rawhtml = rawhtml[namebegin:]
    nameend = rawhtml.find('<')
    name = html.unescape(rawhtml[:nameend]).strip() #convert html to unicode
    name = ' '.join(name.split()) #remove weird double-spaces

    startMSNidchunk = rawhtml.find('small')
    endMSNidchunk = rawhtml.find('</p>')
    MSNidchunk = rawhtml[startMSNidchunk:endMSNidchunk]
    
    #in case there is a biography link and said link happens to have digits in it, we want to ignore them
    biog = MSNidchunk.find('Biography') 
    if not biog == -1:
        MSNidchunk = rawhtml[biog:endMSNidchunk]
    isMSNid = MSNidchunk.find('MathSciNet')
    if isMSNid == -1: #No MSN ID provided
        MSNid = None
    else:
        MSNid = int(''.join(filter(str.isdigit,MSNidchunk)))

    rawhtml = rawhtml[endMSNidchunk:]
    cur.execute('INSERT OR IGNORE INTO Mathematicians (id, name, MSNid) VALUES (?, ?, ?)', (MGPid, name, MSNid))
    if VERBOSE is True:
        print('Inserted into Mathematicians table: NAME', name, 'MSN ID', MSNid)
    
    temppos = rawhtml.find('/div')
    rawhtml = rawhtml[temppos:]
    
    while True: #loop through all degrees
        temppos = rawhtml.find('<')
        rawhtml = rawhtml[temppos:]
        
        if rawhtml[1] == 'p': #no more degrees
            break
        elif not rawhtml[1] == 'd': #if there are more degrees, should start with '<div'
            print('ERROR: data entry failed for', MGPid, name)
            errors.add(MGPid)
            
        startdegtype = rawhtml.find('0.5em') + 7
        rawhtml = rawhtml[startdegtype:]
        enddegtype = rawhtml.find('<') - 1
        degtype = html.unescape(rawhtml[:enddegtype]).strip()
        
        if degtype == '': #this means there is no degree, so break immediately
            break
        if degtype.find('/') != -1 or degtype.find(',') != -1:
            print('Caution: two or more degrees may be conflated for', MGPid, name)
            problems.add(MGPid)

        rawhtml = rawhtml[enddegtype:]
        startuni = rawhtml.find('>') + 1
        rawhtml = rawhtml[startuni:]
        enduni = rawhtml.find('<')
        uni = html.unescape(rawhtml[:enduni]).strip()
        
        startyear = rawhtml.find('>') + 1
        rawhtml = rawhtml[startyear:]
        endyear = rawhtml.find('<')
        yearstr = rawhtml[:endyear].strip()
        if yearstr.find(',') != -1: #if several years, take later one
            print('Caution: two or more degrees may be conflated for', MGPid, name)
            problems.add(MGPid)
            years = yearstr.split(',')
            yearstr = years[len(years)-1].strip()
        elif yearstr.find('/') != -1:
            print('Caution: two or more degrees may be conflated for', MGPid, name)
            problems.add(MGPid)
            years = yearstr.split('/')
            yearstr = years[len(years)-1].strip()
        elif yearstr.find('-') != -1:
            print('Caution: two or more degrees may be conflated for', MGPid, name)
            problems.add(MGPid)
            years = yearstr.split('-')
            yearstr = years[len(years)-1].strip()
        yearstr = ''.join(filter(str.isdigit, yearstr)) #sometimes the dates look like 'c. 1820'
        if yearstr == '': #sometimes the year is blank
            year = None
        else:
            try:
                year = int(yearstr)
            except:
                print('ERROR: parsing degree year failed for', MGPid, name)
                year = None
                errors.add(MGPid)
        
        endnationschunk = rawhtml.find('</div>')
        nationschunk = rawhtml[:endnationschunk]
        nation = ''
        
        while True: #loop through flags, keep last one
            nationpos = nationschunk.find('alt=')
            if nationpos == -1: #no more flags
                break
            startnation = nationpos + 5
            nationschunk = nationschunk[startnation:]
            endnation = nationschunk.find('\"')
            nation = html.unescape(nationschunk[:endnation]).strip()
        
        if not nation == '': #nation field may be blank
            cur.execute('INSERT OR IGNORE INTO NATIONS (name) VALUES (?)', (nation,))
            if VERBOSE is True:
                print('Inserted into Nations table: NAME', nation)
            cur.execute('SELECT id FROM Nations WHERE name = ?', (nation, ))
            nation_id = cur.fetchone()[0]
        else:
            nation_id = None
        
        if not uni == '': #occasionally the university field is blank
            cur.execute('INSERT OR IGNORE INTO UNIVERSITIES (name, nation_id) VALUES (?, ?)', (uni, nation_id))
            if VERBOSE is True:
                print('Inserted into Universities table: NAME', uni, 'NATION ID', nation_id)
            cur.execute('SELECT id FROM Universities WHERE name = ?', (uni, ))
            uni_id = cur.fetchone()[0]
        else:
            uni_id = None
        
        starttitle = rawhtml.find('thesisTitle') + 14
        rawhtml = rawhtml[starttitle:]
        endtitle = rawhtml.find('</span>')
        title = html.unescape(rawhtml[:endtitle]).strip()
        
        rawhtml = rawhtml[endtitle:]
        endMSCadvisorchunk = rawhtml.find('</p>')
        MSCadvisorchunk = rawhtml[:endMSCadvisorchunk]
        
        isMSC = MSCadvisorchunk.find('<div')
        if isMSC == -1: #No MSC number provided
            MSCnum = None
        else:
            MSCnumstart = MSCadvisorchunk.find('on:') + 4
            try:
                MSCnum = int(MSCadvisorchunk[MSCnumstart:MSCnumstart + 2])
            except:
                print('ERROR: Could not parse MSC number as integer for', MGPid, name)
                MSCnum = None
                errors.add(MGPid)
        
        cur.execute('INSERT OR IGNORE INTO Degrees (mathematician_id, university_id, year, type, title, MSCnumber) VALUES (?, ?, ?, ?, ?, ?)', (MGPid, uni_id, year, degtype, title, MSCnum))
        if VERBOSE is True:
            print('Inserted into Degrees table: MGPID', MGPid, 'UNI ID', uni_id, 'DEGREE TYPE', degtype, 'TITLE', title, 'MSC NUMBER', MSCnum)
        cur.execute('SELECT id FROM Degrees WHERE (mathematician_id, type, title) = (?, ?, ?)', (MGPid, degtype, title))
        degreeid = cur.fetchone()[0]
        
        preadvisorpos = MSCadvisorchunk.find('2.75') + 8
        advisorchunk = MSCadvisorchunk[preadvisorpos:]
        
        while True: #loop through all the advisors
            isadvisor = advisorchunk.find('href')
            if isadvisor == -1: #no more advisors
                break
            startadvisor = isadvisor + 16
            advisorchunk = advisorchunk[startadvisor:]
            endadvisor = advisorchunk.find('\"')
            try:
                advisorid = int(advisorchunk[:endadvisor])
            except:
                print('ERROR: Could not parse advisor ID as integer for', MGPid, name)
                errors.add(MGPid)
                break
            
            cur.execute('INSERT OR IGNORE INTO AdvisingRelationships (advisor_id, degree_id) VALUES (?, ?)', (advisorid, degreeid))
            if VERBOSE is True:
                print('Inserted into AdvisingRelationships table: ADVISOR ID', advisorid, 'DEGREE ID', degreeid)
        
        rawhtml = rawhtml[endMSCadvisorchunk + 2:]
    count = count + 1
    if count%1000 == 0:
        conn.commit()
        print('Scraped',count,'files')
conn.close()
print('Cautions issued for the following IDs:', problems)
print('Errors occurred for the following IDs:', errors)