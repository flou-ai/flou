<script lang="ts">
	import SnapshotItem from '$lib/Components/SnapshotItem.svelte';
	import Paginator from '$lib/UI/Paginator.svelte';

	export let ltm: any;
	export let snapshotIndex: any;

	let currentSnapshot: any = {};
	$: {
		if (ltm.snapshots) {
			currentSnapshot = ltm.snapshots[snapshotIndex];
		}
	}
</script>

<div class="controls flex">
	{#if ltm.snapshots.length}
	<div class="snapshot flex">
		<div>
			Snapshot: {snapshotIndex + 1} / {ltm.snapshots.length}
		</div>
		<div>
			Reason: {currentSnapshot?.reason}
		</div>
		<SnapshotItem item={currentSnapshot?.item} />
	</div>
	<Paginator bind:index={snapshotIndex} collection={ltm.snapshots} />
	{/if}
</div>

<style lang="scss">
	.flex {
		display: flex;
		gap: 1rem;
	}
	.controls {
		flex-direction: column;
		margin-bottom: 1rem;
	}
	.snapshot {
		flex-wrap: wrap;
		align-items: center;
	}
</style>
