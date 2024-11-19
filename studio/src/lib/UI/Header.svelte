<script lang="ts">
	import { page } from '$app/stores';
	import { getCurrentRoute } from '$lib/routes';
	import ToggleDarkMode from '$lib/UI/ToggleDarkMode.svelte';

	let name: string|undefined = undefined;
	let icon: any = undefined;

	$: {
		$page;
		const route = getCurrentRoute();
		if (route) {
			({ name, icon } = route);
		}
	}
</script>

<div class="header">
	<div class="left">
		<svelte:component this={icon} size="1.5rem" />
		{name}
	</div>
	<div class="right">
		<ToggleDarkMode />
	</div>
</div>

<style>
	.header {
		display: flex;
		padding: var(--20, 1.25rem) var(--28, 1.75rem);
		justify-content: space-between;
		align-items: center;
		border-bottom: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
	}
	.header div {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
</style>
