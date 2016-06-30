import sys, os
import logging as l
from optparse import OptionParser
from commutemate.gpx_parser import GpxParser
from commutemate.detectors import *
from commutemate.roi import *

class CommutemateCLI(object):
    
    def __init__(self):
        l.basicConfig(stream=sys.stdout, level=l.DEBUG, format='%(asctime)s(%(levelname)s) - %(message)s')
        commands = ['detectstops','clusterize']

        # Parsing commend line arguments
        parser = OptionParser("usage: %prog COMMAND -i FOLDER -o FOLDER" + 
                              "\nAvailable COMMANDs: %s" % ", ".join(commands))
        parser.add_option("-i", "--input", dest="folder", action="store",
                        help="input folder with GPX files (detectstops) or json (clusterize)")
        parser.add_option("-o", "--output",
                        action="store", dest="output_folder", metavar="FOLDER", 
                        help="folder to save the output json files")
        (options, args) = parser.parse_args()

        # Validating arguments
        try:
            commands.index(args[0])
        except:
            parser.error("invalid command: %s. Try running with -h for help" % args[0])
        command = args[0]

        if not options.folder or not options.output_folder:
            parser.error("input and output folders required")

        self.input_folder = self.__get_path(options.folder)
        self.output_folder = self.__get_path(options.output_folder)

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
            ride  = GpxParser(gpx).get_ride_from_track()
            stops = detect_stops(ride)

            stop_count = len(stops)
            total += stop_count
            l.info("%s: %d stop(s) detected" % (os.path.basename(gpx), stop_count))
            for s in stops:
                self.__save_json(os.path.join(self.output_folder, "poi_%s.json" % s.id), s.to_JSON())

        l.info("Done! There was %d stops detected\nThe data is available at %s" % (total, self.output_folder))

    def clusterize(self):
        import numpy
        from sklearn.cluster import DBSCAN
        from scipy.spatial.distance import pdist, squareform
        # Getting all json files in specified folder
        json_files = []
        for f in os.listdir(self.input_folder):
            if f.endswith('.json'):
                json_files.append(os.path.join(self.input_folder, f))
        l.info("There's %d POI(s) to be clusterized. Preparing data..." % len(json_files))

        # Preparing data
        geo_coords = []
        for jsf in json_files:
            poi = self.__load_json(jsf, PointOfInterest)
            geo_coords.append([poi.point.lat, poi.point.lon])
        X = numpy.array(geo_coords)
        Y = numpy.radians(X) # this is the input of scikit Haversine distance formula

        # Running DBSCAN cluster algorithm
        # http://scikit-learn.org/stable/modules/clustering.html#dbscan
        DB_EPS = 0.005 / 6372 # Haversine outputs without considering Earth radius
        DB_MIN_SAMPLES = 5
        DB_METRIC = 'haversine'
        l.info("Running DBSCAN with eps=%0.15f, min_samples=%d, metric=%s" % (DB_EPS, DB_MIN_SAMPLES, DB_METRIC))

        db = DBSCAN(eps=DB_EPS, min_samples=DB_MIN_SAMPLES, metric=DB_METRIC).fit(Y)

        l.info("Done!")

        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        l.info('Estimated number of clusters: %d' % n_clusters)

        print(db.labels_)
        print(len(db.core_sample_indices_))
        print(len(db.components_))

    def __get_path(self, folder):
        return os.path.abspath(os.path.join(os.getcwd(), folder))

    def __save_json(self, filename, content):
        outputFile = open(filename, "w")
        outputFile.write(content)
        outputFile.close()

    def __load_json(self, filename, class_to_deserialize=None):
        f  = open(filename, "r")
        js = f.read()
        if class_to_deserialize:
            js = class_to_deserialize.from_JSON(js)
        f.close()
        return js

def main():
    CommutemateCLI()

if __name__ == "__main__":
    main()
