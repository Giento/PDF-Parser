import glob
import json
import os
from collections import Counter

from MySearch import get_folders, get_urls

if __name__ == "__main__":
    # getting all folders in current working directory
    folders = get_folders()

    urls = {}

    for folder in folders:
        os.chdir("C:/FER/projektR/" + folder)
        for file in glob.glob("*.pdf"):
            pdf_urls = get_urls(folder, file)
            for url in pdf_urls:
                if url not in urls:
                    urls[url] = {'count': 1, 'pdf_files': {file}}
                else:
                    urls[url]['count'] += 1
                    urls[url]['pdf_files'].add(file)
            break
        break

    urls_sorted = dict(sorted(urls.items(), key=lambda x: x[1]['count'], reverse=True))

    for url in urls:
        urls[url]['pdfs_count'] = len(urls[url]['pdf_files'])

    occurrences = dict(Counter(urls))

    # sort by count or, in this case pdfs_count
    # sortirano je po broju razlicitih radova u kojima se pojavilo
    occurrences_sorted = dict(
        sorted(occurrences.items(), key=lambda x: x[1]['pdfs_count'], reverse=True)
    )
    print(occurrences_sorted)

    with open("C:/FER/projektR/occurrences.json", "w") as outfile:
        pass
        # json.dump(occurrences, outfile)
