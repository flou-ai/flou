from flou.ltm import LTM
# Test a concurrent with a loop to self to launch a concurrent state on a transition

class Noop(LTM):
    name = 'noop'


class ConcurrentState(LTM):
    name = 'concurrent_{kwarg}'


class ConcurrentWithLoopLTM(LTM):
    name = 'concurrent_with_loop'

    init = [Noop]
    transitions = [
        {'from': Noop, 'label': 'start_{kwarg}', 'to': {ConcurrentState, Noop}}
    ]


def test_concurrent_self_loop(session):

    root = ConcurrentWithLoopLTM()
    root.start()

    from flou.engine import get_engine
    engine = get_engine()
    engine.transition(root, "start_{kwarg}", params=[{'kwarg': '1'}])
    engine.transition(root, "start_{kwarg}", params=[{'kwarg': '2'}])

    from flou.database import get_db
    db = get_db(session)
    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert len(doneLTM._snapshots) == 9
    assert doneLTM._state['concurrent_1'] == {'_status': 'active'}
    assert doneLTM._state['concurrent_2'] == {'_status': 'active'}
