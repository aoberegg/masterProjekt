
from networkx import *
import numpy as np
from Candidate import Candidate
from Globals import *

class Voteomat:

    def __init__(self):
        self.minOrientation = -50
        self.maxOrientation = 50
        self.network_func_name = g_newman_watts_strogats
        self.networkFunc = self.newman_watts_strogats
        self.networkFunc()

        self.candidates = [];
        self.candidates.append(Candidate(0, g_left_party))
        self.candidates.append(Candidate(0, g_right_party))
        self.distribution_func_name = g_uniform_distribution
        self.set_distribution_func()
        self.counter_force_left = 0
        self.counter_force_right = 0
        self.acceptance = 0.05
        self.affecting_neighbours = True
        self.candidates_affecting = True
        self.candidates_affected = True
        self.counter_force_affecting = True
        self.statistic_up_to_date = False

    def reset(self):
        self.minOrientation = -50
        self.maxOrientation = 50
        self.networkFunc()
        self.distributionFunc()
        for candidate in self.candidates:
            candidate.reset()

        self.set_orientation_candidate(0, self.maxOrientation/2, False)
        self.set_orientation_candidate(1, self.minOrientation/2, False)
        self.statistic_up_to_date = False
        return

    def set_network_func(self, func):
        if func == g_newman_watts_strogats:
            self.networkFunc = self.newman_watts_strogats
        elif func == g_random_regular:
            self.networkFunc = self.random_regular
        elif func == g_barabasi_albert:
            self.networkFunc = self.barabasi_albert
        elif func == g_random_powerlaw_tree:
            self.networkFunc = self.random_powerlaw_tree
        elif func == g_star_network:
            self.networkFunc = self.star_network
        self.network_func_name = func
        self.reset()

    def set_network(self, G):
        self.G = G
        self.statistic_up_to_date = False

    def random_powerlaw_tree(self):
        self.G = networkx.random_powerlaw_tree(g_amount_nodes, tries= 10000)

    def barabasi_albert(self):
        self.G = networkx.barabasi_albert_graph(g_amount_nodes, 2)

    def random_regular(self):
        self.G = networkx.random_regular_graph(3,g_amount_nodes)

    def star_network(self):
        self.G = networkx.star_graph(g_amount_nodes-1)

    def newman_watts_strogats(self):
        self.G = networkx.newman_watts_strogatz_graph(g_amount_nodes, 4,0.5)

    def set_acceptance(self, acceptance):
        self.acceptance = acceptance

    def set_distribution_func(self, func = None):
        if func is None:
            func = self.distribution_func_name

        if func == g_uniform_distribution:
            self.distributionFunc = self.set_nodes_political_behaviour_uniform_distributed
        elif func == g_normal_distribution_left:
            self.distributionFunc = self.set_nodes_political_behaviour_left_normal_distributed
        elif func == g_normal_distribution_right:
             self.distributionFunc = self.set_nodes_political_behaviour_right_normal_distributed
        elif func == g_normal_distribution_avg:
            self.distributionFunc = self.set_nodes_political_behaviour_normal_distributed
        elif func == g_normal_left_and_right:
            self.distributionFunc = self.set_nodes_political_behaviour_left_and_right_distributed
        self.distribution_func_name = func
        self.reset()

    def get_network(self):
        return self.G

    def timestep_network_discussion(self):
        change = 0
        for node in self.G.nodes(data=True):
            if self.affecting_neighbours:
                change += self.neighbour_affect_each_other(node)

            if self.candidates_affecting:
                change += self.candidates_affect_node(node)

        if self.candidates_affected:
            change += self.candidates_get_affected_by_median()

        if self.counter_force_affecting:
            change += self.candidates_get_affected_by_counterforce()
        self.statistic_up_to_date = False
        return change


    def candidates_get_affected_by_counterforce(self):
        change = 0
        for candidate in self.candidates:
            if candidate.party == g_left_party:
                change += self.set_candidate_new(candidate, self.counter_force_left)
            elif candidate.party == g_right_party:
                change += self.set_candidate_new(candidate, self.counter_force_right)
        return change

    def candidates_get_affected_by_median(self):
        median, avg, std = self.get_statistic()
        change = 0
        change += self.set_candidate_new(self.candidates[0], median)
        change += self.set_candidate_new(self.candidates[1], median)
        return change


    def candidates_affect_node(self, node):
        old_orientation = self.G.nodes(data=True)[int(node[0])][1]["orientation"]
        if self.G.nodes(data=True)[int(node[0])][1]["orientation"] < 0:
            new_orientation = self.calc_new_orientation(self.G.nodes(data=True)[int(node[0])][1]["orientation"], self.candidates[1].orientation)
            self.G.nodes(data=True)[int(node[0])][1]["orientation"] = max(new_orientation, self.minOrientation)
        else:
            new_orientation = self.calc_new_orientation(self.G.nodes(data=True)[int(node[0])][1]["orientation"] , self.candidates[0].orientation)
            self.G.nodes(data=True)[int(node[0])][1]["orientation"] = max(new_orientation, self.minOrientation)

        return abs(old_orientation - new_orientation)

    def neighbour_affect_each_other(self, node):
        neighbours = self.G.neighbors(node[0])
        old_orientation = self.G.nodes(data=True)[int(node[0])][1]["orientation"]
        orientation_neighbours = 0
        for neighbour_node in neighbours:
            orientation_neighbours += self.G.nodes(data=True)[int(neighbour_node)][1]["orientation"]
        new_orientation = self.calc_new_orientation(self.G.nodes(data=True)[int(node[0])][1]["orientation"], orientation_neighbours / len(neighbours))
        if new_orientation > 0:
            self.G.nodes(data=True)[int(node[0])][1]["orientation"] = min(new_orientation, self.maxOrientation)
        else:
            self.G.nodes(data=True)[int(node[0])][1]["orientation"] = max(new_orientation, self.minOrientation)

        return abs(old_orientation - new_orientation)

    def calc_new_orientation(self, orientation_from, orientation_to):
        distance = abs(orientation_from - orientation_to)
        if orientation_from > orientation_to:
            orientation_from -= distance * self.acceptance
        else:
            orientation_from += distance * self.acceptance
        return orientation_from

    def set_candidate_new(self, candidate, median):
        orientation_old = candidate.orientation
        candidate.orientation = self.calc_new_orientation(candidate.orientation, median)
        return abs(orientation_old - candidate.orientation)

    def set_nodes_political_behaviour_uniform_distributed(self):
        for node in self.G.nodes(False):
            self.G.node[node]["orientation"] = np.random.uniform(self.minOrientation, self.maxOrientation)

    def set_max_value(self, value):
        if value > 0:
            value = min(value, self.maxOrientation)
        if value < 0:
            value = max(value, self.minOrientation)
        return value

    def set_nodes_political_behaviour_normal_distributed(self):
        for node in self.G.nodes(False):
            value = np.random.normal((self.minOrientation + self.maxOrientation)/2, 10)
            self.G.node[node]["orientation"] = self.set_max_value(value)

    def set_nodes_political_behaviour_left_and_right_distributed(self):
        for node in self.G.nodes(False):
            left = np.random.uniform(0,1)
            if(left < 0.5):
                value = np.random.normal(self.minOrientation / 2, 10)
            else:
                value = np.random.normal(self.maxOrientation / 2, 10)
            self.G.node[node]["orientation"] = self.set_max_value(value)

    def set_nodes_political_behaviour_left_normal_distributed(self):
        for node in self.G.nodes(False):
            value = np.random.normal(self.minOrientation / 2, 10)
            if value > 0:
                value = min(value, 50)
            if value < 0:
                value = max(value, -50)
            self.G.node[node]["orientation"] = self.set_max_value(value)

    def set_nodes_political_behaviour_right_normal_distributed(self):
        for node in self.G.nodes(False):
            value = np.random.normal(self.maxOrientation / 2, 10)
            self.G.node[node]["orientation"] = self.set_max_value(value)

    def set_orientation_candidate(self,candidate, new_value, save_in_list = True):
        self.candidates[candidate].set_orientation(new_value, save_in_list)

    def get_statistic(self, get_median = True, get_avg = True, get_std = True):
        if self.statistic_up_to_date:
            return self.median, self.avg, self.std
        orientation_list = []
        for entry in self.G.nodes(data = True):
            orientation_list.append(entry[1]['orientation'])
        median = 0
        avg = 0
        std = 0
        if(get_median):
            median = np.median(orientation_list)
        if(get_avg):
            avg = np.average(orientation_list)
        if(get_std):
            std = np.std(orientation_list)
        self.median = median
        self.avg = avg
        self.std = std
        self.statistic_up_to_date = True
        return median, avg, std


    def get_amount_voter(self):
        return len(self.G.nodes())


if __name__ == '__main__':
    v = Voteomat()
