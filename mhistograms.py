import sqlite3

conn = sqlite3.connect('mgooddata.sqlite')
cur = conn.cursor()

#unpack dictionaries for nations, universities, degrees, mathematicians, advising relationships
cur.execute('SELECT Nations.id, Nations.name FROM Nations')
nations = dict()
for nation_row in cur:
    nations[nation_row[0]] = nation_row[1]

cur.execute('SELECT Universities.id, Universities.name, Universities.nation_id, Nations.id, Nations.name FROM Universities JOIN Nations ON Universities.nation_id = Nations.id')
universities = dict()
for university_row in cur:
    universities[university_row[0]] = (university_row[1], university_row[4])
print('Loaded', len(universities), 'universities')
    
cur.execute('SELECT Mathematicians.id, Mathematicians.name, Mathematicians.MSNid FROM Mathematicians')
mathematicians = dict()
for mathematician_row in cur:
    mathematicians[mathematician_row[0]] = (mathematician_row[1], mathematician_row[2])
print('Loaded', len(mathematicians), 'mathematicians')

cur.execute('SELECT Degrees.id, Degrees.mathematician_id, Degrees.university_id, Degrees.year, Degrees.type, Degrees.title, Degrees.MSCnumber, Universities.id, Universities.name, Universities.nation_id, Nations.id, Nations.name, Mathematicians.id, Mathematicians.name, Mathematicians.MSNid FROM Degrees JOIN Universities ON Degrees.university_id = Universities.id JOIN Nations ON Universities.nation_id = Nations.id JOIN Mathematicians ON Degrees.mathematician_id = Mathematicians.id')
degrees = dict()
#(name, MSNid, uni name, uni nation, year, type, title, MSC)
for degree_row in cur:
    degrees[degree_row[0]] = (degree_row[13], degree_row[14], degree_row[8], degree_row[11], degree_row[3], degree_row[4], degree_row[5], degree_row[6])
print('Loaded', len(degrees), 'degrees')

cur.execute('SELECT AdvisingRelationships.advisor_id, AdvisingRelationships.degree_id, Degrees.id, Degrees.mathematician_id, Degrees.university_id, Degrees.year, Degrees.type, Degrees.title, Degrees.MSCnumber, advisor.id, advisor.name, advisor.MSNid, advisee.id, advisee.name, advisee.MSNid, Nations.id, Nations.name, Universities.id, Universities.name, Universities.nation_id FROM AdvisingRelationships JOIN Degrees ON AdvisingRelationships.degree_id = Degrees.id JOIN Mathematicians advisee ON Degrees.mathematician_id = advisee.id JOIN Mathematicians advisor ON AdvisingRelationships.advisor_id = advisor.id JOIN Universities ON Degrees.university_id = Universities.id JOIN Nations ON Universities.nation_id = Nations.id')
advrels = list() #no advisingrelationships id, so just do a list of tuples
#(advsor name, advsor MSNid, advsee name, advsee MSNid, uni name, uni nation, year, type, title, MSC)
for advrel_row in cur:
    advrels.append((advrel_row[10], advrel_row[11], advrel_row[13], advrel_row[14], advrel_row[18], advrel_row[16], advrel_row[5], advrel_row[6], advrel_row[7], advrel_row[8]))
print('Loaded', len(advrels), 'advisor-advisee relationships')

deglist = list(degrees.values())

#count degrees by year, university, nation
yearcounts = dict()
unicounts = dict()
nationcounts = dict()
for deg in deglist:
    year = deg[4]
    uni = deg[2]
    nation = deg[3]
    yearcounts[year] = yearcounts.get(year, 0) + 1
    unicounts[uni] = unicounts.get(uni, 0) + 1
    nationcounts[nation] = nationcounts.get(nation, 0) + 1

#these are lists
sortedyears = sorted(yearcounts.items(), key=lambda x:x[1], reverse = True)
sortedunis = sorted(unicounts.items(), key=lambda x:x[1], reverse = True)
sortednations = sorted(nationcounts.items(), key=lambda x:x[1], reverse = True)

print('Top 10 years:')
for k in range(10):
    print('In', sortedyears[k][0], 'there were', sortedyears[k][1], 'degrees')
print('')
print('Top 10 universities:')
for k in range(10):
    print('There were', sortedunis[k][1], 'degrees awarded by', sortedunis[k][0])
print('')
print('Top 10 nations:')
for k in range(10):
    print('There were', sortednations[k][1], 'degrees awarded in', sortednations[k][0])