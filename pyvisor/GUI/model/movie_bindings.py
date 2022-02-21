from typing import Dict, Union, List

from .key_bindings import KeyBindings
from .scorer_action import ScorerAction


class MovieBindings:
    _movie_actions = ["toggleRunMov", "stopToggle",
                      "runMovForward", "runMovReverse",
                      "changeFPShigh", "changeFPSlow",
                      "changeFrameNoHigh1",
                      "changeFrameNoLow1",
                      "changeFrameNoHigh10",
                      "changeFrameNoLow10", ]

    def __init__(self):
        self.scorer_actions = {
            ma: ScorerAction(ma) for ma in MovieBindings._movie_actions
        }  # type: Dict[str, ScorerAction]

    def keys(self):
        return self.scorer_actions.keys()

    def __getitem__(self, movie_action: str):
        return self.scorer_actions[movie_action]

    @staticmethod
    def from_dict(
            d: Dict[str, Dict[str, Union[None, str]]]
    ) -> "MovieBindings":
        bindings = MovieBindings()
        for key in MovieBindings._movie_actions:
            if key not in d:
                continue
            sa = ScorerAction(key)
            sa.key_bindings = KeyBindings.from_dict(d[key])
            bindings.scorer_actions[key] = sa
        return bindings

    def to_dict(self) -> Dict[str, Dict[str, Union[None, str]]]:
        d = {
            key: self.scorer_actions[key].key_bindings.to_dict()
            for key in self.scorer_actions
        }
        return d

    def get_action_assigned_to(self, device: str, button_identifier: str) -> ScorerAction:
        assigned = None
        for key in self.keys():
            action = self[key]
            binding = action.key_bindings[device]
            if binding != button_identifier:
                continue
            if binding is None:
                continue
            if assigned is not None:
                raise RuntimeError("Key {} is assigned to multiple movie actions.".format(button_identifier))
            assigned = action
        return assigned

    def get_actions_without_buttons_assigned(self, device: str) -> List[ScorerAction]:
        items = []
        for name in self.keys():
            action = self[name]
            if action.key_bindings[device] is not None:
                continue
            items.append(action)
        return items
