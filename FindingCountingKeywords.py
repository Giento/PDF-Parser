import glob
import json
import os
import re
from collections import Counter
from pathlib import Path
from multiprocessing import Pool
import time

from PyPDF2 import PdfReader

from MySearch import get_keywords


def find_keywords(folder, file, keywords_to_find):
    kwrds = []
    print(keywords_to_find)

    pdf_path = Path("C:/FER/projektR") / folder / file
    pdf = PdfReader(str(pdf_path))
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
    start = time.time()

    with Pool() as pool:
        keywords = pool.starmap(find_keywords, [(folder, file, keywords_to_find) for file in glob.glob("*.pdf")])

    keywords_count = dict(Counter(keyword for sublist in keywords for keyword in sublist))

    keywords_count_sorted = dict(
        sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)
    )

    end = time.time()
    print(end - start)

    with open("./found_keywords.json", "w") as outfile:
        json.dump(keywords_count_sorted, outfile)
