from collections import defaultdict
from copy import deepcopy
import inspect
from typing import SupportsIndex
import uuid

import parse

from .exceptions import InvalidTransition
from .database import get_db
from .executor import get_executor
from .utils import to_set, get_fqn


class LTMState:
    """
    Abstracts all the state logic for an LTM
    """

    _state = None  # only used by root to save the global state
    _initial_state = (
        None  # shouldn't be updated, it's used for calculating snapshots only
    )
    _snapshots = None
    _rollbacks = None

    @property
    def state(self):
        """
        State shouldn't be updated directly, use `update_state` instead.
        """
        # remove the root name from the fqn as it's directly accessible from the _state
        return get_fqn(self.root._state, self.fqn.partition(".")[2])

    def _init_state(self, recursive=False):
        try:
            self.fqn
        except ValueError:  # if it's a concurrent ltm, skip it
            return

        def get_initial_state_with_status():
            # the _status can be init, queued, active, finished, error (retrying or not)
            initial = self.get_initial_state()
            initial["_status"] = "init"
            return initial

        if self.state is None:
            if self.parent:
                state = self.root._state
                for name in self.fqn.partition(".")[2].split(".")[:-1]:
                    state = state[name]

                state[self.get_name()] = get_initial_state_with_status()
                if self.params:  # if concurrent
                    # update the state so that it creates the key for concurrent states
                    self.parent.update_state({self.get_name(): self.state})
            else:
                self._state = get_initial_state_with_status()

        if recursive and self._sub_ltms:
            for ltm in self._sub_ltms.values():
                ltm._init_state(recursive=True)

    def get_initial_state(self):
        """
        Returns the intial state including the orchestration state

        All internal states start with _
        """
        return {}

    def update_state(self, updates):
        """
        Updates the state, creating or overriding a previous key

        `updates` must be dict with the relative qualifed name of the state as
        keys and their values. e.g.: `self.update_state({'key.subkey': 'value'})`
        """
        # Updates the local state and add to the queue in `root._updates_queue`

        if self.root._updates_queue is None:
            self.root._updates_queue = []
        self.root._updates_queue.append((self.fqn, updates))

        # update local state

        # remove root from base key
        base_key = self.fqn.partition(".")[2]

        # update each key fqn
        for key, value in updates.items():
            # get the base ltm key
            obj = self.root._state
            # enter each subkey
            subkeys, _, innerkey = key.rpartition(".")
            subkeys = f"{base_key}.{subkeys}".strip(".")
            if subkeys:
                for subkey in subkeys.split("."):
                    obj = obj[subkey]
            # save in the last subkey
            obj[innerkey] = value

    def atomic_state_append(self, key, value):
        """
        Inserts a value into a list returning the new value immediately and
        atomically.

        This should only be used where concurrent state updates might clash.

        It's different from `update_state` which is more general and collects
        all updates and executes them after `run` finishes all together in one
        call.

        `key` must be an initialized list already present in the db.
        """
        self.state[key].append(value)
        db = get_db()
        return db.atomic_append(self, key, value)


