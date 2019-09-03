import wptools
import re


from urllib.request import urlopen
import urllib.parse
from bs4 import BeautifulSoup

import pandas as pd

import geopy.geocoders as geo
from geopy.extra.rate_limiter import RateLimiter

import plotly.express as px


base_url = "https://de.wikipedia.org/wiki/"
term = "17._September"
search = base_url + term

html = urlopen(search)

soup = BeautifulSoup(html, 'html.parser')

target = soup.find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')

links = []
for list_item in target:
    links.append(list_item.find('a').find_next_sibling()["href"].lstrip("/wik"))

data = []

for link in links:
    person = {}
    # name = re.sub("_", " ", link)
    # name = re.sub("%C3%BC", "ü", name)
    # name = re.sub("%C3%B6", "ö", name)
    # name = re.sub("%C3%A4", "ä", name)
    # name = re.sub("%E2%80%93", "–", name)
    person['name'] = urllib.parse.unquote(link)
    person['wiki_link'] = base_url + link
    html_person = urlopen(person['wiki_link'])
    soup_person = BeautifulSoup(html_person, 'html.parser')
    wikidata_link = soup_person.find('li', {'id': 't-wikibase'}).find('a')['href']
    print(wikidata_link)
    pattern = re.compile('Q\d+')
    id = pattern.search(wikidata_link).group()
    print(id)
    page = wptools.page(wikibase=id, lang='de')
    page.get_wikidata()
    # person['wiki_data'] = page.data.get('wikidata')
    if page.data.get('wikidata').get('Geburtsort (P19)'):
        place_of_birth = page.data.get('wikidata').get('Geburtsort (P19)')
        person['place_of_birth'] = re.sub(r"\(Q[0-9]*\)", "", place_of_birth)
        # print("Geboren: {}".format(place_of_birth))
    else:
        # print('Keine Angabe zum Geburtsort')
        person['place_of_birth'] = None
    if page.data.get('wikidata').get('Sterbeort (P20)'):
        place_of_death = page.data.get('wikidata').get('Sterbeort (P20)')
        person['place_of_death'] = re.sub(r"\(Q[0-9]*\)", "", place_of_death)
        # print("Gestorben: {}".format(place_of_death))
    else:
        # print('Keine Angabe zum Sterbeort')
        person['place_of_death'] = None        
    data.append(person)

# for d in data:
#     print(d)

df = pd.DataFrame(data)
# print(df.head())
df.to_excel('orte.xlsx', )

geolocator = geo.Nominatim(user_agent='wikidata')
geo.options.default_timeout = 10

geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

df['GeoData'] = df['place_of_birth'].apply(geolocator.geocode)

df['Latitude'] = df['GeoData'].apply(lambda x: x.latitude if x else None)
df['Longitude'] = df['GeoData'].apply(lambda x: x.longitude if x else None)

print(df.head())
print(df.tail())

fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', scope='europe',
                      hover_data=['name', 'place_of_birth'], color='name')

fig.write_html('orte.html')