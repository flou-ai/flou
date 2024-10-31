export default [
    {
        selector: '*',
        style: {
            'font-family': 'Inter',
        }
    },
    {
        selector: 'node',
        style: {
            label: 'data(id)',
            'shape': 'roundrectangle',
            'text-valign': 'center',
            'text-halign': 'center',
            'padding': '20px',
            'width': 'label',
            'height': 'label',
            'border-width': 1,
            'outline-width': '4px',
            'outline-opacity': '00.01',
        }
    },
    {
        selector: 'node.start',
        style: {
            'border-width': 4,
            'border-style': 'double',
        }
    },
    {
        selector: 'node[label]',
        style: {
            label: 'data(label)',
        }
    },
    {
        selector: "node[status='init']",
        style: {
            'background-color': '#EBEBEB',
        }
    },
    {
        selector: "node[status='queued']",
        style: {
            'background-color': '#FFFF80',
        }
    },
    {
        selector: "node[status='active']",
        style: {
            'background-color': '#80FF80',
        }
    },
    {
        selector: "node[status='finished']",
        style: {
            'background-color': '#858585',
        }
    },
    {
        selector: "node:selected",
        style: {
            'outline-opacity': '1',
        }
    },
    {
        selector: 'node:parent',
        style: {
            'padding': '40px',
            'text-valign': 'top',
            'text-margin-y': '30px', // Adjust to position label at the top
        }
    },
    {
        selector: 'node[?executing]',
        style: {
            'border-color': 'black',
            'border-style': 'dashed',
            'border-dash-pattern': [6, 6],
            'border-dash-offset': 0,
        }
    },
    {
        selector: 'edge',
        style: {
            width: 3,
            'target-arrow-shape': 'triangle',
            'curve-style': 'unbundled-bezier',
            label: 'data(displayLabel)',
            'text-background-color': '#fff',
            'text-background-opacity': .5,
            'text-background-shape': 'roundrectangle',
            'text-background-padding': '5px',
        }
    },
    {
        selector: 'edge:loop',
        style: {
            'loop-direction': '135deg', // Adjusts the direction of the loop
            'loop-sweep': '90deg', // Adjusts the sweep (size) of the loop
            'control-point-step-size': 100, // Increases the distance of the loop from the node
        }
    },
    {
        selector: 'edge[?executing]',
        style: {
            'line-style': 'dashed',
            'line-dash-pattern': [6, 6],
            'line-dash-offset': 0,
        }
    },
]