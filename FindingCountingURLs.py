import glob
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

from MySearch import get_folders, get_urls


def process_pdf_file(file, folder):
    pdf_urls = get_urls(folder, file)
    file_urls = {}
    for url, page_num in pdf_urls:
        if url not in file_urls:
            file_urls[url] = {'count': 1, 'pdf_files': {file}, 'page_nums': [page_num]}
        else:
            file_urls[url]['count'] += 1
            file_urls[url]['pdf_files'].add(file)
            file_urls[url]['page_nums'].append(page_num)
    return file_urls


def merge_url_dicts(dict1, dict2):
    for url, data in dict2.items():
        if url not in dict1:
            dict1[url] = {'count': data['count'], 'pdf_files': data['pdf_files'], 'page_nums': [data['page_nums']]}
        else:
            dict1[url]['count'] += data['count']
            dict1[url]['pdf_files'].update(data['pdf_files'])
            dict1[url]['page_nums'].extend(data['page_nums'])


if __name__ == "__main__":
    # getting all folders in current working directory
    folders = get_folders()[0:4]

    urls = {}

    start = time.time()

    for folder in folders:
        os.chdir("C:/FER/projektR/" + folder)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_pdf_file, file, folder) for file in glob.glob("*.pdf")]

            for future in futures:
                merge_url_dicts(urls, future.result())

    urls_sorted = dict(sorted(urls.items(), key=lambda x: x[1]['count'], reverse=True))

    for url in urls:
        urls[url]['pdfs_count'] = len(urls[url]['pdf_files'])

    occurrences = dict(Counter(urls))

    # sort by count or, in this case pdfs_count
    # sortirano je po broju razlicitih radova u kojima se pojavilo
    occurrences_sorted = dict(
        sorted(occurrences.items(), key=lambda x: x[1]['pdfs_count'], reverse=True)
    )

    end = time.time()

    print(occurrences_sorted)

    print(end - start)

    with open("C:/FER/projektR/occurrences_multi.json", "w") as outfile:
        pass
        # json.dump(occurrences, outfile)
