class CallbackHandler:

    def __init__(self):
        self.n_registered = -1
        self.callback_functions = {}

    def register(self, callback) -> int:
        self.n_registered += 1
        self.callback_functions[self.n_registered] = callback
        return self.n_registered

    def pop(self, n: int):
        if n in self.callback_functions:
            self.callback_functions.pop(n)

    def __iter__(self):
        return self.callback_functions.values().__iter__()
