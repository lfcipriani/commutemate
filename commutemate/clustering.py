import os
import datetime
import numpy, gmplot
from sklearn.cluster import DBSCAN
import commutemate.utils as utils
from commutemate.roi import RegionOfInterest

def cluster(X, eps_in_meters, min_samples):
    # Running DBSCAN cluster algorithm
    # http://scikit-learn.org/stable/modules/clustering.html#dbscan
    Y = numpy.radians(X) # this is the input of scikit Haversine distance formula
    DB_EPS = eps_in_meters / 1000 / 6372 # Haversine outputs without considering Earth radius
    db = DBSCAN(eps=DB_EPS, min_samples=min_samples, metric='haversine').fit(Y)
    return db

def create_ROIs(POIs, labels, roi_labels, core_samples_mask, output_folder, add_center_range=0):
    ROIs = []
    for k in roi_labels:
        roi_ = RegionOfInterest()

        class_member_mask = (labels == k)
        core     = POIs[class_member_mask & core_samples_mask]
        non_core = POIs[class_member_mask & ~core_samples_mask]

        roi_.set_poi_list(core.tolist(), RegionOfInterest.CORE)
        roi_.set_poi_list(non_core.tolist(), RegionOfInterest.NON_CORE)
        roi_.calculate_center_range(add_center_range)

        ROIs.append(roi_)

    now = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    i   = 1
    roi_count = len(ROIs)
    for roi_ in ROIs:
        utils.save_json(os.path.join(output_folder, ("roi_%s_%0"+ str(len(str(roi_count))) + "d.json") % (now, i)), roi_.to_JSON())
        i += 1

    return ROIs

def render_map(ROIs, X, labels, core_samples_mask, output_folder, dbscan_radius):
    import gmplot
    gmap = gmplot.GoogleMapPlotter(52.52732, 13.41766, 12)

    black  = '#000000' # noise
    blue   = '#31ABD4' # non-core values
    red    = '#C93660' # core values
    unique_labels = set(labels)
    for k in unique_labels:
        class_member_mask = (labels == k) # array of true/false. true if label equal set of label value

        xy = X[class_member_mask & core_samples_mask]
        gmap.scatter(xy[:, 0], xy[:, 1], red, size=int(dbscan_radius), marker=False)

        xy = X[class_member_mask & ~core_samples_mask]
        gmap.scatter(xy[:, 0], xy[:, 1], black if k == -1 else blue, size=int(dbscan_radius), marker=False)

    for roi in ROIs:
        gmap.scatter([roi.center_range[0]],[roi.center_range[1]],'#DDDDDD', size=roi.center_range[2], marker=False)

    o = os.path.join(output_folder,"map.html")
    gmap.draw(o)

    return o
