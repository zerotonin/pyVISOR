class BehavBinding:
    def __init__(self,animal     ='None',
                      color      = '#C0C0C0',
                      iconPos    = 'None',
                      behaviour  = 'None',
                      keyBinding = 'None',
                      UICdevice  = 'None'):
                      
        self.animal     = animal
        self.iconPos    = iconPos
        self.behaviour  = behaviour
        self.color      = color
        self.keyBinding = keyBinding
        self.UICdevice  = UICdevice

    def __str__(self):
        s = 'BehavBinding:\n'
        for lbl, attr in zip(
                ['animal', 'icon', 'behaviour'],
                [self.animal, self.iconPos, self.behaviour]
        ):
            s += f'  {lbl}: {attr}\n'
        return s

    def __repr__(self):
        return self.__str__()
