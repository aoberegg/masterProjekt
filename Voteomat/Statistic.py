import csv
import os
import errno
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Globals import *
import tkFileDialog



class Statistic:

    def __init__(self, time, voteomat):

        self.foldername = voteomat.network_func_name + voteomat.distribution_func_name
        self.foldertime = time
        self.path = "Statistics//"+self.foldername+"//"
        self.path += g_candidates_affecting_nodes + "=" + str(voteomat.candidates_affecting) + "_"
        self.path += g_candidates_affected_by_median + "=" + str(voteomat.candidates_affected) + "_"
        self.path += g_neighbours_affecting_each_other + "=" + str(voteomat.affecting_neighbours) + "_"
        self.path += g_counterforce_affecting_candidates + "=" + str(voteomat.counter_force_affecting) + "_"
        self.path += "counterforce_left="+str(voteomat.counter_force_left)+"_"+"counterforce_right="+str(voteomat.counter_force_right)+ "_" + time
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
        self.statistic["node_with_minimum_degree_centrality"] = []
        self.min_degree_node = min(nx.degree_centrality(voteomat.get_network()).items(), key = lambda x: x[1])[0]
        self.statistic["node_with_minimum_degree_centrality"].append(voteomat.get_network().nodes(data = True)[self.min_degree_node][1]["orientation"])
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
        self.statistic["network"] = voteomat.get_network().nodes(data=True);

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
        self.statistic["node_with_minimum_degree_centrality"].append(voteomat.get_network().nodes(data = True)[self.min_degree_node][1]["orientation"])
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
        #colors = [[0.9803921568627451, 0.8392156862745098, 0.592156862745098], [0.9137254901960784, 0.16862745098039217, 0.8941176470588236], [0.2235294117647059, 0.34509803921568627, 0.5372549019607843], [0.6039215686274509, 0.9176470588235294, 0.0392156862745098], [0.6235294117647059, 0.09411764705882353, 0.16862745098039217], [0.9803921568627451, 0.5647058823529412, 0.12941176470588237], [0.4235294117647059, 0.8470588235294118, 0.9882352941176471], [0.2196078431372549, 0.11764705882352941, 0.10980392156862745], [0.6235294117647059, 0.6, 1.0], [0.9568627450980393, 0.49019607843137253, 0.5686274509803921], [0.4, 0.23137254901960785, 0.0]]
        colors = [[0.5568627450980392, 0.8352941176470589, 0.6627450980392157], [0.796078431372549, 0.32941176470588235, 0.7333333333333333], [0.7529411764705882, 0.4588235294117647, 0.20784313725490197], [0.2980392156862745, 0.2235294117647059, 0.1843137254901961], [0.44313725490196076, 0.8156862745098039, 0.30980392156862746], [0.803921568627451, 0.6039215686274509, 0.611764705882353], [0.8, 0.7764705882352941, 0.3215686274509804], [0.7686274509803922, 0.2549019607843137, 0.2980392156862745], [0.5019607843137255, 0.47058823529411764, 0.807843137254902], [0.3607843137254902, 0.4666666666666667, 0.25098039215686274], [0.49411764705882355, 0.6627450980392157, 0.7450980392156863], [0.3764705882352941, 0.23137254901960785, 0.396078431372549]]
        color = 0
        fig = plt.figure(1, figsize=(20, 20))

        y_left_counterforce = np.linspace(voteomat.counter_force_left, voteomat.counter_force_left,len(self.statistic["median"]))
        y_right_counterforce = np.linspace(voteomat.counter_force_right, voteomat.counter_force_right, len(self.statistic["median"]))

        handle_left_counterforce, = plt.plot(x,y_left_counterforce, '.', label='Counterforce left', color= colors[color])
        color += 1
        handle_right_counterforce, = plt.plot(x,y_right_counterforce, '+', label='Counterforce left', color= colors[color])
        color += 1

        handle_median, = plt.plot(x, self.statistic["median"], '1', label='Median', color= colors[color])
        color += 1
        handle_avg, = plt.plot(x, self.statistic["avg"], '2', label='Average', color= colors[color])
        color += 1
        handle_std, = plt.plot(x, self.statistic["std"], '3', label='Standard deviation', color= colors[color])
        color += 1

        handle_degree_centrality, = plt.plot(x, self.statistic["node_with_highest_degree_centrality"], '-', label='Node w. max degree centrality', color= colors[color])
        color += 1
        handle_degree_centrality_min, = plt.plot(x, self.statistic["node_with_minimum_degree_centrality"], '4', label='Node w. min degree centrality', color = colors[color])
        color += 1
        handle_closeness_centrality, = plt.plot(x, self.statistic["node_with_highest_closeness_centrality"], 'o', label='Node w. max closeness centrality', color= colors[color])
        color += 1
        handle_betweenness_centrality, = plt.plot(x, self.statistic["node_with_highest_betweenness_centrality"], '--', label='Node w. max betweenness centrality', color= colors[color])
        color += 1

        #handle_affected, = plt.plot(x, np.linspace(voteomat.counter_force_affecting, voteomat.counter_force_affecting, len(self.statistic["median"])), '', label=)

        handles = [handle_left_counterforce, handle_right_counterforce, handle_median, handle_avg, handle_std, handle_degree_centrality, handle_degree_centrality_min, handle_closeness_centrality, handle_betweenness_centrality]
        i = 1
        for candidate in voteomat.candidates:
            candidate_handle, = plt.plot(x, candidate.orientation_over_timesteps, ':', label ='Candidate '+str(i), color= colors[color])
            handles.append(candidate_handle)
            i += 1
            color += 1

        if not self.statistic["node_with_highest_eigenvector_centrality"] == []:
            handle_eigenvector_centrality, = plt.plot(x, self.statistic["node_with_highest_eigenvector_centrality"], '-.', label='Node w. max eigenvector centrality', color= colors[color])
            handles.append(handle_eigenvector_centrality)
            color += 1

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

    def save_network_in_file(self, G, timestep):
        path = self.path + "//network_timestep_"+str(timestep)+".nx"
        nx.write_graphml(G,path)
        #nx.write_edgelist(G, path, data = True)

    def load_network_from_file(self):
        path = tkFileDialog.askopenfilename(filetypes=(("Networkx network", ".nx"),   ("All Files", "*.*")));
        if path is not None:
            return nx.read_graphml(path)
        else:
            return None
