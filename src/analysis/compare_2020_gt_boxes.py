import json
import os
from typing import Any, Dict, List

import pandas as pd


PREDICTIONS_CSV_DIR_PATH = "../../data/label_data/predictions"
ORIGINAL_LABELS_CSV_FILE_PATH = "../../data/label_data/original_label_data_csv"


if __name__ == "__main__":
    sums: Dict[str, Any] = {}
    
    # ***
    #
    dir_names = os.listdir(PREDICTIONS_CSV_DIR_PATH)
    for dir_name in dir_names:
        if dir_name != "2020_1":
            continue
        if os.path.isdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}") is False:
            continue
        file_names = os.listdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv")
        for file_name in file_names:
            bounding_box_coords = file_name.replace(".csv", "")
            
            df = pd.read_csv(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv/{file_name}")
            
            if sums.get(bounding_box_coords) is None:
                sums[bounding_box_coords] = {"2020": len(df), "gt": 0}

    # ***
    #
    file_names = os.listdir(ORIGINAL_LABELS_CSV_FILE_PATH)
    dir_name = "original_labels"
    for file_name in file_names:
        bounding_box_coords = file_name.replace(".csv", "")

        if sums.get(bounding_box_coords) is None:
            continue
        
        df = pd.read_csv(f"{ORIGINAL_LABELS_CSV_FILE_PATH}/{file_name}")
        sums[bounding_box_coords]["gt"] += len(df)

    print(json.dumps(sums, indent=2))