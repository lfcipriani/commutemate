import sys, os, math, json, re
import datetime
import logging as l
from optparse import OptionParser
from commutemate.roi import PointOfInterest, RegionOfInterest
from commutemate.config import Config
from commutemate.gpx_parser import GpxParser
from commutemate.detectors import detect_stops, detect_passes
from commutemate.metrics import Metrics
import commutemate.utils as utils

class CommutemateCLI(object):
    
    def __init__(self):
        l.basicConfig(stream=sys.stdout, level=l.DEBUG, format='%(asctime)s(%(levelname)s) - %(message)s')
        commands = ['detectstops','clusterize','detectpasses','lint','generatemetrics']

        # Parsing commend line arguments
        parser = OptionParser("usage: %prog COMMAND -i GPX_FOLDER -w WORKSPACE_FOLDER [-c CONFIG.INI]" + 
                              "\nAvailable COMMANDs: %s" % ", ".join(commands))
        parser.add_option("-g", "--gpx", dest="gpx_folder", action="store",
                        help="input folder with GPX files (detectstops, detectpasses)")
        parser.add_option("-w", "--workspace",
                        action="store", dest="workspace_folder", 
                        help="workspace where json files could be loaded and saved (all commands)")
        parser.add_option("-c", "--config",
                        action="store", dest="config", 
                        help="config file (optional)")
        parser.add_option("-r", "--roiversion",
                        action="store", dest="roiversion", 
                        help="ROI version (for generating metrics only)")
        (options, args) = parser.parse_args()

        # Validating arguments
        try:
            commands.index(args[0])
        except:
            parser.error("invalid command: %s. Try running with -h for help" % args[0])
        command = args[0]

        if not options.workspace_folder:
            parser.error("workspace folder always required")
        self.workspace_folder = utils.full_path(options.workspace_folder)
        if not os.path.isdir(self.workspace_folder):
            os.makedirs(self.workspace_folder)

        if command == "detectstops" or command == "detectpasses":
            if not options.gpx_folder or not os.path.isdir(options.gpx_folder):
                parser.error("gpx folder required or missing")
            self.gpx_folder = utils.full_path(options.gpx_folder)

        if not options.config:
            self.config = Config()
        else:
            self.config = utils.full_path(options.config)
            if not os.path.exists(self.config):
                parser.error("specified config file does not exist")
            else:
                self.config = Config(self.config)

        if command == "generatemetrics":
            if not options.roiversion:
                parser.error("you need to pass a ROI version such as 20160903_150406 (extracted from roi_20160903_150406_38.json)")
            self.roi_version = options.roiversion

        l.info(self.config.__str__())

        getattr(self,command)()

    def detectstops(self):
        # Getting all gpx files in specified folder
        gpx_files = []
        for f in os.listdir(self.gpx_folder):
            if f.endswith('.gpx'):
                gpx_files.append(os.path.join(self.gpx_folder, f))
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
                utils.save_json(os.path.join(self.workspace_folder, "poi_%s.json" % s.id), s.to_JSON())

        l.info("Done! There was %d stops detected\nThe data is available at %s" % (total, self.workspace_folder))

    def clusterize(self):
        import numpy
        import commutemate.clustering as clustering

        json_files = []
        for f in os.listdir(self.workspace_folder):
            if os.path.basename(f).startswith("poi_") and f.endswith('.json'):
                json_files.append(os.path.join(self.workspace_folder, f))
        l.info("There's %d POI(s) to be clusterized. Preparing data..." % len(json_files))

        geo_coords = []
        POIs = []
        for jsf in json_files:
            poi = utils.load_json(jsf, PointOfInterest)
            POIs.append(poi)
            geo_coords.append([poi.point.lat, poi.point.lon])
        POIs = numpy.array(POIs)
        X = numpy.array(geo_coords)

        l.info("Running DBSCAN with eps=%d meters, min_samples=%d, metric=%s" % (self.config.dbscan_eps_in_meters, self.config.dbscan_min_samples, 'haversine'))

        # ============== clustering with dbscan =============== #
        db = clustering.cluster_with_bearing_weight(POIs, X, self.config.dbscan_eps_in_meters, self.config.dbscan_min_samples)

        l.info("Done!")
        l.info("Creating regions of interest")

        labels = db#.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        # ============== creating ROIs =============== #
        ROIs = clustering.create_ROIs(POIs, labels, self.workspace_folder, self.config.dbscan_eps_in_meters)

        for roi_ in ROIs:
            l.info("ROI: center=[% 11.7f,% 11.7f] range=%3d meters POIs=%3d bea.avg=%6.2f bea.std=%6.2f" % (roi_.center_range[0], roi_.center_range[1], roi_.center_range[2], len(roi_.get_all_poi_coords()), roi_.bearing_avg, roi_.bearing_std))
        l.info("Done! There was %d regions of interest detected\nThe data is available at %s" % (len(ROIs), self.workspace_folder))

        # ============== rendring map =============== #
        l.info("Rendering visualization")
        o = clustering.render_map(ROIs, POIs, X, labels, self.workspace_folder, self.config.dbscan_eps_in_meters)

        l.info("Done!\nThe map visualization is available at %s" % o)

    def detectpasses(self):
        # Getting all gpx files in specified folder
        gpx_files = []
        for f in os.listdir(self.gpx_folder):
            if f.endswith('.gpx'):
                gpx_files.append(os.path.join(self.gpx_folder, f))
        l.info("There's %d gpx files to be proccessed." % len(gpx_files))

        # Loading ROIs
        json_files = []
        for f in os.listdir(self.workspace_folder):
            if os.path.basename(f).startswith("roi_") and f.endswith('.json'):
                json_files.append(os.path.join(self.workspace_folder, f))

        ROIs = []
        for jsf in json_files:
            roi = utils.load_json(jsf, RegionOfInterest)
            ROIs.append(roi)
        l.info("Loaded %d ROIs." % len(json_files))

        # Detecting Passes and storing Points of Interest
        total = 0
        total_stats = {
                "# ROIs entered": 0,
                "# ROIs stop POI": 0, 
                "# ROIs stop without POI": 0, 
                "# ROIs pass": 0,
                "# ROIs pass but no cluster": 0,
            }
        for gpx in gpx_files:
            ride  = GpxParser(gpx).get_ride_from_track(self.config.region_ignores)

            passes, stats = detect_passes(
                    ride, 
                    ROIs, 
                    self.config.dbscan_eps_in_meters, 
                    self.config.dbscan_min_samples, 
                    self.workspace_folder)

            for k in stats.keys():
                total_stats[k] += stats[k]
            passes_count = len(passes)
            total += passes_count
            l.info("%s: %d passe(s) detected" % (os.path.basename(gpx), passes_count))
            for p in passes:
                utils.save_json(os.path.join(self.workspace_folder, "poi_%s.json" % p.id), p.to_JSON())

        l.info("Detection metrics: %s" % total_stats)
        l.info("Done! There was %d passes detected\nThe data is available at %s" % (total, self.workspace_folder))

    def generatemetrics(self):
        # Loading ROIs
        json_files = []
        for f in os.listdir(self.workspace_folder):
            if os.path.basename(f).startswith("roi_" + self.roi_version) and f.endswith('.json'):
                json_files.append(os.path.join(self.workspace_folder, f))

        ROIs = {} 
        pattern = re.compile("roi_(\d+_\d+_\d+)\.")
        for jsf in json_files:
            roi = utils.load_json(jsf, RegionOfInterest)
            ROIs[pattern.search(jsf).group(1)] = roi
        l.info("Loaded %d ROIs." % len(json_files))
        l.info("Generating metrics...")

        obj = Metrics(ROIs, self.workspace_folder).generate()

        output = os.path.join(self.workspace_folder, "metrics.json")
        utils.save_json(os.path.join(output), json.dumps(obj, indent=4))
        l.info("Done! The metrics are available at %s" % output)

    def lint(self):
        # Loading ROIs
        json_files = []
        for f in os.listdir(self.workspace_folder):
            if os.path.basename(f).startswith("roi_") and f.endswith('.json'):
                json_files.append(os.path.join(self.workspace_folder, f))

        ok = True
        for jsf in json_files:
            roi = utils.load_json(jsf, RegionOfInterest)
            clen = len(roi.get_all_poi_coords())
            RegionOfInterest.hydrate_POIs(roi, self.workspace_folder)
            plen = len(roi.get_all_pois())
            if clen != plen:
                l.error("Problem with ROI: %s" % jsf)
                ok = False

        if ok:
            l.info("All ROIs are OK! \o/")
        else:
            l.error("Problem to load ROI may affect the results.")


def main():
    CommutemateCLI()

if __name__ == "__main__":
    main()
