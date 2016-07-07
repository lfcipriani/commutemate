import sys, os, math
import datetime
import logging as l
from optparse import OptionParser
from commutemate.roi import PointOfInterest, RegionOfInterest
from commutemate.config import Config
from commutemate.gpx_parser import GpxParser
from commutemate.detectors import detect_stops
import commutemate.utils as utils

class CommutemateCLI(object):
    
    def __init__(self):
        l.basicConfig(stream=sys.stdout, level=l.DEBUG, format='%(asctime)s(%(levelname)s) - %(message)s')
        commands = ['detectstops','clusterize']

        # Parsing commend line arguments
        parser = OptionParser("usage: %prog COMMAND -i FOLDER -o FOLDER [-c CONFIG.INI]" + 
                              "\nAvailable COMMANDs: %s" % ", ".join(commands))
        parser.add_option("-i", "--input", dest="folder", action="store",
                        help="input folder with GPX files (detectstops) or json (clusterize)")
        parser.add_option("-o", "--output",
                        action="store", dest="output_folder", metavar="FOLDER", 
                        help="folder to save the output json files")
        parser.add_option("-c", "--config",
                        action="store", dest="config", 
                        help="config file (optional)")
        (options, args) = parser.parse_args()

        # Validating arguments
        try:
            commands.index(args[0])
        except:
            parser.error("invalid command: %s. Try running with -h for help" % args[0])
        command = args[0]

        if not options.folder or not options.output_folder:
            parser.error("config, input and output folders required")

        self.input_folder = utils.full_path(options.folder)
        self.output_folder = utils.full_path(options.output_folder)

        if not options.config:
            self.config = Config()
        else:
            self.config = utils.full_path(options.config)
            if not os.path.exists(self.config):
                parser.error("specified config file does not exist")
            else:
                self.config = Config(self.config)

        l.info(self.config.__str__())

        if not os.path.isdir(self.input_folder):
            parser.error("input folder does not exist")

        if not os.path.isdir(self.output_folder):
            os.makedirs(self.output_folder)

        getattr(self,command)()

    def detectstops(self):
        # Getting all gpx files in specified folder
        gpx_files = []
        for f in os.listdir(self.input_folder):
            if f.endswith('.gpx'):
                gpx_files.append(os.path.join(self.input_folder, f))
        l.info("There's %d gpx files to be proccessed. Starting now..." % len(gpx_files))

        # Detecting Stops and storing Points of Interest
        total = 0
        for gpx in gpx_files:
            ride  = GpxParser(gpx).get_ride_from_track(self.config.region_ignores)

            stops = detect_stops(ride)

            stop_count = len(stops)
            total += stop_count
            l.info("%s: %d stop(s) detected" % (os.path.basename(gpx), stop_count))
            for s in stops:
                utils.save_json(os.path.join(self.output_folder, "poi_%s.json" % s.id), s.to_JSON())

        l.info("Done! There was %d stops detected\nThe data is available at %s" % (total, self.output_folder))

    def clusterize(self):
        import numpy
        from sklearn.cluster import DBSCAN

        # Getting all json files in specified folder
        json_files = []
        for f in os.listdir(self.input_folder):
            if os.path.basename(f).startswith("poi_") and f.endswith('.json'):
                json_files.append(os.path.join(self.input_folder, f))
        l.info("There's %d POI(s) to be clusterized. Preparing data..." % len(json_files))

        # Preparing data
        geo_coords = []
        POIs = []
        for jsf in json_files:
            poi = utils.load_json(jsf, PointOfInterest)
            POIs.append(poi)
            geo_coords.append([poi.point.lat, poi.point.lon])
        POIs = numpy.array(POIs)
        X = numpy.array(geo_coords)
        Y = numpy.radians(X) # this is the input of scikit Haversine distance formula

        # Running DBSCAN cluster algorithm
        # http://scikit-learn.org/stable/modules/clustering.html#dbscan
        DB_METERS      = self.config.dbscan_eps_in_meters #  for eps, as float
        DB_MIN_SAMPLES = self.config.dbscan_min_samples

        DB_EPS = DB_METERS / 1000 / 6372 # Haversine outputs without considering Earth radius
        DB_METRIC = 'haversine'
        l.info("Running DBSCAN with eps=%d meters, min_samples=%d, metric=%s" % (DB_METERS, DB_MIN_SAMPLES, DB_METRIC))

        db = DBSCAN(eps=DB_EPS, min_samples=DB_MIN_SAMPLES, metric=DB_METRIC).fit(Y)

        l.info("Done!")
        l.info("Creating regions of interest")

        core_samples_mask = numpy.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True # array of true/false, true for core sample, false otherwise

        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        ROIs = []
        roi_labels = set(labels) - set([-1])
        l.info("ROI: center=[lat,lon] range=in meters POIs=[total] ([core] + [non core])")
        for k in roi_labels:
            roi_ = RegionOfInterest()

            class_member_mask = (labels == k)
            core     = POIs[class_member_mask & core_samples_mask]
            non_core = POIs[class_member_mask & ~core_samples_mask]

            roi_.set_poi_list(core.tolist(), RegionOfInterest.CORE)
            roi_.set_poi_list(non_core.tolist(), RegionOfInterest.NON_CORE)
            roi_.calculate_center_range(DB_METERS)

            l.info("ROI: center=[%3.7f,%3.7f] range=%2.3f meters POIs=%d (%d + %d)" % (roi_.center_range[0], roi_.center_range[1], roi_.center_range[2], len(core) + len(non_core), len(core), len(non_core)))
            ROIs.append(roi_)

        now = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
        i   = 1
        roi_count = len(ROIs)
        for roi_ in ROIs:
            utils.save_json(os.path.join(self.output_folder, ("roi_%s_%0"+ str(len(str(roi_count))) + "d.json") % (now, i)), roi_.to_JSON())
            i += 1

        l.info("Done! There was %d regions of interest detected\nThe data is available at %s" % (len(ROIs), self.output_folder))

        # Rendering map
        l.info("Rendering visualization")
        import gmplot
        gmap = gmplot.GoogleMapPlotter(52.52732, 13.41766, 12)

        black  = '#000000' # noise
        blue   = '#31ABD4' # non-core values
        red    = '#C93660' # core values
        unique_labels = set(labels)
        for k in unique_labels:
            class_member_mask = (labels == k) # array of true/false. true if label equal set of label value

            xy = X[class_member_mask & core_samples_mask]
            gmap.scatter(xy[:, 0], xy[:, 1], red, size=int(DB_METERS), marker=False)

            xy = X[class_member_mask & ~core_samples_mask]
            gmap.scatter(xy[:, 0], xy[:, 1], black if k == -1 else blue, size=int(DB_METERS), marker=False)

        for roi in ROIs:
            gmap.scatter([roi.center_range[0]],[roi.center_range[1]],'#DDDDDD', size=roi.center_range[2], marker=False)

        o = os.path.join(self.output_folder,"map.html")
        gmap.draw(o)
        l.info("Done!\nThe map visualization is available at %s" % o)

def main():
    CommutemateCLI()

if __name__ == "__main__":
    main()
