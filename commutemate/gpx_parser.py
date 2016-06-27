import gpxpy
from commutemate.ride import *

class GpxParser(object):

    def __init__(self, filename):
        gpx_file = open(filename, 'r')
        self.__gpx = gpxpy.parse(gpx_file)

    def get_ride_from_track(self):
        previous_point = None
        ride = Ride()

        for track in self.__gpx.tracks:
            for segment in track.segments:
                points = segment.points

                for i in range(0, len(points)):
                    previous = points[i - 1] if i > 0 else points[0]
                    point    = points[i]

                    timedelta = point.time - previous.time
                    distance  = self.__distance(point, previous)
                    speed_kmh = self.__speed(distance, timedelta)

                    ride.add_point(
                            GeoPoint(point.latitude, 
                                     point.longitude, 
                                     point.elevation, 
                                     speed_kmh, 
                                     gpxpy.utils.total_seconds(timedelta)))

        return ride

    def __distance(self, point, previous):
        if point.elevation and previous.elevation:
            distance = point.distance_3d(previous)
        else:
            distance = point.distance_2d(previous)
        return distance

    def __speed(self, distance, timedelta):
        seconds = gpxpy.utils.total_seconds(timedelta)
        speed_kmh = 0
        if seconds > 0:
            speed_kmh = (distance / 1000.) / (seconds / 60. ** 2)
        return speed_kmh
        