class LTMManager:
    """
    Abstracts all the LTM management logic
    """

    # queue transitions, executions and updates until run() finishes
    _transitions_queue = None
    _execute_queue = None
    _updates_queue = None

    def _init_ltms(self):
        """
        Initialize all the sub ltms
        """

        # start by initializing the current ltm state
        self._init_state()

        # gather all sub LTMs (init + transitions)
        _all_ltms = to_set(deepcopy(self.init))
        if self.transitions:
            for transtion in self.transitions:
                _all_ltms.update(to_set(transtion["from"]))
                _all_ltms.update(to_set(transtion["to"]))

        # instantiate all the LTMs
        if _all_ltms:
            self._sub_ltms = {}
        for ltm in _all_ltms:
            self._sub_ltms[ltm.name] = ltm(self)
            self._sub_ltms[ltm.name]._init_ltms()

    def _set_params(self, params):
        self.params = params

    def get_name(self):
        try:
            return self.name.format(**(self.params or {}))
        except KeyError:
            raise ValueError(f"Missing params for concurrent LTM: {self.name}")

    def get_fqn(self, structure=False):
        """
        Get the Fully Qualified Name of the LTM

        An LTM FQN is dotted syntax of a state location in the LTM hierarchy:

            "{parent_fqn}.{name}"

        For a root LTM it's just the name.

        If there are params placeholders in the name fill them with the current params.

        NOTE: This is not a Python FQN but an LTM FQN
        """
        if structure:
            name = self.name
        else:
            name = self.get_name()

        if self.parent:
            return f"{self.parent.get_fqn(structure)}.{name}"
        return self.name

    fqn = property(get_fqn)

    def perform_transition(self, label, params=None, namespace=None, payload=None):
        """
        Transition the active states via `label` transition.

        A transition can have `payload`.

        A transition can have `params` placeholders for concurrency.

        Each LTM has a default namespace (it's fqn) but a transition can have a
        specific namespace used to connect and transition between different LTMs.
        """
        if not params:
            params = [{}]
        self._init_ltms()

        # transition the active states

        # we have for cases: one -> one, one -> many, many -> one, many -> many
        # we can also have labels with params that spawn or transition concurrent states

        # we need to calculate (active_states - from_states) + to_states
        if self._sub_ltms is None:
            raise InvalidTransition(
                f"Can't transition as I don't have any sub ltms: {label}"
            )

        # get all the active active states in a set as a (class, params) tuple
        active_states = set()

        for key, value in self.state.items():
            # as we store the _sub_ltms with unformatted params (we share the
            # class between instances) we need to get the "spawned" ltms from the state
            # checking each state key with the _sub_ltm names

            # if it's a sub_ltm key (has _status) and it's active
            if isinstance(value, dict) and value.get("_status") == "active":
                # check if the key is a sub_ltm
                for name, ltm in self._sub_ltms.items():
                    result = parse.parse(name, key)
                    if result:
                        # it's a match, add to the active states the class and
                        # the formatted_name tuple
                        active_states.add((ltm.__class__, key))

        # get the states that remain active, remove the ones that transition
        remaining_states = deepcopy(active_states)
        new_states = set()

        one_transitioned = False

        for transition in self.transitions or []:

            # check if we have a matching label
            if not transition["label"] == label:
                continue

            # check if we have a matching namespace
            transition_namespace = transition.get("namespace", self.fqn)
            if transition_namespace != namespace:
                continue

            from_intersection = set()

            # get all the remaining states that are in the from set of the transition
            for ltm_class, ltm_fname in remaining_states:

                # for every params (used in forking/spawning)
                for param in params:
                    # check each ltm in the transition "from"
                    for klass in to_set(transition["from"]):
                        # format it with param
                        klass_fname = klass.name.format(**param)

                        if ltm_fname == klass_fname:
                            # add to from_intersection and the new_states
                            from_intersection.add((klass, ltm_fname))
                            for to_ltm_class in to_set(transition["to"]):
                                to_fname = to_ltm_class.name.format(**param)
                                new_states.add((to_ltm_class, to_fname))

            if not from_intersection:
                continue

            remaining_states -= from_intersection
            one_transitioned = True

        if new_states:

            # execute all the new_states
            for ltm_class, fname in new_states:

                result = parse.parse(ltm_class.name, fname)
                new_params = result.named
                ltm = self._sub_ltms[ltm_class.name]
                ltm._set_params(new_params)
                ltm._init_state(recursive=True)
                self.execute(ltm, payload)

            # move all the transitioned states to "finished"
            transitioned_states = active_states - remaining_states
            for ltm_class, fname in transitioned_states:

                result = parse.parse(ltm_class.name, fname)
                transitioned_params = result.named

                sub_ltm = self._sub_ltms[ltm_class.name]
                sub_ltm._set_params(transitioned_params)
                sub_ltm.update_state({"_status": "finished"})

        # transition every sub ltm recursively
        for key in self.state.keys():
            # check if the key is a sub_ltm
            for name, ltm in self._sub_ltms.items():
                result = parse.parse(name, key)
                if result:
                    try:
                        ltm._set_params(result.named)
                        ltm.perform_transition(label, params, namespace, payload)
                        one_transitioned = True
                    except InvalidTransition:
                        pass

        if not one_transitioned:
            raise InvalidTransition(
                f"No LTM could execute transition in their active states: {label}"
            )

    def execute(self, ltm, payload):
        """
        Queue the LTM for execution
        """
        if self.root._execute_queue is None:
            self.root._execute_queue = []
        self.root._execute_queue.append(
            ({"item_id": uuid.uuid4(), "fqn": ltm.fqn, "payload": payload})
        )
        ltm.update_state({"_status": "queued"})

    @classmethod
    def get_class_fqn(klass):
        return klass.__module__ + "." + klass.__qualname__

    def as_json(self, structure=False):
        """
        Returns the LTM structure as a nested JSON

        ```
        {
            "name": "name",
            "fqn": "name",
            "init": ["ltm1", "ltm2"],
            "ltms": [...],  #nested LTMs
            "transitions": [
                {"from": "ltm1", "to": "ltm2", "label": "transition1"},
                {"from": "ltm1", "to": "ltm2", "label": "transition2", "namespace": "global"},
            ],
        }
        ```
        """
        self._init_ltms()
        structure = {
            "name": self.name,
            "fqn": self.get_fqn(structure),
        }
        if self._sub_ltms:
            structure["ltms"] = [
                ltm.as_json(structure) for ltm in self._sub_ltms.values()
            ]

        if self.init:
            structure["init"] = [ltm.name for ltm in to_set(self.init)]

        # add all transitions
        if self.transitions:
            structure["transitions"] = []
            for transition in self.transitions:
                from_nodes = sorted(to_set(transition["from"]), key=lambda x: x.name)
                to_nodes = sorted(to_set(transition["to"]), key=lambda x: x.name)
                for node_from in from_nodes:
                    for node_to in to_nodes:
                        transition_structure = {
                            "from": node_from.name,
                            "to": node_to.name,
                            "label": transition["label"],
                        }
                        if "namespace" in transition:
                            transition_structure["namespace"] = transition["namespace"]
                            transition_structure["display_label"] = f"{transition['label']} ({transition['namespace']})"
                        else:
                            transition_structure["namespace"] = structure["fqn"]
                            transition_structure["display_label"] = transition["label"]
                        structure["transitions"].append(transition_structure)

        return structure

    def concurrent_instances_as_json(self):
        """
        Returns a dict with a list of instances for every concurrent state.

        The parent fqn is fully instanced while the last concurrent ltm isn't,
        e.g.:

        ```
        {
            "concurrent_{kwarg}: ["concurrent_1", "concurrent_2"],
            "concurrent_1.sub_concurrent_{kwarg}: ["concurrent_1.sub_concurrent_a", "concurrent_1.sub_concurrent_b"],
        }
        ```
        """
        instances = defaultdict(list)

        def combine_dicts(a, b):
            """
            Combine both dicts lists

            As we are using defaultdict(list) we can extend the lists of the first dict
            """
            for i, j in b.items():
                a[i].extend(j)

        self._init_ltms()
        if self._sub_ltms:
            for name, sub_ltm in self._sub_ltms.items():
                if "{" in name:
                    for key in self.state.keys():
                        result = parse.parse(name, key)
                        if result:
                            sub_ltm._set_params(result.named)
                            instances[f"{sub_ltm.get_fqn(structure=True)}"].append(
                                {
                                    "fqn": sub_ltm.get_fqn(),
                                    "structure_fqn": sub_ltm.get_fqn(True),
                                    "fname": sub_ltm.get_name(),
                                    "params": sub_ltm.params,
                                }
                            )
                            combine_dicts(
                                instances, sub_ltm.concurrent_instances_as_json()
                            )
                else:
                    combine_dicts(instances, sub_ltm.concurrent_instances_as_json())
        return instances

    def _set_params_from_fname(self, fname):
        result = parse.parse(self.name, fname)
        self._set_params(result.named)

    def _find_subltm_from_fname(self, fname):
        for name, ltm in self._sub_ltms.items():
            result = parse.parse(name, fname)
            if result:
                return self._sub_ltms[ltm.name]

    def _find_subltm_from_fname(self, fname):
        for name, ltm in self._sub_ltms.items():
            result = parse.parse(name, fname)
            if result:
                return self._sub_ltms[ltm.name]

    def _get_ltm(self, fqn):
        """
        Get a child LTM by its Fully Qualified Name

        In the case of concurrent states, fill the appropiate params in each LTM
        """

        self._init_ltms()

        # remove root from base key
        root, _, key = fqn.partition(".")
        self._set_params_from_fname(root)

        ltm = self
        for key in key.split("."):
            if not key:
                continue
            ltm = ltm._find_subltm_from_fname(key)
            ltm._set_params_from_fname(key)
        return ltm


