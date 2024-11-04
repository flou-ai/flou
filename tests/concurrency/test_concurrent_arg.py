# Test arg with a fork to 2 concurrent final states

from flou.ltm import LTM
from flou.database import get_db
from flou.engine import get_engine


class ConcurrentState(LTM):
    name = 'concurrent_{kwarg}'


class LaunchConcurrentState(LTM):
    name = 'launch_concurrent'

    def run(self, payload=None):
        self.transition('start_{kwarg}', params=[{'kwarg': '1', }, {'kwarg': '2', }])


class ConcurrentLTM(LTM):
    name = 'concurrent'

    init = [LaunchConcurrentState]
    transitions = [
        {'from': LaunchConcurrentState, 'label': 'start_{kwarg}', 'to': ConcurrentState}
    ]


def test_concurrent_arg(session):

    root = ConcurrentLTM()
    root.start()

    db = get_db(session)
    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert len(doneLTM._snapshots) == 6
    assert doneLTM._state['concurrent_1'] == {'_status': 'active'}
    assert doneLTM._state['concurrent_2'] == {'_status': 'active'}


# Test two concurrent states launched by a transition and then only one transitions


class MultipleConcurrentState1(LTM):
    name = 'first_concurrent_{kwarg}'


class MultipleConcurrentState2(LTM):
    name = 'second_concurrent_{kwarg}'


class MultipleConcurrentLTM(LTM):
    name = 'multiple_concurrent'

    init = [LaunchConcurrentState]
    transitions = [
        {'from': LaunchConcurrentState, 'label': 'start_{kwarg}', 'to': MultipleConcurrentState1},
        {'from': MultipleConcurrentState1, 'label': 'next_{kwarg}', 'to': MultipleConcurrentState2}
    ]


def test_multiple_concurrent_arg(session):

    root = MultipleConcurrentLTM()
    root.start()

    db = get_db(session)
    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert len(doneLTM._snapshots) == 6
    assert doneLTM._state['first_concurrent_1'] == {'_status': 'active'}
    assert doneLTM._state['first_concurrent_2'] == {'_status': 'active'}

    assert 'second_concurrent_1' not in doneLTM._state
    assert 'second_concurrent_2' not in doneLTM._state

    engine = get_engine()
    engine.transition(root, "next_{kwarg}", params=[{'kwarg': '1'}])

    doneLTM = db.load_ltm(root.id, snapshots=True)


    assert len(doneLTM._snapshots) == 8

    assert doneLTM._state['first_concurrent_1'] == {'_status': 'finished'}
    assert doneLTM._state['first_concurrent_2'] == {'_status': 'active'}
    assert doneLTM._state['second_concurrent_1'] == {'_status': 'active'}

    assert 'second_concurrent_2' not in doneLTM._state

    engine = get_engine()
    engine.transition(doneLTM, "next_{kwarg}", params=[{'kwarg': '2'}])

    doneLTM = db.load_ltm(root.id, snapshots=True)
    assert doneLTM._state['first_concurrent_1'] == {'_status': 'finished'}
    assert doneLTM._state['first_concurrent_2'] == {'_status': 'finished'}
    assert doneLTM._state['second_concurrent_1'] == {'_status': 'active'}
    assert doneLTM._state['second_concurrent_2'] == {'_status': 'active'}

    # Now try to transition both of them at the same time

    root = MultipleConcurrentLTM()
    root.start()

    db = get_db(session)
    doneLTM = db.load_ltm(root.id, snapshots=True)

    engine = get_engine()
    engine.transition(doneLTM, "next_{kwarg}", params=[{'kwarg': '1'}, {'kwarg': '2'}])

    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert len(doneLTM._snapshots) == 9
    assert doneLTM._state['first_concurrent_1'] == {'_status': 'finished'}
    assert doneLTM._state['first_concurrent_2'] == {'_status': 'finished'}
    assert doneLTM._state['second_concurrent_1'] == {'_status': 'active'}
    assert doneLTM._state['second_concurrent_2'] == {'_status': 'active'}