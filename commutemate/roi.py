import json, os
import hashlib
from commutemate.ride import GeoPoint
import commutemate.utils as utils

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
            distance  = utils.geo_distance(self.point, poi.point)

            self.speed_since_previous_stop = utils.geo_speed(distance, timedelta)

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

class RegionOfInterest(object):

    CORE = 'core'
    NON_CORE = 'non_core'

    def __init__(self):
        self.poi_ids = { RegionOfInterest.CORE: None, RegionOfInterest.NON_CORE: None }
        self.poi_list = { RegionOfInterest.CORE: None, RegionOfInterest.NON_CORE: None }
        self.poi_coords = { RegionOfInterest.CORE: None, RegionOfInterest.NON_CORE: None }
        self.center_range = None

    def set_poi_list(self, poi_list, type_):
        self.poi_list[type_] = poi_list
        self.set_poi_ids([p.id for p in poi_list], type_)
        self.set_poi_coords([[p.point.lat, p.point.lon] for p in poi_list], type_)

    def set_poi_ids(self, poi_ids, type_):
        self.poi_ids[type_] = poi_ids

    def set_poi_coords(self, poi_coords, type_):
        self.poi_coords[type_] = poi_coords
        if type_ == RegionOfInterest.CORE:
            self.__generate_center_range(poi_coords)
        
    def __generate_center_range(self, coords):
        self.center_range = utils.geo_range_from_center(coords)

    def to_dict(self):
        js = {
            "poi_ids": self.poi_ids,
            "poi_coords": self.poi_coords,
            "center_range": self.center_range
        }
        return js

    def to_JSON(self):
        return json.dumps(self.to_dict(), indent=4)

    @staticmethod
    def from_dict(json_dict):
        roi = RegionOfInterest()
        for type_ in [RegionOfInterest.CORE,RegionOfInterest.NON_CORE]:
            roi.set_poi_ids(json_dict["poi_ids"][type_], type_)
            roi.set_poi_coords(json_dict["poi_coords"][type_], type_)
        return roi

    @staticmethod
    def from_JSON(json_str):
        js = json.loads(json_str)
        return RegionOfInterest.from_dict(js)


    @staticmethod
    def hydrate_POIs(roi, json_base_path):
        for type_ in [RegionOfInterest.CORE,RegionOfInterest.NON_CORE]:
            result = []
            for i in roi.poi_ids[type_]:
                result.append(utils.load_json(os.path.join(json_base_path, ("poi_%s.json" % i)),PointOfInterest))
            roi.set_poi_list(result, type_)

