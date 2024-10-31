const isFunction = function (o: any) { return typeof o === 'function'; };
import dagre from '@dagrejs/dagre';
import { defaults } from './defaults';

let assign = Object.assign != null ? Object.assign.bind(Object) : function (tgt: any, ...srcs: any) {
    srcs.forEach((src: any) => {
        Object.keys(src).forEach(k => tgt[k] = src[k]);
    });
};

// constructor
// options : object containing layout options
function DagreLayout(this: any, options: any) {
    this.options = assign({}, defaults, options);
}

// runs the layout
DagreLayout.prototype.run = function () {
    let options = this.options;
    let layout = this;

    let cy = options.cy; // cy is automatically populated for us in the constructor
    let eles = options.eles;

    // Function to build a tree structure of compound nodes
    let buildTree = (elements: any) => {
        // each tree element consistes of:
        // id: {
        //     children: { // optional (if parent)
        //         nodes: {},
        //         edges: {},
        //     },  // recursive structure
        //     element: node,
        // }
        let tree: any = {
            nodes: {},
            edges: {},
        };

        let _buildTree = (nodes: any) => {
            if (nodes.length === 0)
                return

            let _tree: any = {
                nodes: {},
                nodesCollection: {},
                edges: {},
            };

            nodes.forEach((node: any) => {
                const children = node.children();
                let data: any = {
                    element: node
                }
                if (children.length > 0) {
                    data = { ...data, children: _buildTree(children) }
                }
                _tree.nodes[node.id()] = data;
            });
            _tree.nodesCollection = nodes;
            _tree.edges = nodes.connectedEdges();
            return _tree;
        }

        const orphans = elements.filter(':orphans');
        orphans.forEach((node: any) => {
            let data: any = {
                element: node
            }
            const childrenTree = _buildTree(node.children());
            if (childrenTree) {
                data = {
                    ...data,
                    children: childrenTree
                }
            }
            tree.nodes[node.id()] = data;
        });
        tree.nodesCollection = orphans;
        tree.edges = orphans.connectedEdges();
        return tree;
    };
    let compoundTree = buildTree(eles);

    let dfsNodes: any = [];

    // Depth first search to process all groups of compound nodes in correct
    // order (leaf groups first and up)
    let dfs = (tree: any, f: Function) => {
        if (Object.keys(tree.nodes)) {
            Object.values(tree.nodes).forEach((node: any) => {
                if (node.children)
                    dfs(node.children, f)
            });
            f(tree);
        }
    };

    // Layout starts now with helper functions

    // HELPER FUNCTIONS

    let getVal = function (ele: any, val: any) {
        return isFunction(val) ? val.apply(ele, [ele]) : val;
    };

    let bb = options.boundingBox || { x1: 0, y1: 0, w: cy.width(), h: cy.height() };
    if (bb.x2 === undefined) { bb.x2 = bb.x1 + bb.w; }
    if (bb.w === undefined) { bb.w = bb.x2 - bb.x1; }
    if (bb.y2 === undefined) { bb.y2 = bb.y1 + bb.h; }
    if (bb.h === undefined) { bb.h = bb.y2 - bb.y1; }

    let setGObj = function (gObj: any, name: any, val: any) {
        if (val != null) {
            gObj[name] = val;
        }
    };

    let partialLayout = (elements: any) => {

        if (!elements || !elements.nodesCollection || elements.nodesCollection.length === 0) {
            return
        }
        // create new graph
        let g = new dagre.graphlib.Graph({
            multigraph: true,
            compound: false  // we are emulating parents
        });

        let gObj = {};

        setGObj(gObj, 'nodesep', options.nodeSep);
        setGObj(gObj, 'edgesep', options.edgeSep);
        setGObj(gObj, 'ranksep', options.rankSep);
        setGObj(gObj, 'rankdir', options.rankDir);
        setGObj(gObj, 'align', options.align);
        setGObj(gObj, 'ranker', options.ranker);
        setGObj(gObj, 'acyclicer', options.acyclicer);

        g.setGraph(gObj);

        g.setDefaultEdgeLabel(function () { return {}; });
        g.setDefaultNodeLabel(function () { return {}; });

        // add nodes to dagre
        let nodes = elements.nodesCollection;

        if (isFunction(options.sort)) {
            nodes = nodes.sort(options.sort);
        }

        for (let i = 0; i < nodes.length; i++) {

            let node: any = nodes[i];
            let nbb = node.layoutDimensions(options);

            g.setNode(node.id(), {
                width: nbb.w,
                height: nbb.h,
                name: node.id()
            });

            // add original position to scratch();
            node.scratch('originalPosition', node.position());
        }

        // add edges to dagre
        let edges = elements.edges;

        if (isFunction(options.sort)) {
            edges = edges.sort(options.sort);
        }

        for (let i = 0; i < edges.length; i++) {
            let edge = edges[i];

            options = {
                minlen: getVal(edge, options.minLen),
                weight: getVal(edge, options.edgeWeight),
                name: edge.id(),
                label: edge.data().label,
            }
            // ugly hack: on first go it's undefined, you need to call layout again
            if (edge._private.labelBounds.all) {
                options['width'] = edge._private.labelBounds.all.w;
                options['height'] = edge._private.labelBounds.all.h;
            }
            g.setEdge(edge.source().id(), edge.target().id(), options, edge.id());
        }

        // execute layout

        dagre.layout(g);

        // assign dagre nodes to cy nodes' scratch
        let gNodeIds = g.nodes();
        for (let i = 0; i < gNodeIds.length; i++) {
            let id = gNodeIds[i];
            let n = g.node(id);

            cy.getElementById(id).scratch().dagre = n;
        }

        // assign dagre edges to cy edges' scratch
        let gEdgeIds = g.edges();
        for (let i = 0; i < gEdgeIds.length; i++) {
            let id = gEdgeIds[i];
            let n = g.edge(id);

            cy.getElementById(id.name).scratch('dagre', n);
        }

        // calculate bound box
        let dagreBB: any;

        if (options.boundingBox) {
            dagreBB = { x1: Infinity, x2: -Infinity, y1: Infinity, y2: -Infinity };
            nodes.forEach(function (node: any) {
                let dModel = node.scratch().dagre;

                dagreBB.x1 = Math.min(dagreBB.x1, dModel.x);
                dagreBB.x2 = Math.max(dagreBB.x2, dModel.x);

                dagreBB.y1 = Math.min(dagreBB.y1, dModel.y);
                dagreBB.y2 = Math.max(dagreBB.y2, dModel.y);
            });

            dagreBB.w = dagreBB.x2 - dagreBB.x1;
            dagreBB.h = dagreBB.y2 - dagreBB.y1;
        } else {
            dagreBB = bb;
        }

        // constraint positions to options.BoundingBox
        let constrainPos = function (p: any) {
            if (options.boundingBox) {
                let xPct = dagreBB.w === 0 ? 0 : (p.x - dagreBB.x1) / dagreBB.w;
                let yPct = dagreBB.h === 0 ? 0 : (p.y - dagreBB.y1) / dagreBB.h;

                return {
                    x: bb.x1 + xPct * bb.w,
                    y: bb.y1 + yPct * bb.h
                };
            } else {
                return p;
            }
        };

        // Assign the new positions to all leaf nodes
        elements.nodesCollection.layoutPositions(layout, options, function (this: any, ele: any) {
            ele = typeof ele === "object" ? ele : this;
            let dModel = ele.scratch().dagre;

            const newPos = { x: dModel.x, y: dModel.y };
            ele.scratch('originalPosition', newPos);
            return constrainPos(newPos);
        });
        // Assign new positions to all the descendant nodes
        elements.nodesCollection.filter(':parent').forEach((parent: any) => {
            let dModel = parent.scratch().dagre;

            let diff = {
                x: dModel.x - parent.scratch('originalPosition').x,
                y: dModel.y - parent.scratch('originalPosition').y
            }
            parent.scratch('originalPosition', { x: dModel.x, y: dModel.y });

            parent.descendants().layoutPositions(layout, options, function (this: any, ele: any) {
                ele = typeof ele === "object" ? ele : this;
                const newPos = {
                    x: ele.scratch('originalPosition').x + diff.x,
                    y: ele.scratch('originalPosition').y + diff.y
                }
                ele.scratch('originalPosition', newPos);
                return constrainPos(newPos);
            });
        });
        // Assign edges bundled points
        elements.edges.not(':loop').forEach((ele: any) => {
            let dModel = ele.scratch('dagre');
            let allPoints = dModel.points;

            let sourcePoint = allPoints[0];
            let targetPoint = allPoints.at(-1);
            let points = allPoints.slice(1, -1);

            const deltaX = targetPoint.x - sourcePoint.x;
            const deltaY = targetPoint.y - sourcePoint.y;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            const sourceNodePosition = ele.source().scratch('originalPosition');
            const targetNodePosition = ele.target().scratch('originalPosition');
            const normalizedSourcePoint = {
                x: sourcePoint.x - sourceNodePosition.x,
                y: sourcePoint.y - sourceNodePosition.y,
            };
            const normalizedTargetPoint = {
                x: targetPoint.x - targetNodePosition.x,
                y: targetPoint.y - targetNodePosition.y,
            };

            let normalizedWeights = [];
            let perpendicularDistances = [];
            for (let i = 0; i < points.length; i++) {
                let controlPoint = points[i];

                let normalizedWeight;
                let perpendicularDistance;
                if (deltaX === 0) {
                    if (deltaY === 0) {
                        normalizedWeight = 0;
                    } else {
                        normalizedWeight = ((controlPoint.y - sourcePoint.y) / deltaY); // between 0 and 1
                    }
                    perpendicularDistance = controlPoint.x - sourcePoint.x;
                } else {
                    // Compute the length of the segment
                    const segmentLengthSquared = deltaX * deltaX + deltaY * deltaY;

                    // Project controlPoint onto the line segment (sourcePoint -> targetPoint)
                    const t = ((controlPoint.x - sourcePoint.x) * deltaX + (controlPoint.y - sourcePoint.y) * deltaY) / segmentLengthSquared;

                    // Clamp t between 0 and 1 to find the nearest point on the segment
                    const clampedT = Math.max(0, Math.min(1, t));

                    // Find the coordinates of the nearest point on the segment
                    const nearestX = sourcePoint.x + clampedT * deltaX;
                    const nearestY = sourcePoint.y + clampedT * deltaY;

                    // Compute the perpendicular distance from controlPoint to the nearest point
                    const distanceX = controlPoint.x - nearestX;
                    const distanceY = controlPoint.y - nearestY;
                    perpendicularDistance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);

                    // Determine the direction (positive/negative) based on the cross product
                    const crossProduct = (deltaX * (controlPoint.y - sourcePoint.y)) - (deltaY * (controlPoint.x - sourcePoint.x));
                    perpendicularDistance = crossProduct >= 0 ? perpendicularDistance : -perpendicularDistance;

                    normalizedWeight = clampedT;

                }
                normalizedWeights.push(normalizedWeight);
                perpendicularDistances.push(perpendicularDistance * 2);
            }
            ele.style({
                'curve-style': 'unbundled-bezier',
                'control-point-weights': normalizedWeights,
                'control-point-distances': perpendicularDistances,
                'edge-distances': 'endpoint',
                'source-endpoint': `${normalizedSourcePoint.x} ${normalizedSourcePoint.y}`,
                'target-endpoint': `${normalizedTargetPoint.x} ${normalizedTargetPoint.y}`,
            })
        });
    }

    dfs(compoundTree, partialLayout);

    return this; // chaining
};

// registers the extension on a cytoscape lib ref
let register = function (cytoscape: any) {
    if (!cytoscape) { return; } // can't register if cytoscape unspecified

    cytoscape('layout', 'dagreCompound', DagreLayout); // register with cytoscape.js
};

export default register;