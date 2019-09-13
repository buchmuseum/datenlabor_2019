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
    person['name'] = urllib.parse.unquote(link)
    # Der Wikidata-Link
    person['wiki_link'] = base_url + link
    # Lade die Seite zur Person
    html_person = urlopen(person['wiki_link'])
    # Lese die Seite aus und verarbeite sie
    soup_person = BeautifulSoup(html_person, 'html.parser')
    # Finde das li-Element mit der spezifischen ID
    # Finde in dem Element den Link und greife auf das Attribut href zu
    wikidata_link = soup_person.find('li', {'id': 't-wikibase'}).find('a')['href']
    # Sicherheitshalber ausgeben
    print(wikidata_link)
    # Erstelle einen Regulären Ausdruck für 'Q12345etc.'
    pattern = re.compile(r'Q\d+')
    # Suche nach diesem Pattern und verweise auf das Ergebnis mit 'id'
    id = pattern.search(wikidata_link).group()
    # Ausgeben
    print(id)
    # Jetzt kommt die Wikidata-Abfrage!
    # Rufe die deutsche Wikidata-Seite auf mit der entsprechende id
    page = wptools.page(wikibase=id, lang='de')
    # Lade die Daten herunter
    page.get_wikidata()
    # Falls ein Geburtsort eingetragen ist...
    # Im page-Objekt gibt es ein Attribut data. In diesem gibt es ein Dict
    # namens wikidata. Darin ist wiederum der Geburtsort...
    if page.data.get('wikidata').get('Geburtsort (P19)'):
        # Lege einen Verweis an
        place_of_birth = page.data.get('wikidata').get('Geburtsort (P19)')
        # Und speichere ihn im Dict ab.
        # Aber: Ersetze alles, was nach Wikidata-Bezeichnungen aussieht.
        # Suche im Ort nach 'Q' und Zahlen und ersetze mit einem leeren String
        person['place_of_birth'] = re.sub(r"\(Q[0-9]*\)", "", place_of_birth)
    # Falls es keinen Ort gibt, trage None ein.
    else:
        person['place_of_birth'] = None
    # Das gleiche für den Steerbeort.
    if page.data.get('wikidata').get('Sterbeort (P20)'):
        place_of_death = page.data.get('wikidata').get('Sterbeort (P20)')
        person['place_of_death'] = re.sub(r"\(Q[0-9]*\)", "", place_of_death)
    else:
        person['place_of_death'] = None
    # Zum Schluss: Ergänze die Liste um das Dict.
    data.append(person)


# Jetzt kommt es zu Pandas
# Erstelle einen neuen DataFrame und verweise auf ihn.
df = pd.DataFrame(data)
# Zum Abspeichern...
#  df.to_excel('orte.xlsx')

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
df['GeoData'] = df['place_of_birth'].apply(geolocator.geocode)

# Nimm die neue Spalte und trage den Latitude-Wert in eine neue Spalte ein.
# Lambda-funktionen: anonyme Funktionen, hier wieder wie mit einer For-Schleife
df['Latitude'] = df['GeoData'].apply(lambda x: x.latitude if x else None)
# Nimm die neue Spalte und trage den Longitude-Wert in eine neue Spalte ein.
df['Longitude'] = df['GeoData'].apply(lambda x: x.longitude if x else None)

# Ausgeben
print(df.head())
print(df.tail())

# Erstelle ein figure-Objekt, greife auf den DataFrame zurück...
fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', scope='europe',
                      hover_data=['name', 'place_of_birth'], color='name')

# Speiche das figure-Objekt in die Datei...
fig.write_html('orte.html')
