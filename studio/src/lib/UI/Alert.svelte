<script lang="ts">
	export let level: 'info' | 'success' | 'warning' | 'danger' = 'info';
	import { CheckCircle, Info, Warning, XCircle } from 'phosphor-svelte';
</script>

<div class={'alert ' + level}>
	<div class="icon">
		{#if level === 'info'}
			<Info size="1.5rem" />
		{:else if level === 'warning'}
			<Warning size="1.5rem" />
		{:else if level === 'danger'}
			<XCircle size="1.5rem" />
		{:else if level === 'success'}
			<CheckCircle size="1.5rem" />
		{/if}
	</div>
	<div>
		<slot></slot>
	</div>
</div>

<style lang="scss">
	.info {
		background-color: var(--secondary-cyan);
	}
	.warning {
		background-color: var(--secondary-yellow);
	}
	.danger {
		background-color: var(--secondary-red);
	}
	.success {
		background-color: var(--secondary-mint);
	}
    .alert, .icon {
		display: flex;
        align-items: center;
    }
	.alert {
		gap: 1rem;
		padding: 1rem;
		border-radius: 0.5rem;
		margin-bottom: 1rem;
		color: #1c1c1c;
		& :global(a),
		& :global(p),
		& :global(span) {
			font-size: inherit;
			font-weight: inherit;
			color: #1c1c1c;
		}
	}
</style>
