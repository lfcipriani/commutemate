class GeoPoint(object):

    def __init__(self, latitude, longitude, altitude, speed=None):
        self.lat = latitude
        self.lon = longitude
        self.altitude = altitude
        if speed:
            self.speed = speed

