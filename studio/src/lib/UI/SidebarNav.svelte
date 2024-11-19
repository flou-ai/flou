<script lang="ts">
	export let selected: Boolean = false;
	export let disabled: Boolean = false;
	export let route: string | undefined = undefined;

	function isExternal(url: string) {
		return url.startsWith('http://') || url.startsWith('https://');
	}
</script>

<div class="nav {selected ? 'selected' : ''} {disabled ? 'disabled' : ''}">
	{#if route && !disabled}
		<a
			href={route}
			target={isExternal(route) ? '_blank' : undefined}
			rel={isExternal(route) ? 'noopener noreferrer' : undefined}
		>
			<slot></slot>
		</a>
	{:else}
		<slot></slot>
	{/if}
</div>

<style>
	.nav {
		padding: var(--12, 0.75rem);
	}
	.nav,
	.nav a {
		display: flex;
		align-items: center;
		align-content: center;
		gap: 0.75rem var(--12, 0.75rem);
		align-self: stretch;
		flex-wrap: wrap;
	}
	a {
		text-decoration: none;
		color: var(--black-100, #1c1c1c);
		width: 100%;
	}
	.selected,
	.nav:hover {
		border-radius: var(--8, 0.5rem);
	}
	.nav:hover {
		background: var(--primary-light, #f7f9fb);

	}
	.selected {
		background: var(--primary-purple-50, #f7f9fb);
	}
	.disabled {
		opacity: 0.5;
	}
</style>
