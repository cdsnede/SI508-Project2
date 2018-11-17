from secrets import google_places_key
from alternate_advanced_caching import *
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import plotly

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

        base = "https://www.nps.gov"
        #address = requests.get(base+url).text
        address = check_cache(base+url)
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

    def __str__(self):
        return self.name
############################
## NPS homepage cache and run ##
############################
cache_file = "cache.json"
cache = Cache(cache_file)
#site="nps"
#topic="national_sites"

#original createid. do not delete
#def create_id(site, topic):
#    return "{}_{}_{}.json".format(site, topic, str(datetime.now()).replace(' ', ''))

def create_uid(base, params=None):
    if params:
        return "{}_{}.json".format(base, params)
    else:
        return "{}.json".format(base)

def check_cache(base, params=None):
    if params:
        UID=create_uid(base, params)
        response = cache.get(UID)
        if response == None:
            response = requests.get(base, params).text
            cache.set(UID, response, 7)
    else:
        UID=create_uid(base)
        response = cache.get(UID)
        if response == None:
            response = requests.get(base).text
            cache.set(UID, response, 7)
    return response

def get_state_urls():
    #parse homepage, find state link, go to state link, retrieve list of parks
    base = "https://www.nps.gov"
    response=check_cache(base)
    soup = BeautifulSoup(response, 'html.parser')
    searchbar=soup.find('body').find_all('div', class_='SearchBar')
    menu=searchbar[0].find('ul', class_='dropdown-menu')
    links=menu.find_all('a')
    stateurls=[]
    slash='/'
    for link in links:
        stateurls.append(link.get('href'))
    return stateurls

stateurls=get_state_urls()
#######################
#     get state info     #
#######################

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    #state_abbr=state_abbr.lower()#find state link, go to state link, retrieve list of parks
    slash='/'
    base = "https://www.nps.gov"
    splitstate=[]
    for state in stateurls:
        splitstate.append(state.split("/"))
    for i in splitstate:
        if i[2] == state_abbr:
            go_to_state=slash.join(i)
            stateinfo=check_cache(base+go_to_state)
            #stateinfo = requests.get(base+go_to_state).text
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

abbrev='mi'
parklist=get_sites_for_state(abbrev)

    #eventually use this to do get_nearby_places(park)

#########################
## google places stuff ##
#########################

#paramsdict={'key':google_places_key}
#google_base = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

#def create_id(site, params):
#    return "{}_{}.json".format(site, params)

#googleUID = create_id(site, paramsdict)
#google_response = google_cache.get(googleUID)
#if google_response == None:
#    print('*********NOT IN CACHE***********')
#    google_response = requests.get(google_base, paramsdict)
#    google_places_info=json.loads(google_response.text)
#    google_cache.set(googleUID, google_places_info, 7)


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
##Define a function `get_nearby_places(site_object)` that accepts an instance of `NationalSite` as input, looks up a site by name using the Google Places AP,I and returns a list of up to 20 nearby places, where “nearby” is defined as within 10km (note: 20 results is the default maximum number returned by the Google Places API without paging).
#  - Getting the list of nearby places will require two calls to the google places API:
#    - one to get the GPS coordinates for a site (tip: do a text search for <site.name> <site.type>, e.g. “Death Valley National Park” or “Sleeping Bear Dunes National Lakeshore” instead of “Death Valley” or “Sleeping Bear”, to ensure a more precise match--it turns out there are lots of places called “Death Valley” that aren’t National Parks!),
#    - AND another one to get the places that are nearby that location.
 # - get_nearby_places(site_object) should return a list of `NearbyPlace` instances.

def get_nearby_places_for_site(national_site):
    paramsdict={}
    paramsdict['key']='AIzaSyDQGvVsAJfiMnnzQBjsUW-9Oou_1Sx2PAc'
    paramsdict['input']='{} {}'.format(national_site.name, national_site.type)
    paramsdict['inputtype']='textquery'
    paramsdict['fields']='geometry'
    site_base = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    placedata=check_cache(site_base, paramsdict)
    findplace=json.loads(placedata)
    coords=''
    for place in findplace['candidates']:
        latitude=place['geometry']['location']['lat']
        longitude=place['geometry']['location']['lng']
        coords=str(latitude)+','+str(longitude)
    nearby_paramsdict={}
    nearby_paramsdict['location']=coords
    nearby_paramsdict['key']='AIzaSyDQGvVsAJfiMnnzQBjsUW-9Oou_1Sx2PAc'
    nearby_paramsdict['radius']=10000
    nearby_base='https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    nearby_data=check_cache(nearby_base, nearby_paramsdict)
    nearbyplaces=json.loads(nearby_data)
    print(nearby_data) #not parsed yet, but works at geting 20 places

test_place=parklist[1]
get_nearby_places_for_site(test_place)
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
