__author__ = 'aoberegg'


class Candidate:
    def __init__(self, orientation, party):
        self.orientation = orientation;
        self.party = party
        self.orientation_over_timesteps = []

    def set_orientation(self, orientation, save_in_list=True):
        self.orientation = orientation
        if(save_in_list):
            self.orientation_over_timesteps.append(round(self.orientation,2))


    def get_orientation(self):
        return self.orientation

    def to_save(self):
        candidate_dict = {}
        candidate_dict["orientation_over_time"] = self.orientation_over_timesteps
        candidate_dict["party"] = self.party
        return candidate_dict

    def reset(self):
        self.orientation_over_timesteps = []