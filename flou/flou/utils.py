from collections.abc import Iterable


pop_or_none = lambda l: l.pop(0) if l else None


def to_set(value):
    """
    Cast to set if element or Iterable
    """
    if isinstance(value, set):
        return value
    if isinstance(value, Iterable):
        return set(value)
    if value:
        return { value }
    else:
        return set()


def to_list(value):
    """
    Cast to set if element or Iterable
    """
    if isinstance(value, Iterable):
        return list(value)
    if value:
        return [ value ]
    else:
        return []


def get_fqn(obj, fqn):
    """
    Access obj[fqn[0]]...[fqn[n]]
    """

    for name in fqn.split('.'):
        if name == '':
            continue
        if obj is None:
            return None
        if name in obj:
            obj = obj[name]
        else:
            return None
    return obj