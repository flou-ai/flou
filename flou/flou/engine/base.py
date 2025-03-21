from copy import deepcopy
from flou.conf import Engine


class BaseEngine:
    conf = None

    def __init__(self, conf: Engine):
        self.conf = conf

    def execute(self, ltm, item_id, fqn, payload):
        raise NotImplementedError

    def transition(self, ltm, item_id, label, params, namespace, payload):
        raise NotImplementedError

    def start(self, payload=None, params=None, playground=False):
        raise NotImplementedError

    def consume_queues(self, ltm):

        transitions_queue = deepcopy(ltm.root._transitions_queue)
        ltm.root._transitions_queue = []
        execute_queue = deepcopy(ltm.root._execute_queue)
        ltm.root._execute_queue = []

        while transitions_queue:
            transition_args = transitions_queue.pop(0)
            self.transition(ltm, **transition_args)

        while execute_queue:
            execute_args = execute_queue.pop(0)
            self.execute(ltm, **execute_args)