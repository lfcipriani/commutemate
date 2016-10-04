import gpxpy
from commutemate.ride import *
import commutemate.utils as utils

class GpxParser(object):

    def __init__(self, filename):
        gpx_file = open(filename, 'r')
        self.__gpx = gpxpy.parse(gpx_file)
        self.region_ignores = []

    def get_ride_from_track(self, region_ignores=[]):
        self.region_ignores = region_ignores
        previous_point = None
        total_distance = 0
        total_duration = 0
        ride = Ride()
        orig = None
        dest = None

        for track in self.__gpx.tracks:
            for segment in track.segments:
                points = segment.points

                for i in range(0, len(points)):
                    if self.__should_ignore(points[i]):
                        continue
                    if not orig:
                        orig = points[i]

                    previous   = points[i - 1] if i > 0 else points[0]
                    point      = points[i]
                    next_point = points[i + 1] if i < len(points)-1 else points[-1]

                    timedelta = point.time - previous.time
                    distance  = utils.geo_distance(point, previous)
                    speed_kmh = utils.geo_speed(distance, timedelta)
                    bearing   = utils.geo_bearing((point.latitude,point.longitude), (next_point.latitude,next_point.longitude)) 
                    
                    total_duration += gpxpy.utils.total_seconds(timedelta)
                    total_distance += distance

                    ride.add_point(
                            GeoPoint(point.latitude, 
                                    point.longitude, 
                                    point.elevation, 
                                    speed_kmh, 
                                    gpxpy.utils.total_seconds(timedelta),
                                    point.time,
                                    bearing))

                    dest = points[i]

        ride.set_origin(GeoPoint(orig.latitude, orig.longitude, orig.elevation, 0, 0, orig.time, 0))
        ride.set_destination(GeoPoint(dest.latitude, dest.longitude, dest.elevation, 0, 0, dest.time, 0))
        ride.distance = total_distance
        ride.duration = total_duration
        return ride

    def __should_ignore(self, point):
        for rg in self.region_ignores:
            if utils.is_inside_range(rg, point):
                return True
        return False

