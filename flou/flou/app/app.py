from flou.ltm import LTM
from flou.registry import registry


class FirstState(LTM):
    name = 'first_state'

    def run(self, payload=None):
        self.transition('continue')


class SecondState(LTM):
    name = 'second_state'


class MyLTM(LTM):
    name = 'root'
    init = [FirstState]
    transitions = [{'from': FirstState, 'label': 'continue', 'to': SecondState}]


registry.register(MyLTM)