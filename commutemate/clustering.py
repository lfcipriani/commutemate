import os
import datetime
import numpy, gmplot
from sklearn.cluster import DBSCAN
import commutemate.utils as utils
from commutemate.roi import RegionOfInterest, PointOfInterest

def cluster(X, eps_in_meters, min_samples):
    # Running DBSCAN cluster algorithm
    # http://scikit-learn.org/stable/modules/clustering.html#dbscan
    Y = numpy.radians(X) # this is the input of scikit Haversine distance formula
    DB_EPS = eps_in_meters / 1000 / 6372 # Haversine outputs without considering Earth radius
    db = DBSCAN(eps=DB_EPS, min_samples=min_samples, metric='haversine').fit(Y)
    return db

def create_ROIs(POIs, labels, roi_labels, output_folder, add_center_range=0):
    ROIs = []
    for k in roi_labels:
        roi_ = RegionOfInterest()

        class_member_mask = (labels == k)
        stop_POIs = [item for item in POIs[class_member_mask] if item.poi_type == PointOfInterest.TYPE_STOP]
        pass_POIs = [item for item in POIs[class_member_mask] if item.poi_type == PointOfInterest.TYPE_PASS]

        roi_.set_poi_list(stop_POIs, PointOfInterest.TYPE_STOP)
        roi_.set_poi_list(pass_POIs, PointOfInterest.TYPE_PASS)
        roi_.calculate_center_range(add_center_range)

        ROIs.append(roi_)

    now = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    i   = 1
    roi_count = len(ROIs)
    for roi_ in ROIs:
        utils.save_json(os.path.join(output_folder, ("roi_%s_%0"+ str(len(str(roi_count))) + "d.json") % (now, i)), roi_.to_JSON())
        i += 1

    return ROIs

def render_map(ROIs, POIs, X, labels, output_folder, dbscan_radius):
    import gmplot

    roi_points = [[roi.center_range[0], roi.center_range[1]] for roi in ROIs]
    center = utils.geo_range_from_center(roi_points)
    gmap = gmplot.GoogleMapPlotter(center[0], center[1], 12)

    black  = '#000000' # noise
    green  = '#0BDE4E' # passes
    red    = '#E84D2A' # stops
    whitey = '#DDDDDD' # ROI center
    unique_labels = set(labels)
    for k in unique_labels:
        class_member_mask = (labels == k) # array of true/false. true if label equal set of label value

        if k == -1:
            xy = X[class_member_mask]
            gmap.scatter(xy[:, 0], xy[:, 1], black, size=int(dbscan_radius), marker=False)
        else:
            xy = numpy.array([[item.point.lat, item.point.lon] for item in POIs[class_member_mask] if item.poi_type == PointOfInterest.TYPE_STOP])
            if len(xy) > 0:
                gmap.scatter(xy[:, 0], xy[:, 1], red, size=int(dbscan_radius), marker=False)
            xy = numpy.array([[item.point.lat, item.point.lon] for item in POIs[class_member_mask] if item.poi_type == PointOfInterest.TYPE_PASS])
            if len(xy) > 0:
                gmap.scatter(xy[:, 0], xy[:, 1], green, size=int(dbscan_radius), marker=False)

    for roi in ROIs:
        gmap.scatter([roi.center_range[0]],[roi.center_range[1]],whitey, size=roi.center_range[2], marker=False)

    o = os.path.join(output_folder,"map.html")
    gmap.draw(o)

    return o
