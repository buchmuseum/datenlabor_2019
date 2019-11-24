#!/usr/bin/env python
# coding: utf-8

# # Scraping von Wikidata

# Zuerst werden die notwendigen Bibliotheken eingebunden.

# In[1]:


import requests

import pandas as pd


# Jetzt erstellen wir einen String, mit der SPARQL-Abfrage: Wir suchen Name, Ort, Bezeichnung des Ortes, seine Koordinaten und das Geburtsdatum.
# 
# Danach legen wir die URL für die Suchabfrage fest.

# In[2]:


query = """
SELECT ?name ?place ?placeLabel ?coord ?date
WHERE {   
    ?person wdt:P1477 ?name;    # Irgendeine Person mit der Eigenschaft "hat Namen"
            wdt:P569 ?date;     # Person mit Geburtsdatum
            wdt:P19 ?place.     # Person mit Geburtsort
    ?place wdt:P625 ?coord.     # Von dem Ort die Koordinaten 
    FILTER (datatype(?date) = xsd:dateTime) # Das Datum hat das Format eines Datums
    FILTER (month(?date) = 11)              # 11. Monat = November
    FILTER (day(?date) = 26)                # 26. Tag des Monats
    FILTER (year(?date) <= 1900)            # Jahresbereich eingrenzen
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
 } 
"""
url = 'https://query.wikidata.org/sparql'


# Anschließend übergeben wir den String an die Such-URL. Die Serverantwort ist ein in JSON serialisiertes Dictionary.

# In[3]:


data = requests.get(url, params={'query': query, 'format': 'json'}).json()
# data 


# Im JSON sind die uns interessierenden Daten unter 'results' und 'bindings' abgelegt. Wir erstellen eine neue Liste namens 'personen' und tragen dort von jedem Eintrag die jeweiligen Werte aus `name`, `birthday`, `place` und `coord` ein. Diese Bezeichnungen stammen aus unserer SPARQL-Abfrage.

# In[4]:


personen = []
for item in data['results']['bindings']:
    personen.append({'name': item['name']['value'],
                    'birthday': item['date']['value'],
                    'place': item['placeLabel']['value'],
                    'coord': item['coord']['value']}
                   )
personen[:5]


# Jetzt erstellen aus der Liste einen Dataframe.

# In[5]:


df = pd.DataFrame(personen)
df.head()


# Das Format in der Spalte `birthday` ist noch nicht im Datumsformat. Das ändern wir hiermit.

# In[6]:


df['birthday'] = pd.to_datetime(df['birthday'])
df.tail()


# Nun greifen wir auf jeden Eintrag in der `coord`-Spalte, übergeben den Wert an die Lambda-Funktion, entfernen den String 'Point()', erstellen eine Liste und greifen auf den ersten Wert zurück, den wir im Dataframe unter `lon` ablegen.

# In[7]:


df['lon'] = df['coord'].apply(lambda x: x.strip('Point()').split()[0])
df['lon'] = df['lon'].astype(float)
df['lon']


# Das gleiche machen wir für die Spalte `lat`.

# In[8]:


df['lat'] = df['coord'].apply(lambda x: x.strip('Point()').split()[1])
df['lat'] = df['lat'].astype(float)
df['lat']


# Nun binden wir `plotly.express` ein und erstellen eine Karte.

# In[9]:


import plotly.express as px


# In[10]:


px.scatter_geo(df, lon='lon', lat='lat', scope='europe', text='place')


# In[ ]:




