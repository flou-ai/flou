<script lang="ts">
	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';
	import Block from '$lib/UI/Block.svelte';
	import { formatDate } from '$lib/utils';
	import InlineEditTextArea from '$lib/UI/InlineEditTextArea.svelte';

	import type { PageData } from './$types';
	export let data: PageData;

	function handleDescriptionSave(newDescription: string) {
		data.experiment.description = newDescription;
		// Add any additional logic to persist the change if necessary
	}

	function isRollback(trialIndex: number): boolean {
		const trial = data.experiment.trials[trialIndex];
		return data.experiment.trials.some(
			(t: any) => t.ltm_id === trial.ltm_id && new Date(t.created_at) > new Date(trial.created_at)
		);
	}
</script>

{#if data.experiment === undefined}
	<p>Loading...</p>
{:else}
	<div class="container">
		<Block>
			<h2>
				#{data.experiment.index}
				<InlineEditTextArea
					value={data.experiment.name}
					on:save={(event) => handleDescriptionSave(event.detail)}
				/>
			</h2>
			<dl class="details">
				<div>
					<dt># Trials</dt>
					<dd>{data.experiment.trials.length}</dd>
				</div>

				<div>
					<dt>Created At</dt>
					<dd>{formatDate(data.experiment.created_at)}</dd>
				</div>
				<div>
					<dt>Updated At</dt>
					<dd>{formatDate(data.experiment.updated_at)}</dd>
				</div>
			</dl>
			<dl class="details">
				<div>
					<dt class="label">Description</dt>
					<dd>
						<InlineEditTextArea
							value={data.experiment.description}
							on:save={(event) => handleDescriptionSave(event.detail)}
						/>
					</dd>
				</div>
			</dl>
			<!-- <dl class="details">
				<dt>Description</dt>

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
				<dt>
					Do you want to run your code to a dataset? Define how to apply your dataset to an LTM
				</dt>
			</dl> -->
		</Block>
		<Block>
			<div class="table-header">
				<h3>Trials</h3>
				<div class="table-controls">
					<a href="/experiments/{data.experiment.id}/trials/new">
						<Plus size="1rem" /> New Trial
					</a>
				</div>
			</div>
			<table>
				<tr>
					<th>#</th>
					<th>Name</th>
					<th>Created At</th>
					<th>Updated At</th>
					<th></th>
				</tr>
				{#each data.experiment.trials as trial, i}
					<tr>
						<td>{i + 1}</td>
						<td>{trial.name} #{trial.index}</td>
						<td>{formatDate(trial.created_at)}</td>
						<td>{formatDate(trial.updated_at)}</td>
						<td>
							{#if isRollback(i)}
								<a href="/inspect/{trial.ltm_id}?rollback={trial.rollback_index}">
									<ListMagnifyingGlass size="1.25rem" />
								</a>
							{:else}
								<a href="/playground/{trial.ltm_id}">
									<ListMagnifyingGlass size="1.25rem" />
								</a>
							{/if}
						</td>
					</tr>
				{/each}
			</table>
		</Block>
	</div>
{/if}

<style lang="scss">
	:root {
		--horizontal-gap: 3rem;
	}

	.container {
		display: grid;
		gap: var(--20, 1.25rem);
	}
	.container > div {
		display: flex;
		flex-direction: column;
		position: relative;
	}
	.details {
		display: flex;
		gap: var(--horizontal-gap);
		flex-wrap: wrap;
	}

	.details > div {
		position: relative;
	}
	dt {
		/* 14 regular */
		font-size: 0.75rem;
		line-height: 1.25rem; /* 142.857% */
		margin-bottom: var(--4, 0.25rem);
		color: var(--black-40, rgba(28, 28, 28, 0.4));
	}
	dd {
		margin: 0;
		line-height: 1.5rem; /* 133.333% */
	}

	dl > div:not(:first-child) > dt::before {
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