class LTM(LTMManager, LTMState):
    name = None
    init = None
    transitions = None

    parent = None  # only the root ltm doesn't have parents
    _sub_ltms = None
    params = None

    created_at = None
    updated_at = None

    def __init__(
        self,
        parent=None,
        id=None,
        state=None,
        internal_state=None,
        snapshots=None,
        rollbacks=None,
        playground=None,
        source_id=None,
        created_at=None,
        updated_at=None,
        params=None,
    ):
        self.parent = parent
        self.id = id
        self.params = params
        self._state = state
        self._initial_state = deepcopy(state) or {}
        self._snapshots = snapshots
        self._rollbacks = rollbacks
        self._playground = playground
        self._source_id = source_id
        self.created_at = created_at
        self.updated_at = updated_at

    def run(self, payload=None) -> int:
        """
        The code to run when the state is executed.

        For subltms this method should run all the init ltms.

        WARNING: Don't code this method directly, use `.execute()` instead
        """
        if self.init:
            self._init_ltms()
            for ltm in self.init:
                self.execute(self._sub_ltms[ltm.name], payload)

    def transition(self, label, payload=None, params=None, namespace=None):
        """
        Transition every ltm with the given label
        """
        if not namespace:
            if self.parent:
                namespace = self.parent.fqn
            else:
                # FIXME: I don't like this becasuse it means different things in different parts
                namespace = self.fqn

        if self.root._transitions_queue is None:
            self.root._transitions_queue = []
        self.root._transitions_queue.append(
            {
                "item_id": uuid.uuid4(),
                "label": label,
                "params": params,
                "namespace": namespace,
                "payload": payload,
            }
        )

    def start(self, payload=None, playground=False):
        """
        Start the ltm
        """
        if self.parent:
            raise ValueError("Only the root ltm can be started")

        if self.id:
            raise ValueError("Only a new ltm can be started")

        self._init_ltms()
        self.id = get_executor().start(self, payload=payload, playground=playground)
        return self.id

    @property
    def root(self):
        if self.parent:
            return self.parent.root
        else:
            return self
