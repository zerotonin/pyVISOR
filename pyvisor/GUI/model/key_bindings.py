from typing import Union, Dict


class KeyBindings:

    def __init__(self):
        self.xbox = None  # type: Union[str, None]
        self.playstation = None  # type: Union[str, None]
        self.keyboard = None  # type: Union[str, None]
        self.free = None  # type: Union[str, None]

    def get(self, device: str) -> Union[str, None]:
        if device == 'X-Box':
            return self.xbox
        elif device == 'Playstation':
            return self.playstation
        elif device == "Keyboard":
            return self.keyboard
        elif device == "Free":
            return self.free
        raise KeyError("Unknown device '{}'".format(device))

    def __getitem__(self, device: str) -> Union[str, None]:
        return self.get(device)

    def to_dict(self) -> Dict[str, Union[None, str]]:
        return {
            "X-Box": self.xbox,
            "Playstation": self.playstation,
            "Keyboard": self.keyboard,
            "Free": self.free
        }

    @staticmethod
    def from_dict(d: Dict[str, Union[None, str]]):
        bindings = KeyBindings()
        if "X-Box" in d:
            bindings.xbox = d['X-Box']
        if "Free" in d:
            bindings.free = d['Free']
        if "Playstation" in d:
            bindings.playstation = d['Playstation']
        if "Keyboard" in d:
            bindings.keyboard = d['Keyboard']
        return bindings
