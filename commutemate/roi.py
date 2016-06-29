import json
import hashlib
from commutemate.ride import GeoPoint
from commutemate.gpx_parser import geo_distance, geo_speed

class PointOfInterest(object):

    TYPE_STOP = "stop"
    TYPE_PASS = "pass"

    def __init__(self, point, point_type, origin, destination):
        self.point = point
        self.poi_type = point_type
        self.origin = origin
        self.destination = destination
        self.previous_stop = None
        self.speed_since_previous_stop = 0
        self.duration = 0
        self.__generate_id()

    def __generate_id(self):
        md5 = hashlib.md5()
        md5.update(self.point.time.__str__())
        md5.update(self.point.lat.__str__())
        md5.update(self.point.lon.__str__())
        self.id = md5.hexdigest()

    def set_duration(self, duration):
        self.duration = duration

    def set_previous_stop(self, poi):
        if poi != None:
            timedelta = self.point.time - poi.point.time
            distance  = geo_distance(self.point, poi.point)

            self.speed_since_previous_stop = geo_speed(distance, timedelta)

        self.previous_stop = poi.id if poi else None

    def to_dict(self):
        js = {
            "id": self.id,
            "point": self.point.to_dict(),
            "poi_type": self.poi_type,
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "previous_stop": self.previous_stop,
            "speed_since_previous_stop": self.speed_since_previous_stop,
            "duration": self.duration
        }
        return js

    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=4)

    @staticmethod
    def from_dict(json_dict):
        poi = PointOfInterest(
                    GeoPoint.from_dict(json_dict["point"]), 
                    json_dict["poi_type"],
                    GeoPoint.from_dict(json_dict["origin"]), 
                    GeoPoint.from_dict(json_dict["destination"]))
        poi.duration                  = json_dict["duration"]
        poi.previous_stop             = json_dict["previous_stop"]
        poi.speed_since_previous_stop = json_dict["speed_since_previous_stop"]
        return poi

    @staticmethod
    def from_JSON(json_str):
        js = json.loads(json_str)
        return PointOfInterest.from_dict(js)

    def __str__(self):
        s = "PointOfInterest("
        s += "poi_type=%s, " % (self.poi_type)
        s += "point=%s, " % (self.point.__str__())
        s += "speed_since_previous_stop=%2.6f kmh, " % (self.speed_since_previous_stop)
        s += "duration=%d)" % (self.duration)
        return s
