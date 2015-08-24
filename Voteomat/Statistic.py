import csv
import os
import errno
import networkx as nx



class Statistic:

    def __init__(self, time, voteomat):
        self.foldername = voteomat.network_func_name + voteomat.distribution_func_name
        self.foldertime = time
        self.statistic = {}
        self.statistic["networkfunc"] = voteomat.network_func_name
        self.statistic["distributionfunc"] = voteomat.distribution_func_name
        median, avg, std = voteomat.get_statistic()
        self.statistic["median"] = []
        self.statistic["median"].append(median)
        self.statistic["avg"] = []
        self.statistic["avg"].append(avg)
        self.statistic["std"] = []
        self.statistic["std"].append(std)

        node =  max( nx.degree_centrality(voteomat.get_network()).items(),key = lambda x: x[1])
        self.statistic["node_with_highest_degree_centrality"] = voteomat.get_network().nodes(data = True)[node[0]]

        self.path = self.foldername+"//"+self.foldertime
        self.make_sure_path_exists(self.path)
        self.writer = csv.writer(open(self.path + "//statistic.csv", 'w'))
        for key, val in self.statistic.items():
            self.writer.writerow([key,val])

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        #write down initial settings:
            #networkfunc
            #distribution
            #median
            #acceptance
            #write down which orientation the most central point (most neighbours?!) in the network had + how central the point is that means the avg degree of the network + the degree of the most central point
            #median, avg, std

#        self.affecting_neighbours = True
#        self.candidates_affecting = True
        #self.candidates_affected = True
#        self.counter_force_affecting = True#
        #candidates orientation

  #  def write_statistic(self, voteomat):
        #'#writestatistic

    def __del__(self):
        self.file.close()

