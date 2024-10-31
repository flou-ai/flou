<div class="block">
	{#if $$slots.title || $$slots.controls}
		<div class="header">
			<div class="title">
				<slot name="title"></slot>
			</div>
			<div class="controls">
				<slot name="controls"></slot>
			</div>
		</div>
	{/if}
	<slot></slot>
</div>

<style lang="scss">
	.block {
		display: flex;
		flex-direction: column;
		flex: 1;
		padding: var(--24, 1.5rem);
		align-items: flex-start;
		gap: var(--28, 1.75rem);
		border-radius: var(--16, 1rem);
		background: var(--primary-light, #f7f9fb);
	}
	.header {
		display: flex;
		flex-direction: row;
		width: 100%;
		align-items: center;
		.title {
			flex-grow: 1;
		}
	}
</style>
