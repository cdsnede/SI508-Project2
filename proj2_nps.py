from secrets import google_places_key
from alternate_advanced_caching import *
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json

####################
## set up classes ##
####################

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NationalSite():
    def __init__(self, type, name, desc, url=None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url

        address = requests.get(base+url).text
        addressSoup=BeautifulSoup(address, 'html.parser')
        addressP=addressSoup.find('p', class_='adr')
        self.address_street = addressP.find('span', itemprop='streetAddress').text
        self.address_city = addressP.find('span', itemprop='addressLocality').text
        self.address_state = addressP.find('span', itemprop='addressRegion').text
        self.address_zip = addressP.find('span', itemprop='postalCode').text

    def __str__(self):
        #need to add in self.address_street - has weird line break
        return "{}, ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)


class NearbyPlace():
    def __init__(self, name):
        self.name = name


############################
## homepage cache and run ##
############################
cache_file = "nps.json"
site="nps"
topic="national_sites"
cache = Cache(cache_file)
base = "https://www.nps.gov"

def create_id(site, topic):
    return "{}_{}.json".format(site, topic)

UID = create_id(site, topic)
response = cache.get(UID)

if response == None:
    response = requests.get(base).text
    cache.set(UID, response, 7)

def process_homepage(response):
        #parse homepage, find state link, go to state link, retrieve list of parks
        soup = BeautifulSoup(response, 'html.parser')
        searchbar=soup.find('body').find_all('div', class_='SearchBar')
        menu=searchbar[0].find('ul', class_='dropdown-menu')
        links=menu.find_all('a')
        stateurls=[]
        slash='/'
        for link in links:
            stateurls.append(link.get('href'))
        return stateurls

stateurls=process_homepage(response)
#######################
#     get state info     #
#######################
#original do not delete
#def create_id(site, topic):
#    return "{}_{}_{}.json".format(site, topic, str(datetime.now()).replace(' ', ''))



## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    #find state link, go to state link, retrieve list of parks
    slash='/'
    splitstate=[]
    for state in stateurls:
        splitstate.append(state.split("/"))
    for i in splitstate:
        if i[2] == state_abbr:
            go_to_state=slash.join(i)
            stateinfo = requests.get(base+go_to_state).text
            statesoup=BeautifulSoup(stateinfo, 'html.parser')
            parksoup=statesoup.find_all('ul',id="list_parks")
            sites=parksoup[0].find_all('li', class_='clearfix')
            parklist=[]
            for site in sites:
                type=site.find('h2').text
                name=site.find('h3').find('a').text
                desc=site.find('p').text
                parkurl=site.find('h3').find('a').get('href')
                park = NationalSite(type, name, desc, parkurl)
                parklist.append(park)
            return parklist

abbrev='ok'
parklist=get_sites_for_state(abbrev)
for park in parklist:
    print(park)

## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    return []

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    pass

## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    pass
