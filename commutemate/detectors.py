import copy, os
import commutemate.utils as utils
from commutemate.ride import *
from commutemate.roi import PointOfInterest, RegionOfInterest

STOPPED_SPEED_KMH_THRESHOLD = 1.5

def detect_stops(ride, stop_duration_cap = None):
    stops         = []
    on_a_stop     = False
    duration      = 0
    stop_buffer   = None
    previous_stop = None
    ignored_time  = 0

    for p in ride.points[1:]:
        if p.speed < STOPPED_SPEED_KMH_THRESHOLD:
            on_a_stop = True
            duration += p.seconds_from_previous
            stop_buffer = p
        else:
            if on_a_stop:
                poi = PointOfInterest(stop_buffer, PointOfInterest.TYPE_STOP, ride.origin, ride.destination)
                if stop_duration_cap and duration > stop_duration_cap:
                    ignored_time += (duration - stop_duration_cap)
                    duration = stop_duration_cap
                poi.set_duration(duration)
                poi.set_previous_stop(previous_stop)
                stops.append(poi)

                on_a_stop     = False
                duration      = 0
                stop_buffer   = None
                previous_stop = poi

    return stops, ignored_time

def detect_passes(ride, ROIs, eps_in_meters, min_samples, workspace_folder):
    import numpy
    import commutemate.clustering as clustering

    stops         = []
    on_a_stop     = False
    stop_buffer   = None
    previous_stop = None

    passes        = []
    on_a_roi      = False
    pass_buffer   = []
    current_roi   = None
    previous_pass = None

    stats = {
            "# ROIs entered": 0,
            "# ROIs stop POI": 0, 
            "# ROIs stop without POI": 0, 
            "# ROIs pass": 0,
            "# ROIs pass but no cluster": 0,
            "pass_speed_list": []
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
                    # Updating POI with preivous ROIs info
                    poi = utils.load_json(os.path.join(workspace_folder, "poi_%s.json" % poi.id), PointOfInterest)
                    poi.previous_stop_ROI = previous_stop.id if previous_stop else None
                    poi.previous_pass_ROI = previous_pass.id if previous_pass else None
                    utils.save_json(os.path.join(workspace_folder, "poi_%s.json" % poi.id), poi.to_JSON())
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
                pass_in_cluster = []

                # check from all the points inside a ROI which ones are inside the original cluster
                for ppass in pass_buffer:
                    poi   = PointOfInterest(ppass, PointOfInterest.TYPE_PASS, ride.origin, ride.destination)
                    poi.set_duration(0)
                    poi.set_previous_stop(previous_stop)
                    poi.previous_stop_ROI = previous_stop.id if previous_stop else None
                    poi.previous_pass_ROI = previous_pass.id if previous_pass else None

                    # need to hydrate ROI to have POIs bearing info
                    RegionOfInterest.hydrate_POIs(current_roi, workspace_folder)
                    current_roi.set_poi_list([poi], PointOfInterest.TYPE_PASS)
                    POIs = numpy.array(current_roi.get_all_pois())
                    X = numpy.array(current_roi.get_all_poi_coords())

                    # If pass point is not part of stop cluster, this means that the pass is in another direction
                    db = clustering.cluster_with_bearing_weight(POIs, X, eps_in_meters, min_samples)
                    n_clusters_ = len(set(db))

                    if n_clusters_ == 1:
                        pass_in_cluster.append(poi)

                    current_roi.set_poi_list([], PointOfInterest.TYPE_PASS)

                if len(pass_in_cluster) > 0:
                    # we have officially a pass, the crowd goes crazy
                    stats["# ROIs pass"] += 1
                    poi = pass_in_cluster[len(pass_in_cluster)/2] # get buffer mid point as point for POI
                    stats["pass_speed_list"].append(poi.point.speed)
                    previous_pass = poi
                    passes.append(poi)
                else:
                    stats["# ROIs pass but no cluster"] += 1

                on_a_stop     = False
                stop_buffer   = None
                on_a_roi      = False
                pass_buffer   = []
                current_roi   = None

    return passes, stats

def __inside_a_ROI(point, ROIs):
    for roi in ROIs:
        if utils.is_inside_range(roi.center_range, point):
            return copy.deepcopy(roi)
    return None
