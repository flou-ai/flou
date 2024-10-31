<script lang="ts">
	import { getContext, onMount } from 'svelte';

	export let title = '';
	export let icon = '';
	export let value = Symbol();

	const items: any = getContext('items');
	const activeTabValue: any = getContext('activeTabValue');

	let item = { title, value, icon };

	onMount(() => {
		if (!$activeTabValue) {
			$activeTabValue = value;
		}

		const item = { title, value, icon };
		$items = [...$items, item];
		return () => {
			$items = $items.filter((t: any) => t.value !== value);
		};
	});

    let updateItems = () => {
		const index = $items.findIndex((t: any) => t.value === value);
		if (index !== -1) {
            $items = [
                ...$items.slice(0, index),
                { title, value, icon },
                ...$items.slice(index + 1)
            ];
        }
    }
	$: {
        title;
        value;
        icon;
        // update items in a function to prevent infinite loop
        updateItems();
	}
</script>

{#if $activeTabValue === value}
	<slot />
{/if}
