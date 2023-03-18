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

    for page in pdf.pages:
        o = page.getObject()
        if o.__contains__(key):
            ann = o[key]
            for a in ann:
                u = a.getObject()
                if ank in u.keys():
                    if u[ank].get(uri):
                        pdf_urls.extend(
                            re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', u[ank][uri])
                        )
        else:
            text = page.extract_text()
            text = ''.join(text.split())
            pdf_urls.extend(
                re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
            )
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
