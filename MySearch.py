import os
import re

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


def get_urls(folder, file):
    pdf = PdfReader("C:/FER/projektR/" + folder + "/" + file)
    key = '/Annots'
    uri = '/URI'
    ank = '/A'
    pdf_urls = []

    for i, page in enumerate(pdf.pages):
        o = page.getObject()
        page_num = i + 1
        if o.__contains__(key):
            ann = o[key]
            for a in ann:
                u = a.getObject()
                if ank in u.keys():
                    if u[ank].get(uri):
                        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', u[ank][uri])
                        pdf_urls.extend([(url, page_num / len(pdf.pages)) for url in urls])
        else:
            text = page.extract_text()
            text = ''.join(text.split())
            urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
            pdf_urls.extend([(url, page_num / len(pdf.pages)) for url in urls])

    # remove doi.org domain
    # pdf_urls.remove('https://doi.org')

    # returns all found urls (in a single file!), contains duplicates!
    return pdf_urls


def get_keywords() -> object:
    wb = openpyxl.load_workbook('Obrada rezultata.xlsx')
    ws = wb.active

    keywords = []
    for row in ws.iter_rows(values_only=True):
        if row[0] is not None:
            keywords.append(row[0])

    # last row is TOTAL, so we have to remove it
    keywords.remove('TOTAL')

    return keywords
