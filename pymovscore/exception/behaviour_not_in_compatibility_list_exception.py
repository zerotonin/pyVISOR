class BehaviourNotInCompatibilityListException(Exception):

    def __init__(self, this_behaviour, other_behaviour):
        msg = "behaviour {} does not have behaviour {} listed as compatible!".format(
            this_behaviour, other_behaviour)
        super(BehaviourNotInCompatibilityListException, self).__init__(msg)
        self.error = {"this_behaviour": this_behaviour,
                      "other_behaviour": other_behaviour}
