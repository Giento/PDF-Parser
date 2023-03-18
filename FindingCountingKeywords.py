import glob
import os
import re
from collections import Counter

from PyPDF2 import PdfReader

from MySearch import get_keywords


def find_keywords(folder, file, keywords_to_find):
    kwrds = []
    print(keywords_to_find)

    pdf = PdfReader("C:/FER/projektR/" + folder + "/" + file)
    for page in pdf.pages:
        text = page.extract_text()
        text = ''.join(text.split())
        for keyword in keywords_to_find:
            kwrds.extend(
                re.findall(keyword, text)
            )
    return kwrds


if __name__ == "__main__":
    folder = "01 S_P IEEE"
    keywords_to_find = get_keywords()
    keywords = []
    os.chdir("C:/FER/projektR/" + folder)

    for file in glob.glob("*.pdf"):
        keywords.extend(find_keywords(folder, file, keywords_to_find))
        # break

    keywords_count = dict(Counter(keywords))

    print(keywords_count)
