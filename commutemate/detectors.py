import commutemate.utils as utils
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
                poi.set_previous_stop(previous_stop)
                stops.append(poi)

                on_a_stop     = False
                duration      = 0
                stop_buffer   = None
                previous_stop = poi

    return stops

def detect_passes(ride, ROIs):
    passes        = []
    on_a_stop     = False
    on_a_roi      = False
    stop_buffer   = None
    pass_buffer   = []
    previous_stop = None
    current_roi   = None
    stats = {
            "# ROIs entered": 0,
            "# ROIs stop POI": 0, 
            "# ROIs stop without POI": 0, 
            "# ROIs pass": 0,
        }

    for p in ride.points[1:]:

        if not current_roi:
            roi = __inside_a_ROI(p, ROIs)
        elif current_roi and utils.is_inside_range(current_roi.center_range, p):
            roi = current_roi
        else: 
            roi = None

        if roi:
            on_a_roi = True
            if not current_roi:
                stats["# ROIs entered"] += 1
            current_roi = roi

            if p.speed < STOPPED_SPEED_KMH_THRESHOLD:
                on_a_stop = True
                stop_buffer = p
            else:
                pass_buffer.append(p)
        else:
            if on_a_stop:
                poi = PointOfInterest(stop_buffer, PointOfInterest.TYPE_STOP, ride.origin, ride.destination)
                if current_roi.is_poi_included(poi.id):
                    previous_stop = poi
                    stats["# ROIs stop POI"] += 1
                else:
                    stats["# ROIs stop without POI"] += 1

                on_a_stop     = False
                stop_buffer   = None
                on_a_roi      = False
                pass_buffer   = []
                current_roi   = None

            elif on_a_roi:
                stats["# ROIs pass"] += 1
                ppass = pass_buffer[len(pass_buffer)/2] # get buffer mid point as point for POI
                poi   = PointOfInterest(ppass, PointOfInterest.TYPE_PASS, ride.origin, ride.destination)
                poi.set_duration(0)
                poi.set_previous_stop(previous_stop)
                # TODO only append if point is part of the cluster
                # TODO update ROI with new POI
                passes.append(poi)

                on_a_stop     = False
                stop_buffer   = None
                on_a_roi      = False
                pass_buffer   = []
                current_roi   = None

    return passes, stats

def __inside_a_ROI(point, ROIs):
    # TODO use a index to search implement that
    for roi in ROIs:
        if utils.is_inside_range(roi.center_range, point):
            return roi
    return None
