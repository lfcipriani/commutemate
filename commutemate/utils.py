import gpxpy, os, sys

# GEO utils
# Uses gpxpy formulas
def geo_distance(point, previous):
    if point.elevation and previous.elevation:
        distance = gpxpy.geo.distance(point.latitude, point.longitude, point.elevation, previous.latitude, previous.longitude, previous.elevation)
    else:
        distance = gpxpy.geo.distance(point.latitude, point.longitude, None, previous.latitude, previous.longitude, None)
    return distance

def geo_speed(distance, timedelta):
    seconds = gpxpy.utils.total_seconds(timedelta)
    speed_kmh = 0
    if seconds > 0:
        speed_kmh = (distance / 1000.) / (seconds / 60. ** 2)
    return speed_kmh

# FILE utils
def full_path(folder):
    return os.path.abspath(os.path.join(os.getcwd(), folder))

def save_json(filename, content):
    outputFile = open(filename, "w")
    outputFile.write(content)
    outputFile.close()

def load_json(filename, class_to_deserialize=None):
    f  = open(filename, "r")
    js = f.read()
    if class_to_deserialize:
        js = class_to_deserialize.from_JSON(js)
    f.close()
    return js
