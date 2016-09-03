import os
import numpy
import commutemate.utils as utils
from commutemate.roi import PointOfInterest, RegionOfInterest

class Metrics(object):

    def __init__(self, ROIs, workspace_folder):
        self.ROIs = ROIs
        self.workspace_folder = workspace_folder
        self.POIs = {} 
        self.metrics = {}

        for id, roi in self.ROIs.iteritems():
            item = {}
            item["meta"] = {} 
            item["meta"]["id"] = id
            item["meta"]["center_range"] = roi.center_range
            item["meta"]["lat"] = roi.center_range[0]
            item["meta"]["lon"] = roi.center_range[1]
            item["meta"]["range"] = roi.center_range[2]
            item["meta"]["bearing_avg"] = roi.bearing_avg
            item["meta"]["bearing_std"] = roi.bearing_std

            self.metrics[id] = item

    def generate(self):
        for id, roi in self.ROIs.iteritems():
            self.poi_type_distribution(id, roi)
            self.stop_durations(id, roi)
            self.pass_speeds(id, roi)

        return self.metrics

    def poi_type_distribution(self, id, roi):
        metric = {}
        stop_count = len(roi.poi_ids[PointOfInterest.TYPE_STOP])
        pass_count = len(roi.poi_ids[PointOfInterest.TYPE_PASS])
        metric["stops"] = stop_count
        metric["passes"] = pass_count
        metric["total"] = stop_count + pass_count
        self.metrics[id]["poi_type_distribution"] = metric

    def stop_durations(self, id, roi):
        metric = []
        for poi_id in roi.poi_ids[PointOfInterest.TYPE_STOP]:
            poi = self.__load_POI(poi_id)
            metric.append(poi.duration)
        self.metrics[id]["stop_durations"] = metric
        self.metrics[id]["stop_duration_avg"] = numpy.mean(metric)
        self.metrics[id]["stop_duration_std"] = numpy.std(metric)

    def pass_speeds(self, id, roi):
        metric = []
        for poi_id in roi.poi_ids[PointOfInterest.TYPE_PASS]:
            poi = self.__load_POI(poi_id)
            metric.append(round(poi.point.speed, 2))
        self.metrics[id]["pass_speeds"] = metric
        self.metrics[id]["pass_speed_avg"] = numpy.mean(metric)
        self.metrics[id]["pass_speed_std"] = numpy.std(metric)

    def __load_POI(self, id):
        poi = self.POIs.get(id, None)
        if not poi:
            poi = utils.load_json(os.path.join(self.workspace_folder, "poi_%s.json" % id), PointOfInterest)
            self.POIs[id] = poi
        return poi

