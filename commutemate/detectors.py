from commutemate.ride import *

STOPPED_SPEED_KMH_THRESHOLD = 1.5

def detect_stops(ride):
    stops       = []
    on_a_stop   = False
    duration    = 0
    stop_buffer = None

    for p in ride.points[1:]:
        if p.speed < STOPPED_SPEED_KMH_THRESHOLD:
            on_a_stop = True
            duration += p.seconds_from_previous
            stop_buffer = p
        else:
            if on_a_stop:
                stops.append(stop_buffer)
                # TODO save total duration
                on_a_stop   = False
                duration    = 0
                stop_buffer = None

    # TODO create POI object instead
    return stops
