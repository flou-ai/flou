<script lang="ts">
	import { onMount } from 'svelte';
	import { SunDim, Moon } from 'phosphor-svelte';
	let theme: string;

	onMount(() => {
		if (typeof window !== 'undefined') {
			let localStorageTheme: string | null = localStorage.getItem('theme');
			if (localStorageTheme) {
				theme = localStorageTheme;
			} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
				theme = 'dark';
			} else {
				theme = 'light';
			}
		}
	});

	const toggleTheme = () => {
		theme = theme === 'light' ? 'dark' : 'light';
		localStorage.setItem('theme', theme);
	};

	$: {
		if (typeof window !== 'undefined') {
			document.documentElement.setAttribute('data-theme', theme);
		}
	}
</script>

<button type="button" on:click={toggleTheme}>
	<div class="light">
		<SunDim size="1.5rem" class="light" />
	</div>
	<div class="dark">
		<Moon size="1.5rem" class="dark" />
	</div>
</button>

<style>
	button {
		background: none;
		border: none;
		padding: 0;
		color: var(--black-100, #fff);
	}
</style>
