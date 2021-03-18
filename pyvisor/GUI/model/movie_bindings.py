from typing import Dict, Union

from .key_bindings import KeyBindings


class MovieBindings:
    movie_actions = ["toggleRunMov", "stopToggle",
                     "runMovForward", "runMovReverse",
                     "changeFPShigh", "changeFPSlow",
                     "changeFrameNoHigh1",
                     "changeFrameNoLow1",
                     "changeFrameNoHigh10",
                     "changeFrameNoLow10", ]

    def __init__(self):

        self.key_bindings = {
            ma: KeyBindings() for ma in MovieBindings.movie_actions
        }  # type: Dict[str, KeyBindings]

    def keys(self):
        return self.key_bindings.keys()

    @staticmethod
    def from_dict(
            d: Dict[str, Dict[str, Union[None, str]]]
    ) -> "MovieBindings":
        bindings = MovieBindings()
        for key in MovieBindings.movie_actions:
            if key not in d:
                continue
            bindings.key_bindings[key] = KeyBindings.from_dict(d[key])
        return bindings

    def to_dict(self) -> Dict[str, Dict[str, Union[None, str]]]:
        d = {
            key: self.key_bindings[key].to_dict()
            for key in self.key_bindings
        }
        return d
