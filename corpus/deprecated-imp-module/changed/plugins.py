import imp


def load(name):
    return imp.load_module(name, *imp.find_module(name))
