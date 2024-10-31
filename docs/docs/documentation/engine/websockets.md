# Websockets

Flou offers a websocket endpoint to keep up with your app up to date with an LTM
execution and status in real-time.

The websocket endpoint is: `ws://localhost:8000/ws/{ltm_id}` replacing
`{ltm_id}` with the id of the ltm instance you want to subscribe to.

Each websocket message returns the latest snapshot diff:

```json
{
    "id": {ltm_id},
    "snapshot": {snapshot_patch}
}
```

From the original LTM state you can apply successive snapshot patches to stay up
to date with the latest state.

## Using the websocket

To connect to the WebSocket, initiate a connection to
`ws://localhost:8000/ws/{ltm_id}`. For example, using JavaScript:

```javascript
const ltmId = 123;

// get the LTM initial state
const ltmUrl = `http://localhost:8000/api/v0/ltm/${ltmId}`;

let ltm;

let getLtm = async () => {
    await fetch(ltmUrl)
        .then((response) => {
            ltm = data.json();
        })
        .catch((error) => {
            console.log(error);
        });
};

// connect to the websocket to receive updates
const socket = new WebSocket(`ws://localhost:8000/ws/${ltmId}`);

socket.onopen = () => {
    console.log("WebSocket connection established");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data.detail);

    // append the new snapshot to the ltm data
    ltm = { ...ltm, snapshots: [...ltm.snapshots, data.snapshot] };

    let time = data.snapshot['time'];  // the server time at which the snapshot was taken
    let reason = data.snapshot['reason'];  // the reason for the snapshot
    let item = data.snapshot['item'];  // the details of the snapshot
};

socket.onclose = () => {
    console.log("WebSocket connection closed");
};
```

## Recreating the LTM state from snapshots

From a list of snapshots patches we can recreate the latest state of the LTM.
We will be using
[fast-json-patch](https://www.npmjs.com/package/fast-json-patch) to apply the
patches consecutively.

```javascript
let recreateState = () => {
    let state = {};
    for (snapshot in ltm.snapshots) {
        jsonpatch.applyPatch(state, jsonpatch.deepClone(snapshot['patch']));
    return state;
};
```
