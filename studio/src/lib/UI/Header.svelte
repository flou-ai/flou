<script lang="ts">
	import { page } from '$app/stores';
	import { routes } from '$lib/routes';
	import ToggleDarkMode from '$lib/UI/ToggleDarkMode.svelte';
	import { Sidebar } from 'phosphor-svelte';

	let title: string|undefined = undefined;

	$: {
		const currentPath = $page.url.pathname;
		const matchingRoute = routes.find((route: any) => currentPath.startsWith(route.path));
		title = matchingRoute?.name;
	}
</script>

<div class="header">
	<div class="left">
		<Sidebar size="1.5rem" />
		{title}
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
