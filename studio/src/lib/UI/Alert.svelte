<script lang="ts">
	export let level: 'info' | 'success' | 'warning' | 'danger' = 'info';
	export let icon: any = null;
	import { CheckCircle, Info, Warning, XCircle } from 'phosphor-svelte';

	$: icon = icon ?? (level === 'info' ? Info : level === 'warning' ? Warning : level === 'danger' ? XCircle : CheckCircle);
</script>

<div class={'alert ' + level}>
	<div class="icon">
		<svelte:component this={icon} size="1.5rem" />
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
    }
	.alert {
		gap: 1rem;
		align-items: center;
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
		:global(p) {
			&:not(:first-child) {
				margin-bottom: 0;
			}
			&:not(:last-child) {
				margin-top: 0;
			}
		}
	}
    .icon {
        align-self: start;
	}
</style>
