# Using the REST API & CLI

You have two choices to interact with Flou's Engine, a REST API and the CLI.
They have the same capabilities but are suited for different use cases.

## REST API reference documentation

You can visit <http://localhost:8000/docs> and check out the complete REST API
reference documentation.

## Command Line Interface help

By calling `flou --help` from your terminal you can see all the cli commands.

## Listing registered LTMs

To create a LTM you will need to know it's FQN (Fully Qualified Name) of the
Python class. You can get it by listing all your registered LTMs:

=== "REST API"

    ``` bash
    curl -X 'GET' \
        'http://localhost:8000/api/v0/ltm/registry' \
        -H 'accept: application/json'
    ```

    ```json title="Sample output"
    [
        {
            "fqn": "flou.app.SampleLTM",
            "name": "sample_ltm"
        }
    ]
    ```

=== "CLI"

    ``` bash
    flou registry
    ```

    ```json title="Sample output"
    ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
    ┃ name       ┃ fqn                ┃
    ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
    │ sample_ltm │ flou.app.SampleLTM │
    └────────────┴────────────────────┘
    ```

## Creating an LTM instance

You can then create a new instance with the `FQN` and possible `payload`:

=== "REST API"

    ``` bash
    curl -X 'POST' \
        'http://localhost:8000/api/v0/ltm' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "fqn": "flou.app.SampleLTM",
            "payload": {}
        }'
    ```

    ```bash title="Sample output"
    {
        "id": 1
    }
    ```

=== "CLI"

    ``` bash
    flou create flou.app.SampleLTM
    ```

    ```bash title="Sample output"
    Created LTM root, id: 1, kwargs: {}
    ```

Creating an LTM returns a unique id across all Networks of Agents.

## Listing all LTMs

You can list all the LTM's instances by:

=== "REST API"

    ``` bash
    curl -X 'GET' \
        'http://localhost:8000/api/v0/ltm' \
        -H 'accept: application/json'
    ```

    ```json title="Sample output"
    [
        {
            "id": 1,
            "name": "sample_ltm",
            "fqn": "flou.app.SampleLTM",
            "snapshots_count": 1,
            "created_at": "2024-09-01 21:32:43",
            "updated_at": "2024-09-01 21:32:43"
        }
    ]
    ```

=== "CLI"

    ``` bash
    flou get 1
    ```

    ```bash title="Sample output"
    ┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
    ┃ id  ┃ name       ┃ fqn                ┃ #snapshots ┃ created_at          ┃ updated_at          ┃
    ┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
    │ 1   │ sample_ltm │ flou.app.SampleLTM │ 1          │ 2024-09-01 21:32:43 │ 2024-09-01 21:32:43 │
    └─────┴────────────┴────────────────────┴────────────┴─────────────────────┴─────────────────────┘

    ```

## Retrieving an instance

You will need the instance ID and call:

=== "REST API"

    ``` bash
    curl -X 'GET' \
        'http://localhost:8000/api/v0/ltm/1' \
        -H 'accept: application/json'
    ```

    ```json title="Sample output"
    {
        "name": "sample_ltm",
        "state": {
            "_status": "active",
            ...
        },
        "snapshots": [
            {
            "time": "2024-09-01 18:32:43.473991",
            "reason": "start",
            "item": {...},
            "patch": [...],
            "execute_queue": [...],
            "transitions_queue": [...]
            },
            ...
        ],
        "fqn": "tests.concurrency.test_concurrent_arg.ConcurrentLTM",
        "params": null,
        "structure": {
            ...
        },
        "concurrent_instances": {...},
        "created_at": "2024-09-01 21:32:43",
        "updated_at": "2024-09-01 21:32:43"
    }
    ```

=== "CLI"

    ``` bash
    flou get 1
    ```

    ```bash title="Sample output"
    ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
    ┃ name       ┃ fqn                ┃ state   ┃ params ┃ structur┃ concurrent_instances ┃ created_at          ┃ uploaded_at         ┃
    ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
    │ sample_ltm │ flou.app.SampleLTM │ {       │ None   │ {       │ {                    │ 2024-09-01 21:32:43 │ 2024-09-01 21:32:43 │
    │            │                    │     ... │        │     ... │     ...              │                     │                     │
    └────────────┴────────────────────┴─────────┴────────┴─────────┴──────────────────────┴─────────────────────┴─────────────────────┘
    ```

## Performing a transition

To perform a transition you need to know the transition `label`, it's
`namespace`, your desired `params` and `payload`.

=== "REST API"

    ``` bash
    curl -X 'POST' \
        'http://localhost:8000/api/v0/ltm/1/transition' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "transition": "sample_transition",
            "namespace": "sample_ltm",
            "params": [],
            "payload": {}
        }'
    ```

    ```json title="Sample output"
    true
    ```

=== "CLI"

    ``` bash
    flou transition 1 sample_transition
    ```

    ```bash title="Sample output"
    Launched transition sample_ltm for LTM sample_ltm, id: 1 with payload: None
    ```

If you want a blocking call until another transition is performed un can use the
`wait_until_transition` parameter that blocks the return until the transition
you requested is performed. This way you can mimic a regular LLM call from your
app and swap it to a Network of Agents without changing much of your app's code.
Use the `namespace:label` format.

=== "REST API"

    ``` bash
    curl -X 'POST' \
        'http://localhost:8000/api/v0/ltm/1/transition' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
            "transition": "sample_transition",
            "namespace": "sample_ltm",
            "params": [],
            "payload": {},
            "wait_until_transition": "namespace:another_transition",
        }'
    ```

    ```json title="Sample output"
    true
    ```