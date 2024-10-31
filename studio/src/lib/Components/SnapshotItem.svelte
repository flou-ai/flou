<script lang="ts">
	export let item: any = {};
</script>

{#if item}
{#each Object.keys(item) as key}
	{#if item[key] !== null && key != 'item_id'}
		<span>
			{key}:
			{#if typeof item[key] === 'object'}
				{JSON.stringify(item[key], null, 2)}
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
	}
</style>
