<script lang="ts">
	import Sidebar from '$lib/UI/Sidebar.svelte';
	import Header from '$lib/UI/Header.svelte';
	import '../../global.scss';
</script>

<div class="container">
    <nav>
        <Sidebar></Sidebar>
    </nav>
    <header><Header/></header>
    <main>
        <slot></slot>
    </main>
</div>

<style>
	.container {
		display: grid;
		grid-template-areas:
			'nav header'
			'nav content';
		grid-template-columns: auto 1fr ;
		grid-template-rows: auto 1fr ;
        height: 100vh;
        background: var(--white-100, #1c1c1c);
		max-width: 100vw;
	}
	header {
		grid-area: header;
	}

	nav {
		grid-area: nav;
		margin-left: 0.5rem;
	}

	main {
		grid-area: content;
		padding: var(--20, 1.25rem);
        overflow: scroll;
	}
</style>
