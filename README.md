# Name: Courtney Snede

# Files Needed

- proj2_nps.py
- secrets.py
- alternate_advanced_caching.py
- cache.json (my program will create this for you the first time you run it.)

# Dependencies Needed

1. This is a python program. I use python3 so I know it works on that. I haven't checked older versions.

2. Accounts needed (they're free):
 - Google API key with the Places API enabled (save your API key in the secrets.py file)
 - Plotly (username, key go in Plotly's credentials file. See their documentation for details)

2. Other libraries/modules needed:
 - BeautifulSoup (BS4)
 - datetime  
 - requests
 - json
 - Plotly (installation instructions here: https://plot.ly/python/getting-started/)

# Description of program

This program works via the command prompt. Based on what you enter this program can scrape information about National Sites from NPS.gov, use Google's Places API to get the location coordinates of those sites as well as nearby places, and display these results as a scatter plot map in your browser (via Plotly).

## Command Prompts

- exit : Exits the program
- help : Lists available command prompts
- list : 2 part command. 2nd part is a state abbreviation. This prints a numbered list of all National Sites in the state you specified.
- nearby : 2 part command. 2nd part is the number of the site in your list that you want to get nearby places for. This command only works after you've run <list>.
- map : This will display a map of a list (national sites) or nearby places (1 national site + nearby places), depending on what command you ran last. The Star icons are National Sites. The Circles are the places nearby the site.
