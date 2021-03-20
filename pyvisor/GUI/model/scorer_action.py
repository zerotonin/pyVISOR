from .key_bindings import KeyBindings


class ScorerAction:

    def __init__(self, name: str, icon_path: str=None):
        self.key_bindings = KeyBindings()
        self.name = name
        self.icon_path = icon_path
