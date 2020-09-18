from typing import List, Dict, Any


class BehavBinding:
    def __init__(self,
                 animal     ='None',
                 color      = '#C0C0C0',
                 icon_path  ='None',
                 behaviour  = 'None',
                 keyBinding = 'None',
                 device  ='None'):
                      
        self.animal     = animal
        self.icon_path    = icon_path
        self.behaviour  = behaviour
        self.color      = color
        self.keyBinding = keyBinding
        self.device  = device

    def __str__(self):
        s = 'BehavBinding:\n'
        for lbl, attr in zip(
                ['animal', 'icon', 'behaviour'],
                [self.animal, self.icon_path, self.behaviour]
        ):
            s += f'  {lbl}: {attr}\n'
        return s

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'key': self.keyBinding,
            'animal': self.animal,
            'behaviour': self.behaviour,
            'icon_path': self.icon_path,
            'color': self.color,
            'device': self.device,
        }
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BehavBinding":
        if len(d) != 6:
            msg = "Can't generate BehavBinding from dict. Dict needs to have exactly 6 keys: 'animal', 'color', "
            msg += "'icon_path', 'behaviour', 'key', 'device'.\n"
            msg += "Your dictionary:\n"
            msg += str(d)
            raise ValueError(msg)
        return BehavBinding(
            d['animal'],
            d['color'],
            d['icon_path'],
            d['behaviour'],
            d['key'],
            d['device']
        )

    @staticmethod
    def from_object_dict_to_savable_dict(bindings: Dict[str, "BehavBinding"]) -> Dict[str, Any]:
        d = {}
        for key in bindings:
            if key in d:
                raise ValueError(f"Button '{key}' is already in dict. Make sure buttons are uniquely assigned!")
            d[key] = bindings[key].to_dict()
        return d

    @staticmethod
    def from_savable_dict_to_dict_of_objects(plain_dict: Dict[str, Dict[str, Any]]) -> Dict[str, 'BehavBinding']:
        d = {}
        for key in plain_dict:
            if key in d:
                raise ValueError(f"Button '{key}' is already in dict. Make sure buttons are uniquely assigned!")
            d[key] = BehavBinding.from_dict(plain_dict[key])
        return d