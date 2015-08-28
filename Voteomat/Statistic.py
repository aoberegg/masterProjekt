import csv
import os
import errno
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import copy
from Globals import *



class Statistic:

    def __init__(self, time, voteomat):

        self.foldername = voteomat.network_func_name + voteomat.distribution_func_name
        self.foldertime = time
        self.path = "Statistics//"+self.foldername+"//"
        self.path += g_candidates_affecting_nodes + "=" + str(voteomat.candidates_affecting) + "_"
        self.path += g_candidates_affected_by_median + "=" + str(voteomat.candidates_affected) + "_"
        self.path += g_neighbours_affecting_each_other + "=" + str(voteomat.affecting_neighbours) + "_"
        self.path += g_counterforce_affecting_candidates + "=" + str(voteomat.counter_force_affecting) + "_" + time
        self.make_sure_path_exists(self.path)
        self.file = open(self.path + "//statistic.csv", 'w')
        self.statistic = {}
        self.statistic["networkfunc"] = voteomat.network_func_name
        self.statistic["distributionfunc"] = voteomat.distribution_func_name
        self.statistic["acceptance"] = voteomat.acceptance
        median, avg, std = voteomat.get_statistic()
        self.statistic["median"] = []
        self.statistic["median"].append(median)
        self.statistic["avg"] = []
        self.statistic["avg"].append(avg)
        self.statistic["std"] = []
        self.statistic["std"].append(std)


        self.statistic["node_with_highest_degree_centrality"] = []
        self.max_degree_node = max( nx.degree_centrality(voteomat.get_network()).items(),key = lambda x: x[1])[0]
        self.statistic["node_with_highest_degree_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_degree_node][1]["orientation"])
        self.statistic["node_with_highest_closeness_centrality"] = []
        self.max_closeness_node = max( nx.closeness_centrality(voteomat.get_network()).items(),key = lambda x: x[1])[0]
        self.statistic["node_with_highest_closeness_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_closeness_node][1]["orientation"])
        self.statistic["node_with_highest_betweenness_centrality"] = []
        self.max_betweenness_node = max(nx.betweenness_centrality(voteomat.get_network()).items() ,key = lambda x: x[1])[0]
        self.statistic["node_with_highest_betweenness_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_betweenness_node][1]["orientation"])
        try:
            self.statistic["node_with_highest_eigenvector_centrality"] = []
            self.max_eigenvector_node = max( nx.eigenvector_centrality(voteomat.get_network(), max_iter = 1000).items(),key = lambda x: x[1])[0]
            self.statistic["node_with_highest_eigenvector_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_eigenvector_node][1]["orientation"])
        except nx.NetworkXError:
            print "Eigenvector centrality not possible."

        freeman = self.freeman_centrality([x[1] for x in nx.degree_centrality(voteomat.get_network()).items()], max( nx.degree_centrality(voteomat.get_network()).items(),key = lambda x: x[1])[1])
        self.statistic["freeman_centrality"] = round(freeman,2)

        self.statistic["affecting_neighbours"] = voteomat.affecting_neighbours
        self.statistic["affecting_candidates"] = voteomat.candidates_affecting
        self.statistic["affected_canddiates"] = voteomat.candidates_affected
        self.statistic["affecting_counter_force"] = voteomat.counter_force_affecting
        self.statistic["affecting_counter_force_left"] = voteomat.counter_force_left
        self.statistic["affecting_counter_force_right"] = voteomat.counter_force_right

        self.statistic["candidates"] = []
        for candidate in voteomat.candidates:
            self.statistic["candidates"].append(candidate.to_save())

    def freeman_centrality(self, centralities, max_centrality):
        sum = 0
        for centrality in centralities:
            sum += max_centrality - centrality
        return ((sum) / (len(centralities)-2))

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


    def write_statistic(self, voteomat):
        median, avg, std = voteomat.get_statistic()
        self.statistic["median"].append(median)
        self.statistic["avg"].append(avg)
        self.statistic["std"].append(std)

        self.statistic["node_with_highest_degree_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_degree_node][1]["orientation"])
        self.statistic["node_with_highest_closeness_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_closeness_node][1]["orientation"])
        self.statistic["node_with_highest_betweenness_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_betweenness_node][1]["orientation"])

        if not self.statistic["node_with_highest_eigenvector_centrality"] == []:
            self.statistic["node_with_highest_eigenvector_centrality"].append(voteomat.get_network().nodes(data = True)[self.max_eigenvector_node][1]["orientation"])

    def network_converged(self, voteomat):
        self.create_plots(voteomat)
        self.writer = csv.writer(self.file)
        for key, val in self.statistic.items():
            self.writer.writerow([key,val])
        self.file.close()


    def create_plots(self, voteomat):

        x = np.linspace(0, len(self.statistic["median"]), len(self.statistic["median"]))

        fig = plt.figure(1, figsize=(20, 20))
        handle_median, = plt.plot(x, self.statistic["median"], '-', label='Median')
        handle_avg, = plt.plot(x, self.statistic["avg"], '-', label='Average')
        handle_std, = plt.plot(x, self.statistic["std"], '-', label='Standard deviation')

        handle_degree_centrality, = plt.plot(x, self.statistic["node_with_highest_degree_centrality"], '-', label='Node w. max degree centrality')
        handle_closeness_centrality, = plt.plot(x, self.statistic["node_with_highest_closeness_centrality"], '-', label='Node w. max closeness centrality')
        handle_betweenness_centrality, = plt.plot(x, self.statistic["node_with_highest_betweenness_centrality"], '-', label='Node w. max betweenness centrality')

        #handle_affected, = plt.plot(x, np.linspace(voteomat.counter_force_affecting, voteomat.counter_force_affecting, len(self.statistic["median"])), '', label=)

        handles = [handle_median, handle_avg, handle_std, handle_degree_centrality, handle_closeness_centrality, handle_betweenness_centrality]
        i = 1
        for candidate in voteomat.candidates:
            candidate_handle, = plt.plot(x, candidate.orientation_over_timesteps, '-', label ='Candidate '+str(i))
            handles.append(candidate_handle)
            i += 1

        if not self.statistic["node_with_highest_eigenvector_centrality"] == []:
            handle_eigenvector_centrality, = plt.plot(x, self.statistic["node_with_highest_eigenvector_centrality"], '-', label='Node w. max eigenvector centrality')
            handles.append(handle_eigenvector_centrality)

        plt.legend(handles= handles)
        plt.xlabel("Timestep")
        plt.ylabel("Political orientation")

        text = g_candidates_affecting_nodes + " = " + str(voteomat.candidates_affecting) + "\n"
        text += g_candidates_affected_by_median + " = " + str(voteomat.candidates_affected) + "\n"
        text += g_neighbours_affecting_each_other + " = " + str(voteomat.affecting_neighbours)+ "\n"
        text += g_counterforce_affecting_candidates + " = " + str(voteomat.counter_force_affecting)+ "\n"
        text += "Network function =  " + str(voteomat.network_func_name)
        text += "Distribution = " + str(voteomat.distribution_func_name)

        plt.suptitle("Voting process")

        fig.savefig(self.path+"//statistic.png")
        plt.close()

    def save_histogram(self, histogram, timestep):
        histogram.savefig(self.path+"//histogramm_timestep_"+ str(timestep))

    def save_network(self, network, timestep):
        network.savefig(self.path+"//network_timestep_"+str(timestep))
