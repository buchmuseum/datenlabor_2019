"""
Scraping von Wikidata II

Beispielskript für das Datenlabor der DNB, Workshop vom 16. bis 18. September
2019 in der Deutschen Nationalbibliothek Leipzig

Autoren: André Wendler und Ramon Voges

Lizenz: CC BY
"""

# Wie bei wiki.py
from urllib.request import urlopen
import urllib.parse
from bs4 import BeautifulSoup

# Neue Importe
import wptools
import re

import pandas as pd

import geopy.geocoders as geo
from geopy.extra.rate_limiter import RateLimiter

import plotly.express as px


def get_soup(url):
    """Get the BeautifulSoup object for URL"""
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_links(url):
    """Find all the links in the specified section"""
    section = get_soup(url).find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')
    links = []
    for list_item in section:
        links.append(list_item.find('a').find_next_sibling()["href"].lstrip("/wik"))
    return links

def get_wikidata(url):
    """Get wikidata for every person in URL"""
    wikidata = []
    links = get_links(url)
    for link in links:
        person = {}
        person['name'] = urllib.parse.unquote(link).replace("_", " ")
        person['wiki_link'] = base_url + link
        soup_person = get_soup(person['wiki_link'])
        wikidata_link = soup_person.find('li', {'id': 't-wikibase'}).find('a')['href']
        pattern = re.compile(r'Q\d+')
        id = pattern.search(wikidata_link).group()
        page = wptools.page(wikibase=id, lang='de')
        page.get_wikidata()
        place_of_birth = page.data.get('wikidata').get('Geburtsort (P19)') or None
        person['place_of_birth'] = re.sub(r"\(Q[0-9]*\)", "", place_of_birth) if place_of_birth else None
        wikidata.append(person)
    return wikidata

def geolocate(wikidata, place):
    """Geolocate the PLACE in WIKIDATA"""
    geolocator = geo.Nominatim(user_agent='wikidata')
    geo.options.default_timeout = 10
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for data in wikidata:
        if data[place]:
            data['GeoData'] = geocode(data[place])
            data['Latitude'] = data['GeoData'].latitude
            data['Longitude'] = data['GeoData'].longitude
    return wikidata

def plot_data(wikidata, place):
    """Plot a map for PLACE in WIKIDATA"""
    data = geolocate(wikidata, place)
    df = pd.DataFrame(data)
    fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', scope='europe',
                        hover_data=['name', 'place_of_birth'], color='name')
    fig.write_html('orte.html')

if __name__ == "__main__":
    base_url = "https://de.wikipedia.org/wiki/"
    term = "17._September"
    search = base_url + term
    data = get_wikidata(search)
    plot_data(data, 'place_of_birth')
