<script lang="ts">
	export let item: any = {};

	import { JsonView } from '@zerodevx/svelte-json-view';
</script>

{#if item}
{#each Object.keys(item) as key}
	{#if item[key] !== null && key != 'item_id'}
		<span class="item">
			{key}:
			{#if typeof item[key] === 'object'}
				<JsonView json={item[key]} depth={-1} />
			{:else}
				{item[key]}
			{/if}
		</span>
	{/if}
{/each}
{/if}

<style lang="scss">
	span {
		font-size: inherit;
		display: block;
		text-wrap: nowrap;
		max-width: 600px;
		text-overflow: ellipsis;
		overflow: hidden;
	}
	.item :global(*) {
		font-size: inherit;
	}
</style>
