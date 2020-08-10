import os
from typing import Any, Dict, List

import pandas as pd


PREDICTIONS_CSV_DIR_PATH = "../../data/label_data/predictions"
ORIGINAL_LABELS_CSV_FILE_PATH = "../../data/label_data/original_label_data_csv"


if __name__ == "__main__":
    sums: Dict[str, Any] = {}
    bounding_box_coords: List[str] = []

    # ***
    #
    dir_names = os.listdir(PREDICTIONS_CSV_DIR_PATH)
    for dir_name in dir_names:
        if dir_name.find("2020_stadtgarten") == -1:
            continue
        if os.path.isdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}") is False:
            continue
        file_names = os.listdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv")
        for file_name in file_names:
            if file_name.replace(".csv", "") not in bounding_box_coords:
                bounding_box_coords.append(file_name.replace(".csv", ""))
            
            if sums.get(dir_name) is None:
                sums[dir_name] = 0
            
            df = pd.read_csv(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv/{file_name}")
            sums[dir_name] += len(df)

    # ***
    #
    file_names = os.listdir(ORIGINAL_LABELS_CSV_FILE_PATH)
    dir_name = "original_labels"
    for file_name in file_names:
        if file_name.replace(".csv", "") not in bounding_box_coords:
            continue

        if sums.get(dir_name) is None:
            sums[dir_name] = 0
        
        df = pd.read_csv(f"{ORIGINAL_LABELS_CSV_FILE_PATH}/{file_name}")
        sums[dir_name] += len(df)


    print(sums)