from commutemate.ride import *
from commutemate.roi import PointOfInterest

STOPPED_SPEED_KMH_THRESHOLD = 1.5

def detect_stops(ride):
    stops         = []
    on_a_stop     = False
    duration      = 0
    stop_buffer   = None
    previous_stop = None

    for p in ride.points[1:]:
        if p.speed < STOPPED_SPEED_KMH_THRESHOLD:
            on_a_stop = True
            duration += p.seconds_from_previous
            stop_buffer = p
        else:
            if on_a_stop:
                poi = PointOfInterest(stop_buffer, PointOfInterest.TYPE_STOP, ride.origin, ride.destination)
                poi.set_duration(duration)
                poi.set_previous_stop(previous_stop);
                stops.append(poi)

                on_a_stop     = False
                duration      = 0
                stop_buffer   = None
                previous_stop = poi

    return stops
