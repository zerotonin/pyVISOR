class BehaviourAlreadyInCompatibilityListException(Exception):

    def __init__(self, this_behaviour, other_behaviour):
        msg = "behaviour {} already has behaviour {} listed as compatible!".format(
            this_behaviour, other_behaviour)
        super(BehaviourAlreadyInCompatibilityListException, self).__init__(msg)
        self.error = {"this_behaviour": this_behaviour,
                      "other_behaviour": other_behaviour}
