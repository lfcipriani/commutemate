import gpxpy, os, sys, math

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

def is_inside_range(range_, geopoint):
    distance = gpxpy.geo.distance(range_[0], range_[1], None, geopoint.latitude, geopoint.longitude, None)
    return (distance <= range_[2])

def geo_range_from_center(points):
    max_lat = -500.
    max_lon = -500.
    min_lat = 500.
    min_lon = 500.

    for p in points:
        if p[0] > max_lat:
            max_lat = p[0] 
        if p[1] > max_lon:
            max_lon = p[1]
        if p[0] < min_lat:
            min_lat = p[0]
        if p[1] < min_lon:
            min_lon = p[1]
    center_lat = min_lat + ((max_lat - min_lat)/2)
    center_lon = min_lon + ((max_lon - min_lon)/2)

    max_distance = -1
    for p in points:
        distance = gpxpy.geo.distance(p[0], p[1], None, center_lat, center_lon, None)
        if distance > max_distance:
            max_distance = distance

    return (center_lat, center_lon, max_distance)

# based on: https://gist.github.com/jeromer/2005586
def geo_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def geo_end_of_bearing(point, bearing, distance):
    if (type(point) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat    = math.radians(point[0])
    lon    = math.radians(point[1])
    brng   = math.radians(bearing)
    km     = distance / 1000
    radius = 6372

    lat2 = math.asin(math.sin(lat) * math.cos(km/radius) + 
            math.cos(lat) * math.sin(km/radius) * math.cos(brng))
    lon2 = lon + math.atan2(math.sin(brng) * math.sin(km/radius) * math.cos(lat), 
            math.cos(km/radius) - math.sin(lat) * math.sin(lat2))

    return (math.degrees(lat2), math.degrees(lon2))

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

