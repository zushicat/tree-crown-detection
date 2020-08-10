import json
import os
from typing import Any, Dict, List

from _geo import create_suburb_polygons, check_point_in_suburb_polygons
from _tree_crown_analysis import get_treecrown_diameter_in_meter

import pandas as pd
import utm


PREDICTIONS_CSV_DIR_PATH = "../../data/label_data/predictions"


if __name__ == "__main__":
    create_suburb_polygons()

    year_sum: Dict[str, int] = {}
    tree_list: List[Dict[str, Any]] = []

    # ***
    #
    dir_names = os.listdir(PREDICTIONS_CSV_DIR_PATH)
    for dir_name in dir_names:
        if os.path.isdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}") is False:
            continue
        file_names = os.listdir(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv")
        for file_name in file_names:
            try:
                x_min, y_min, x_max, y_max = [int(x) for x in file_name.replace(".csv", "").split("_")]
            except Exception as e:
                # print(f"ERROR: {e}")
                continue

            df = pd.read_csv(f"{PREDICTIONS_CSV_DIR_PATH}/{dir_name}/csv/{file_name}")
            for i, row in df.iterrows():
                x_min_utm: int = round(row.xmin/4) + x_min
                y_min_utm: int = round(row.ymin/4) + y_min
                x_max_utm: int = round(row.xmax/4) + x_min
                y_max_utm: int = round(row.xmax/4) + y_min

                center_x_utm: int = round((x_max_utm - x_min_utm)/2 + x_min_utm)
                center_y_utm: int = round((y_max_utm - y_min_utm)/2 + y_min_utm)

                center_lat, center_lng = utm.to_latlon(center_x_utm, center_y_utm, 32, 'U')

                lat_min, lng_min = utm.to_latlon(x_min_utm, y_min_utm, 32, 'U')
                lat_max, lng_max = utm.to_latlon(x_max_utm, y_max_utm, 32, 'U')
                
                polygon_check = check_point_in_suburb_polygons(center_lat, center_lng)
                
                if polygon_check is None:
                    continue

                diameter: int = get_treecrown_diameter_in_meter(row.xmin, row.ymin, row.xmax, row.ymax)
                
                tmp = {
                    "file_name": file_name,
                    "dir": dir_name,
                    "center_x_utm": center_x_utm,
                    "center_y_utm": center_y_utm,
                    "center_lat": center_lat,
                    "center_lng": center_lng,
                    "x_min_utm": x_min_utm,
                    "y_min_utm": y_min_utm,
                    "x_max_utm": x_max_utm,
                    "y_max_utm": y_max_utm,
                    "lat_min": lat_min,
                    "lng_min": lng_min,
                    "lat_max": lat_max,
                    "lng_max": lng_max,
                    "x_min_img": round(row.xmin),
                    "y_min_img": round(row.ymin),
                    "x_max_img": round(row.xmax),
                    "y_may_img": round(row.ymax),
                    "diameter": diameter
                }

                # ****
                # find cropped trees parts at image border -> skip
                a_len = round(row.xmax) - round(row.xmin)
                b_len = round(row.ymax) - round(row.ymin)
                prop = a_len/b_len if a_len < b_len else b_len/a_len
                prop = round(prop, 1)

                if prop < 0.7:
                    if round(row.xmin) == 0 or round(row.ymin) == 0 or round(row.xmax) == 400 or round(row.ymax) == 400:
                        # print(a_len, b_len, prop, round(row.xmin), round(row.xmax), round(row.ymin), round(row.ymax))
                        continue

                tree_list.append(tmp)

                if year_sum.get(dir_name) is None:
                    year_sum[dir_name] = 0
                year_sum[dir_name] += 1

    print(year_sum)

    df = pd.DataFrame(tree_list)
    df.to_csv("../../data/analysis/stadtgarten_trees.csv", index=False) 
    