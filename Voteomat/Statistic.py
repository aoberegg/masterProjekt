



class Statistic:

    def __init__(self, filename, voteomat):
        self.foldername = voteomat.network_func_name + voteomat.distribution_func_name
        self.filename = filename

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

