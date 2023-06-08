import glob
import json
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import openpyxl
from PyPDF2 import PdfReader


def get_folders():
    directories = []

    for file in os.listdir():
        if os.path.isdir(file):
            if file == '.idea' or file == '__pycache__':
                continue
            directories.append(file)

    return directories


def get_list_of_keywords() -> object:
    wb = openpyxl.load_workbook('Obrada rezultata.xlsx')
    ws = wb.active

    keywords = []
    for row in ws.iter_rows(values_only=True):
        if row[0] is not None:
            keywords.append(row[0])

    # last row is TOTAL, so we have to remove it
    keywords.remove('TOTAL')

    return keywords


def get_references(pdf_reader, keywords):
    references = {}

    num_pages = len(pdf_reader.pages)
    reference_section = False
    ref_string = ""

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        # Find the starting page of the references section
        if "REFERENCES" in text:
            reference_section = True

        # Extract information only if in reference section
        if reference_section:
            ref_string += text.replace('\n', ' ')

    ref_list = re.findall(r'\[\d+\][^\[]*', ref_string)
    for ref in ref_list:
        ref = ''.join(ref.split())
        number = re.search(r'\[(\d+)\]', ref).group(1)
        url = re.findall(r'(https?://\S+)', ref)
        matching_keywords = [keyword for keyword in keywords if keyword.lower() in ref.lower()]

        domain = ''
        if url:
            url = url[0].split()[
                0]  # Getting the first URL and removing any trailing whitespace or new line character if present
            domain = urlparse(url).netloc

        if number not in references.keys():
            references[number] = {'url': domain, 'keywords': matching_keywords}

    return references


def process_pdf_file(file, folder, keywords_to_find):
    references = {}
    path = Path("C:/FER/projektR") / folder / file
    file_path = str(path)
    file_identifier = str(folder) + '/' + str(file)

    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        references = get_references(pdf_reader, keywords_to_find)

    num_pages = len(pdf_reader.pages)
    url_dict = {}
    keyword_dict = {}

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        citation_blocks = re.findall(r'\[\d+(?:-\d+)?(?:,\s*\d+)*\]', text)
        for block in citation_blocks:
            block = block[1:-1]
            block_refs = block.split(',')
            for ref in block_refs:
                start, end = (ref.split('-') + [None])[:2]
                ref_range = range(int(start), int(end or start) + 1)
                for ref_num in ref_range:
                    ref_data = references.get(str(ref_num), None)
                    if ref_data:
                        url = ref_data.get('url', '')
                        if url:
                            if url not in url_dict:
                                url_dict[url] = {'count': 1, 'pdf_files': {file_identifier},
                                                 'page_nums': [(page_num + 1) / num_pages]}
                            else:
                                url_dict[url]['count'] += 1
                                url_dict[url]['pdf_files'].add(file_identifier)
                                url_dict[url]['page_nums'].append((page_num + 1) / num_pages)

                        keywords = ref_data.get('keywords', [])
                        for keyword in keywords:
                            if keyword not in keyword_dict:
                                keyword_dict[keyword] = {'count': 1, 'pdf_files': {file_identifier},
                                                         'page_nums': [(page_num + 1) / num_pages]}
                            else:
                                keyword_dict[keyword]['count'] += 1
                                keyword_dict[keyword]['pdf_files'].add(file_identifier)
                                keyword_dict[keyword]['page_nums'].append((page_num + 1) / num_pages)

    return url_dict, keyword_dict


def merge_url_dicts(dict1, dict2):
    for url, data in dict2.items():
        if url in dict1:
            dict1[url]['count'] += data['count']
            dict1[url]['pdf_files'].update(data['pdf_files'])
            dict1[url]['page_nums'].extend(data['page_nums'])
        else:
            dict1[url] = {'count': data['count'], 'pdf_files': data['pdf_files'], 'page_nums': data['page_nums']}
    return dict1


def merge_keyword_dicts(dict1, dict2):
    for keyword, data in dict2.items():
        if keyword in dict1:
            dict1[keyword]['count'] += data['count']
            dict1[keyword]['pdf_files'].update(data['pdf_files'])
            dict1[keyword]['page_nums'].extend(data['page_nums'])
        else:
            dict1[keyword] = {'count': data['count'], 'pdf_files': data['pdf_files'], 'page_nums': data['page_nums']}
    return dict1


def run(folders, keywords_to_find):
    urls = {}
    keywords = {}

    start = time.time()

    for folder in folders:
        os.chdir("C:/FER/projektR/" + folder)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_pdf_file, file, folder, keywords_to_find) for file in glob.glob("*.pdf")]

            for future in futures:
                file_urls, file_keywords = future.result()
                merge_url_dicts(urls, file_urls)
                merge_keyword_dicts(keywords, file_keywords)

    for url in urls:
        urls[url]['pdfs_count'] = len(urls[url]['pdf_files'])

    for keyword in keywords:
        keywords[keyword]['pdfs_count'] = len(keywords[keyword]['pdf_files'])

    urls = dict(sorted(urls.items(), key=lambda item: item[1]['count'], reverse=True))
    keywords = dict(sorted(keywords.items(), key=lambda item: item[1]['count'], reverse=True))

    end = time.time()

    print(end - start)

    with open("C:/FER/projektR/urls.json", "w") as outfile:
        urls_serializable = {
            url: {
                'count': data['count'],
                'pdf_files': list(data['pdf_files']),
                'pdfs_count': data['pdfs_count'],
                'page_nums': data['page_nums']
            }
            for url, data in urls.items()
        }
        json.dump(urls_serializable, outfile)

    with open("C:/FER/projektR/keywords.json", "w") as outfile:
        keywords_serializable = {
            keyword: {
                'count': data['count'],
                'pdf_files': list(data['pdf_files']),
                'pdfs_count': data['pdfs_count'],
                'page_nums': data['page_nums']
            }
            for keyword, data in keywords.items()
        }
        json.dump(keywords_serializable, outfile)


if __name__ == "__main__":
    # getting all folders in current working directory
    folders = get_folders()[0:1]
    keywords_to_find = get_list_of_keywords()

    run(folders, keywords_to_find)
