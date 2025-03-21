<script lang="ts">
	import { onMount } from 'svelte';
	import { PUBLIC_API_BASE_URL } from '$env/static/public';

	import { ListMagnifyingGlass, Plus } from 'phosphor-svelte';
	import { formatDate } from '$lib/utils';

	const listUrl = `${PUBLIC_API_BASE_URL}datasets/`;
	let datasets: any[];

	onMount(async () => {
		await getDatasets();
	});

	// Get the datasets from the API
	let getDatasets = async () => {
		await fetch(listUrl)
			.then((response) => response.json())
			.then((data) => {
				datasets = data;
			})
			.catch((error) => {
				console.log(error);
				return [];
			});
	};
</script>

<div class="table-header">
	<h2>Datasets</h2>
	<div class="table-controls">
		<a href="/datasets/new">
			<Plus size="1rem" /> New Dataset
		</a>
	</div>
</div>

{#if datasets === undefined}
	<p>Loading...</p>
{:else if datasets.length === 0}
	<a href="/datasets/new">Create your first dataset</a>
{:else}
	<table>
		<tr>
			<th>#</th>
			<th>Name</th>
			<th># Items</th>
			<th>Created At</th>
			<th>Updated At</th>
			<th></th>
		</tr>
		{#each datasets as dataset}
			<tr>
				<td>{dataset.index}</td>
				<td>{dataset.name}</td>
				<td>{dataset.items_count}</td>
				<td>{formatDate(dataset.created_at)}</td>
				<td>{formatDate(dataset.updated_at)}</td>
				<td>
					<a href="datasets/{dataset.id}">
						<ListMagnifyingGlass size="1.25rem" />
					</a>
				</td>
			</tr>
		{/each}
	</table>
{/if}

<style lang="scss">
</style> 