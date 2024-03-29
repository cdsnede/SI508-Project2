from secrets import google_places_key
from alternate_advanced_caching import *
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import plotly.plotly as py

####################
## set up classes ##
####################

class NationalSite():
    def __init__(self, type, name, desc, url=None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url

        base = "https://www.nps.gov"
        address = check_cache(base+url)
        addressSoup=BeautifulSoup(address, 'html.parser')
        try:
            addressP=addressSoup.find('p', class_='adr')
            self.address_street = addressP.find('span', itemprop='streetAddress').text.replace("\n", "")
            self.address_city = addressP.find('span', itemprop='addressLocality').text.replace("\n", "")
            self.address_state = addressP.find('span', itemprop='addressRegion').text.replace("\n", "")
            self.address_zip = addressP.find('span', itemprop='postalCode').text.replace("\n", "")
        except:
            self.address_street = "Not Listed"
            self.address_city = "Not Listed"
            self.address_state = "Not Listed"
            self.address_zip = "Not Listed"

    def __str__(self):
        return "{}, ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)


class NearbyPlace():
    def __init__(self, name, lng, lat):
        self.name = name
        self.lng = lng
        self.lat = lat

    def __str__(self):
        return self.name

##################
## set up cache ##
##################
#data from the same search will expire after 7 days. to change this modify the integer in lines 67 & 73
cache_file = "cache.json"
cache = Cache(cache_file)

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

######################
## set up functions ##
######################

def get_state_urls():
    #parses NPS.gov homepage, returns list of all state URLs
    base = "https://www.nps.gov"
    response = check_cache(base)
    soup = BeautifulSoup(response, 'html.parser')
    searchbar = soup.find('body').find_all('div', class_='SearchBar')
    menu = searchbar[0].find('ul', class_='dropdown-menu')
    links = menu.find_all('a')
    stateurls = []
    slash='/'
    for link in links:
        stateurls.append(link.get('href'))
    return stateurls


def get_sites_for_state(state_abbr):
    #takes a state abbreviation, returns list of all national sites for that state
    stateurls = get_state_urls()
    slash = '/'
    base = "https://www.nps.gov"
    splitstate = []
    for state in stateurls:
        splitstate.append(state.split("/"))
    for i in splitstate:
        if i[2] == state_abbr:
            go_to_state = slash.join(i)
            stateinfo = check_cache(base+go_to_state)
            statesoup = BeautifulSoup(stateinfo, 'html.parser')
            parksoup = statesoup.find_all('ul',id="list_parks")
            sites = parksoup[0].find_all('li', class_='clearfix')
            parklist = []
            for site in sites:
                type = site.find('h2').text
                name = site.find('h3').find('a').text
                desc = site.find('p').text
                parkurl = site.find('h3').find('a').get('href')
                park = NationalSite(type, name, desc, parkurl)
                parklist.append(park)
            return parklist


def get_googleapi_coordinates(national_site):
    #takes a NationalSite class instance, returns the latitude & longitude coordinates of the site
    paramsdict = {}
    paramsdict['key'] = google_places_key
    paramsdict['input'] = '{}_{}'.format(national_site.name, national_site.type)
    paramsdict['inputtype'] = 'textquery'
    paramsdict['fields'] = 'geometry,formatted_address'
    site_base = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    placedata = check_cache(site_base, paramsdict)
    findplace = json.loads(placedata)
    latitude = 0
    longitude = 0
    formatted_address = ''
    for place in findplace['candidates']:
        try:
            formatted_address = place['formatted_address']
            formatted_address = formatted_address.split()
            latitude = place['geometry']['location']['lat']
            longitude = place['geometry']['location']['lng']
            return latitude,longitude,formatted_address
        except:
            return latitude,longitude,formatted_address


def get_nearby_places_for_site(national_site):
    #takes a NationalSite class instance and returns a list of (up to) 20 nearby places
    paramsdict = {}
    paramsdict['key'] = google_places_key
    paramsdict['input'] = '{} {}'.format(national_site.name, national_site.type)
    paramsdict['inputtype'] = 'textquery'
    paramsdict['fields'] = 'geometry'
    site_base = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    placedata = check_cache(site_base, paramsdict)
    findplace = json.loads(placedata)
    coords = ''
    for place in findplace['candidates']:
        try:
            latitude = place['geometry']['location']['lat']
            longitude = place['geometry']['location']['lng']
            coords = str(latitude)+','+str(longitude)
        except:
            print("Sorry, we couldn't find that location. Try another.")
    nearby_paramsdict = {}
    nearby_paramsdict['location'] = coords
    nearby_paramsdict['key'] = google_places_key
    nearby_paramsdict['radius'] = 10000
    nearby_base = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    nearby_data = check_cache(nearby_base, nearby_paramsdict)
    nearbyplaces = json.loads(nearby_data)
    nearbyplaces_list = []
    for loc in nearbyplaces['results']:
        lat = loc['geometry']['location']['lat']
        lng = loc['geometry']['location']['lng']
        name = loc['name']
        nearbyplaces_list.append(NearbyPlace(name,lng,lat))
    return nearbyplaces_list


def plot_sites_for_state(state_abbr):
    #accepts state abbrev, creates Plotly map for national sites in that state
    lon_vals = []
    lat_vals = []
    text_vals = []
    statelist = get_sites_for_state(state_abbr)
    state_title = state_abbr.upper()
    for site in statelist:
        text_vals.append(site.name)
        sitecoords = get_googleapi_coordinates(site)
        if state_abbr == 'ca' or state_abbr == 'ak':
            if site.address_state == 'HI':
                sitecoords = (0,0,0)
        if sitecoords and sitecoords[0] != 0:
            lat_vals.append(sitecoords[0])
        if sitecoords and sitecoords[1] != 0:
            lon_vals.append(sitecoords[1])

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat -1, max_lat+1]
    lon_axis = [min_lon-1, max_lon+1]
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    data = [dict(type = 'scattergeo', locationmode = 'USA-states', lon = lon_vals, lat = lat_vals, text = text_vals, mode = 'markers', marker = dict(size = 8, symbol = 'star',))]

    layout = dict(title = 'National Sites in {}<br>(Hover for names)'.format(state_title), geo = dict(scope='usa', projection=dict(type='albers usa'),showland = True, landcolor = "rgb(250, 250, 250)", subunitcolor = "rgb(100, 217, 217)", countrycolor = "rgb(217, 100, 217)", lataxis = {'range': lat_axis}, lonaxis = {'range': lon_axis}, center= {'lat': center_lat, 'lon': center_lon }, countrywidth = 3, subunitwidth = 3))

    fig = dict(data=data, layout=layout)
    py.plot(fig, validate=False, filename='National Sites by State')



