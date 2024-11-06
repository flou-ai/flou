<script lang="ts">
	import { CaretRight } from 'phosphor-svelte';

	export let ariaInvalid: any;
	export let required: any = false;
	export let value: any;
	export let options: any;
    export let emptyLabel: string = "Select";
    export let label: string = "Select";

</script>

<label for="ltm">
	{label}
	<div class="select">
		<select bind:value={value} id="ltm" aria-invalid={ariaInvalid} {required}>
			<option value="">{emptyLabel}</option>
			{#each options as [ option_value, option_name ]}
				<option value={option_value}>{option_name}</option>
			{/each}
		</select>
		<div class="passthrough">
			<CaretRight />
		</div>
	</div>
</label>

<style lang="scss">
	.select {
		display: flex;
		position: relative;
		width: 100%;
	}
	select {
		padding-right: 2rem;
	}

	.passthrough {
		position: absolute;
		right: 0;
		pointer-events: none;
	}
</style>
