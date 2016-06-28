class GeoPoint(object):

    def __init__(self, latitude, longitude, elevation, speed, seconds_from_previous):
        self.lat = latitude
        self.lon = longitude
        self.elevation = elevation
        self.speed = speed
        self.seconds_from_previous = seconds_from_previous

class Ride(object):

    def __init__(self, origin=None, destination=None):
        self.points = []
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

class RideError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

