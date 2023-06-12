import logging
import re
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, file: str, folder: str, keywords_to_find: List[str], project_path: str):
        self.file = file
        self.folder = folder
        self.keywords_to_find = keywords_to_find
        self.project_path = project_path
        self.references = {}
        self.url_dict = {}
        self.keyword_dict = {}

    def run(self):
        try:
            self._process_pdf_file(self.project_path)
            return self.url_dict, self.keyword_dict
        except Exception as e:
            logger.error(f"Failed to process PDF file {self.file}. Error: {str(e)}")
            raise

    def _get_references(self, pdf_reader):
        num_pages = len(pdf_reader.pages)
        reference_section = False
        ref_string = ""

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            if "REFERENCES" in text:
                reference_section = True

            if reference_section:
                ref_string += text.replace('\n', ' ')

        ref_list = re.findall(r'\[\d+\][^\[]*', ref_string)
        for ref in ref_list:
            ref = ''.join(ref.split())
            number = re.search(r'\[(\d+)\]', ref).group(1)
            url = re.findall(r'(https?://\S+)', ref)
            matching_keywords = [keyword for keyword in self.keywords_to_find if
                                 keyword.lower() in ref.lower()]

            domain = ''
            if url:
                url = url[0].split()[0]
                domain = urlparse(url).netloc

            if number not in self.references.keys():
                self.references[number] = {'url': domain, 'keywords': matching_keywords}

    def _process_pdf_file(self, project_path: str):
        path = Path(project_path) / self.folder / self.file
        file_path = str(path)
        file_identifier = str(self.folder) + '/' + str(self.file)

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                self._get_references(pdf_reader)
                self._extract_data_from_pdf(pdf_reader, file_identifier)
        except Exception as e:
            logger.error(f"Failed to read PDF file {file_path}. Error: {str(e)}")
            raise

    def _extract_data_from_pdf(self, pdf_reader, file_identifier):
        num_pages = len(pdf_reader.pages)
        for page_num, page in enumerate(pdf_reader.pages):
            end = False
            text = page.extract_text()
            citation_blocks = re.findall(r'\[\d+(?:\s*-\s*\d+)?(?:,\s*\d+)*\]', text)
            for block in citation_blocks:
                if "REFERENCES" in text and block == '[1]':
                    end = True
                    break
                block = block[1:-1]
                block_refs = block.split(',')
                for ref in block_refs:
                    start, end = (ref.split('-') + [None])[:2]
                    ref_range = range(int(start), int(end or start) + 1)
                    for ref_num in ref_range:
                        ref_data = self.references.get(str(ref_num), None)
                        if ref_data:
                            url = ref_data.get('url', '')
                            if url:
                                if url not in self.url_dict:
                                    self.url_dict[url] = {'count': 1, 'pdf_files': {file_identifier},
                                                          'page_nums': [(page_num + 1) / num_pages]}
                                else:
                                    self.url_dict[url]['count'] += 1
                                    self.url_dict[url]['pdf_files'].add(file_identifier)
                                    self.url_dict[url]['page_nums'].append((page_num + 1) / num_pages)

                            keywords = ref_data.get('keywords', [])
                            for keyword in keywords:
                                if keyword not in self.keyword_dict:
                                    self.keyword_dict[keyword] = {'count': 1, 'pdf_files': {file_identifier},
                                                                  'page_nums': [(page_num + 1) / num_pages]}
                                else:
                                    self.keyword_dict[keyword]['count'] += 1
                                    self.keyword_dict[keyword]['pdf_files'].add(file_identifier)
                                    self.keyword_dict[keyword]['page_nums'].append((page_num + 1) / num_pages)
            if end:
                break
