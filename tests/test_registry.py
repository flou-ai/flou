from flou.registry import registry
from flou.ltm import LTM


class MyLTM(LTM):
    name = 'root'


def test_registry():
    registry._registry = []
    registry.register(MyLTM)

    assert registry.get_ltms() == [MyLTM]