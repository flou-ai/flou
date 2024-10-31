<script lang="ts">
	import Block from '$lib/UI/Block.svelte';
	import { Confetti } from 'phosphor-svelte';
</script>

<Block>
	<div>
		<h1>
			Welcome to Flou.ai
			<Confetti size="3rem" />
		</h1>
		<p>The framework for LLM-powered apps.</p>
	</div>
</Block>

<style lang="scss">
	div {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem;
		align-self: center;
	}

	h1 {
		margin: 0;
	}
</style>
