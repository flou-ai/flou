<script lang="ts">
	import { CaretRight } from 'phosphor-svelte';

	export let currentRoot: string;
	export let currentRootInstance: string;
	export let updateRoot;

	let nestedLtms: any;
	$: {
		let currentPath = '';
		let currentInstancePath = '';
		nestedLtms = [];
		// do both currentRoot & currentRootInstance
		let instanceKeys = currentRootInstance.split('.')
		currentRoot.split('.').forEach((sub, i) => {
			if (sub === '') return;
			if (currentPath) {
				currentPath = `${currentPath}.${sub}`;
				currentInstancePath = `${currentInstancePath}.${instanceKeys[i]}`;
			}
			else {
				currentPath = sub;
				currentInstancePath = instanceKeys[i];
			}
			nestedLtms.push({ path: currentPath, instancePath: currentInstancePath, name: sub, instanceName:  instanceKeys[i]});
		});
	}
</script>

<div id="breadcrumbs">
	{#each nestedLtms as ltm, i}
		{#if i > 0}
			<CaretRight size="1.25rem" />
		{/if}
		<button on:click={() => updateRoot(ltm.path, ltm.instancePath)} class:selected={i == nestedLtms.length - 1}
			>{ltm.instanceName}</button
		>
	{/each}
</div>

<style lang="scss">
	#breadcrumbs {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
</style>