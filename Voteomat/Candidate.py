__author__ = 'aoberegg'


class Candidate:
    def __init__(self, orientation, party):
        self.orientation = orientation;
        self.party = party

    def set_orientation(self,orientation):
        self.orientation = orientation

    def get_orientation(self):
        return self.orientation

#