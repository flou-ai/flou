export let options = {
    name: 'dagreCompound',
    acyclicer: 'greedy',
    nodeSep: 100,
    ranker: 'network-simplex',
    nodeDimensionsIncludeLabels: true,
    sort: (a: any, b: any) => {
        if (a.data('init')) return -1;
        return 1;
    },
};