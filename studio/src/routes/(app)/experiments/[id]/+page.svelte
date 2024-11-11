<script lang="ts">
	import Block from '$lib/UI/Block.svelte';
	import { formatDate } from '$lib/utils';
	import InlineEditTextArea from '$lib/UI/InlineEditTextArea.svelte';

	import type { PageData } from './$types';
	export let data: PageData;

	function handleDescriptionSave(newDescription: string) {
		data.experiment.description = newDescription;
		// Add any additional logic to persist the change if necessary
	}
</script>

{#if data.experiment === undefined}
	<p>Loading...</p>
{:else}
	<div class="container">
		<Block>
			<small>name:</small>
			<h2>{data.experiment.name}</h2>
			<small>Description:</small>
			<!-- Replace static paragraph with InlineEditTextArea -->
			<InlineEditTextArea
				value={data.experiment.description}
				on:save={event => handleDescriptionSave(event.detail)}
			/>
			<small># Trials:</small>
			<p>{data.experiment.trials.length}</p>
			<dl class="details">
				<dt>Created At</dt>
				<dd>{data.experiment.created_at}</dd>
				<dt>Updated At</dt>
				<dd>{data.experiment.updated_at}</dd>
			</dl>
			<dl class="details">
				<dt>Description</dt>
				<dd>do you have a hypothesis? what are you developing or testing?</dd>
				<dt>What are your goals with this experiment?</dt>
				<dd>Goals, Success criteria, Metric optimization</dd>
				<dt>Results & Conclusions</dt>
				<dd>What are your current conclusions?</dd>
			</dl>
			<dl class="details">
				<dt>Experiment config</dt>
				<dt>Trials config: schemas & evaluators</dt>
				<dd>What data/metrics do you need in each trial to feed the evaluators?</dd>

				<dt>Segments config: schemas & evaluators</dt>
				<dd>Aggregates per segment run: add dataset or upgrade dataset</dd>
				<dt>Do you want to run your code to a dataset? Define how to apply your dataset to an LTM</dt>


			</dl>
		</Block>
		<Block>
			<h3>Trials</h3>
			<table>
				<tr>
					<th>#</th>
					<th>Name</th>
					<th>Created At</th>
					<th>Updated At</th>
					<th></th>
				</tr>
				{#each data.experiment.trials as trial}
					<tr>
						<td>{trial.index}</td>
						<td>{trial.name}</td>
						<td>{formatDate(trial.created_at)}</td>
						<td>{formatDate(trial.updated_at)}</td>
						<td>
							<!-- <a href="experiments/{experiment.id}">
						<ListMagnifyingGlass size="1.25rem" />
					</a> -->
						</td>
					</tr>
				{/each}
			</table>
		</Block>
	</div>
{/if}

<style lang="scss">
	.container {
		display: grid;
		gap: var(--20, 1.25rem);
	}
	.container > div {
		display: flex;
		flex-direction: column;
	}
	.details {
		display: grid;
		grid-auto-flow: column;
		grid-template-rows: repeat(50, min-content); /* doesn't assume 3 defs but M<50 */
		position: relative;
		--horizontal-gap: var(--28, 1.75rem);
		gap: 0 var(--horizontal-gap);
	}
	dt {
		grid-row-start: 1; /* reset, next column */

		/* 14 regular */
		font-size: 0.875rem;
		font-style: normal;
		font-weight: 400;
		line-height: 1.25rem; /* 142.857% */
		margin-bottom: var(--4, 0.25rem);
	}
	dd {
		margin: 0;

		/* 18 semibold */
		font-size: 1.125rem;
		font-style: normal;
		font-weight: 600;
		line-height: 1.5rem; /* 133.333% */
	}

	dt:not(:first-child)::before {
		content: '';
		border-right: 1px solid var(--black-10, rgba(28, 28, 28, 0.1));
		position: absolute;
		height: 100%;
		transform: translatex(calc(-1 * var(--horizontal-gap) / 2));
	}
	// .flex-column {
	// 	flex-grow: 1;
	// 	align-self: stretch;
	// 	display: flex;
	// 	flex-direction: column;
	// }
	// .info {
	// 	width: 100%;
	// 	display: flex;
	// 	flex-direction: column;
	// }
</style>
