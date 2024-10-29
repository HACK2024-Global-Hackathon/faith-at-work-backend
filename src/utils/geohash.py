import pygeohash as pgh

def encode(latitude: float, longitude: float) -> str:
    return pgh.encode(latitude, longitude, precision=6)

def decode(geohash: str):
    return pgh.decode(geohash)
