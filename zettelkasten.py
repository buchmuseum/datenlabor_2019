"""
Kulturobjkte in Datenobjekte übertragen

Beispielskript für das Datenlabor der DNB, Workshop vom 16. bis 18. September
2019 in der Deutschen Nationalbibliothek Leipzig

Autoren: André Wendler und Ramon Voges

Lizenz: CC BY
"""

zettel1 = "Guido van Rossum, De Serpenti Libri, 1455"

autor = "Guido van Rossum"
zahl = 1455
titel = "De Serpenti Libri"

autor = autor.upper()
titel = titel.lower()
jahr = str(zahl)

# Konkatenieren
zettel2 = autor + ", " + jahr + ", " + titel
# Interpolieren
zettel3 = "{}, {}, {}".format(autor, jahr, titel)

kasten = [zettel1, zettel2]

kasten.append(zettel3)

print(kasten)
for zettel in kasten:
    print(zettel)

counted = len(kasten)
print(counted)

zettelkasten = []

zettel = {"author": autor, "title": titel, "year": zahl}
zettelkasten.append(zettel)
zettelkasten.append(zettel)
zettelkasten.append(zettel)

counter = 0
for zettel in zettelkasten:
    for k, v in zettel.items():
        print("{}: {}".format(k, v))
    counter += zettel.get("year")

print(counter)

finde = "Guido".upper()

if finde in zettel.get("author"):
    print('Hab ihn!')
else:
    print('Leider nicht gefunden...')
