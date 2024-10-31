<script lang="ts">
	import { setContext } from 'svelte';
	import { writable } from 'svelte/store';

	export let activeTabValue = null;
	const items: any = writable([]);

	const activeTabValueStore = writable(activeTabValue);

	setContext('items', items);
	setContext('activeTabValue', activeTabValueStore);

	$: activeTabValue = $activeTabValueStore;
</script>

<ul>
	{#each $items as item}
		<li class:active={$activeTabValueStore === item.value}>
			<button on:click={() => ($activeTabValueStore = item.value)}>
				{#if item.icon}
					<i class={item.icon}></i>
				{/if}
				{item.title}
			</button>
		</li>
	{/each}
</ul>

<slot />

<style>
	ul {
		display: flex;
		padding: var(--4, 4px);
		align-items: center;
		align-content: center;
		gap: 4px var(--4, 4px);
		flex-wrap: wrap;
		list-style: none;
		border-radius: 12px;
		background: var(--black-5, rgba(28, 28, 28, 0.05));
        margin: 0 0 1rem 0;
		width: fit-content;
	}
	li {
		/* margin-bottom: -1px; */
		display: flex;
		padding: var(--4, 4px) var(--8, 8px);
		justify-content: center;
		align-items: center;
		gap: var(--4, 4px);
		border-radius: var(--8, 8px);
	}

    li.active, li:hover {
		background: var(--black-100, #1c1c1c);
    }

    button {
        padding: 0;

    }
    li.active button, li:hover button {
        color: var(--white-100, #FFF);
    }

</style>
