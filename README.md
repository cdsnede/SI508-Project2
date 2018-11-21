# Name: Courtney Snede

# Files Needed

- proj2_nps.py
- secrets.py
- alternate_advanced_caching.py
- cache.json (my program will create this for you the first time you run it.)

# Dependencies Needed

1. This is a python program. I use python3 so I know it works with that. I haven't checked older versions.

2. Keys needed (they're free):
 - Google API key with the Places API enabled (save your API key in the secrets.py file)
 - Plotly (username, key go in Plotly's credentials file. See their documentation for details)

3. Other libraries/modules needed:
 - BeautifulSoup (BS4)
 - datetime  
 - requests
 - json
 - Plotly (installation instructions here: https://plot.ly/python/getting-started/)

# Description of program

This program works via the command prompt. Based on what you enter this program can scrape information about National Sites from NPS.gov, use Google's Places API to get the location coordinates of those sites as well as nearby places, and display these results as a scatter plot map in your browser (via Plotly). Each time you run a valid command the results are saved the cache file. Further searches of the same name will pull from the cache until 7 days after your original search.

# Running the program

1. Save your Google Places API key in the secrets.py folder.
2. Save your Plotly username & key in the Plotly credentials file per their instructions (https://plot.ly/python/getting-started/)
3. Run this in your command prompt: python3 proj2_nps.py
4. Enter any of the commands listed below to interact with the program.

# Valid Command Prompts

- exit : Exits the program
- help : Lists available command prompts
- list : 2 part command. 2nd part is a state abbreviation. This prints a numbered list of all National Sites in the state you specified.
- After running 'list' you can run the following 2 commands:
- nearby : 2 part command. 2nd part is the number of the site in your list that you want to get nearby places for. (This command only works after you've run <list>.)
- map : This has 2 possibilities. If you run <list> then <map> you'll get a map of your list (National Sites in the state you chose). If you run <list> then <nearby> (and a number) then <map>, you'll get a map of places nearby the site you chose. The blue star icons are National Sites. Orange circles are the places nearby the site.

# Examples of possible output
![alt text](https://github.com/cdsnede/SI508-Project2/blob/master/Example_Command_Prompt.png "Example of National Site List")

![alt text](https://github.com/cdsnede/SI508-Project2/blob/master/Example_Map.png "Example of National Site Map")
