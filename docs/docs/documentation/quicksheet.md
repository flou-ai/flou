# Quicksheet

## Installing and running

```shell
pip install flou
touch app.py
touch requirements.txt
touch .env
flou compose up
```

## LTMs

```python
from flou import LTM
from flou.registry import registry


class MyState(LTM):
    name = 'my_state'

    def run(self, **params):
        label = 'my_transition'
        params = {}
        self.transition(label, **params)

        self.update_store({'internal_store_key': 'store_value'})
        self.root.update_store({'global_key': 'global_value'})

        print(self.store['internal_store_key'])  # prints 'store_value'
        print(self.root.store['global_key'])  # prints 'global_value'

class EndState(LTM):
    def run(self, **params):
        print('end')


class MyNetwork(LTM):
    name = 'my_ltm'
    init = [MyState]  # init can be simple states or sub machines
    transitions = [
        {'from': MyState, label: 'my_transition', 'to': EndState}
    ]

registry.register(MyNetwork)
```

* `LTM.name`: the name of the ltm. Allowed names: `^[a-z][a-z0-9_]*$`
* `LTM.init`: start these ltms when the current one is executed
* `LTM.transitions`: list of `{'from': FromLTMClass, 'label': transition_label, 'to': ToLTMClass}`
  `from` and `to` can be a single class or an iterable of classes
* `LTM.start()`: start the root LTM, should be called only once
* `LTM.root`: returns the `root` LTM
* `LTM.parent`: returns the `parent` LTM
* `LTM.store`: returns a dict with the current LTM store, you can use `self.root.store` for global store. Don't assign directly, see `LTM.update_store`
* `LTM.update_store(update_list)`: pass a list of `{key: value}` to update the store. Use `self.root.update_store` to update the global store
* `LTM.atomic_store_append(key, value)`: atomically and immediately append `value` to a pre initialized list `key` in `self.store`. Use only in concurrent states.
* `LTM.transition(label, payload, params, namespace)`: transition all LTMS with `label` transition
