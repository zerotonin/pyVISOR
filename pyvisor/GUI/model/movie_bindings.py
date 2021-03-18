from typing import Dict

from .key_bindings import KeyBindings


class MovieBindings:

    def __init__(self):
        movie_actions = ["toggleRunMov", "stopToggle", "runMovForward", "runMovReverse",
                         "changeFPShigh", "changeFPSlow",
                         "changeFrameNoHigh1",
                         "changeFrameNoLow1",
                         "changeFrameNoHigh10",
                         "changeFrameNoLow10", ]

        self.key_bindings = {
            ma: KeyBindings() for ma in movie_actions
        }  # type: Dict[str, KeyBindings]
