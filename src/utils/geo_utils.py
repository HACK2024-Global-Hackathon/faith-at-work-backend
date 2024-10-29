import math
import pygeohash as pgh
from typing import Tuple

def encode(latitude: float, longitude: float, precision) -> str:
    return pgh.encode(latitude, longitude, precision=precision)

def decode(geohash: str) -> Tuple[float]:
    return pgh.decode(geohash)

def euclidean_distance(latA, longA, latB, longB) -> float:
    return math.dist((latA, longA), (latB, longB))
