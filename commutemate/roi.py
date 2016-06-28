class PointOfInterest(object):

    TYPE_STOP = 0
    TYPE_PASS = 1

    def __init__(self, point, point_type, origin, destination):
        self.point = point
        self.type = point_type
        self.origin = origin
        self.destination = destination
        self.previous_stop = None
        self.duration = 0

    def set_duration(self, duration):
        self.duration = duration

    def set_previous_stop(self, poi):
        self.previous_stop = poi
        # TODO self.speed_since_previous_stop = TBD




