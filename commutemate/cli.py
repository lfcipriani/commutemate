import sys, os
import logging as l
from optparse import OptionParser
from commutemate.config import Config
from commutemate.gpx_parser import GpxParser
from commutemate.detectors import *
from commutemate.roi import *
import commutemate.utils as utils

class CommutemateCLI(object):
    
    def __init__(self):
        l.basicConfig(stream=sys.stdout, level=l.DEBUG, format='%(asctime)s(%(levelname)s) - %(message)s')
        commands = ['detectstops','clusterize']

        # Parsing commend line arguments
        parser = OptionParser("usage: %prog COMMAND -i FOLDER -o FOLDER -c CONFIG.INI" + 
                              "\nAvailable COMMANDs: %s" % ", ".join(commands))
        parser.add_option("-i", "--input", dest="folder", action="store",
                        help="input folder with GPX files (detectstops) or json (clusterize)")
        parser.add_option("-o", "--output",
                        action="store", dest="output_folder", metavar="FOLDER", 
                        help="folder to save the output json files")
        parser.add_option("-c", "--config",
                        action="store", dest="config", 
                        help="config file")
        (options, args) = parser.parse_args()

        # Validating arguments
        try:
            commands.index(args[0])
        except:
            parser.error("invalid command: %s. Try running with -h for help" % args[0])
        command = args[0]

        if not options.folder or not options.output_folder or not options.config:
            parser.error("config, input and output folders required")

        self.input_folder = utils.full_path(options.folder)
        self.output_folder = utils.full_path(options.output_folder)
        self.config = utils.full_path(options.config)

        if not os.path.isdir(self.input_folder):
            parser.error("input folder does not exist")

        if not os.path.exists(self.config):
            parser.error("specified config file does not exist")
        else:
            self.config = Config(self.config)

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
            if f.endswith('.json'):
                json_files.append(os.path.join(self.input_folder, f))
        l.info("There's %d POI(s) to be clusterized. Preparing data..." % len(json_files))

        # Preparing data
        geo_coords = []
        POIs = []
        for jsf in json_files:
            poi = utils.load_json(jsf, PointOfInterest)
            POIs.append(poi)
            geo_coords.append([poi.point.lat, poi.point.lon])
        X = numpy.array(geo_coords)
        Y = numpy.radians(X) # this is the input of scikit Haversine distance formula

        # Running DBSCAN cluster algorithm
        # http://scikit-learn.org/stable/modules/clustering.html#dbscan
        DB_METERS      = 7. #  for eps, as float
        DB_MIN_SAMPLES = 4

        DB_EPS = DB_METERS / 1000 / 6372 # Haversine outputs without considering Earth radius
        DB_METRIC = 'haversine'
        l.info("Running DBSCAN with eps=%d meters, min_samples=%d, metric=%s" % (DB_METERS, DB_MIN_SAMPLES, DB_METRIC))

        db = DBSCAN(eps=DB_EPS, min_samples=DB_MIN_SAMPLES, metric=DB_METRIC).fit(Y)

        l.info("Done!")

        l.info("Rendering visualization")
        core_samples_mask = numpy.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True # array of true/false, true for core sample, false otherwise

        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

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

        o = os.path.join(self.output_folder,"map.html")
        gmap.draw(o)
        l.info("Done! There is %d regions of interest detected\nThe map visualization is available at %s" % (n_clusters_, o))

def main():
    CommutemateCLI()

if __name__ == "__main__":
    main()
