#make some line graphs

import sqlite3

conn = sqlite3.connect('mgooddata.sqlite')
cur = conn.cursor()

cur.execute('SELECT Degrees.id, Degrees.mathematician_id, Degrees.university_id, Degrees.year, Degrees.type, Degrees.title, Degrees.MSCnumber, Universities.id, Universities.name, Universities.nation_id, Nations.id, Nations.name, Mathematicians.id, Mathematicians.name, Mathematicians.MSNid FROM Degrees JOIN Universities ON Degrees.university_id = Universities.id JOIN Nations ON Universities.nation_id = Nations.id JOIN Mathematicians ON Degrees.mathematician_id = Mathematicians.id')
deglist = list()
#(name, MSNid, uni name, uni nation, year, type, title, MSC)
for degree_row in cur:
    deglist.append((degree_row[13], degree_row[14], degree_row[8], degree_row[11], degree_row[3], degree_row[4], degree_row[5], degree_row[6]))
print('Loaded', len(deglist), 'degrees')

#find top 10 schools, nations, MSC numbers
unicounts = dict()
nationcounts = dict()
MSCcounts = dict()
for deg in deglist:
    uni = deg[2]
    nation = deg[3]
    MSC = deg[7]
    if not MSC is None:
        MSCcounts[MSC] = MSCcounts.get(MSC, 0) + 1
    unicounts[uni] = unicounts.get(uni, 0) + 1
    nationcounts[nation] = nationcounts.get(nation, 0) + 1

unis = sorted(unicounts, key = unicounts.get, reverse = True)
unis = unis[:10]
nations = sorted(nationcounts, key = nationcounts.get, reverse = True)
nations = nations[:10]
MSCs = sorted(MSCcounts, key = MSCcounts.get, reverse = True)
MSCs = MSCs[:10]

print(unis)
print(nations)
print(MSCs)

YEARSTART = 1900
YEAREND = 2024
YEARS = range(YEARSTART, YEAREND + 1)

#make dictionaries tracking number of degs for top 10 unis/nations/MSCs in range YEARS
uniyearcounts = dict()
nationyearcounts = dict()
MSCyearcounts = dict()
for deg in deglist:
    year = deg[4]
    uni = deg[2]
    nation = deg[3]
    MSC = deg[7]
    if year is None:
        continue
    elif YEARSTART > year or year > YEAREND:
        continue
    if uni in unis:
        unikey = (year, uni)
        uniyearcounts[unikey] = uniyearcounts.get(unikey, 0) + 1
    if nation in nations:
        nationkey = (year, nation)
        nationyearcounts[nationkey] = nationyearcounts.get(nationkey, 0) + 1
    if MSC in MSCs:
        MSCkey = (year, MSC)
        MSCyearcounts[MSCkey] = MSCyearcounts.get(MSCkey, 0) + 1
        
#make js file for graph of number of degrees of top unis per year
fhand = open('mdegsbyuni.js','w')
fhand.write("mdegsbyuni = [ ['Year'")
for uni in unis:
    fhand.write(",'" + uni + "'")
fhand.write("]")

for year in YEARS:
    fhand.write(",\n['" + str(year) + "'")
    for uni in unis:
        key = (year, uni)
        val = uniyearcounts.get(key, 0)
        fhand.write("," + str(val))
    fhand.write("]");

fhand.write("\n];\n")
fhand.close()

#make js file for graph of number of degrees of top nations per year
fhand = open('mdegsbynation.js','w')
fhand.write("mdegsbynation = [ ['Year'")
for nation in nations:
    fhand.write(",'"+nation+"'")
fhand.write("]")

for year in YEARS:
    fhand.write(",\n['" + str(year) + "'")
    for nation in nations:
        key = (year, nation)
        val = nationyearcounts.get(key, 0)
        fhand.write("," + str(val))
    fhand.write("]");

fhand.write("\n];\n")
fhand.close()

#make js file for graph of number of degrees of top MSC numbers per year
fhand = open('mdegsbyMSC.js','w')
fhand.write("mdegsbyMSC = [ ['Year'")
for MSC in MSCs:
    fhand.write(",'"+str(MSC)+"'")
fhand.write("]")

for year in YEARS:
    fhand.write(",\n['" + str(year) + "'")
    for MSC in MSCs:
        key = (year, MSC)
        val = MSCyearcounts.get(key, 0)
        fhand.write("," + str(val))
    fhand.write("]");

fhand.write("\n];\n")
fhand.close()

print('Output written to mdegsbyuni.js, mdegsbynation.js, mdegsbyMSC.js')
