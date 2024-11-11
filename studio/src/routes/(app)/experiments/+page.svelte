<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';
	import { formatDate } from '$lib/utils';

	const listUrl = `${PUBLIC_API_BASE_URL}experiments/`;
	let experiments: any[];

	onMount(async () => {
		await getExperiments();
	});

	// Get the snapshots from the API
	let getExperiments = async () => {
		await fetch(listUrl)
			.then((response) => response.json())
			.then((data) => {
				experiments = data;
			})
			.catch((error) => {
				console.log(error);
				return [];
			});
	};
</script>

<h2>Experiments</h2>
<div class="table-header">
	<h3> </h3>
	<div class="table-controls">
		<a href="/experiments/new">
			<Plus size="1rem" /> New Experiment
		</a>
	</div>
</div>

{#if experiments === undefined}
	<p>Loading...</p>
{:else if experiments.length === 0}
	<a href="/experiments/new">Create your first experiment</a>
{:else}
	<table>
		<tr>
			<th>#</th>
			<th>Name</th>
			<th># Trials</th>
			<th>Created At</th>
			<th>Updated At</th>
			<th></th>
		</tr>
		{#each experiments as experiment}
			<tr>
				<td>{experiment.index}</td>
				<td>{experiment.name}</td>
				<td>{experiment.trials_count}</td>
				<td>{formatDate(experiment.created_at)}</td>
				<td>{formatDate(experiment.updated_at)}</td>
				<td>
					<a href="experiments/{experiment.id}">
						<ListMagnifyingGlass size="1.25rem" />
					</a>
				</td>
				<!-- <td>Updated At: {formatDate(ltm.updated_at)}</td> -->
			</tr>
		{/each}
	</table>
{/if}

<style lang="scss">
	.table-header {
		display: flex;
		justify-content: space-between;
	}
</style>
