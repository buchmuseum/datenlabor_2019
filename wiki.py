"""
Scraping von Wikipedia

Beispielskript für das Datenlabor der DNB, Workshop vom 16. bis 18. September
2019 in der Deutschen Nationalbibliothek Leipzig

Autoren: André Wendler und Ramon Voges

Lizenz: CC BY
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.parse

# Deutsche Wikipediaseiten
base_url = "https://de.wikipedia.org/wiki/"
# Wonach wir suchen
term = "17._September"
# Beides ergibt zusammen unsere URL
search = base_url + term

# Laden der Seite und verknüpfen mit der Bezeichnung 'html'
html = urlopen(search)

# Parsen des HTML-Codes
soup = BeautifulSoup(html, 'html.parser')

# Wir suchen einen span, der die ID 'Vor_dem...' hat.
# Dann gehen wir zu seinem Eltern-Tag.
# Und suchen das nächste Geschwistertag, in dem wir alle li-Elemente auswählen.
# Um die Schritte zu verdeutlichen: print(section)
section = soup.find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')
#  section = soup.find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')

# Eine Liste für unsere Links
links = []
# Greife auf jedes li-Element in dem Abschnitt zu.
for list_item in section:
    # Wichtig: Wir löschen links die Zeichen "/", "w", "i" und "k"
    links.append(list_item.find('a').find_next_sibling()["href"].lstrip("/wik"))

# Zur Kontrolle geben wir die Liste aus.
print(links)

# Nimm aus der Links-Liste jeden Link...
for link in links:
    # Zur Kontrolle
    print(base_url + link)
    # Rufe die Seite auf
    site = urlopen(base_url + link)
    # Parse die Seite
    person_wiki = BeautifulSoup(site, 'html.parser')
    # Schreibe in das Verzeichnis "wiki" die entsprechende Text-Datei
    # Zusatz-Feature: Nutze urllib und wandle den Namen schön um.
    # Damit es keine Probleme mit den Dateiendungen gibt: Tilge die Pubkte
    # HINWEIS: Vorher muss das Verzeichnis wiki angelegt werden!
    with open("wiki/" + urllib.parse.unquote(link).strip(".") + ".txt", 'w') as f:
        f.write(person_wiki.get_text())
