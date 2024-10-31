Flou python package
===================


First steps
-----------

1. Install with `pip install flou`

1. Create a `.env` file


Labeled Transition Models
-------------------------

`LTM` is the base class that acts both as a State Machine and as a State. Here
we'll explore its public API.

For a simple state:

```
from flou import LTM


class MyState(LTM):
    name = 'my_state'

    def run(self, **params):
        label = 'my_transition'
        params = {}
        self.transition(label, **params)

        self.update_state({'internal_state_key': 'state_value'})
        self.root.update_state({'global_key': 'global_value'})

        print(self.state['internal_state_key'])  # prints 'state_value'
        print(self.root.state['global_key'])  # prints 'global_value'
```

When executing a state's `run()` method the updates and transitions will be
queued until the state finishes executing.

For a simple state machine:

```
class EndState(LTM):
    def run(self, **params):
        print('end')


class MyLtm(LTM):
    name = 'my_ltm'
    init = [MyState]  # init can be simple states or sub machines
    transitions = [
        {'from': MyState, label: 'my_transition', 'to': EndState}
    ]
```


TODO:

- add `init`/`start` example
- maybe change `LTM.init` to `start`
- improve nomenclature

Reference:

* `LTM.name`: the name of the ltm. Allowed names: `^[a-z][a-z0-9_]*$`
* `LTM.init`: start these ltms when the current one is executed
* `LTM.transitions`: list of `{'from': FromLTMClass, 'label': transition_label, 'to': ToLTMClass}`
  `from` and `to` can be a single class or an iterable of classes
* `LTM.start()`: start the root LTM, should be called only once
* `LTM.run(**payload)`: code to execute when the LTM gets executed. Should not be called directly

* `LTM.root`: returns the `root` LTM
* `LTM.parent`: returns the `parent` LTM
* `LTM.state`: returns a dict with the current LTM state, you can use `self.root.state` for global state. Don't assign directly, see `LTM.update_state`
* `LTM.update_state(update_list)`: pass a list of `{key: value}` to update the state. Use `self.root.update_state` to update the global state
* `LTM.atomic_state_append(key, value)`: atomically and immediately append `value` to a pre initialized list `key` in `self.state`. Use only in concurrent states.
* `LTM.transition(label, payload, params, namespace)`: transition all LTMS with `label` transition


Internals
---------

### LTM statuses

When LTMs are first created they start with their `_status='init'`. When tasked
to executed they are switch to `queued` and when executed they go to `active`.
Once transitioned from them they go to `completed`.

### One class for State Machines and for States or two classes?

Right now we are testing with one class for both, in a previous iteration we had
two clases: `State` and `Machine`. We might split them again.

### Why queue transitions and updates till `run()` finishes?

* Transitions: We make sure all state executions are triggered after a successful
update to the db.
* Updates: This way we limit writes to the db and transaction rollbacks.