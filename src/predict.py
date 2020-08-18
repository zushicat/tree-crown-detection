import os
from typing import Any, Dict, List, Optional

from _create_xml import create_label_xml

from deepforest import deepforest
import pandas as pd
# import matplotlib.pyplot as plt


SCRIPT_DIR = os.path.abspath(os.getcwd())
IMAGE_DIR_PATH = "../data/image_data"
LABEL_DIR_PATH = "../data/predictions"
MODEL_DIR_PATH = "../data/model_data"

IMAGE_WIDTH = 400
IMAGE_HEIGHT = 400

MODEL = deepforest.deepforest(saved_model=f"{MODEL_DIR_PATH}/model.h5")


def _predict_image(image_path: str) -> Optional[pd.DataFrame]:
    try:
        return MODEL.predict_image(f"{image_path}", show=False, return_plot = False)
    except:
        return None


def _create_label_dir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    for sub_dir in ["csv", "xml"]:
        sub_dir_path = f"{dir_path}/{sub_dir}"
        if not os.path.exists(sub_dir_path):
            os.makedirs(sub_dir_path)


def _save_csv_prediction(file_path: str, df_prediction: pd.DataFrame) -> None:
    df_prediction.to_csv(file_path, index=False)


def _save_xml_prediction(label_file_path: str, image_folder: str, image_file_name: str, df_prediction: pd.DataFrame) -> None:
    prediction: Dict[str, Any] = {
            "folder": image_folder,
            "filename": image_file_name,
            "path": f"{image_folder}/{image_file_name}",
            "width": IMAGE_WIDTH,
            "height": IMAGE_HEIGHT,
            "label_boxes": []
        }

    for index, row in df_prediction.iterrows():
        '''
        xmin,ymin,xmax,ymax,score,label
        '''
        tmp = {
            "xmin": row["xmin"],
            "ymin": row["ymin"],
            "xmax": row["xmax"],
            "ymax": row["ymax"],
            "label": row["label"],
        }
        prediction["label_boxes"].append(tmp)
    
    xml_file: str = create_label_xml(prediction)
    
    with open(label_file_path, "w") as f:
        f.write(xml_file)


if __name__ == "__main__":
    image_dirs = os.listdir(IMAGE_DIR_PATH)
    for image_dir in image_dirs:
        if image_dir.find("neustadt_sued") == -1:
            continue
        
        current_image_dir_path = f"{IMAGE_DIR_PATH}/{image_dir}"
        if os.path.isdir(current_image_dir_path) is False:
            continue

        print(image_dir)

        label_dir = f"{LABEL_DIR_PATH}/{image_dir}"
        _create_label_dir(label_dir)
        
        image_file_names = os.listdir(current_image_dir_path)
        for image_file_name in image_file_names:
            try:
                image_file_path = f"{current_image_dir_path}/{image_file_name}"
                df_prediction = _predict_image(image_file_path)

                csv_label_path = f"{label_dir}/csv/{image_file_name.replace('.png', '.csv')}"
                _save_csv_prediction(csv_label_path, df_prediction)

                xml_label_path = f"{label_dir}/xml/{image_file_name.replace('.png', '.xml')}"
                _save_xml_prediction(xml_label_path, image_dir, image_file_name, df_prediction)
            except:
                continue
