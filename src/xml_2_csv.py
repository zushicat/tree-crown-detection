'''
Covert original XML labels (from processed Baumkataster data) to csv labels
'''
import os
from typing import Any, Dict, List

from bs4 import BeautifulSoup
import pandas as pd


XML_LABEL_PATH = "../data/label_data/original_label_data_xml"
CSV_LABEL_PATH = "../data/label_data/original_label_data_csv"


def _create_label_csv(xml_file_path: str) -> pd.DataFrame:
    with open(xml_file_path) as f:
        xml_doc = BeautifulSoup(f.read(), 'xml')
    
    box_list: List[Dict[str, Any]] = []
    for box in xml_doc.find_all("object"):
        tmp = {
            "xmin": box.find("xmin").string,
            "ymin": box.find("ymin").string,
            "xmax": box.find("xmax").string,
            "ymax": box.find("ymax").string,
            "label": "Tree"  # use default label instead label in XML box.find("name").string,
        }
        box_list.append(tmp)
    
    return pd.DataFrame(box_list)


if __name__ == "__main__":
    xml_file_names = os.listdir(XML_LABEL_PATH)
    for xml_file_name in xml_file_names:
        df = _create_label_csv(f"{XML_LABEL_PATH}/{xml_file_name}")
        df.to_csv(f'{CSV_LABEL_PATH}/{xml_file_name.replace(".xml", ".csv")}', index=False)
