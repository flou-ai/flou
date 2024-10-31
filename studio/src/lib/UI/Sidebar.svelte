<script lang="ts">
	import Logo from '$lib/UI/Logo.svelte';
	import SidebarNav from '$lib/UI/SidebarNav.svelte';
	import { User } from 'phosphor-svelte';
	import { routes } from '$lib/routes';
</script>

<div class="sidebar">
	<Logo />

	{#each routes as route}
		{#if route.title}
			<p class="nav-title">{route.name}</p>
		{:else if route.showInNav !== false && !route.section}
			<SidebarNav route={route.path} disabled={route.disabled}>
				<svelte:component this={route.icon} size="1.5rem" />
				{route.name}
			</SidebarNav>
		{/if}
	{/each}

	<div class="bottom">
		<SidebarNav disabled>
			<div class="bg-rounded">
				<User />
			</div>
			My profile
		</SidebarNav>
	</div>
</div>

<style>
	.sidebar {
		display: flex;
		width: 13.25rem;
		padding: var(--28, 1.75rem) var(--16, 1rem);
		flex-direction: column;
		align-items: flex-start;
		flex-shrink: 0;
		border-right: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
		height: 100%;
		box-sizing: border-box;
	}
	.nav-title {
		color: var(--black-40, rgba(28, 28, 28, 0.4));
		/* 14 Regular */
		font-size: 0.875rem;
		line-height: 1.25rem; /* 142.857% */
		margin-top: 2rem;
	}
	.bottom {
		margin-top: auto;
		display: flex;
		flex-direction: column;
		width: 100%;
	}

	.bg-rounded {
		border-radius: var(--80, 5rem);
		background: var(--black-5, rgba(28, 28, 28, 0.05));
		display: flex;
		width: var(--24, 1.5rem);
		height: var(--24, 1.5rem);
		justify-content: center;
		align-items: center;
	}
</style>
