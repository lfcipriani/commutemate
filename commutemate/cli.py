import sys, os
import logging as l
from optparse import OptionParser
from commutemate.gpx_parser import GpxParser
from commutemate.detectors import *

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
                
    def __get_path(self, folder):
        return os.path.abspath(os.path.join(os.getcwd(), folder))

    def __save_json(self, filename, content):
        outputFile = open(filename, "w")
        outputFile.write(content)
        outputFile.close()

def main():
    CommutemateCLI()

if __name__ == "__main__":
    main()
