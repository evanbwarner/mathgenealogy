# mathgenealogy
some fun with the mathematics genealogy project

Here is some simple code to scrape and organize some of the data from the Mathematics Genealogy Project (https://www.genealogy.math.ndsu.nodak.edu/). 

Important note: if you do use this code, please send a few bucks to the Project to cover any costs it might incur: https://northdakotastate-ndus.nbsstore.net/mathematics-genealogy-project-donation

This repository is all written in Python 3; it also uses the database software SQLITE.

1. mload.py scrapes the site and dumps a "relevant chunk" of the html of each webpage (corresponding to a person) in a SQLITE database mdata.sqlite. The process can be aborted and restarted at any point and is very time-consuming. The database mdata.sqlite has one table Pages having columns id (the MGP's id for each person) and html (the "relevant chunk" of html, as a string). After completion mdata.sqlite will be about 780MB.

2. mnormalize.py uses mdata.sqlite to create a SQLITE database mgooddata.sqlite, storing the relevant data in a clean and relational way. There are five tables in mgooddata.sqlite: 
      Mathematicians with columns id (the MGP's id), name, and MSNid (MathSciNet ID)
      Nations with columns id, name
      Universities with columns id, name, nation_id
      Degrees with data id, mathematician_id, university_id, year, type (e.g. 'PhD'), title (dissertation title), dissMSC (Mathematics Subject Classification number of the dissertation)
      AdvisingRelationships with data id, degree_id, advisor_id (pointing to an entry in Mathematicians table)
To justify this, note that a single mathematician may have more than one degree, each with more than one advisor. Theoretically one might want a 'degree type' table but it would be a bit ad hoc (lots of translations, etc.) so I didn't bother even if it is a bit redundant data-wise. After completion mgooddata.sqlite will be about 52MB. There data in the MGP is not always presented in a consistent way, so some arbitrary choices have to be made for a few pages in every thousand (see, e.g., the page for Arthur Cayley: https://www.genealogy.math.ndsu.nodak.edu/id.php?id=7824). mnormalize.py builds a list of these problematic pages if you want to clean up even more by hand.

3. There are a few files that extract some of the data in various simple ways. The file mhistograms.py counts degrees by year, university, and nation and prints out the top 10 from each. The file mline.py writes some json files that graph number of degrees per top 10 universities, nations, and MSC numbers over time. To view after running, open mdegsbyuni.htm, mdegsbynation.htm, and mdegsbyMSC.htm, respectively. The file mdisstitles.py answers a few questions I had about dissertation titles: it tracks the average length of dissertation titles over time (it doesn't change much!) and uses an automatic language detection package langid to guess the language of each dissertation title. Results by year and language are passed to json files and can be viewed at mdegsbylang.htm. The graph supports anecdotal evidence that French has held on better than German as English slowly crowds out everything else.
