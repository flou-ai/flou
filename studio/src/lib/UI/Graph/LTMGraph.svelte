<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';
	import { browser } from '$app/environment';
	import { getNodeStatus, ltmToGraph, matchFQN, fqnToJsonPatchPath } from './Utils';

	import cytoscape from 'cytoscape';
	import dagreCompound from './Layout/layout';
	import { options as layoutOptions } from './Layout/options';
	import Layers from 'cytoscape-layers';

	import GraphStyles from '$lib/UI/Graph/GraphStyles';
	import Fold from './Fold.svelte';
	import Tooltip from './Tooltip.svelte';
	import Breadcrumbs from './Breadcrumbs.svelte';

	// attributes
	export let ltm;
	export let state: any;
	export let concurrent: any;
	export let currentSnapshot: any;
	export let cy: cytoscape.Core;

	// graphs container
	let containerElement: HTMLDivElement;
	let parentElement: HTMLDivElement;

	// Interactivity
	let currentRoot: string = '';
	let currentRootInstance: string = '';
	let hiddenElements: any;
	let foldedLTMs: string[] = [];
	let currentSelection: cytoscape.NodeSingular | null = null;
	let tooltip: Tooltip;

	// Animations
	let animationFrame: number;
	let lastAnimationTime = performance.now();
	let dashOffset = 0;
	const dashSpeed = 20; // Speed of dash movement in pixels per second

	const updateContainerDimensions = async () => {
		if (!parentElement) return;
		if (cy) {
			// the ugliest of hacks so the graph "shrinks" when the viewport
			// shrinks. Haven't found any nicer workaround.
			parentElement.style.display = 'none';
			cy.resize();
			parentElement.style.display = 'block';
			cy.resize();
			fitCy();
		}
	};

	const fitCy = async () => {
		if (cy) {
			cy.minZoom(1e-50);
			cy.fit();
			cy.minZoom(cy.zoom());
		}
	};

	onMount(async () => {
		window.addEventListener('resize', updateContainerDimensions);

		currentRoot = ltm.name;
		currentRootInstance = ltm.name;
		cytoscape.use(Layers);
		cytoscape.use(dagreCompound);

		cy = cytoscape({
			container: containerElement,
			// @ts-ignore
			style: GraphStyles,
			layout: layoutOptions,
			minZoom: 1e-50,
			maxZoom: 0.8,
			boxSelectionEnabled: false
			// autolock: true,
		});

		hiddenElements = cy.collection();

		// enter on double click
		cy.on('dblclick', 'node', function (e) {
			var node = e.target;
			if (node._private.children.length > 0) {
				updateRoot(node.data('id'));
			}
		});
		// @ts-ignore
		const layers = cy.layers();

		const tooltipLayer = layers.append('html', {
			stopClicks: true
		});
		// tooltipLayer.node.append(tooltipElement);
		tooltip = new Tooltip({
			target: tooltipLayer.node,
			props: {
				...{ state, concurrent, updateRoot, currentRootInstance },
				node: currentSelection,
				transform: ''
			}
		});
		tooltipLayer.node.style.opacity = '0';

		cy.on('select', 'node', (e) => {
			const node = e.target as cytoscape.NodeSingular;
			if (currentSelection) {
				currentSelection.off('position', undefined, updateTooltip);
			}
			currentSelection = node;
			updateTooltip(e);
			currentSelection.on('position', updateTooltip);
			tooltipLayer.node.style.opacity = '1';
		});
		cy.on('unselect', () => {
			if (currentSelection) {
				currentSelection.off('position', undefined, updateTooltip);
			}
			currentSelection = null;
			tooltipLayer.node.style.opacity = '0';
		});

		const layer = layers.append('html', { id: 'iddd' });
		// Add fold/unfold button
		layers.renderPerNode(layer, (elem: HTMLElement, node: any, bb: any) => {
			const padding = 10;
			// this is needed because when removing elements the fold changes node (sometimes)
			elem.replaceChildren();
			if (elem.children.length === 0 && node.data('isParent')) {
				let fold = new Fold({
					target: elem,
					props: {
						node: node,
						// @ts-ignore
						updateFold: (folded: boolean, id: string) => {
							if (folded) {
								foldedLTMs = [...foldedLTMs, id];
							} else {
								foldedLTMs = foldedLTMs.filter((e) => e !== id);
							}
							updateGraph();
						}
					}
				});
				elem.style.translate = `${bb.w - elem.offsetWidth - padding}px ${padding}px`;
			}
		});

		// Restrict panning to keep objects visible (pan range is defined by bounding box)
		cy.on('pan', () => {
			const boundingBox = cy.elements().renderedBoundingBox();
			// @ts-ignore
			const extents = cy.renderedExtent();
			let pan = cy.pan();

			let xMin, xMax, yMin, yMax;
			if (extents.h > boundingBox.h) {
				yMin = 0;
				yMax = extents.h - boundingBox.h;
			} else {
				yMin = extents.h - boundingBox.h;
				yMax = 0;
			}
			if (extents.w > boundingBox.w) {
				xMin = 0;
				xMax = extents.w - boundingBox.w;
			} else {
				xMin = extents.w - boundingBox.w;
				xMax = 0;
			}

			// Adjust pan values based on the boundaries
			if (pan.x < xMin) pan.x = xMin; // Don't allow panning too far left
			if (pan.x > xMax) pan.x = xMax; // Don't allow panning too far right
			if (pan.y < yMin) pan.y = yMin; // Don't allow panning too far up
			if (pan.y > yMax) pan.y = yMax; // Don't allow panning too far down
		});

		cy.add(ltmToGraph(ltm));
		updateGraph();

		// Start animations
		animateCurrentExecutions();
	});

	onDestroy(() => {
		if (browser) {
			window.removeEventListener('resize', updateContainerDimensions);
		}
		cancelAnimationFrame(animationFrame);
	});

	// Interactivity

	let updateGraph = async () => {
		if (!cy) return;

		let _isHiddenElement = (ele: any) => {
			let id;
			if (ele.isNode()) {
				id = ele.data('id');
			} else {
				id = ele.data('source');
			}
			// is element folded
			let isFolded = foldedLTMs.some((prefix) => id.startsWith(`${prefix}.`));

			// is element visible
			let insideRoot = id.startsWith(`${currentRoot}.`);

			return isFolded || !insideRoot;
		};

		// When removing a node it removes all children so we need to clear the
		// `parent` of the current Root elements so they don't get removed
		cy.nodes().forEach((node) => {
			if (node.data('parent') === currentRoot) {
				// Save the parent in the _parent data
				node.data('_parent', currentRoot);
				node.move({ parent: null });
			}
		});

		// remove elements in foldedLTMs
		let toRemove = cy.elements().filter(_isHiddenElement);
		hiddenElements = hiddenElements.union(toRemove);
		cy.remove(toRemove);

		// add elements no longer in foldedLTMs
		let elementsToRestore = cy.collection();
		hiddenElements = hiddenElements.filter((ele: any) => {
			let isHidden = _isHiddenElement(ele);
			if (!isHidden) {
				elementsToRestore = elementsToRestore.add(ele);
			}
			return isHidden;
		});
		elementsToRestore.sort((a, b) => b.data('id').length - a.data('id').length);
		elementsToRestore.restore();

		// update all nodes
		cy.nodes().forEach((node) => {
			// fix parent
			if (node.data('_parent')) {
				node.move({ parent: node.data('_parent') });
				node.data('_parent', undefined);
			}
			node.data('status', getNodeStatus(state.state, ltm, node.data().id, currentRootInstance));

			// check if we are executing the node
			let executing = false;
			if (state.reason === 'execute') {
				const pattern = node.data('id');
				const target = state.item.fqn;
				const fqnMatch = matchFQN(pattern, target);

				executing = fqnMatch.isMatch;
			}
			node.data('executing', executing);
		});

		// update all edges
		cy.edges().forEach((edge) => {
			// check if we are executing the edge
			let executing = false;
			if (state.reason === 'transition') {
				const pattern = edge.data('namespace');
				const target = state.item.namespace;
				const namespaceMatch = matchFQN(pattern, target);

				// for multiple edges with the same label/namespace we need to
				// calculate from which node it was executed:
				// check the patch to see which source node changed from active
				// to finished
				currentSnapshot.patch.some((patch: any) => {
					const path = `${fqnToJsonPatchPath(edge.source().data().id)}_status`;
					if (patch.op === 'replace' && patch.path === path && patch.value === 'finished') {
						executing = edge.data('label') === state.item.label && namespaceMatch.isMatch;
					}
				});
				console.log('executing', executing);
			}
			edge.data('executing', executing);
		});

		cy.layout(layoutOptions).run();
		await tick(); // ugly hack to await rendering to get label width and height for layout
		cy.layout(layoutOptions).run();
		fitCy();
	};

	// Tooltip
	let updateTooltip = (e: { target: any }) => {
		if (!currentSelection) return;

		const bb = currentSelection.boundingBox({ includeOverlays: false });

		tooltip.$set({
			transform: `translate3d(${bb.x2 + 5}px, ${bb.y1}px, 0px)`,
			node: currentSelection
		});
	};
	$: {
		if (tooltip) {
			tooltip.$set({ state });
		}
	}

	// Root
	let updateRoot = (rootFQN: string, instanceFQN: string | null = null) => {
		cy.trigger('unselect'); // We need this to hide the tooltip as the node
		// is removed and `unselect` is not being called

		currentRoot = rootFQN;
		currentRootInstance = instanceFQN || rootFQN;
		tooltip.$set({ currentRootInstance });
	};
	$: {
		currentRoot;
		updateGraph();
	}

	// Change of state
	$: state, updateGraph();

	// Animations

	let animateCurrentExecutions = () => {
		if (!cy) return;
		const currentTime = performance.now();
		const elapsedTime = (currentTime - lastAnimationTime) / 1000; // Convert ms to seconds
		lastAnimationTime = currentTime;

		dashOffset -= dashSpeed * elapsedTime;

		cy.edges('[?executing]').style({
			'line-dash-offset': dashOffset
		});
		cy.nodes('[?executing]').style({
			'border-dash-offset': dashOffset
		});
		animationFrame = requestAnimationFrame(animateCurrentExecutions); // Continue animating
	};
</script>

<Breadcrumbs {currentRoot} {currentRootInstance} {updateRoot} />

<div id="parent" bind:this={parentElement}>
	<div id="graph-container" bind:this={containerElement}></div>
</div>

<style lang="scss">
	#parent {
		width: 100% !important;
	}
	#parent {
		flex-grow: 1;
		position: relative;
		overflow: hidden;
	}
	#graph-container {
		width: 100%;
		height: 100%;
		min-width: 100%;
		min-height: 60vh;
	}
</style>
