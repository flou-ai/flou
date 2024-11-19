<script lang="ts">
	import { onMount } from 'svelte';
	import SnapshotItem from './SnapshotItem.svelte';
	export let step = 0;
	export let indexes: any = [];
	export let snapshots: any = [];

	// const zipLongest = (placeholder: any = undefined, ...arrays: any) => {
	//  const length = Math.max(...arrays.map((arr: any) => arr.length));
	//  return Array.from({ length }, (value, index) =>
	//      arrays.map((array: any) => (array.length - 1 >= index ? array[index] : placeholder))
	//  );
	// };
	// $: zippedSnapshots = zipLongest(undefined, [ltm.snapshots, ...ltm.rollbacks.map((r: any) => r.snapshots)]);
	let groups: any = {};
	let ended: any = [];

	onMount(async () => {
		ended = [];
		indexes.forEach((i: number) => {
			if (step < snapshots[i].length) {
				if (!(snapshots[i][step].item.item_id in groups)) {
					groups[snapshots[i][step].item.item_id] = [];
				}
				groups[snapshots[i][step].item.item_id].push(i);
			} else if (step === snapshots[i].length) {
				console.log('im inside');
				ended.push(i);
			}
		});
		console.log(ended, groups);
	});
</script>

{#if Object.keys(groups).length > 0}
	{#if Object.keys(groups).length < 2}
		{#each Object.entries(groups) as [id, groupIndexes]}
			<li>
				reason: {snapshots[groupIndexes[0]][step].reason}
				<SnapshotItem item={snapshots[groupIndexes[0]][step]?.item} />
				{#if ended.length > 0}
					ended: {JSON.stringify(ended)}
				{/if}
			</li>
			<svelte:self step={step + 1} indexes={groupIndexes} {snapshots} />
		{/each}
	{:else}
		{#if ended.length > 0}
			ended: {JSON.stringify(ended)}
		{/if}
		<li>
			{#each Object.entries(groups) as [id, groupIndexes]}
				<details>
				<summary>
                    indexes: {JSON.stringify(groupIndexes)}
                </summary>
					<ul>
						<li>
							reason: {snapshots[groupIndexes[0]][step].reason}
							<SnapshotItem item={snapshots[groupIndexes[0]][step].item} />
						</li>
						<svelte:self step={step + 1} indexes={groupIndexes} {snapshots} />
					</ul>
				</details>
			{/each}
		</li>
	{/if}
{:else if ended.length > 0}
	<li>
		ended: {JSON.stringify(ended)}
	</li>
{/if}

<style lang="scss">
	* {
		font-size: 0.75rem;
		line-height: 1.125rem;
	}
	li {
		position: relative;
		list-style: none;
		padding-left: 20px;

		&::before {
			content: '';
			position: absolute;
			left: 0;
			top: 0.7em;
			height: 1px;
			width: 10px;
			background: #666;
		}

		&::after {
			content: '';
			position: absolute;
			left: 0;
			top: 0;
			bottom: 0;
			width: 1px;
			background: #666;
		}

		&:first-child::after {
			top: 0.7em;
		}

		&:last-child::after {
			height: 0.7em;
		}
	}

	details {
		position: relative;
		padding-left: 0;

		&::before {
			content: '';
			position: absolute;
			left: -20px;
			top: 0;
			bottom: 0;
			width: 1px;
			background: #666;
		}
		&:last-child::before {
			content: '';
			position: absolute;
			left: -20px;
			top: 0;
			height: 0.7em;
			width: 1px;
			background: #666;
		}

		&:not(:first-child)::after {
			content: '';
			position: absolute;
			left: 0;
			top: 0.7em;
			height: 1px;
			width: 10px;
			background: #666;
		}
		&:not(:first-child)::after {
			left: -20px;
		}
	}
    ul {
        padding-left: 0;
    }
</style>