def plot_nearby_for_site(site_object):
    #accepts a NationalSite instance, creates Plotly map for up to 20 nearby places
    natl_site_lon_vals = []
    natl_site_lat_vals = []
    natl_site_text_vals = []
    natl_site_text_vals.append(site_object.name)
    natl_site_data=get_googleapi_coordinates(site_object)
    if natl_site_data[0] != 0:
        natl_site_lat_vals.append(natl_site_data[0])
    if natl_site_data[1] != 0:
        natl_site_lon_vals.append(natl_site_data[1])

    nearby_sites_lon_vals = []
    nearby_sites_lat_vals = []
    nearby_sites_text_vals = []
    nearbylist = get_nearby_places_for_site(site_object)
    for nearby_place in nearbylist:
        nearby_sites_text_vals.append(nearby_place.name)
        nearby_sites_lat_vals.append(nearby_place.lat)
        nearby_sites_lon_vals.append(nearby_place.lng)

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in nearby_sites_lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in nearby_sites_lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat -1, max_lat+1]
    lon_axis = [min_lon-1, max_lon+1]
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    trace1=dict(type = 'scattergeo', locationmode = 'USA-states', lon = natl_site_lon_vals, lat = natl_site_lat_vals, text = natl_site_text_vals, mode = 'markers', marker = dict(size = 8, symbol = 'star',))

    trace2=dict(type = 'scattergeo', locationmode = 'USA-states', lon = nearby_sites_lon_vals, lat = nearby_sites_lat_vals, text = nearby_sites_text_vals, mode = 'markers', marker = dict(size = 6, symbol = 'circle'))

    data = [trace1, trace2]

    layout = dict(title = 'Places Nearby {}<br>(Hover for names)'.format(site_object.name), geo = dict(scope='usa', projection=dict(type='albers usa'),showland = True, landcolor = "rgb(250, 250, 250)", subunitcolor = "rgb(100, 217, 217)", countrycolor = "rgb(217, 100, 217)", lataxis = {'range': lat_axis}, lonaxis = {'range': lon_axis}, center= {'lat': center_lat, 'lon': center_lon }, countrywidth = 3, subunitwidth = 3))

    fig = dict(data=data, layout=layout)

    py.plot(fig, validate=False, filename='Nearby Sites')


##########
## main ##
##########
sites_list = None
sitename = None
inp = input("Hi! Enter a command to start the program. Enter 'help' for a list of commands.: ")
inp = inp.lower()
lastcommand = ''
while inp != 'exit':
    if inp == 'help':
        print("Valid commands include: \n * <list> * followed by <state abbreviation> in the next prompt. This returns a numbered list of national sites in that state.\n * <help> * Returns this list of commands \n * <exit> * To exit program. \n\n After running the <list> command you can also run: \n * <map> * Shows a map of national sites in the state you chose.\n * <nearby> * followed by a <number> in the next prompt. This returns a list of places nearby the site you chose.\n * After running <nearby> you can also run <map> to see a map of the nearby sites.\n")
    elif inp == 'list':
        lastcommand = 'list'
        state_abbr = input("Enter valid state abbreviation: ")
        state_abbr = state_abbr.lower()
        try:
            sites_list = get_sites_for_state(state_abbr)
            counter = 1
            for pl in sites_list:
                print(counter, pl)
                counter+=1
        except:
            print('Not a valid state abbreviaton')
    elif inp == 'nearby':
        lastcommand='nearby'
        if not sites_list:
            print("Oops! You have to enter <list> before entering <nearby>")
        else:
            num = input("Enter the number of the place you want to search nearby (see your list above): ")
            try:
                index = int(num)-1
                sitename = sites_list[index]
                nearbysites_list = get_nearby_places_for_site(sitename)
                if len(nearbysites_list) == 0:
                    print("Sorry. We couldn't find that site.")
                for p in nearbysites_list:
                    print(p)

            except:
                print("Oops! That wasn't a valid number")

    elif inp == 'map':
        if lastcommand == 'nearby':
            plot_nearby_for_site(sitename)
        elif lastcommand =='list':
            plot_sites_for_state(state_abbr)
        else:
            print("Oops! You have to enter <list> before entering <map>")
    else:
        print('Enter valid command: ')

    inp = input("Enter a command: ")
    inp = inp.lower()
