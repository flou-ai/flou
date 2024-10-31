<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowsIn, ArrowsOut } from 'phosphor-svelte';

	export let node: any;
	export let updateFold;
	let folded = false;

	onMount(async () => {
		folded = node.scratch('_folded');
	});

	let fold = async () => {
		folded = !folded;
		node.scratch('_folded', folded);
		updateFold(folded, node.data('id'));
	};
</script>

<div class="fold">
	<button on:click={fold}>
		{#if folded}
			<ArrowsOut />
		{:else}
			<ArrowsIn />
		{/if}
	</button>
</div>

<style lang="scss">
	.fold button {
		padding: 0;
	}
</style>