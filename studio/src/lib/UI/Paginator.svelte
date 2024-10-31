 <script lang="ts">
    import { CaretLeft, CaretRight, CaretLineLeft, CaretLineRight } from 'phosphor-svelte';
    import { createEventDispatcher } from 'svelte';

    export let index = 0;
    export let collection: any[] = [];

    let dispatch = createEventDispatcher();

    let setIndex = (newIndex: number) => {
		newIndex = Math.max(0, Math.min(newIndex, collection.length - 1));
        if (newIndex !== index) {
            index = newIndex;
        }
    };

    // $: index, setIndex(index);

 </script>

	<div class="paginator">
		<button
			on:click={() => {
				setIndex(0);
			}}
			disabled={index === 0}
		>
			<CaretLineLeft size="1.25rem" />
		</button>
		<button
			on:click={() => {
				setIndex(index - 1);
			}}
			disabled={index === 0}
		>
			<CaretLeft size="1.25rem" />
		</button>

		{#if index - 2 >= 0}
			<button
				on:click={() => {
					setIndex(index - 2);
				}}
			>
				{index - 1}
			</button>
		{/if}

		{#if index - 1 >= 0}
			<button
				on:click={() => {
					setIndex(index - 1);
				}}
			>
				{index}
			</button>
		{/if}

		<button class="selected">
			{index + 1}
		</button>

		{#if index + 1 < collection.length}
			<button
				on:click={() => {
					setIndex(index + 1);
				}}
			>
				{index + 2}
			</button>
		{/if}

		{#if index + 2 < collection.length}
			<button
				on:click={() => {
					setIndex(index + 2);
				}}
			>
				{index + 3}
			</button>
		{/if}

		<button
			on:click={() => {
				setIndex(index + 1);
			}}
			disabled={index === collection.length - 1}
		>
			<CaretRight size="1.25rem" />
		</button>

		<button
			on:click={() => {
				setIndex(collection.length - 1);
			}}
			disabled={index === collection.length - 1}
		>
			<CaretLineRight size="1.25rem" />
		</button>
	</div>


<style lang="scss">
	.paginator {
		display: flex;
		gap: 0.5rem var(--8, 0.5rem);
		align-items: center;
		font-size: 0.875rem;
		font-style: normal;
		font-weight: 400;
		line-height: 1.25rem; /* 142.857% */
	}
	.paginator button {
		width: 1.75rem;
		aspect-ratio: 1;
	}
</style>
