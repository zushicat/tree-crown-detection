import json
import os
from typing import Any, Dict, List

from _tree_crown_analysis import get_treecrown_diameter_in_meter

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
        if os.path.isdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}") is False:
            continue
        file_names = os.listdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv")
        for file_name in file_names:
            # if file_name.replace(".csv", "") not in bounding_box_coords:
            #     bounding_box_coords.append(file_name.replace(".csv", ""))
            
            # if sums.get(dir_name) is None:
            #     sums[dir_name] = 0
            
            df = pd.read_csv(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv/{file_name}")
            for i, row in df.iterrows():
                diameter: int = get_treecrown_diameter_in_meter(row.xmin, row.ymin, row.xmax, row.ymax)

                if sums.get(diameter) is None:
                    sums[diameter]: Dict[str, int] = {}
                if sums[diameter].get(dir_name) is None:
                    sums[diameter][dir_name] = 0
                sums[diameter][dir_name] += 1

    lines: List[Dict[str, Any]] = []
    for diameter, diameter_vals in sums.items():
        tmp: Dict[str, Any] = {"diameter": diameter}
        for year, counts in diameter_vals.items():
            tmp[year] = counts
        lines.append(tmp)

    df = pd.DataFrame(lines)
    df.to_csv("../../data/analysis/treecrown_diameter_distribution_years_2.csv", index=False) 
    