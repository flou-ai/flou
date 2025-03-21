<script lang="ts">
	import Block from '$lib/UI/Block.svelte';
	import { Confetti, ArrowRight, Book, RocketLaunch } from 'phosphor-svelte';
</script>

<Block>
	<div>
		<h1>
			Welcome to Flou.ai
			<Confetti size="2.5rem" />
		</h1>
		<p>The framework for LLM-powered apps.</p>
		
		<div class="links-container">
			<a href="https://flou.ai/getting-started" class="link-card" target="_blank" rel="noopener noreferrer">
				<div class="icon-container">
					<RocketLaunch size="1.5rem" />
				</div>
				<div class="link-content">
					<h2>Getting Started</h2>
					<p>Build your first LLM-powered app</p>
				</div>
				<ArrowRight size="1rem" />
			</a>
			
			<a href="https://flou.ai/documentation" class="link-card" target="_blank" rel="noopener noreferrer">
				<div class="icon-container">
					<Book size="1.5rem" />
				</div>
				<div class="link-content">
					<h2>Documentation</h2>
					<p>Explore guides and API references</p>
				</div>
				<ArrowRight size="1rem" />
			</a>
		</div>
	</div>
</Block>

<style lang="scss">
	div {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 1.5rem;
		align-self: center;
	}

	h1 {
		margin: 0;
		font-size: 2.5rem;
		line-height: 3rem;
	}
	
	.links-container {
		display: flex;
		gap: 1rem;
		margin-top: 1.5rem;
		flex-wrap: wrap;
		justify-content: center;
	}
	
	.link-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		background: var(--white-100, #fff);
		border-radius: 0.75rem;
		border: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
		text-decoration: none;
		transition: all 0.2s ease;
		
		&:hover {
			transform: translateY(-2px);
			box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.05);
			border-color: var(--black-20, rgba(28, 28, 28, 0.2));
		}
		
		.icon-container {
			display: flex;
			align-items: center;
			justify-content: center;
			width: 2.5rem;
			height: 2.5rem;
			border-radius: 0.5rem;
			background: var(--primary-light, #f7f9fb);
			color: var(--black-100, #1c1c1c);
		}
		
		.link-content {
			flex: 1;
			
			h2 {
				margin: 0;
				color: var(--black-100, #1c1c1c);
				font-size: 1rem;
				line-height: 1.25rem;
			}
			
			p {
				margin: 0.125rem 0 0;
				color: var(--black-80, rgba(28, 28, 28, 0.8));
				font-size: 0.75rem;
				line-height: 1rem;
			}
		}
	}
</style>
