from urllib.request import urlopen
from bs4 import BeautifulSoup

# wikipedia.set_lang('de')

# seite = wikipedia.page('17. September')
base_url = "https://de.wikipedia.org"
what = "/wiki/"
term = "17._September"
search = base_url + what + term

html = urlopen(search)

soup = BeautifulSoup(html, 'html.parser')

# h3 = soup.find_all('h3')

# section = h3[8]

section = soup.find("span", {'id': 'Vor_dem_18._Jahrhundert'}).find_parent().find_next_sibling().find_all('li')


links = []
for list_item in section:
    links.append(list_item.find('a').find_next_sibling()["href"].lstrip("/wik"))

print(links)

for link in links:
    print(base_url + what + link)
    site = urlopen(base_url + what + link)
    person_wiki = BeautifulSoup(site, 'html.parser')
    with open("wiki/" + link.strip(".") + ".txt", 'w') as f: 
        f.write(person_wiki.get_text())