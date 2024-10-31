class Registry(object):
    """
    Registers all root LTMs

    Register a new LTM with `register(model)`.
    Get all the LTMs with get_ltms.
    """
    instance = None
    _registry = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance
        else:
            inst = cls.instance = super(Registry, cls).__new__(cls)
            return inst

    def __init__(self):
        self._registry = []

    def register(self, ltm_class):

        self._registry.append(ltm_class)

    def get_ltms(self):
        return self._registry


def get_registry():
    # Return registry
    if hasattr(get_registry, 'instance'):
        return get_registry.instance
    else:
        inst = get_registry.instance = Registry()
        return inst


registry = get_registry()