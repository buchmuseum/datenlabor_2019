"""
Scraping von Wikidata

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


base_url = "https://de.wikipedia.org/wiki/"
term = "17._September"
search = base_url + term

html = urlopen(search)

soup = BeautifulSoup(html, 'html.parser')

section = soup.find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')

links = []
for list_item in section:
    links.append(list_item.find('a').find_next_sibling()["href"].lstrip("/wik"))


# Ab hier wird es neu...
# Eine Liste für die Daten
data = []

# Für jeden Eintrag in unserer Links-Liste...
for link in links:
    # Lege ein Dictionary an
    person = {}
    # Erster Eintrag: der Name, aber schön geschrieben...
    person['name'] = urllib.parse.unquote(link).replace("_", " ")
    # Der Wikidata-Link
    person['wiki_link'] = base_url + link
    # Lade die Seite zur Person
    html_person = urlopen(person['wiki_link'])
    # Lese die Seite aus und verarbeite sie
    soup_person = BeautifulSoup(html_person, 'html.parser')
    # Finde das li-Element mit der spezifischen ID
    # Finde in dem Element den Link und greife auf das Attribut href zu
    wikidata_link = soup_person.find('li', {'id': 't-wikibase'}).find('a')['href']

    # Erstelle einen Regulären Ausdruck für 'Q12345etc.'
    pattern = re.compile(r'Q\d+')
    # Suche nach diesem Pattern und verweise auf das Ergebnis mit 'id'
    id = pattern.search(wikidata_link).group()
    # Jetzt kommt die Wikidata-Abfrage!
    # Rufe die deutsche Wikidata-Seite auf mit der entsprechende id
    page = wptools.page(wikibase=id, lang='de')
    # Lade die Daten herunter
    page.get_wikidata()
    # Falls ein Geburtsort eingetragen ist...
    # Im page-Objekt gibt es ein Attribut data. In diesem gibt es ein Dict
    # namens wikidata. Darin ist wiederum der Geburtsort...    
    place_of_birth = page.data.get('wikidata').get('Geburtsort (P19)') or None
    # Wenn ein Geburtsort angegeben ist
    # if place_of_birth:
    #     # Speichere ihn im Dict ab
    #     person['place_of_birth'] = re.sub(r"\(Q[0-9]*\)", "", place_of_birth)
    # # Ansonsten trage None ein
    # else:
    #     person['place_of_birth'] = None
    person['place_of_birth'] = re.sub(r"\(Q\d+\)", "", place_of_birth) if place_of_birth else None

    data.append(person)

# Erstelle einen neuen Geolokalisator. User-Agent muss angegeben werden.
geolocator = geo.Nominatim(user_agent='wikidata')
# Sicherheitshalber...
geo.options.default_timeout = 10

# Um den Server nicht zu überlasten
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Nimm im DataFrame aus jeder Zeile den Geburtsort und übergib den Wert an den
# Geolokalisator, der die Koordination etc. abruft. Die zurückgegebenen Werte
# werden in einer neuen Spalte abgelegt.
# Wie eine For-Schleife, hier aber für Pandas.
# df['GeoData'] = df['place_of_birth'].apply(geolocator.geocode)
for d in data:
    if d['place_of_birth']:
        d['GeoData'] = geocode(d['place_of_birth'])
        d['Latitude'] = d['GeoData'].latitude
        d['Longitude'] = d['GeoData'].longitude

# Jetzt kommt es zu Pandas
# Erstelle einen neuen DataFrame und verweise auf ihn.
df = pd.DataFrame(data)
# Erstelle ein figure-Objekt, greife auf den DataFrame zurück...
fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', scope='europe',
                      hover_data=['name', 'place_of_birth'], color='name')

# Speiche das figure-Objekt in die Datei...
fig.write_html('orte.html')
