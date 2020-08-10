'''
Get crown diameter in meter from bbox information
'''
import pandas as pd


PREDICTIONS_CSV_DIR_PATH = "../../data/label_data/predictions_20_epochs"
RESOLUTION = 400
FACTOR = RESOLUTION/1000


def _get_proportional_value(value: int) -> int:
    '''
    Position on the original 1000 x 1000 meter area
    '''
    return round(value / FACTOR / 10)


def get_treecrown_diameter_in_meter(xmin: int, ymin: int, xmax: int, ymax: int) -> int:
    '''
    Assume circle: get diameter from square with max sidelength
    '''
    x_len = xmax - xmin
    y_len = ymax - ymin
    max_diameter = x_len if x_len > y_len else y_len
    
    max_diameter = _get_proportional_value(round(max_diameter))

    return max_diameter


if __name__ == "__main__":
    df = pd.read_csv(f"{PREDICTIONS_CSV_DIR_PATH}/2020_1/csv/356200_5644200_356300_5644300.csv")
    for i, row in df.iterrows():
        diameter: int = get_treecrown_diameter_in_meter(row.xmin, row.ymin, row.xmax, row.ymax)
        print(diameter)
