import json
from gpxpy.gpxfield import TimeConverter

class GeoPoint(object):

    def __init__(self, latitude, longitude, elevation, speed, seconds_from_previous, time, bearing):
        self.lat = self.latitude = latitude
        self.lon = self.longitude = longitude
        self.elevation = elevation
        self.speed = speed
        self.seconds_from_previous = seconds_from_previous
        self.time = time
        self.bearing = bearing

    def to_dict(self):
        tc = TimeConverter()
        js = {
            "lat": self.lat,
            "lon": self.lon,
            "elevation": self.elevation,
            "speed": self.speed,
            "seconds_from_previous": self.seconds_from_previous,
            "time": tc.to_string(self.time),
            "bearing": self.bearing
        }
        return js

    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=4)

    @staticmethod
    def from_dict(json_dict):
        tc = TimeConverter()
        geo_point = GeoPoint(json_dict["lat"], json_dict["lon"], json_dict["elevation"], json_dict["speed"], json_dict["seconds_from_previous"], tc.from_string(json_dict["time"]), json_dict["bearing"])
        return geo_point

    @staticmethod
    def from_JSON(json_str):
        js = json.loads(json_str)
        return GeoPoint.from_dict(js)

    def __str__(self):
        return "GeoPoint(lat=%3.7f, lon=%3.7f, speed=%2.6f kmh, secs_from_prev=%d, time=%s, elev=%d, bearing=%3.2f)" % (self.lat, self.lon, self.speed, self.seconds_from_previous, self.time, self.elevation, self.bearing)

class Ride(object):

    def __init__(self, origin=None, destination=None):
        self.points = []
        self.distance = 0
        self.duration = 0
        if origin:
            self.set_origin(origin)
        if destination:
            self.set_destination(destination)

    def add_point(self, geo_point):
        if isinstance(geo_point, GeoPoint):
            self.points.append(geo_point)
        else:
            raise RideError("Point should be instance of GeoPoint")

    def point_count(self):
        return len(self.points)

    def set_origin(self, origin):
        self.origin = origin

    def set_destination(self, destination):
        self.destination = destination

    def to_JSON(self):
        plist = [p.to_dict() for p in self.points]
        js = {
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "points": plist
        }
        return json.dumps(js, indent=4)

    @staticmethod
    def from_JSON(json_str):
        js = json.loads(json_str)
        ride = Ride(GeoPoint.from_dict(js["origin"]), GeoPoint.from_dict(js["destination"]))
        [ ride.add_point(GeoPoint.from_dict(jsp)) for jsp in js["points"] ]
        return ride

class RideError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

