from flou.ltm import LTM
from ..utils import convert_lists_to_sets


# Test join of concurrent states


class LaunchConcurrentState(LTM):
    name = 'launch_concurrent'

    def run(self, payload=None):
        self.transition('start_{kwarg}', params=self.parent.launch_params)


class ToDoneConcurrentState(LTM):
    name = 'concurrent_{kwarg}'

    def run(self, payload=None):
        self.transition('done_{kwarg}', params=[self.params], payload=self.params)


class WaitForAllStates(LTM):
    name = 'wait_for_all'

    def get_initial_state(self):
        initial = super().get_initial_state()
        initial['done'] = []
        return initial

    def run(self, payload=None):
        done = self.atomic_state_append('done', payload)
        if convert_lists_to_sets(done) == convert_lists_to_sets(self.parent.launch_params):
            self.transition('done_all')


class DoneState(LTM):
    name = 'done'


class ConcurrentJoinLTM(LTM):
    name = 'concurrent'

    init = [LaunchConcurrentState]

    launch_params = [{'kwarg': '1'}, {'kwarg': '2'}]

    transitions = [
        {'from': LaunchConcurrentState, 'label': 'start_{kwarg}', 'to': ToDoneConcurrentState},
        {'from': ToDoneConcurrentState, 'label': 'done_{kwarg}', 'to': WaitForAllStates},
        {'from': WaitForAllStates, 'label': 'done_all', 'to': DoneState},
    ]


def test_join(session):

    root = ConcurrentJoinLTM()
    root.start()

    from flou.database import get_db
    db = get_db(session)

    done_LTM = db.load_ltm(root.id)

    assert done_LTM._state['done'] == {'_status': 'active'}
