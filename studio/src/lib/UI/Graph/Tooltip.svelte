<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowURightDown } from 'phosphor-svelte';
	import { getDottedPath } from './Utils';

	export let node: any;
	export let transform = '';
	export let updateRoot;
	export let state: any;
	export let concurrent: any;
	export let currentRootInstance: any;

	let element: HTMLDivElement;
	onMount(async () => {});

	let status: any;
	$: data = (node && node.data()) || {};
	$: {
		if (element) {
			element.style.transform = transform;
		}
	}

	let instances: any = [];
	$: {
		currentRootInstance;
		instances = [];
		if (concurrent[data.id]) {
			instances = concurrent[data.id].filter((instance: any) => {
				// check if the instance exists in the current snapshot by
				// checking if it exists in the state
				let existsInSnapshot = getDottedPath(state.state, instance.fqn);

				// Filter instances that are children of selected instances
				let isChildOfRootInstance = instance.fqn.startsWith(`${currentRootInstance}.`);
				return existsInSnapshot && isChildOfRootInstance;
			});
		}
	}
</script>

<div class="tooltip" bind:this={element}>
	{#if data?.isParent}
		<button on:click={() => updateRoot(data.id)} title="step into">
			<ArrowURightDown />
		</button>
	{/if}
	{#if data?.label?.includes('{')}
		<div>
			instances:
			{#each instances as instance}
				<div class="instance">
					{#each Object.entries(instance.params) as [param, value]}
						<span title={instance.fqn}>
							{param}: {value}
						</span>
					{/each}
					<button
						on:click={() => updateRoot(instance.structure_fqn, instance.fqn)}
						title="step into"
					>
						<ArrowURightDown />
					</button>
				</div>
			{:else}
				<div>No instances</div>
			{/each}
		</div>
	{:else}
		<div>
			status: {data.status}
		</div>
	{/if}
</div>

<style lang="scss">
	.tooltip {
		position: absolute;
		background-color: black;
		padding: 0.5rem;
		border-radius: 0.3rem;
		display: flex;
		flex-direction: column;
		max-width: 100rem;
		width: max-content;
		&,
		button {
			color: var(--white-80);
		}
	}
	.tooltip div {
		text-wrap: pretty;
	}
	.tooltip::after {
		content: ' ';
		position: absolute;
		top: 1rem;
		right: 100%; /* To the left of the tooltip */
		margin-top: -5px;
		border-width: 5px;
		border-style: solid;
		border-color: transparent black transparent transparent;
	}

	.instance {
		display: flex;
	}
</style>
