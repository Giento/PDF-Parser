from typing import Dict


class DataMerger:
    @staticmethod
    def merge_dicts(dict1: Dict[str, Dict], dict2: Dict[str, Dict]) -> Dict[str, Dict]:
        for key, data in dict2.items():
            if key in dict1:
                dict1[key]['count'] += data['count']
                dict1[key]['pdf_files'].update(data['pdf_files'])
                dict1[key]['page_nums'].extend(data['page_nums'])
            else:
                dict1[key] = {'count': data['count'], 'pdf_files': data['pdf_files'], 'page_nums': data['page_nums']}
        return dict1
