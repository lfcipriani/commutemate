import gpxpy
from commutemate.ride import *
import commutemate.utils as utils

class GpxParser(object):

    def __init__(self, filename):
        gpx_file = open(filename, 'r')
        self.__gpx = gpxpy.parse(gpx_file)

    def get_ride_from_track(self):
        previous_point = None
        ride = Ride()
        orig = self.__gpx.tracks[0].segments[0].points[0]
        dest = self.__gpx.tracks[-1].segments[-1].points[-1] 
        ride.set_origin(GeoPoint(orig.latitude, orig.longitude, orig.elevation, 0, 0, orig.time))
        ride.set_destination(GeoPoint(dest.latitude, dest.longitude, dest.elevation, 0, 0, dest.time))

        for track in self.__gpx.tracks:
            for segment in track.segments:
                points = segment.points

                for i in range(0, len(points)):
                    previous = points[i - 1] if i > 0 else points[0]
                    point    = points[i]

                    timedelta = point.time - previous.time
                    distance  = utils.geo_distance(point, previous)
                    speed_kmh = utils.geo_speed(distance, timedelta)

                    ride.add_point(
                            GeoPoint(point.latitude, 
                                     point.longitude, 
                                     point.elevation, 
                                     speed_kmh, 
                                     gpxpy.utils.total_seconds(timedelta),
                                     point.time))

        return ride

