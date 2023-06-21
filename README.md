# Analiza korištenja stručnih izvora u znanstvenim radovima iz područja kibernetičke sigurnosti

Ovaj Python projekt analizira sadržaj PDF datoteka, posebno citiranje URL-ova i ključnih riječi, te rezultate zapisuje u JSON datoteke. Također pruža funkcionalnost za daljnju obradu ovih rezultata i generiranje rangiranja, koja se spremaju kao TXT datoteke. Projekt se sastoji od četiri Python skripte:

- `main.py` je glavna skripta koja izvodi analizu PDF datoteka.
- `data_merger.py` sadrži pomoćnu klasu za spajanje rječnika, koja se koristi tijekom analize.
- `pdf_processor.py` definira klasu koja obrađuje jednu PDF datoteku, izvlačeći URL-ove i ključne riječi.
- `generate_tables.py` je samostalna skripta koja obrađuje izlazne JSON datoteke kako bi generirala rang liste, koje se spremaju kao TXT datoteke.

## Preduvjeti

Da biste pokrenuli ovaj projekt, trebat će vam:

- Python 3.7 ili noviji
- Python paketi `openpyxl`, `PyPDF2`, i `argparse` moraju biti instalirani. Instalirajte ih koristeći pip:

```
pip install openpyxl PyPDF2 argparse
```

## Pokretanje projekta

Projekt je dizajniran za pokretanje iz komandne linije.

### Pokretanje main.py

1. Pokrenite skriptu `main.py` koristeći sljedeću naredbu:

```
python main.py
```

Ova skripta analizira sve PDF datoteke u direktoriju projekta (koji je određen konstantom `PROJECT_PATH` u skripti), izvlači URL-ove i ključne riječi te sprema rezultate u dvije JSON datoteke (koje su određene konstantama `URLS_JSON_FILE` i `KEYWORDS_JSON_FILE` u skripti).

Skripta koristi listu ključnih riječi učitanu iz Excel datoteke (koju određuje konstanta `KEYWORDS_EXCEL_FILE` u skripti), te isključuje određene direktorije (koje određuje set `EXCLUDED_FOLDERS` u skripti).

### Pokretanje generate_tables.py

Nakon pokretanja `main.py`, možete pokrenuti `generate_tables.py` za daljnju obradu rezultata i generiranje rangiranja.

1. Pokrenite skriptu `generate_tables.py` koristeći sljedeću naredbu:

```
python generate_tables.py urls_file keywords_file to_remove_file output_file
```

Ova skripta prima četiri argumenta:

- `urls_file` je putanja do JSON datoteke s podacima URL-ova (npr. izlaz iz `main.py`).
- `keywords_file` je putanja do JSON datoteke s podacima ključnih riječi (npr. izlaz iz `main.py`).
- `to_remove_file` je putanja do tekstualne datoteke koja navodi domene ili ključne riječi koje treba isključiti iz rangiranja.
- `output_file` je prefiks za izlazne TXT datoteke. Generirat će se tri datoteke, s postfiksima `_introduction.txt`, `_research.txt`, i `_discussion_conclusion.txt`.

## Logiranje

Skripte bilježe informacije i pogreške u datoteku za bilježenje (određenu imenom datoteke u pozivu `logging.basicConfig` u `main.py`). Ako nešto pođe po zlu, provjerite ovu datoteku za više informacija.

## Modificiranje projekta

Možete modificirati konstante u `main.py` i `pdf_processor.py` kako biste promijenili direktorij projekta, datoteku s ključnim riječima i druge postavke.
