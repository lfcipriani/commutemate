from commutemate.gpx_parser import geo_distance, geo_speed

class PointOfInterest(object):

    TYPE_STOP = "stop"
    TYPE_PASS = "pass"

    def __init__(self, point, point_type, origin, destination):
        self.point = point
        self.type = point_type
        self.origin = origin
        self.destination = destination
        self.previous_stop = None
        self.speed_since_previous_stop = 0
        self.duration = 0

    def set_duration(self, duration):
        self.duration = duration

    def set_previous_stop(self, poi):
        self.previous_stop = poi

        if poi != None:
            timedelta = self.point.time - self.previous_stop.point.time
            distance  = geo_distance(self.point, self.previous_stop.point)

            self.speed_since_previous_stop = geo_speed(distance, timedelta)

    def __str__(self):
        s = "PointOfInterest("
        s += "type=%s, " % (self.type)
        s += "point=%s, " % (self.point.__str__())
        s += "speed_since_previous_stop=%2.6f kmh, " % (self.speed_since_previous_stop)
        s += "duration=%d)" % (self.duration)
        return s
