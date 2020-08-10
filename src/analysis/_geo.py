import json
from math import cos, pi, sin, sqrt
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import Point, Polygon, MultiPoint, LineString
import utm


SUBURB_POLYGONS: List[Dict[str, Any]] = []
NEIGHBOURING_SUBURBS: Dict[str, Any] = {}


def _create_point(lat: float, lng: float) -> Point:
    return Point(lng, lat)


def check_point_in_suburb_polygons(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    '''
    returns:
    {'OBJECTID': 52, 'NUMMER': '802', 'NAME': 'Kalk', 'NR_STADTBEZIRK': '8', 'STADTBEZIRK': 'Kalk', 'FLAECHE': 2967093, 'LINK': None}

    or None
    '''
    point = _create_point(lat, lng)
    for polygon_data in SUBURB_POLYGONS:
        if polygon_data["polygon"].contains(point):
            return polygon_data["properties"]
    return None


def create_suburb_polygons():
    '''
    properties:
    {'OBJECTID': 52, 'NUMMER': '802', 'NAME': 'Kalk', 'NR_STADTBEZIRK': '8', 'STADTBEZIRK': 'Kalk', 'FLAECHE': 2967093, 'LINK': None}
    '''
    global SUBURB_POLYGONS

    with open("../../data/geojson/stadtgarten.json") as f:
        features = json.load(f)["features"]

    for feature in features:
        coords = [tuple(x) for x in feature["geometry"]["coordinates"][0]]
        
        SUBURB_POLYGONS.append({
            "polygon": Polygon(coords),
            "properties": feature["properties"]
        })
        

def find_neighbouring_suburbs() -> None:
    bounding_boxes: List[Any] = []
    properties: List[Any] = []
    for polygon in SUBURB_POLYGONS:
        
        tmp = polygon["polygon"].bounds

        x1, y1, _, _ = utm.from_latlon(tmp[0], tmp[1]) #(tmp[1], tmp[0])
        x2, y2, _, _ = utm.from_latlon(tmp[2], tmp[3]) #(tmp[3], tmp[2])
        
        utm_polygon = Polygon(((x1, y1), (x1, y2), (x2, y1), (x2, y2)))
        utm_polygon = utm_polygon.buffer(1000.0)
        
        bounding_boxes.append(utm_polygon)
        properties.append(polygon["properties"])
        
    # for b in bounding_boxes:
    #     print(b)
    
    for i in range(len(bounding_boxes)-1):
        p = bounding_boxes[i]
        p_name = properties[i]["NUMMER"]

        if NEIGHBOURING_SUBURBS.get(p_name) is None:
            NEIGHBOURING_SUBURBS[p_name] = []

        for j in range(i+1, len(bounding_boxes)):
            q = bounding_boxes[j]
            q_name = properties[j]["NUMMER"]
            
            if p.intersects(q): # or p.overlaps(q) or p.touches(q):
                if NEIGHBOURING_SUBURBS.get(q_name) is None:
                    NEIGHBOURING_SUBURBS[q_name] = []

                if q_name not in NEIGHBOURING_SUBURBS[p_name]:
                    NEIGHBOURING_SUBURBS[p_name].append(q_name)
                if p_name not in NEIGHBOURING_SUBURBS[q_name]:
                    NEIGHBOURING_SUBURBS[q_name].append(p_name)
                
                NEIGHBOURING_SUBURBS[p_name].sort()
                NEIGHBOURING_SUBURBS[q_name].sort()
            
    # print(json.dumps(NEIGHBOURING_SUBURBS, indent=2, ensure_ascii=False))


def get_neighbouring_suburbs() -> Dict[str, Any]:
    return NEIGHBOURING_SUBURBS


def get_earth_radius(lat: float) -> Tuple[float, float]:
    '''
    latitude doesn't change significantly within 1 city (regarding earth radius), hence: calculate 1 time with Cologne latitude
    See also:
    https://stackoverflow.com/questions/238260/how-to-calculate-the-bounding-box-for-a-given-lat-lng-location
    '''
    def WGS84EarthRadius(lat: float) -> Tuple[int, int]:
        # http://en.wikipedia.org/wiki/Earth_radius
        An = WGS84_a*WGS84_a * cos(lat)
        Bn = WGS84_b*WGS84_b * sin(lat)
        Ad = WGS84_a * cos(lat)
        Bd = WGS84_b * sin(lat)

        return sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )
    
    lat: float = deg2rad(lat)

    # Semi-axes of WGS-84 geoidal reference
    WGS84_a = 6378137.0  # Major semiaxis [m]
    WGS84_b = 6356752.3  # Minor semiaxis [m]

    earth_radius = WGS84EarthRadius(lat)  # Radius of Earth at given latitude
    earth_pradius = earth_radius * cos(lat)  # Radius of the parallel at given latitude

    return int(earth_radius), int(earth_pradius)


def deg2rad(degrees: float) -> float:
    ''' degrees to radians '''
    return pi * degrees / 180.0


def rad2deg(radians: float) -> float:
    ''' radians to degrees '''
    return 180.0 * radians / pi


def get_bounding_box_around_lat_lng_center(lat: float, lng: float, pseudo_radius_meter: int, earth_radius: int, earth_pradius: int) -> Tuple[float, float, float, float]:
    '''
    See also:
    https://stackoverflow.com/questions/238260/how-to-calculate-the-bounding-box-for-a-given-lat-lng-location
    '''
    lat: float = deg2rad(lat)
    lng: float = deg2rad(lng)
    half_side: int = int(1000 * (pseudo_radius_meter * 0.001))  # half side in Km: 50m -> 0.05 km

    min_lat: float = rad2deg(lat - half_side/earth_radius)
    max_lat: float = rad2deg(lat + half_side/earth_radius)
    min_lng: float = rad2deg(lng - half_side/earth_pradius)
    max_lng: float = rad2deg(lng + half_side/earth_pradius)

    return min_lat, max_lat, min_lng, max_lng


if __name__ == "__main__":
    create_suburb_polygons()
    bla = check_point_in_suburb_polygons(50.945772669292516, 6.936531689877734)
    print(bla)
