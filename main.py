import glob
import json
import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict

import openpyxl

from data_merger import DataMerger
from pdf_processor import PDFProcessor

PROJECT_PATH = "C:/FER/projektR"
EXCLUDED_FOLDERS = {'.idea', '__pycache__'}
KEYWORDS_EXCEL_FILE = 'Obrada rezultata.xlsx'
URLS_JSON_FILE = "urls_new_gpt.json"
KEYWORDS_JSON_FILE = "keywords_new_gpt.json"

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_list_of_keywords() -> List[str]:
    try:
        wb = openpyxl.load_workbook(os.path.join(PROJECT_PATH, KEYWORDS_EXCEL_FILE))
        ws = wb.active

        keywords = [row[0] for row in ws.iter_rows(values_only=True) if row[0]]
        keywords.remove('TOTAL')

        return keywords
    except Exception as e:
        logger.error(f"Failed to get list of keywords. Error: {str(e)}")
        raise


def get_folders() -> List[str]:
    return [file for file in os.listdir(PROJECT_PATH) if os.path.isdir(file) and file not in EXCLUDED_FOLDERS]


def run(folders: List[str], keywords_to_find: List[str]):
    urls = {}
    keywords = {}

    for folder in folders:
        os.chdir(os.path.join(PROJECT_PATH, folder))
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(PDFProcessor(file, folder, keywords_to_find, PROJECT_PATH).run) for file in
                       glob.glob("*.pdf")]

            for future in futures:
                try:
                    file_urls, file_keywords = future.result()
                    DataMerger.merge_dicts(urls, file_urls)
                    DataMerger.merge_dicts(keywords, file_keywords)
                except Exception as e:
                    logger.error(f"Failed to process PDF files in folder {folder}. Error: {str(e)}")

    urls, keywords = process_final_data(urls), process_final_data(keywords)

    write_to_json_file(os.path.join(PROJECT_PATH, URLS_JSON_FILE), urls)
    write_to_json_file(os.path.join(PROJECT_PATH, KEYWORDS_JSON_FILE), keywords)


def process_final_data(data_dict: Dict[str, Dict]) -> Dict[str, Dict]:
    for key in data_dict:
        data_dict[key]['pdfs_count'] = len(data_dict[key]['pdf_files'])

    return dict(sorted(data_dict.items(), key=lambda item: item[1]['count'], reverse=True))


def write_to_json_file(file_path: str, data: Dict[str, Dict]):
    try:
        serializable_data = {
            key: {
                'count': value['count'],
                'pdf_files': list(value['pdf_files']),
                'pdfs_count': value['pdfs_count'],
                'page_nums': value['page_nums']
            }
            for key, value in data.items()
        }
        with open(file_path, "w") as outfile:
            json.dump(serializable_data, outfile)
    except Exception as e:
        logger.error(f"Failed to write data to JSON file {file_path}. Error: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        folders = get_folders()
        keywords_to_find = get_list_of_keywords()

        start = time.time()
        run(folders, keywords_to_find)
        print(f"Execution Time: {time.time() - start} seconds")
        logger.info(f"Execution Time: {time.time() - start} seconds")
    except Exception as e:
        logger.error(f"Program terminated with error: {str(e)}")
