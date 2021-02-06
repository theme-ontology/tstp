

# simple memoization
class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        key = (tuple(args), tuple(sorted(kwargs.items())))
        return self[key]

    def __missing__(self, key):
        args, kwargs = key
        result = self[key] = self.func(*args, **dict(kwargs))
        return result


