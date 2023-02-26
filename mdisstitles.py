#let's look at dissertation titles over time

import sqlite3
import langid

conn = sqlite3.connect('mgooddata.sqlite')
cur = conn.cursor()

cur.execute('SELECT Degrees.id, Degrees.mathematician_id, Degrees.university_id, Degrees.year, Degrees.type, Degrees.title, Degrees.MSCnumber, Universities.id, Universities.name, Universities.nation_id, Nations.id, Nations.name, Mathematicians.id, Mathematicians.name, Mathematicians.MSNid FROM Degrees JOIN Universities ON Degrees.university_id = Universities.id JOIN Nations ON Universities.nation_id = Nations.id JOIN Mathematicians ON Degrees.mathematician_id = Mathematicians.id')
deglist = list()
#(name, MSNid, uni name, uni nation, year, type, title, MSC)
for degree_row in cur:
    deglist.append((degree_row[13], degree_row[14], degree_row[8], degree_row[11], degree_row[3], degree_row[4], degree_row[5], degree_row[6]))
print('Loaded', len(deglist), 'degrees')

#count langs and make dictionaries tracking avg diss length, and number of disses per year in various langs
langcounts = dict()
dissyearlength = dict()
dissyearcounts = dict()
langyearcounts = dict()
for deg in deglist:    
    lang = langid.classify(deg[6])[0]
    langcounts[lang] = langcounts.get(lang, 0) + 1
    year = deg[4]
    if year is None:
        continue
    langkey = (year, lang)
    langyearcounts[langkey] = langyearcounts.get(langkey, 0) + 1
    length = len(deg[6])
    if length > 0: #don't want to consider if title not present
        dissyearcounts[year] = dissyearcounts.get(year, 0) + 1
        dissyearlength[year] = dissyearlength.get(year, 0) + length
    
langs = sorted(langcounts, key = langcounts.get, reverse = True)
langs = langs[:10]    
    
YEARSTART = 1900
YEAREND = 2024
YEARS = range(YEARSTART, YEAREND + 1)

#make js file for graph of number of degrees with diss in given lang per year
fhand = open('mdegsbylang.js','w')
fhand.write("mdegsbylang = [ ['Year'")
for lang in langs:
    fhand.write(",'" + lang + "'")
fhand.write("]")

for year in YEARS:
    fhand.write(",\n['" + str(year) + "'")
    for lang in langs:
        key = (year, lang)
        val = langyearcounts.get(key, 0)
        fhand.write("," + str(val))
    fhand.write("]");

fhand.write("\n];\n")
fhand.close()

print('Avg. length of diss. title by year in characters')
for year in YEARS:
    try:
        avg = float(dissyearlength[year])/float(dissyearcounts[year])
        print(str(year) + ':', avg)
    except:
        continue